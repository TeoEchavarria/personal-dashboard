"""
Data Processors Module
Pure functions for processing and transforming data.
"""

from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean a DataFrame by removing duplicates and handling missing values.
    
    Args:
        df: Input DataFrame
        
    Returns:
        Cleaned DataFrame
    """
    if df.empty:
        return df
    
    # Remove duplicates
    df_clean = df.drop_duplicates()
    
    # Handle missing values
    df_clean = df_clean.fillna(method='ffill')
    
    return df_clean

def aggregate_by_date(df: pd.DataFrame, date_column: str, value_column: str, 
                     agg_func: str = 'sum') -> pd.DataFrame:
    """
    Aggregate data by date.
    
    Args:
        df: Input DataFrame
        date_column: Name of the date column
        value_column: Name of the value column to aggregate
        agg_func: Aggregation function ('sum', 'mean', 'count', etc.)
        
    Returns:
        Aggregated DataFrame
    """
    if df.empty or date_column not in df.columns or value_column not in df.columns:
        return pd.DataFrame()
    
    # Ensure date column is datetime
    df_copy = df.copy()
    df_copy[date_column] = pd.to_datetime(df_copy[date_column])
    
    # Group by date and aggregate
    grouped = df_copy.groupby(df_copy[date_column].dt.date)[value_column].agg(agg_func)
    
    return grouped.reset_index()

def calculate_moving_average(df: pd.DataFrame, column: str, window: int = 7) -> pd.DataFrame:
    """
    Calculate moving average for a column.
    
    Args:
        df: Input DataFrame
        column: Column to calculate moving average for
        window: Window size for moving average
        
    Returns:
        DataFrame with moving average column added
    """
    if df.empty or column not in df.columns:
        return df
    
    df_copy = df.copy()
    df_copy[f'{column}_ma_{window}'] = df_copy[column].rolling(window=window).mean()
    
    return df_copy

def filter_by_date_range(df: pd.DataFrame, date_column: str, 
                        start_date: str, end_date: str) -> pd.DataFrame:
    """
    Filter DataFrame by date range.
    
    Args:
        df: Input DataFrame
        date_column: Name of the date column
        start_date: Start date (YYYY-MM-DD format)
        end_date: End date (YYYY-MM-DD format)
        
    Returns:
        Filtered DataFrame
    """
    if df.empty or date_column not in df.columns:
        return df
    
    df_copy = df.copy()
    df_copy[date_column] = pd.to_datetime(df_copy[date_column])
    
    mask = (df_copy[date_column] >= start_date) & (df_copy[date_column] <= end_date)
    return df_copy.loc[mask]

def pivot_data(df: pd.DataFrame, index: str, columns: str, values: str) -> pd.DataFrame:
    """
    Pivot data using specified columns.
    
    Args:
        df: Input DataFrame
        index: Column to use as index
        columns: Column to use as columns
        values: Column to use as values
        
    Returns:
        Pivoted DataFrame
    """
    if df.empty or index not in df.columns or columns not in df.columns or values not in df.columns:
        return pd.DataFrame()
    
    return df.pivot(index=index, columns=columns, values=values)

def calculate_percentages(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """
    Calculate percentage distribution for a categorical column.
    
    Args:
        df: Input DataFrame
        column: Categorical column to calculate percentages for
        
    Returns:
        DataFrame with percentage column added
    """
    if df.empty or column not in df.columns:
        return df
    
    df_copy = df.copy()
    total = len(df_copy)
    df_copy[f'{column}_percentage'] = df_copy[column].value_counts() / total * 100
    
    return df_copy
