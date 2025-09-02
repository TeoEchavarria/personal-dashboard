"""
Health Analytics Module
Advanced analytics for health and biometric data visualization.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import json
import os
from ..utils.config import config

def get_health_data(method: str, days: int = 30) -> pd.DataFrame:
    """
    Get health data for a specific method from the last N days.
    
    Args:
        method: Health Connect method name
        days: Number of days to look back
    
    Returns:
        DataFrame with processed health data
    """
    data_config = config.get_data_config()
    csv_path = os.path.join(data_config['directory'], f"{method}.csv")
    
    if not os.path.exists(csv_path):
        return pd.DataFrame()
    
    try:
        df = pd.read_csv(csv_path)
        if df.empty:
            return df
        
        # Parse dates with flexible format
        df['start'] = pd.to_datetime(df['start'], format='ISO8601', errors='coerce')
        df['ingested_at'] = pd.to_datetime(df['ingested_at'], format='ISO8601', errors='coerce')
        
        # Remove rows with invalid dates
        df = df.dropna(subset=['start'])
        
        # Filter by date range - ensure timezone compatibility
        cutoff_date = pd.Timestamp(datetime.now() - timedelta(days=days)).tz_localize('UTC')
        
        # Make sure start column has timezone info
        if df['start'].dt.tz is None:
            df['start'] = df['start'].dt.tz_localize('UTC')
        else:
            df['start'] = df['start'].dt.tz_convert('UTC')
            
        df = df[df['start'] >= cutoff_date]
        
        # Parse JSON data
        if 'data_json' in df.columns:
            df['parsed_data'] = df['data_json'].apply(lambda x: json.loads(x) if pd.notna(x) else {})
        
        return df.sort_values('start')
    
    except Exception as e:
        print(f"Error loading health data for {method}: {e}")
        return pd.DataFrame()

def extract_biometric_value(df: pd.DataFrame, method: str, value_key: str) -> List[float]:
    """
    Extract specific biometric values from parsed data.
    
    Args:
        df: DataFrame with parsed health data
        method: Health method name
        value_key: Key to extract from the data
    
    Returns:
        List of extracted values
    """
    values = []
    if 'parsed_data' not in df.columns:
        return values
    
    for _, row in df.iterrows():
        try:
            data = row['parsed_data']
            if method in data and value_key in data[method]:
                values.append(float(data[method][value_key]))
        except (KeyError, ValueError, TypeError):
            continue
    
    return values

def calculate_body_composition_metrics() -> Dict[str, Any]:
    """
    Calculate comprehensive body composition metrics.
    
    Returns:
        Dictionary with body composition analysis
    """
    metrics = {
        'weight': {'current': None, 'trend': None, 'data': []},
        'height': {'current': None, 'data': []},
        'bodyFat': {'current': None, 'trend': None, 'data': []},
        'leanBodyMass': {'current': None, 'trend': None, 'data': []},
        'bmi': {'current': None, 'category': None},
        'basalMetabolicRate': {'current': None, 'trend': None, 'data': []},
        'last_updated': None
    }
    
    # Weight data
    weight_df = get_health_data('weight', days=90)
    if not weight_df.empty:
        weights = extract_biometric_value(weight_df, 'weight', 'inKilograms')
        if weights:
            metrics['weight']['current'] = weights[-1]
            metrics['weight']['data'] = weights
            metrics['weight']['trend'] = calculate_trend(weights)
            metrics['last_updated'] = weight_df['start'].iloc[-1].isoformat()
    
    # Height data
    height_df = get_health_data('height', days=365)  # Height changes rarely
    if not height_df.empty:
        heights = extract_biometric_value(height_df, 'height', 'inMeters')
        if heights:
            metrics['height']['current'] = heights[-1]
            metrics['height']['data'] = heights
    
    # Body fat data
    bodyfat_df = get_health_data('bodyFat', days=90)
    if not bodyfat_df.empty:
        bodyfats = extract_biometric_value(bodyfat_df, 'bodyFat', 'percentage')
        if bodyfats:
            metrics['bodyFat']['current'] = bodyfats[-1]
            metrics['bodyFat']['data'] = bodyfats
            metrics['bodyFat']['trend'] = calculate_trend(bodyfats)
    
    # Lean body mass data
    leanmass_df = get_health_data('leanBodyMass', days=90)
    if not leanmass_df.empty:
        leanmass = extract_biometric_value(leanmass_df, 'leanBodyMass', 'inKilograms')
        if leanmass:
            metrics['leanBodyMass']['current'] = leanmass[-1]
            metrics['leanBodyMass']['data'] = leanmass
            metrics['leanBodyMass']['trend'] = calculate_trend(leanmass)
    
    # BMR data
    bmr_df = get_health_data('basalMetabolicRate', days=90)
    if not bmr_df.empty:
        bmr_values = extract_biometric_value(bmr_df, 'basalMetabolicRate', 'inKilocaloriesPerDay')
        if bmr_values:
            metrics['basalMetabolicRate']['current'] = bmr_values[-1]
            metrics['basalMetabolicRate']['data'] = bmr_values
            metrics['basalMetabolicRate']['trend'] = calculate_trend(bmr_values)
    
    # Calculate BMI
    if metrics['weight']['current'] and metrics['height']['current']:
        weight_kg = metrics['weight']['current']
        height_m = metrics['height']['current']
        bmi = weight_kg / (height_m ** 2)
        metrics['bmi']['current'] = round(bmi, 1)
        metrics['bmi']['category'] = get_bmi_category(bmi)
    
    return metrics

def calculate_vital_signs_metrics() -> Dict[str, Any]:
    """
    Calculate vital signs and cardiovascular metrics.
    
    Returns:
        Dictionary with vital signs analysis
    """
    metrics = {
        'heartRate': {'current': None, 'resting': None, 'trend': None, 'data': []},
        'bloodPressure': {'systolic': None, 'diastolic': None, 'data': []},
        'oxygenSaturation': {'current': None, 'data': []},
        'respiratoryRate': {'current': None, 'data': []},
        'bodyTemperature': {'current': None, 'data': []},
        'last_updated': None
    }
    
    # Heart rate data
    hr_df = get_health_data('heartRate', days=30)
    if not hr_df.empty:
        heart_rates = extract_biometric_value(hr_df, 'heartRate', 'beatsPerMinute')
        if heart_rates:
            metrics['heartRate']['current'] = heart_rates[-1]
            metrics['heartRate']['data'] = heart_rates
            metrics['heartRate']['trend'] = calculate_trend(heart_rates)
            metrics['last_updated'] = hr_df['start'].iloc[-1].isoformat()
    
    # Resting heart rate
    rhr_df = get_health_data('restingHeartRate', days=30)
    if not rhr_df.empty:
        resting_hrs = extract_biometric_value(rhr_df, 'restingHeartRate', 'beatsPerMinute')
        if resting_hrs:
            metrics['heartRate']['resting'] = resting_hrs[-1]
    
    # Blood pressure
    bp_df = get_health_data('bloodPressure', days=30)
    if not bp_df.empty:
        systolic = extract_biometric_value(bp_df, 'bloodPressure', 'systolic')
        diastolic = extract_biometric_value(bp_df, 'bloodPressure', 'diastolic')
        if systolic and diastolic:
            metrics['bloodPressure']['systolic'] = systolic[-1]
            metrics['bloodPressure']['diastolic'] = diastolic[-1]
            metrics['bloodPressure']['data'] = list(zip(systolic, diastolic))
    
    # Oxygen saturation
    o2_df = get_health_data('oxygenSaturation', days=30)
    if not o2_df.empty:
        o2_values = extract_biometric_value(o2_df, 'oxygenSaturation', 'percentage')
        if o2_values:
            metrics['oxygenSaturation']['current'] = o2_values[-1]
            metrics['oxygenSaturation']['data'] = o2_values
    
    # Body temperature
    temp_df = get_health_data('bodyTemperature', days=30)
    if not temp_df.empty:
        temps = extract_biometric_value(temp_df, 'bodyTemperature', 'inCelsius')
        if temps:
            metrics['bodyTemperature']['current'] = temps[-1]
            metrics['bodyTemperature']['data'] = temps
    
    return metrics

def calculate_fitness_metrics() -> Dict[str, Any]:
    """
    Calculate fitness and activity metrics.
    
    Returns:
        Dictionary with fitness analysis
    """
    metrics = {
        'steps': {'daily_avg': None, 'total': None, 'trend': None, 'data': []},
        'distance': {'daily_avg': None, 'total': None, 'data': []},
        'calories': {'active': None, 'total': None, 'bmr': None, 'data': []},
        'vo2Max': {'current': None, 'data': []},
        'sleep': {'avg_duration': None, 'efficiency': None, 'data': []},
        'last_updated': None
    }
    
    # Steps data
    steps_df = get_health_data('steps', days=30)
    if not steps_df.empty:
        steps_values = extract_biometric_value(steps_df, 'steps', 'count')
        if steps_values:
            metrics['steps']['total'] = sum(steps_values)
            metrics['steps']['daily_avg'] = int(np.mean(steps_values))
            metrics['steps']['data'] = steps_values
            metrics['steps']['trend'] = calculate_trend(steps_values)
            metrics['last_updated'] = steps_df['start'].iloc[-1].isoformat()
    
    # Distance data
    distance_df = get_health_data('distance', days=30)
    if not distance_df.empty:
        distances = extract_biometric_value(distance_df, 'distance', 'inMeters')
        if distances:
            metrics['distance']['total'] = sum(distances) / 1000  # Convert to km
            metrics['distance']['daily_avg'] = round(np.mean(distances) / 1000, 2)
            metrics['distance']['data'] = [d/1000 for d in distances]
    
    # Calories data
    active_cal_df = get_health_data('activeCaloriesBurned', days=30)
    total_cal_df = get_health_data('totalCaloriesBurned', days=30)
    
    if not active_cal_df.empty:
        active_cals = extract_biometric_value(active_cal_df, 'activeCaloriesBurned', 'inKilocalories')
        if active_cals:
            metrics['calories']['active'] = int(np.mean(active_cals))
    
    if not total_cal_df.empty:
        total_cals = extract_biometric_value(total_cal_df, 'totalCaloriesBurned', 'inKilocalories')
        if total_cals:
            metrics['calories']['total'] = int(np.mean(total_cals))
            metrics['calories']['data'] = total_cals
    
    # VO2 Max
    vo2_df = get_health_data('vo2Max', days=90)
    if not vo2_df.empty:
        vo2_values = extract_biometric_value(vo2_df, 'vo2Max', 'inMillilitersPerMinuteKilogram')
        if vo2_values:
            metrics['vo2Max']['current'] = vo2_values[-1]
            metrics['vo2Max']['data'] = vo2_values
    
    return metrics

def calculate_trend(values: List[float]) -> str:
    """
    Calculate trend direction from a list of values.
    
    Args:
        values: List of numeric values
    
    Returns:
        Trend direction: 'up', 'down', or 'stable'
    """
    if len(values) < 2:
        return 'stable'
    
    # Calculate linear regression slope
    x = np.arange(len(values))
    slope = np.polyfit(x, values, 1)[0]
    
    # Determine trend based on slope
    if slope > 0.01:  # Threshold for significant increase
        return 'up'
    elif slope < -0.01:  # Threshold for significant decrease
        return 'down'
    else:
        return 'stable'

def get_bmi_category(bmi: float) -> str:
    """
    Get BMI category based on value.
    
    Args:
        bmi: BMI value
    
    Returns:
        BMI category string
    """
    if bmi < 18.5:
        return 'Underweight'
    elif bmi < 25:
        return 'Normal'
    elif bmi < 30:
        return 'Overweight'
    else:
        return 'Obese'

def get_health_score() -> Dict[str, Any]:
    """
    Calculate an overall health score based on available metrics.
    
    Returns:
        Dictionary with health score and breakdown
    """
    score_components = {
        'body_composition': 0,
        'cardiovascular': 0,
        'fitness': 0,
        'overall': 0
    }
    
    # This is a simplified scoring system
    # In a real application, you'd use medical guidelines and algorithms
    
    body_metrics = calculate_body_composition_metrics()
    vital_metrics = calculate_vital_signs_metrics()
    fitness_metrics = calculate_fitness_metrics()
    
    # Body composition score (0-100)
    if body_metrics['bmi']['current']:
        bmi = body_metrics['bmi']['current']
        if 18.5 <= bmi <= 25:
            score_components['body_composition'] = 85
        elif 25 < bmi <= 30:
            score_components['body_composition'] = 70
        else:
            score_components['body_composition'] = 50
    
    # Cardiovascular score (0-100)
    if vital_metrics['heartRate']['resting']:
        rhr = vital_metrics['heartRate']['resting']
        if 60 <= rhr <= 80:
            score_components['cardiovascular'] = 85
        elif 50 <= rhr <= 90:
            score_components['cardiovascular'] = 70
        else:
            score_components['cardiovascular'] = 50
    
    # Fitness score (0-100)
    if fitness_metrics['steps']['daily_avg']:
        steps = fitness_metrics['steps']['daily_avg']
        if steps >= 10000:
            score_components['fitness'] = 90
        elif steps >= 7500:
            score_components['fitness'] = 75
        elif steps >= 5000:
            score_components['fitness'] = 60
        else:
            score_components['fitness'] = 40
    
    # Overall score
    scores = [v for v in score_components.values() if v > 0]
    if scores:
        score_components['overall'] = int(np.mean(scores))
    
    return score_components

def get_comprehensive_health_data() -> Dict[str, Any]:
    """
    Get comprehensive health data for dashboard visualization.
    
    Returns:
        Complete health data dictionary
    """
    return {
        'body_composition': calculate_body_composition_metrics(),
        'vital_signs': calculate_vital_signs_metrics(),
        'fitness': calculate_fitness_metrics(),
        'health_score': get_health_score(),
        'generated_at': datetime.now().isoformat()
    }
