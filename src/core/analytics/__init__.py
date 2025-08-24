"""
Analytics Module
Functions for data analysis and generating insights.
"""

from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def calculate_basic_statistics(df: pd.DataFrame, numeric_columns: List[str]) -> Dict[str, Any]:
    """
    Calculate basic statistics for numeric columns.
    
    Args:
        df: Input DataFrame
        numeric_columns: List of numeric column names
        
    Returns:
        Dictionary with statistics for each column
    """
    if df.empty:
        return {}
    
    stats = {}
    for col in numeric_columns:
        if col in df.columns and df[col].dtype in ['int64', 'float64']:
            stats[col] = {
                'mean': df[col].mean(),
                'median': df[col].median(),
                'std': df[col].std(),
                'min': df[col].min(),
                'max': df[col].max(),
                'count': df[col].count()
            }
    
    return stats

def detect_trends(df: pd.DataFrame, date_column: str, value_column: str) -> Dict[str, Any]:
    """
    Detect trends in time series data.
    
    Args:
        df: Input DataFrame
        date_column: Name of the date column
        value_column: Name of the value column
        
    Returns:
        Dictionary with trend analysis results
    """
    if df.empty or date_column not in df.columns or value_column not in df.columns:
        return {}
    
    df_copy = df.copy()
    df_copy[date_column] = pd.to_datetime(df_copy[date_column])
    df_copy = df_copy.sort_values(date_column)
    
    # Calculate linear trend
    x = np.arange(len(df_copy))
    y = df_copy[value_column].values
    slope, intercept = np.polyfit(x, y, 1)
    
    # Calculate trend strength (R-squared)
    y_pred = slope * x + intercept
    r_squared = 1 - np.sum((y - y_pred) ** 2) / np.sum((y - np.mean(y)) ** 2)
    
    return {
        'slope': slope,
        'intercept': intercept,
        'r_squared': r_squared,
        'trend_direction': 'increasing' if slope > 0 else 'decreasing',
        'trend_strength': 'strong' if abs(r_squared) > 0.7 else 'weak'
    }

def identify_outliers(df: pd.DataFrame, column: str, method: str = 'iqr') -> pd.DataFrame:
    """
    Identify outliers in a column.
    
    Args:
        df: Input DataFrame
        column: Column to analyze
        method: Method to use ('iqr' or 'zscore')
        
    Returns:
        DataFrame with outlier flag column
    """
    if df.empty or column not in df.columns:
        return df
    
    df_copy = df.copy()
    
    if method == 'iqr':
        Q1 = df_copy[column].quantile(0.25)
        Q3 = df_copy[column].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        df_copy[f'{column}_outlier'] = (
            (df_copy[column] < lower_bound) | (df_copy[column] > upper_bound)
        )
    
    elif method == 'zscore':
        z_scores = np.abs((df_copy[column] - df_copy[column].mean()) / df_copy[column].std())
        df_copy[f'{column}_outlier'] = z_scores > 3
    
    return df_copy

def calculate_correlation_matrix(df: pd.DataFrame, numeric_columns: List[str]) -> pd.DataFrame:
    """
    Calculate correlation matrix for numeric columns.
    
    Args:
        df: Input DataFrame
        numeric_columns: List of numeric column names
        
    Returns:
        Correlation matrix DataFrame
    """
    if df.empty:
        return pd.DataFrame()
    
    # Filter only numeric columns that exist in the DataFrame
    available_columns = [col for col in numeric_columns if col in df.columns]
    
    if not available_columns:
        return pd.DataFrame()
    
    return df[available_columns].corr()

def generate_summary_report(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate a comprehensive summary report for a DataFrame.
    
    Args:
        df: Input DataFrame
        
    Returns:
        Dictionary with summary information
    """
    if df.empty:
        return {}
    
    report = {
        'shape': df.shape,
        'columns': list(df.columns),
        'data_types': df.dtypes.to_dict(),
        'missing_values': df.isnull().sum().to_dict(),
        'duplicate_rows': df.duplicated().sum(),
        'memory_usage': df.memory_usage(deep=True).sum()
    }
    
    # Add numeric column statistics
    numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
    if numeric_columns:
        report['numeric_statistics'] = calculate_basic_statistics(df, numeric_columns)
    
    # Add categorical column information
    categorical_columns = df.select_dtypes(include=['object']).columns.tolist()
    if categorical_columns:
        report['categorical_info'] = {}
        for col in categorical_columns:
            report['categorical_info'][col] = {
                'unique_values': df[col].nunique(),
                'most_common': df[col].mode().iloc[0] if not df[col].mode().empty else None
            }
    
    return report

def calculate_performance_metrics(actual: List[float], predicted: List[float]) -> Dict[str, float]:
    """
    Calculate performance metrics for predictions.
    
    Args:
        actual: List of actual values
        predicted: List of predicted values
        
    Returns:
        Dictionary with performance metrics
    """
    if len(actual) != len(predicted) or len(actual) == 0:
        return {}
    
    actual = np.array(actual)
    predicted = np.array(predicted)
    
    # Calculate metrics
    mse = np.mean((actual - predicted) ** 2)
    rmse = np.sqrt(mse)
    mae = np.mean(np.abs(actual - predicted))
    
    # Calculate R-squared
    ss_res = np.sum((actual - predicted) ** 2)
    ss_tot = np.sum((actual - np.mean(actual)) ** 2)
    r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
    
    return {
        'mse': mse,
        'rmse': rmse,
        'mae': mae,
        'r_squared': r_squared
    }
