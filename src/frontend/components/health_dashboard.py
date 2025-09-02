"""
Futuristic Health Dashboard Components
Advanced visualizations for health data including 3D body visualization.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List
import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.analytics.health_analytics import get_comprehensive_health_data

def create_minimal_theme():
    """Create a minimal futuristic color theme for visualizations."""
    return {
        'bg_color': '#ffffff',
        'primary': '#2c3e50',
        'secondary': '#3498db',
        'accent': '#e74c3c',
        'success': '#27ae60',
        'warning': '#f39c12',
        'danger': '#e74c3c',
        'text': '#2c3e50',
        'grid': '#ecf0f1',
        'light_gray': '#f8f9fa',
        'medium_gray': '#95a5a6',
        'border': '#bdc3c7'
    }

def create_body_composition_chart(health_data: Dict[str, Any]) -> go.Figure:
    """
    Create a clean, minimal body composition visualization.
    
    Args:
        health_data: Comprehensive health data dictionary
    
    Returns:
        Plotly figure with body composition metrics
    """
    theme = create_minimal_theme()
    body_comp = health_data.get('body_composition', {})
    
    # Create a clean donut chart for BMI visualization
    fig = go.Figure()
    
    # BMI visualization
    bmi = body_comp.get('bmi', {}).get('current', 0)
    weight = body_comp.get('weight', {}).get('current', 0)
    height = body_comp.get('height', {}).get('current', 0)
    bmr = body_comp.get('basalMetabolicRate', {}).get('current', 0)
    
    if bmi > 0:
        # BMI categories visualization
        categories = ['Underweight', 'Normal', 'Overweight', 'Obese']
        ranges = [18.5, 25, 30, 40]
        colors = [theme['secondary'], theme['success'], theme['warning'], theme['danger']]
        
        # Determine current category
        current_category = 0
        if bmi >= 30:
            current_category = 3
        elif bmi >= 25:
            current_category = 2
        elif bmi >= 18.5:
            current_category = 1
        
        # Create horizontal bar chart for BMI ranges
        fig.add_trace(go.Bar(
            y=categories,
            x=ranges,
            orientation='h',
            marker={
                'color': [colors[i] if i == current_category else theme['light_gray'] for i in range(len(categories))],
                'line': {'color': theme['border'], 'width': 1}
            },
            text=[f'{r}' for r in ranges],
            textposition='inside',
            name='BMI Ranges'
        ))
        
        # Add current BMI indicator
        fig.add_shape(
            type="line",
            x0=bmi, x1=bmi,
            y0=-0.5, y1=3.5,
            line={'color': theme['text'], 'width': 3, 'dash': "dash"},
        )
        
        fig.add_annotation(
            x=bmi,
            y=3.7,
            text=f"Your BMI: {bmi:.1f}",
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=2,
            arrowcolor=theme['text'],
            font={'size': 14, 'color': theme['text'], 'family': 'Arial'}
        )
    
    fig.update_layout(
        title={
            'text': 'Body Mass Index Analysis',
            'x': 0.5,
            'font': {'size': 18, 'color': theme['text'], 'family': 'Arial'}
        },
        paper_bgcolor=theme['bg_color'],
        plot_bgcolor=theme['bg_color'],
        font={'color': theme['text'], 'family': 'Arial'},
        showlegend=False,
        height=300,
        margin={'l': 80, 'r': 20, 't': 60, 'b': 40}
    )
    
    fig.update_xaxes(
        title='BMI Value',
        gridcolor=theme['grid'],
        tickcolor=theme['text'],
        title_font={'color': theme['text']},
        tickfont={'color': theme['text']},
        range=[15, 35]
    )
    
    fig.update_yaxes(
        tickcolor=theme['text'],
        title_font={'color': theme['text']},
        tickfont={'color': theme['text']}
    )
    
    return fig

def create_key_metrics_chart(health_data: Dict[str, Any]) -> go.Figure:
    """
    Create a clean metrics overview chart.
    
    Args:
        health_data: Health data dictionary
    
    Returns:
        Plotly metrics chart figure
    """
    theme = create_minimal_theme()
    body_comp = health_data.get('body_composition', {})
    fitness = health_data.get('fitness', {})
    
    # Prepare data for metrics
    metrics = []
    values = []
    colors = []
    
    # Weight
    weight = body_comp.get('weight', {}).get('current')
    if weight:
        metrics.append('Weight')
        values.append(weight)
        colors.append(theme['primary'])
    
    # BMI
    bmi = body_comp.get('bmi', {}).get('current')
    if bmi:
        metrics.append('BMI')
        values.append(bmi)
        # Color based on BMI category
        if 18.5 <= bmi <= 25:
            colors.append(theme['success'])
        elif 25 < bmi <= 30:
            colors.append(theme['warning'])
        else:
            colors.append(theme['danger'])
    
    # BMR (scaled down for visualization)
    bmr = body_comp.get('basalMetabolicRate', {}).get('current')
    if bmr:
        metrics.append('BMR/100')
        values.append(bmr / 100)  # Scale down for better visualization
        colors.append(theme['secondary'])
    
    # Distance
    distance = fitness.get('distance', {}).get('daily_avg')
    if distance:
        metrics.append('Distance (km)')
        values.append(distance)
        colors.append(theme['accent'])
    
    if not metrics:
        # Return empty figure if no data
        fig = go.Figure()
        fig.update_layout(
            title="No health data available",
            paper_bgcolor=theme['bg_color'],
            plot_bgcolor=theme['bg_color']
        )
        return fig
    
    # Create bar chart
    fig = go.Figure(data=[
        go.Bar(
            x=metrics,
            y=values,
            marker={
                'color': colors,
                'line': {'color': theme['border'], 'width': 1}
            },
            text=[f'{v:.1f}' for v in values],
            textposition='outside',
            textfont={'color': theme['text'], 'size': 12}
        )
    ])
    
    fig.update_layout(
        title={
            'text': 'Key Health Metrics',
            'x': 0.5,
            'font': {'size': 18, 'color': theme['text'], 'family': 'Arial'}
        },
        paper_bgcolor=theme['bg_color'],
        plot_bgcolor=theme['bg_color'],
        font={'color': theme['text'], 'family': 'Arial'},
        showlegend=False,
        height=300,
        margin={'l': 40, 'r': 40, 't': 60, 'b': 40}
    )
    
    fig.update_xaxes(
        tickcolor=theme['text'],
        title_font={'color': theme['text']},
        tickfont={'color': theme['text'], 'size': 11}
    )
    
    fig.update_yaxes(
        gridcolor=theme['grid'],
        tickcolor=theme['text'],
        title_font={'color': theme['text']},
        tickfont={'color': theme['text']}
    )
    
    return fig

def create_health_trend_chart(health_data: Dict[str, Any]) -> go.Figure:
    """
    Create a time series chart showing health trends.
    
    Args:
        health_data: Health data dictionary
    
    Returns:
        Plotly time series figure
    """
    theme = create_futuristic_theme()
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Weight Trend', 'Heart Rate', 'BMR', 'Activity'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]],
        vertical_spacing=0.1,
        horizontal_spacing=0.1
    )
    
    # Sample data for demonstration (in real app, use actual time series data)
    dates = pd.date_range(start='2025-08-01', end='2025-09-02', freq='D')
    
    # Weight trend
    body_comp = health_data.get('body_composition', {})
    if body_comp.get('weight', {}).get('current'):
        base_weight = body_comp['weight']['current']
        weight_data = base_weight + np.random.normal(0, 0.5, len(dates))
        
        fig.add_trace(
            go.Scatter(
                x=dates, y=weight_data,
                mode='lines+markers',
                line={'color': theme['primary'], 'width': 2},
                marker={'color': theme['primary'], 'size': 4},
                name='Weight (kg)'
            ),
            row=1, col=1
        )
    
    # Heart rate data
    vital_signs = health_data.get('vital_signs', {})
    if vital_signs.get('heartRate', {}).get('resting'):
        base_hr = vital_signs['heartRate']['resting']
        hr_data = base_hr + np.random.normal(0, 3, len(dates))
        
        fig.add_trace(
            go.Scatter(
                x=dates, y=hr_data,
                mode='lines+markers',
                line={'color': theme['danger'], 'width': 2},
                marker={'color': theme['danger'], 'size': 4},
                name='Heart Rate (bpm)'
            ),
            row=1, col=2
        )
    
    # BMR data
    if body_comp.get('basalMetabolicRate', {}).get('current'):
        base_bmr = body_comp['basalMetabolicRate']['current']
        bmr_data = base_bmr + np.random.normal(0, 20, len(dates))
        
        fig.add_trace(
            go.Scatter(
                x=dates, y=bmr_data,
                mode='lines+markers',
                line={'color': theme['warning'], 'width': 2},
                marker={'color': theme['warning'], 'size': 4},
                name='BMR (kcal/day)'
            ),
            row=2, col=1
        )
    
    # Activity data (steps)
    fitness = health_data.get('fitness', {})
    if fitness.get('steps', {}).get('daily_avg'):
        base_steps = fitness['steps']['daily_avg']
        steps_data = np.random.poisson(base_steps, len(dates))
        
        fig.add_trace(
            go.Scatter(
                x=dates, y=steps_data,
                mode='lines+markers',
                line={'color': theme['success'], 'width': 2},
                marker={'color': theme['success'], 'size': 4},
                name='Steps'
            ),
            row=2, col=2
        )
    
    fig.update_layout(
        title={
            'text': '📈 TEMPORAL BIOMETRIC ANALYSIS',
            'x': 0.5,
            'font': {'size': 18, 'color': theme['primary'], 'family': 'Courier New'}
        },
        paper_bgcolor=theme['bg_color'],
        plot_bgcolor=theme['bg_color'],
        font={'color': theme['text'], 'family': 'Courier New'},
        showlegend=False,
        height=500
    )
    
    # Update all axes with proper formatting
    fig.update_xaxes(
        gridcolor=theme['grid'], 
        tickcolor=theme['text'],
        tickfont={'color': theme['text']}
    )
    fig.update_yaxes(
        gridcolor=theme['grid'], 
        tickcolor=theme['text'],
        tickfont={'color': theme['text']}
    )
    
    return fig

def create_health_score_gauge(health_data: Dict[str, Any]) -> go.Figure:
    """
    Create a clean, minimal health score gauge.
    
    Args:
        health_data: Health data dictionary
    
    Returns:
        Plotly gauge figure
    """
    theme = create_minimal_theme()
    health_score = health_data.get('health_score', {})
    overall_score = health_score.get('overall', 0)
    
    # Determine color based on score
    if overall_score >= 80:
        bar_color = theme['success']
    elif overall_score >= 60:
        bar_color = theme['warning']
    else:
        bar_color = theme['danger']
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=overall_score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Health Score", 'font': {'size': 16, 'color': theme['text'], 'family': 'Arial'}},
        number={'font': {'size': 40, 'color': theme['text']}},
        gauge={
            'axis': {
                'range': [None, 100], 
                'tickcolor': theme['text'],
                'tickfont': {'color': theme['text'], 'size': 12}
            },
            'bar': {'color': bar_color, 'thickness': 0.3},
            'bgcolor': theme['light_gray'],
            'borderwidth': 2,
            'bordercolor': theme['border'],
            'steps': [
                {'range': [0, 60], 'color': theme['light_gray']},
                {'range': [60, 80], 'color': theme['light_gray']},
                {'range': [80, 100], 'color': theme['light_gray']}
            ]
        }
    ))
    
    fig.update_layout(
        paper_bgcolor=theme['bg_color'],
        plot_bgcolor=theme['bg_color'],
        font={'color': theme['text'], 'family': 'Arial'},
        height=250,
        margin={'l': 20, 'r': 20, 't': 40, 'b': 20}
    )
    
    return fig

def render_minimal_health_dashboard():
    """
    Render a clean, minimal health dashboard.
    """
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        color: #2c3e50;
        font-family: 'Arial', sans-serif;
        font-size: 2.2em;
        font-weight: 300;
        margin-bottom: 40px;
        letter-spacing: 2px;
    }
    
    .metric-card {
        background: #ffffff;
        border: 1px solid #ecf0f1;
        border-radius: 8px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: box-shadow 0.3s ease;
    }
    
    .metric-card:hover {
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    
    .status-indicator {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 8px;
    }
    
    .status-good { background-color: #27ae60; }
    .status-warning { background-color: #f39c12; }
    .status-info { background-color: #3498db; }
    
    .section-title {
        color: #2c3e50;
        font-size: 1.4em;
        font-weight: 300;
        margin: 30px 0 20px 0;
        border-bottom: 2px solid #ecf0f1;
        padding-bottom: 10px;
    }
    
    .summary-text {
        color: #7f8c8d;
        font-size: 0.9em;
        text-align: center;
        margin-top: 30px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Main header
    st.markdown('<h1 class="main-header">Health Dashboard</h1>', unsafe_allow_html=True)
    
    # Get comprehensive health data
    try:
        health_data = get_comprehensive_health_data()
    except Exception as e:
        st.error(f"Error loading health data: {e}")
        health_data = {
            'body_composition': {},
            'vital_signs': {},
            'fitness': {},
            'health_score': {'overall': 0}
        }
    
    # Health Score at the top
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.plotly_chart(
            create_health_score_gauge(health_data),
            use_container_width=True,
            config={'displayModeBar': False}
        )
    
    st.markdown('<div class="section-title">Body Composition Analysis</div>', unsafe_allow_html=True)
    
    # Main charts layout
    col1, col2 = st.columns(2)
    
    with col1:
        # BMI Analysis
        st.plotly_chart(
            create_body_composition_chart(health_data),
            use_container_width=True,
            config={'displayModeBar': False}
        )
    
    with col2:
        # Key Metrics
        st.plotly_chart(
            create_key_metrics_chart(health_data),
            use_container_width=True,
            config={'displayModeBar': False}
        )
    
    st.markdown('<div class="section-title">Current Health Metrics</div>', unsafe_allow_html=True)
    
    # Data summary section with clean cards
    body_comp = health_data.get('body_composition', {})
    vital_signs = health_data.get('vital_signs', {})
    fitness = health_data.get('fitness', {})
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        weight = body_comp.get('weight', {}).get('current')
        height = body_comp.get('height', {}).get('current')
        bmi = body_comp.get('bmi', {}).get('current')
        
        if weight and height and bmi:
            status_class = "status-good" if 18.5 <= bmi <= 25 else "status-warning" if bmi <= 30 else "status-info"
            st.markdown(f"""
            <div class="metric-card">
                <h4><span class="status-indicator {status_class}"></span>Physical Profile</h4>
                <p><strong>Height:</strong> {height:.2f} m</p>
                <p><strong>Weight:</strong> {weight:.1f} kg</p>
                <p><strong>BMI:</strong> {bmi:.1f}</p>
                <p><strong>Category:</strong> {body_comp.get('bmi', {}).get('category', 'N/A')}</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        bmr = body_comp.get('basalMetabolicRate', {}).get('current')
        hr = vital_signs.get('heartRate', {}).get('current')
        rhr = vital_signs.get('heartRate', {}).get('resting')
        
        if bmr or hr or rhr:
            st.markdown(f"""
            <div class="metric-card">
                <h4><span class="status-indicator status-info"></span>Metabolic Health</h4>
                <p><strong>BMR:</strong> {bmr:.0f} kcal/day</p>
                <p><strong>Heart Rate:</strong> {hr or 'N/A'} bpm</p>
                <p><strong>Resting HR:</strong> {rhr or 'N/A'} bpm</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        steps = fitness.get('steps', {}).get('daily_avg')
        distance = fitness.get('distance', {}).get('daily_avg')
        calories = fitness.get('calories', {}).get('active')
        
        if distance or steps or calories:
            status_class = "status-good" if (steps and steps >= 8000) else "status-warning"
            st.markdown(f"""
            <div class="metric-card">
                <h4><span class="status-indicator {status_class}"></span>Activity Level</h4>
                <p><strong>Daily Steps:</strong> {steps or 'N/A'}</p>
                <p><strong>Distance:</strong> {distance:.2f} km</p>
                <p><strong>Active Calories:</strong> {calories or 'N/A'} kcal</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Last update info
    last_updated = health_data.get('generated_at')
    if last_updated:
        update_time = datetime.fromisoformat(last_updated.replace('Z', '+00:00')).strftime('%B %d, %Y at %H:%M UTC')
        st.markdown(f'<p class="summary-text">Data last updated on {update_time}</p>', unsafe_allow_html=True)
    
    st.markdown('<p class="summary-text">Health metrics are automatically updated from your connected devices</p>', unsafe_allow_html=True)
