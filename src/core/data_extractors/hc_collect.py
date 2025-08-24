# hc_collect.py
import os, json, time, csv, io
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Tuple
import requests
from tenacity import retry, wait_exponential, stop_after_attempt
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

BASE_URL   = os.getenv("HCG_BASE_URL", "https://api.hcgateway.shuchir.dev").rstrip("/")
USERNAME   = os.getenv("HCG_USERNAME")
PASSWORD   = os.getenv("HCG_PASSWORD")
TICK_SEC   = int(os.getenv("TICK_SECONDS", "180"))
METHODS_MODE = os.getenv("METHODS", "CORE").upper()

CORE_METHODS = ["steps", "heartRate", "sleepSession", "distance", "totalCaloriesBurned"]
ALL_METHODS = [
  "activeCaloriesBurned","basalBodyTemperature","basalMetabolicRate","bloodGlucose","bloodPressure",
  "bodyFat","bodyTemperature","boneMass","cervicalMucus","distance","exerciseSession","elevationGained",
  "floorsClimbed","heartRate","height","hydration","leanBodyMass","menstruationFlow","menstruationPeriod",
  "nutrition","ovulationTest","oxygenSaturation","power","respiratoryRate","restingHeartRate","sleepSession",
  "speed","steps","stepsCadence","totalCaloriesBurned","vo2Max","weight","wheelchairPushes"
]
METHODS = ALL_METHODS if METHODS_MODE == "ALL" else CORE_METHODS

DATA_DIR  = "data"
STATE_DIR = "state"
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(STATE_DIR, exist_ok=True)

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def load_state(method: str) -> Dict[str, Any]:
    path = os.path.join(STATE_DIR, f"{method}.json")
    if not os.path.exists(path):
        # Por defecto: traer últimas 24h si no hay estado previo
        since = (datetime.now(timezone.utc) - timedelta(hours=24)).replace(microsecond=0).isoformat()
        return {"last_since": since, "seen_ids": []}
    with open(path, "r") as f:
        return json.load(f)

def save_state(method: str, state: Dict[str, Any]) -> None:
    path = os.path.join(STATE_DIR, f"{method}.json")
    with open(path, "w") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

class TokenBundle:
    def __init__(self, token: str, refresh: str, expiry: str):
        self.token = token
        self.refresh = refresh
        # expiry ISO -> datetime
        self.expiry_dt = datetime.fromisoformat(expiry.replace("Z", "+00:00"))

    def is_expiring(self, buffer_minutes: int = 5) -> bool:
        return datetime.now(timezone.utc) + timedelta(minutes=buffer_minutes) >= self.expiry_dt

def login(username: str, password: str) -> TokenBundle:
    """
    Pura: recibe credenciales y devuelve {token, refresh, expiry}.
    POST /api/v2/login
    """
    url = f"{BASE_URL}/api/v2/login"
    r = requests.post(url, json={"username": username, "password": password}, timeout=30)
    r.raise_for_status()
    data = r.json()
    return TokenBundle(data["token"], data["refresh"], data["expiry"])

def refresh_token(refresh: str) -> TokenBundle:
    """
    Pura: recibe refresh y devuelve {token, refresh, expiry} nuevos.
    POST /api/v2/refresh
    """
    url = f"{BASE_URL}/api/v2/refresh"
    r = requests.post(url, json={"refresh": refresh}, timeout=30)
    r.raise_for_status()
    data = r.json()
    return TokenBundle(data["token"], data["refresh"], data["expiry"])

class TokenManager:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.bundle: TokenBundle = login(username, password)

    def ensure(self) -> str:
        """Devuelve un token válido, refrescando si se acerca el expiry."""
        if self.bundle.is_expiring():
            self.bundle = refresh_token(self.bundle.refresh)
        return self.bundle.token

