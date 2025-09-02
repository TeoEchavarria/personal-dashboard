# hc_collect.py
import os, json, time, csv, io
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Tuple
import requests
from tenacity import retry, wait_exponential, stop_after_attempt
import pandas as pd

# Import configuration from centralized config module
from ..utils.config import config

# Load configuration
hcg_config = config.get_hcg_config()
data_config = config.get_data_config()
api_config = config.get_api_config()

BASE_URL = hcg_config['base_url']
USERNAME = hcg_config['username']
PASSWORD = hcg_config['password']
TICK_SEC = hcg_config['tick_seconds']
METHODS_MODE = hcg_config['methods_mode']

# Get methods from configuration
CORE_METHODS = config.get_hcg_core_methods()
ALL_METHODS = config.get_hcg_all_methods()
METHODS = config.get_hcg_methods()

DATA_DIR = data_config['directory']
STATE_DIR = data_config['state_directory']
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(STATE_DIR, exist_ok=True)

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def parse_iso_datetime(iso_string: str) -> datetime:
    """
    Parse ISO datetime string and ensure it's timezone-aware (UTC).
    
    Args:
        iso_string: ISO format datetime string
        
    Returns:
        Timezone-aware datetime object in UTC
    """
    if not iso_string:
        raise ValueError("Empty datetime string")
    
    # Handle Z suffix (Zulu time = UTC)
    if iso_string.endswith('Z'):
        dt = datetime.fromisoformat(iso_string.replace("Z", "+00:00"))
    else:
        dt = datetime.fromisoformat(iso_string)
    
    # Ensure timezone-aware (assume UTC if naive)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    return dt

def ensure_utc_aware(dt: datetime) -> datetime:
    """
    Ensure a datetime object is timezone-aware (UTC).
    
    Args:
        dt: datetime object
        
    Returns:
        Timezone-aware datetime in UTC
    """
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt

def load_state(method: str) -> Dict[str, Any]:
    path = os.path.join(STATE_DIR, f"{method}.json")
    if not os.path.exists(path):
        # Por defecto: traer últimas 24h si no hay estado previo
        since = (datetime.now(timezone.utc) - timedelta(hours=24)).replace(microsecond=0).isoformat()
        return {"last_since": since, "seen_ids": []}
    
    with open(path, "r") as f:
        state = json.load(f)
        
    # Validate and fix the last_since format if needed
    if "last_since" in state and state["last_since"]:
        try:
            # Try to parse and reformat to ensure consistency
            dt = parse_iso_datetime(state["last_since"])
            state["last_since"] = dt.isoformat()
        except Exception:
            print(f"Warning: Invalid last_since format for {method}: {state['last_since']}")
            # Reset to 24h ago if invalid
            since = (datetime.now(timezone.utc) - timedelta(hours=24)).replace(microsecond=0).isoformat()
            state["last_since"] = since
    
    return state

def save_state(method: str, state: Dict[str, Any]) -> None:
    path = os.path.join(STATE_DIR, f"{method}.json")
    
    # Ensure last_since is in proper format before saving
    if "last_since" in state and state["last_since"]:
        try:
            # Parse and reformat to ensure consistency
            dt = parse_iso_datetime(state["last_since"])
            state["last_since"] = dt.isoformat()
        except Exception:
            print(f"Warning: Could not normalize last_since for {method}: {state['last_since']}")
    
    with open(path, "w") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

class TokenBundle:
    def __init__(self, token: str, refresh: str, expiry: str):
        self.token = token
        self.refresh = refresh
        # Parse expiry ISO string and ensure it's timezone-aware
        self.expiry_dt = parse_iso_datetime(expiry)

    def is_expiring(self, buffer_minutes: int = 5) -> bool:
        # Both datetimes are now guaranteed to be timezone-aware
        now_utc = datetime.now(timezone.utc)
        return now_utc + timedelta(minutes=buffer_minutes) >= self.expiry_dt

def login(username: str, password: str) -> TokenBundle:
    """
    Pura: recibe credenciales y devuelve {token, refresh, expiry}.
    POST /api/v2/login
    """
    url = f"{BASE_URL}/api/v2/login"
    r = requests.post(url, json={"username": username, "password": password}, timeout=api_config['timeout'])
    r.raise_for_status()
    data = r.json()
    return TokenBundle(data["token"], data["refresh"], data["expiry"])

def refresh_token(refresh: str) -> TokenBundle:
    """
    Pura: recibe refresh y devuelve {token, refresh, expiry} nuevos.
    POST /api/v2/refresh
    """
    url = f"{BASE_URL}/api/v2/refresh"
    r = requests.post(url, json={"refresh": refresh}, timeout=api_config['timeout'])
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
    r = requests.post(url, headers=headers, json={"queries": queries}, timeout=api_config['timeout'] * 2)
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

def build_query_date_range(start_date: str, end_date: str = None) -> Dict[str, Any]:
    """
    Filtra por rango de fechas.
    
    Args:
        start_date: Fecha de inicio en formato ISO (ej: "2024-01-01T00:00:00Z")
        end_date: Fecha de fin en formato ISO (opcional, si no se proporciona usa fecha actual)
    
    Returns:
        Query dict con filtros de fecha
    """
    query = {"start": {"$gte": start_date}}
    
    if end_date:
        # Si se proporciona end_date, filtramos que start sea menor o igual al end_date
        query["start"]["$lte"] = end_date
    
    return query

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

