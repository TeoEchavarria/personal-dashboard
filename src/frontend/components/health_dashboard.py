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

def create_futuristic_theme():
    """Create a futuristic color theme for visualizations."""
    return {
        'bg_color': '#0a0a0a',
        'primary': '#00ffff',
        'secondary': '#ff00ff',
        'accent': '#ffff00',
        'success': '#00ff00',
        'warning': '#ff8800',
        'danger': '#ff0044',
        'text': '#ffffff',
        'grid': '#333333'
    }

def create_3d_body_hologram(health_data: Dict[str, Any]) -> go.Figure:
    """
    Create a 3D holographic representation of the human body with health metrics.
    
    Args:
        health_data: Comprehensive health data dictionary
    
    Returns:
        Plotly 3D figure representing the body hologram
    """
    theme = create_futuristic_theme()
    
    # Create a simplified 3D human figure using scatter3d
    # Head
    head_x = [0, 0, 0]
    head_y = [0, 0, 0] 
    head_z = [1.7, 1.65, 1.75]
    
    # Torso points
    torso_x = [0, -0.15, 0.15, 0, -0.2, 0.2, 0, -0.15, 0.15, 0]
    torso_y = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    torso_z = [1.6, 1.5, 1.5, 1.4, 1.3, 1.3, 1.2, 1.1, 1.1, 1.0]
    
    # Arms
    left_arm_x = [-0.2, -0.3, -0.4, -0.35, -0.3]
    left_arm_y = [0, 0, 0, 0, 0]
    left_arm_z = [1.4, 1.3, 1.2, 1.1, 1.0]
    
    right_arm_x = [0.2, 0.3, 0.4, 0.35, 0.3]
    right_arm_y = [0, 0, 0, 0, 0]
    right_arm_z = [1.4, 1.3, 1.2, 1.1, 1.0]
    
    # Legs
    left_leg_x = [-0.1, -0.1, -0.1, -0.1]
    left_leg_y = [0, 0, 0, 0]
    left_leg_z = [1.0, 0.7, 0.4, 0.0]
    
    right_leg_x = [0.1, 0.1, 0.1, 0.1]
    right_leg_y = [0, 0, 0, 0]
    right_leg_z = [1.0, 0.7, 0.4, 0.0]
    
    fig = go.Figure()
    
    # Add body parts with different colors based on health metrics
    body_composition = health_data.get('body_composition', {})
    vital_signs = health_data.get('vital_signs', {})
    
    # Determine colors based on health status
    heart_color = theme['success'] if vital_signs.get('heartRate', {}).get('current') else theme['grid']
    body_color = theme['primary'] if body_composition.get('bmi', {}).get('current') else theme['grid']
    
    # Head (brain activity indicator)
    fig.add_trace(go.Scatter3d(
        x=head_x, y=head_y, z=head_z,
        mode='markers',
        marker=dict(size=15, color=theme['accent'], opacity=0.8),
        name='Neural Activity',
        hovertemplate='<b>Brain</b><br>Status: Active<extra></extra>'
    ))
    
    # Torso (main body metrics)
    fig.add_trace(go.Scatter3d(
        x=torso_x, y=torso_y, z=torso_z,
        mode='markers+lines',
        marker=dict(size=8, color=body_color, opacity=0.7),
        line=dict(color=body_color, width=4),
        name='Body Core',
        hovertemplate='<b>Body Core</b><br>' +
                     f'BMI: {body_composition.get("bmi", {}).get("current", "N/A")}<br>' +
                     f'Weight: {body_composition.get("weight", {}).get("current", "N/A")} kg<extra></extra>'
    ))
    
    # Heart area (special marker for cardiovascular health)
    fig.add_trace(go.Scatter3d(
        x=[-0.05], y=[0], z=[1.35],
        mode='markers',
        marker=dict(
            size=20,
            color=heart_color,
            symbol='diamond',
            opacity=0.9,
            line=dict(color=theme['danger'], width=2)
        ),
        name='Heart',
        hovertemplate='<b>Heart</b><br>' +
                     f'Rate: {vital_signs.get("heartRate", {}).get("current", "N/A")} bpm<br>' +
                     f'Resting: {vital_signs.get("heartRate", {}).get("resting", "N/A")} bpm<extra></extra>'
    ))
    
    # Arms
    fig.add_trace(go.Scatter3d(
        x=left_arm_x + right_arm_x, 
        y=left_arm_y + right_arm_y, 
        z=left_arm_z + right_arm_z,
        mode='markers+lines',
        marker=dict(size=6, color=theme['secondary'], opacity=0.6),
        line=dict(color=theme['secondary'], width=3),
        name='Arms',
        hovertemplate='<b>Arms</b><br>Status: Active<extra></extra>'
    ))
    
    # Legs
    fig.add_trace(go.Scatter3d(
        x=left_leg_x + right_leg_x,
        y=left_leg_y + right_leg_y,
        z=left_leg_z + right_leg_z,
        mode='markers+lines',
        marker=dict(size=6, color=theme['primary'], opacity=0.6),
        line=dict(color=theme['primary'], width=3),
        name='Legs',
        hovertemplate='<b>Legs</b><br>Mobility: Active<extra></extra>'
    ))
    
    # Add energy field effect around the body
    theta = np.linspace(0, 2*np.pi, 20)
    energy_x = 0.6 * np.cos(theta)
    energy_y = 0.6 * np.sin(theta)
    energy_z = np.full_like(theta, 1.2)
    
    fig.add_trace(go.Scatter3d(
        x=energy_x, y=energy_y, z=energy_z,
        mode='markers',
        marker=dict(size=3, color=theme['accent'], opacity=0.3),
        name='Energy Field',
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # Configure layout for futuristic look
    fig.update_layout(
        title={
            'text': '🧬 BIOMETRIC HOLOGRAM',
            'x': 0.5,
            'font': {'size': 20, 'color': theme['primary'], 'family': 'Courier New'}
        },
        scene=dict(
            bgcolor=theme['bg_color'],
            xaxis=dict(
                showbackground=True,
                backgroundcolor='rgba(0, 255, 255, 0.1)',
                gridcolor=theme['grid'],
                showticklabels=False,
                title=''
            ),
            yaxis=dict(
                showbackground=True,
                backgroundcolor='rgba(255, 0, 255, 0.1)',
                gridcolor=theme['grid'],
                showticklabels=False,
                title=''
            ),
            zaxis=dict(
                showbackground=True,
                backgroundcolor='rgba(255, 255, 0, 0.1)',
                gridcolor=theme['grid'],
                showticklabels=False,
                title=''
            ),
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.2)
            )
        ),
        paper_bgcolor=theme['bg_color'],
        plot_bgcolor=theme['bg_color'],
        font=dict(color=theme['text'], family='Courier New'),
        showlegend=True,
        legend=dict(
            bgcolor='rgba(0, 0, 0, 0.8)',
            bordercolor=theme['primary'],
            borderwidth=1,
            font=dict(color=theme['text'])
        ),
        height=500
    )
    
    return fig