@retry(wait=wait_exponential(multiplier=1, min=1, max=30), stop=stop_after_attempt(3))
def fetch_method(method: str, bearer: str, queries: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    POST /api/v2/fetch/{method}
    queries: dict Mongo-style. Ej.: {"start": {"$gte": "2025-08-23T00:00:00Z"}}
    """
    url = f"{BASE_URL}/api/v2/fetch/{method}"
    headers = {"Authorization": f"Bearer {bearer}", "Content-Type": "application/json"}
    r = requests.post(url, headers=headers, json={"queries": queries}, timeout=60)
    if r.status_code == 401:
        # Que falle para que el @retry no haga busy loop; el caller manejará refresh
        raise requests.HTTPError("401 Unauthorized", response=r)
    r.raise_for_status()
    return r.json()

def build_query_since(since_iso: str) -> Dict[str, Any]:
    """
    Filtra por start >= since
    """
    return {"start": {"$gte": since_iso}}

def append_csv(method: str, rows: List[Dict[str, Any]]) -> None:
    """
    Guarda incrementalmente. Estructura CSV:
    _id, id, start, end, app, data_json, ingested_at
    """
    if not rows:
        return
    csv_path = os.path.join(DATA_DIR, f"{method}.csv")
    records = []
    stamp = utc_now_iso()
    for rec in rows:
        records.append({
            "_id": rec.get("_id"),
            "id": rec.get("id"),
            "start": rec.get("start"),
            "end": rec.get("end"),
            "app": rec.get("app"),
            "data_json": json.dumps(rec.get("data", {}), ensure_ascii=False),
            "ingested_at": stamp,
        })
    df = pd.DataFrame.from_records(records)
    # Si ya existe, concat y de-dup por _id
    if os.path.exists(csv_path):
        old = pd.read_csv(csv_path)
        merged = pd.concat([old, df], ignore_index=True)
        merged = merged.drop_duplicates(subset=["_id"], keep="last")
        merged.to_csv(csv_path, index=False)
    else:
        df.drop_duplicates(subset=["_id"], keep="last").to_csv(csv_path, index=False)

def collect_once(tm: TokenManager, method: str) -> Tuple[int, str]:
    """
    Corre una ingesta de un método:
    - Lee estado (last_since)
    - Hace fetch con start >= last_since
    - Dedup y guarda CSV
    - Actualiza estado con el max(end|start) observado
    Devuelve (nuevos_registros, nuevo_last_since)
    """
    st = load_state(method)
    since = st.get("last_since")
    # 1) token válido
    token = tm.ensure()
    # 2) fetch con manejo de 401 → refresh inmediato y reintento 1 vez
    try:
        items = fetch_method(method, token, build_query_since(since))
    except requests.HTTPError as e:
        if e.response is not None and e.response.status_code == 401:
            tm.bundle = refresh_token(tm.bundle.refresh)
            items = fetch_method(method, tm.bundle.token, build_query_since(since))
        else:
            raise
    if not isinstance(items, list):
        items = []
    # 3) ordena por (end|start)
    def end_or_start_iso(x):
        return x.get("end") or x.get("start") or "1970-01-01T00:00:00Z"
    items.sort(key=end_or_start_iso)
    # 4) guarda CSV incremental con dedup
    before = 0
    append_csv(method, items)
    # 5) actualiza last_since al máximo (end|start)
    if items:
        new_since = end_or_start_iso(items[-1])
        st["last_since"] = new_since
        save_state(method, st)
        return (len(items), new_since)
    else:
        return (0, since)

def main():
    if not USERNAME or not PASSWORD:
        raise SystemExit("Configura HCG_USERNAME y HCG_PASSWORD en .env")
    tm = TokenManager(USERNAME, PASSWORD)
    print(f"[{utc_now_iso()}] Iniciando collector. Métodos: {METHODS_MODE} ({len(METHODS)})")
    while True:
        cycle_start = utc_now_iso()
        total = 0
        for m in METHODS:
            try:
                n, new_since = collect_once(tm, m)
                total += n
                print(f"[{cycle_start}] {m:<20} +{n} (since={new_since})")
            except Exception as e:
                print(f"[{cycle_start}] {m:<20} ERROR: {e}")
        # Espera al próximo tick
        time.sleep(TICK_SEC)

if __name__ == "__main__":
    main()