def collect_once(tm: TokenManager, method: str, start_date: str = None, end_date: str = None) -> Tuple[int, str]:
    """
    Corre una ingesta de un método:
    - Lee estado (last_since) o usa start_date si se proporciona
    - Hace fetch con filtros de fecha apropiados
    - Dedup y guarda CSV
    - Actualiza estado con el max(end|start) observado (solo si no se usan fechas específicas)
    Devuelve (nuevos_registros, nuevo_last_since)
    """
    st = load_state(method)
    
    # Determinar el query a usar
    if start_date:
        # Si se proporciona start_date, usar query de rango
        query = build_query_date_range(start_date, end_date)
        since = start_date  # Para el retorno
        update_state = False  # No actualizar estado cuando se usan fechas específicas
    else:
        # Comportamiento original: usar last_since del estado
        since = st.get("last_since")
        query = build_query_since(since)
        update_state = True
    
    # 1) token válido
    token = tm.ensure()
    # 2) fetch con manejo de 401 → refresh inmediato y reintento 1 vez
    try:
        items = fetch_method(method, token, query)
    except requests.HTTPError as e:
        if e.response is not None and e.response.status_code == 401:
            tm.bundle = refresh_token(tm.bundle.refresh)
            items = fetch_method(method, tm.bundle.token, query)
        else:
            raise
    if not isinstance(items, list):
        items = []
    # 3) ordena por (end|start)
    def end_or_start_iso(x):
        return x.get("end") or x.get("start") or "1970-01-01T00:00:00Z"
    items.sort(key=end_or_start_iso)
    # 4) guarda CSV incremental con dedup
    append_csv(method, items)
    # 5) actualiza last_since al máximo (end|start) solo si no se usan fechas específicas
    if items and update_state:
        new_since = end_or_start_iso(items[-1])
        st["last_since"] = new_since
        save_state(method, st)
        return (len(items), new_since)
    else:
        # Si se usan fechas específicas o no hay items, retornar el since original
        return (len(items), since)

def initialize_token_manager() -> TokenManager:
    """Initialize and return a TokenManager instance."""
    if not config.validate_hcg_config():
        raise ValueError("Configura HCG_USERNAME y HCG_PASSWORD en .env")
    return TokenManager(USERNAME, PASSWORD)

def collect_method_data(method: str, tm: TokenManager = None, start_date: str = None, end_date: str = None) -> Tuple[int, str, str]:
    """
    Collect data for a single method.
    
    Args:
        method: Health Connect method name
        tm: TokenManager instance (will create new if None)
        start_date: Start date for data collection (ISO format, optional)
        end_date: End date for data collection (ISO format, optional)
    
    Returns:
        Tuple of (new_records_count, new_last_since, error_message)
    """
    if tm is None:
        tm = initialize_token_manager()
    
    try:
        n, new_since = collect_once(tm, method, start_date, end_date)
        return n, new_since, ""
    except Exception as e:
        return 0, "", str(e)

def collect_all_methods_data(tm: TokenManager = None, start_date: str = None, end_date: str = None) -> Dict[str, Tuple[int, str, str]]:
    """
    Collect data for all configured methods.
    
    Args:
        tm: TokenManager instance (will create new if None)
        start_date: Start date for data collection (ISO format, optional)
        end_date: End date for data collection (ISO format, optional)
    
    Returns:
        Dictionary with method names as keys and (count, since, error) as values
    """
    if tm is None:
        tm = initialize_token_manager()
    
    results = {}
    for method in METHODS:
        results[method] = collect_method_data(method, tm, start_date, end_date)
    
    return results

def get_method_raw_data(method: str, limit: int = 5) -> pd.DataFrame:
    """
    Get raw data for a method (first N rows from CSV).
    
    Args:
        method: Health Connect method name
        limit: Number of rows to return
    
    Returns:
        DataFrame with raw data
    """
    csv_path = os.path.join(DATA_DIR, f"{method}.csv")
    
    if not os.path.exists(csv_path):
        return pd.DataFrame()
    
    try:
        df = pd.read_csv(csv_path)
        return df.head(limit)
    except Exception as e:
        print(f"Error reading {method} data: {e}")
        return pd.DataFrame()

def get_method_last_update(method: str) -> str:
    """
    Get the last update timestamp for a method.
    
    Args:
        method: Health Connect method name
    
    Returns:
        Last update timestamp or "Never" if no data
    """
    state = load_state(method)
    last_since = state.get("last_since", "")
    
    if not last_since:
        return "Never"
    
    try:
        # Use utility function to parse datetime consistently
        dt = parse_iso_datetime(last_since)
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    except Exception as e:
        # If parsing fails, return the raw string with error info
        return f"Invalid date: {last_since}"

def get_all_methods_status() -> Dict[str, Dict[str, Any]]:
    """
    Get status information for all methods.
    
    Returns:
        Dictionary with method status information
    """
    status = {}
    
    for method in METHODS:
        csv_path = os.path.join(DATA_DIR, f"{method}.csv")
        record_count = 0
        
        if os.path.exists(csv_path):
            try:
                df = pd.read_csv(csv_path)
                record_count = len(df)
            except Exception:
                record_count = 0
        
        status[method] = {
            "last_update": get_method_last_update(method),
            "record_count": record_count,
            "has_data": record_count > 0
        }
    
    return status