def create_vital_signs_radar(health_data: Dict[str, Any]) -> go.Figure:
    """
    Create a radar chart for vital signs.
    
    Args:
        health_data: Health data dictionary
    
    Returns:
        Plotly radar chart figure
    """
    theme = create_futuristic_theme()
    vital_signs = health_data.get('vital_signs', {})
    body_comp = health_data.get('body_composition', {})
    fitness = health_data.get('fitness', {})
    
    # Normalize values to 0-100 scale for radar chart
    categories = []
    values = []
    
    # Heart Rate (normalized: 60-100 bpm = 100%, outside range = lower score)
    if vital_signs.get('heartRate', {}).get('resting'):
        rhr = vital_signs['heartRate']['resting']
        if 60 <= rhr <= 80:
            hr_score = 100
        elif 50 <= rhr <= 90:
            hr_score = 80
        else:
            hr_score = 50
        categories.append('Heart Rate')
        values.append(hr_score)
    
    # BMI (normalized)
    if body_comp.get('bmi', {}).get('current'):
        bmi = body_comp['bmi']['current']
        if 18.5 <= bmi <= 25:
            bmi_score = 100
        elif 25 < bmi <= 30:
            bmi_score = 70
        else:
            bmi_score = 40
        categories.append('Body Mass')
        values.append(bmi_score)
    
    # Steps (normalized: 10k+ = 100%)
    if fitness.get('steps', {}).get('daily_avg'):
        steps = fitness['steps']['daily_avg']
        steps_score = min(100, (steps / 10000) * 100)
        categories.append('Activity')
        values.append(steps_score)
    
    # BMR (normalized based on typical ranges)
    if body_comp.get('basalMetabolicRate', {}).get('current'):
        bmr = body_comp['basalMetabolicRate']['current']
        bmr_score = min(100, (bmr / 2000) * 100)  # Rough normalization
        categories.append('Metabolism')
        values.append(bmr_score)
    
    # Add some default categories if we don't have enough data
    if len(categories) < 3:
        categories.extend(['Hydration', 'Sleep', 'Stress'])
        values.extend([75, 80, 60])  # Default values
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        fillcolor=f'rgba(0, 255, 255, 0.3)',
        line=dict(color=theme['primary'], width=3),
        marker=dict(color=theme['primary'], size=8),
        name='Current Status'
    ))
    
    # Add ideal/target values
    ideal_values = [90] * len(categories)  # Target 90% for all categories
    fig.add_trace(go.Scatterpolar(
        r=ideal_values,
        theta=categories,
        fill='toself',
        fillcolor='rgba(0, 255, 0, 0.1)',
        line=dict(color=theme['success'], width=2, dash='dash'),
        name='Target Zone'
    ))
    
    fig.update_layout(
        polar=dict(
            bgcolor=theme['bg_color'],
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                gridcolor=theme['grid'],
                tickcolor=theme['text'],
                tickfont=dict(color=theme['text'])
            ),
            angularaxis=dict(
                gridcolor=theme['grid'],
                tickcolor=theme['text'],
                tickfont=dict(color=theme['text'], size=12)
            )
        ),
        title={
            'text': '⚡ VITAL SIGNS MATRIX',
            'x': 0.5,
            'font': {'size': 18, 'color': theme['primary'], 'family': 'Courier New'}
        },
        paper_bgcolor=theme['bg_color'],
        plot_bgcolor=theme['bg_color'],
        font=dict(color=theme['text'], family='Courier New'),
        showlegend=True,
        legend=dict(
            bgcolor='rgba(0, 0, 0, 0.8)',
            bordercolor=theme['primary'],
            borderwidth=1
        ),
        height=400
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
                line=dict(color=theme['primary'], width=2),
                marker=dict(color=theme['primary'], size=4),
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
                line=dict(color=theme['danger'], width=2),
                marker=dict(color=theme['danger'], size=4),
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
                line=dict(color=theme['warning'], width=2),
                marker=dict(color=theme['warning'], size=4),
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
                line=dict(color=theme['success'], width=2),
                marker=dict(color=theme['success'], size=4),
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
        font=dict(color=theme['text'], family='Courier New'),
        showlegend=False,
        height=500
    )
    
    # Update axes
    fig.update_xaxes(gridcolor=theme['grid'], tickcolor=theme['text'])
    fig.update_yaxes(gridcolor=theme['grid'], tickcolor=theme['text'])
    
    return fig

