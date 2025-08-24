"""
Data Extractors Module
Functions for extracting data from various sources.
"""

from typing import Dict, List, Any, Optional
import pandas as pd
import requests
import json

def extract_csv_data(file_path: str) -> pd.DataFrame:
    """
    Extract data from CSV file.
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        DataFrame with the extracted data
    """
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return pd.DataFrame()

def extract_api_data(url: str, params: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Extract data from API endpoint.
    
    Args:
        url: API endpoint URL
        params: Query parameters
        
    Returns:
        Dictionary with the API response data
    """
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching API data: {e}")
        return {}