def create_health_score_gauge(health_data: Dict[str, Any]) -> go.Figure:
    """
    Create a futuristic gauge for overall health score.
    
    Args:
        health_data: Health data dictionary
    
    Returns:
        Plotly gauge figure
    """
    theme = create_futuristic_theme()
    health_score = health_data.get('health_score', {})
    overall_score = health_score.get('overall', 0)
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=overall_score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "🎯 HEALTH SCORE", 'font': {'size': 20, 'color': theme['primary']}},
        delta={'reference': 80, 'increasing': {'color': theme['success']}, 'decreasing': {'color': theme['danger']}},
        gauge={
            'axis': {'range': [None, 100], 'tickcolor': theme['text']},
            'bar': {'color': theme['primary']},
            'steps': [
                {'range': [0, 50], 'color': 'rgba(255, 0, 68, 0.3)'},
                {'range': [50, 80], 'color': 'rgba(255, 136, 0, 0.3)'},
                {'range': [80, 100], 'color': 'rgba(0, 255, 0, 0.3)'}
            ],
            'threshold': {
                'line': {'color': theme['accent'], 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig.update_layout(
        paper_bgcolor=theme['bg_color'],
        plot_bgcolor=theme['bg_color'],
        font={'color': theme['text'], 'family': 'Courier New'},
        height=300
    )
    
    return fig

def render_futuristic_health_dashboard():
    """
    Render the complete futuristic health dashboard.
    """
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        color: #00ffff;
        font-family: 'Courier New', monospace;
        font-size: 2.5em;
        margin-bottom: 30px;
        text-shadow: 0 0 20px #00ffff;
        animation: glow 2s ease-in-out infinite alternate;
    }
    
    @keyframes glow {
        from { text-shadow: 0 0 20px #00ffff, 0 0 30px #00ffff; }
        to { text-shadow: 0 0 30px #00ffff, 0 0 40px #00ffff; }
    }
    
    .metric-card {
        background: linear-gradient(135deg, rgba(0,255,255,0.1), rgba(255,0,255,0.1));
        border: 1px solid #00ffff;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 0 20px rgba(0,255,255,0.3);
    }
    
    .status-indicator {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 8px;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    .status-online { background-color: #00ff00; }
    .status-warning { background-color: #ff8800; }
    .status-offline { background-color: #ff0044; }
    </style>
    """, unsafe_allow_html=True)
    
    # Main header
    st.markdown('<h1 class="main-header">🧬 BIOMETRIC COMMAND CENTER 🧬</h1>', unsafe_allow_html=True)
    
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
    
    # System status indicators
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h4>🔬 BIOMETRIC SENSORS</h4>
            <span class="status-indicator status-online"></span>ACTIVE
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h4>💓 CARDIAC MONITOR</h4>
            <span class="status-indicator status-online"></span>TRACKING
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h4>🏃 ACTIVITY TRACKER</h4>
            <span class="status-indicator status-warning"></span>PARTIAL
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h4>🧠 NEURAL INTERFACE</h4>
            <span class="status-indicator status-online"></span>CONNECTED
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Main dashboard layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # 3D Body Hologram
        st.plotly_chart(
            create_3d_body_hologram(health_data),
            use_container_width=True,
            config={'displayModeBar': False}
        )
        
        # Health trends
        st.plotly_chart(
            create_health_trend_chart(health_data),
            use_container_width=True,
            config={'displayModeBar': False}
        )
    
    with col2:
        # Health Score Gauge
        st.plotly_chart(
            create_health_score_gauge(health_data),
            use_container_width=True,
            config={'displayModeBar': False}
        )
        
        # Vital Signs Radar
        st.plotly_chart(
            create_vital_signs_radar(health_data),
            use_container_width=True,
            config={'displayModeBar': False}
        )
    
    # Data summary section
    st.markdown("### 📊 BIOMETRIC DATA SUMMARY")
    
    body_comp = health_data.get('body_composition', {})
    vital_signs = health_data.get('vital_signs', {})
    fitness = health_data.get('fitness', {})
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 🏋️ BODY COMPOSITION")
        weight = body_comp.get('weight', {}).get('current')
        bmi = body_comp.get('bmi', {}).get('current')
        bmr = body_comp.get('basalMetabolicRate', {}).get('current')
        
        if weight:
            st.metric("Weight", f"{weight:.1f} kg")
        if bmi:
            st.metric("BMI", f"{bmi:.1f}", delta=body_comp.get('bmi', {}).get('category', ''))
        if bmr:
            st.metric("BMR", f"{bmr:.0f} kcal/day")
    
    with col2:
        st.markdown("#### ❤️ VITAL SIGNS")
        hr = vital_signs.get('heartRate', {}).get('current')
        rhr = vital_signs.get('heartRate', {}).get('resting')
        temp = vital_signs.get('bodyTemperature', {}).get('current')
        
        if hr:
            st.metric("Heart Rate", f"{hr:.0f} bpm")
        if rhr:
            st.metric("Resting HR", f"{rhr:.0f} bpm")
        if temp:
            st.metric("Body Temp", f"{temp:.1f}°C")
    
    with col3:
        st.markdown("#### 🏃 FITNESS METRICS")
        steps = fitness.get('steps', {}).get('daily_avg')
        distance = fitness.get('distance', {}).get('daily_avg')
        calories = fitness.get('calories', {}).get('active')
        
        if steps:
            st.metric("Daily Steps", f"{steps:,}")
        if distance:
            st.metric("Daily Distance", f"{distance:.1f} km")
        if calories:
            st.metric("Active Calories", f"{calories:.0f} kcal")
    
    # Last update info
    last_updated = health_data.get('generated_at')
    if last_updated:
        st.markdown(f"**Last Updated:** {last_updated}")
    
    st.markdown("---")
    st.markdown(
        '<p style="text-align: center; color: #00ffff; font-family: Courier New;">🔬 BIOMETRIC ANALYSIS COMPLETE 🔬</p>',
        unsafe_allow_html=True
    )
