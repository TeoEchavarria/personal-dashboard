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
import time

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.analytics.health_analytics import get_comprehensive_health_data
from core.data_extractors.hc_collect import push_height_data, push_weight_data, initialize_token_manager

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

def create_hospital_theme():
    """Create a hospital-style color theme for medical visualizations with CSS custom properties."""
    return {
        # Use CSS custom properties for consistent theming
        'bg_color': 'var(--bg-primary)',
        'primary': 'var(--primary-blue)',
        'secondary': 'var(--primary-blue-dark)',
        'accent': 'var(--success-green)',
        'success': 'var(--success-green)',
        'warning': 'var(--warning-amber)',
        'danger': 'var(--danger-red)',
        'text': 'var(--text-primary)',
        'text_light': 'var(--text-secondary)',
        'grid': 'var(--border-primary)',
        'light_gray': 'var(--bg-tertiary)',
        'medium_gray': 'var(--text-tertiary)',
        'border': 'var(--border-secondary)',
        'card_bg': 'var(--surface-elevated)',
        'shadow': 'var(--shadow-sm)'
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

def create_editable_metric_card(title: str, current_value: float, unit: str, metric_type: str, 
                               token_manager) -> None:
    """
    Create an editable metric card with instant push functionality.
    
    Args:
        title: Display title for the metric
        current_value: Current value to display
        unit: Unit of measurement
        metric_type: Type of metric ('height' or 'weight')
        token_manager: Token manager for API calls
    """
    
    # Create container for the metric
    with st.container():
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Check for demo value first, then current value
            demo_value = st.session_state.get(f"demo_{metric_type}_value")
            display_value = demo_value if demo_value is not None else current_value
            is_demo = demo_value is not None
            demo_mode = st.session_state.get("demo_mode", False)
            
            # Display current value
            if display_value:
                demo_indicator = " (Demo)" if is_demo else ""
                color = "#e67e22" if is_demo else "#3498db"  # Orange for demo, blue for real
                st.markdown(f"""
                <div style="background: #ffffff; border: 1px solid #ecf0f1; border-radius: 8px; 
                           padding: 20px; margin: 10px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <h4><span style="width: 8px; height: 8px; border-radius: 50%; 
                              background-color: {color}; display: inline-block; margin-right: 8px;"></span>
                        {title}{demo_indicator}</h4>
                    <p><strong>Current:</strong> {display_value:.2f} {unit}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background: #ffffff; border: 1px solid #ecf0f1; border-radius: 8px; 
                           padding: 20px; margin: 10px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <h4><span style="width: 8px; height: 8px; border-radius: 50%; 
                              background-color: #f39c12; display: inline-block; margin-right: 8px;"></span>
                        {title}</h4>
                    <p><strong>No data available</strong></p>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            # Change button
            if st.button("✏️ Change", key=f"change_{metric_type}", 
                        help=f"Update {title.lower()}", type="secondary"):
                st.session_state[f"edit_{metric_type}"] = True
        
        # Show edit form if button was clicked
        if st.session_state.get(f"edit_{metric_type}", False):
            with st.form(f"edit_{metric_type}_form"):
                st.markdown(f"**Update {title}**")
                
                # Input field with appropriate range and step
                # Use demo value if available, otherwise current value
                demo_value = st.session_state.get(f"demo_{metric_type}_value")
                default_value = demo_value if demo_value is not None else current_value
                
                if metric_type == "height":
                    new_value = st.number_input(
                        f"New {title} ({unit})",
                        min_value=0.5,
                        max_value=2.5,
                        value=default_value if default_value else 1.70,
                        step=0.01,
                        format="%.2f"
                    )
                else:  # weight
                    new_value = st.number_input(
                        f"New {title} ({unit})",
                        min_value=20.0,
                        max_value=300.0,
                        value=default_value if default_value else 70.0,
                        step=0.1,
                        format="%.1f"
                    )
                
                col1, col2 = st.columns(2)
                with col1:
                    submit = st.form_submit_button("💾 Save & Push", type="primary")
                with col2:
                    cancel = st.form_submit_button("❌ Cancel")
                
                if submit:
                    # Check if demo mode is enabled
                    demo_mode = st.session_state.get("demo_mode", False)
                    
                    if demo_mode:
                        # Demo mode: simulate successful push
                        with st.spinner(f"Simulating {title.lower()} data push..."):
                            time.sleep(1)  # Simulate network delay
                            # Store the new value in session state for display
                            st.session_state[f"demo_{metric_type}_value"] = new_value
                            st.success(f"✅ Demo: {title} updated to {new_value} {unit} (not pushed to gateway)")
                            st.session_state[f"edit_{metric_type}"] = False
                            st.rerun()
                    else:
                        # Real mode: attempt to push to Health Connect Gateway
                        with st.spinner(f"Pushing {title.lower()} data..."):
                            try:
                                st.write("🔍 **Debug Info**: Attempting to push data to Health Connect Gateway...")
                                
                                # Capture stdout to show debug info in UI
                                import io
                                import sys
                                from contextlib import redirect_stdout
                                
                                debug_output = io.StringIO()
                                
                                with redirect_stdout(debug_output):
                                    if metric_type == "height":
                                        success, message = push_height_data(new_value, token_manager)
                                    else:  # weight
                                        success, message = push_weight_data(new_value, token_manager)
                                
                                # Show debug output in the UI
                                debug_text = debug_output.getvalue()
                                if debug_text:
                                    with st.expander("🔍 Debug Output (Click to see details)", expanded=False):
                                        st.text(debug_text)
                                
                                if success:
                                    st.success(f"✅ {message}")
                                    st.session_state[f"edit_{metric_type}"] = False
                                    # Force a refresh of the dashboard
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.error(f"❌ {message}")
                                    
                            except Exception as e:
                                error_msg = str(e)
                                st.error(f"❌ **Error Details**: {error_msg}")
                                
                                # Show the debug output even on error
                                debug_text = debug_output.getvalue() if 'debug_output' in locals() else "No debug output captured"
                                with st.expander("🔍 Full Debug Information", expanded=True):
                                    st.text(debug_text)
                                    st.text(f"\nException Type: {type(e).__name__}")
                                    st.text(f"Exception Message: {str(e)}")
                                    
                                    # Show traceback
                                    import traceback
                                    tb = traceback.format_exc()
                                    st.text(f"\nFull Traceback:\n{tb}")
                                
                                # Offer demo mode if FCM token error is detected
                                if "fcm token" in error_msg.lower() or "push functionality requires" in error_msg.lower():
                                    st.info("💡 **Tip**: Enable Demo Mode to test the interface without gateway push requirements")
                                    if st.button("🎭 Enable Demo Mode", key=f"enable_demo_{metric_type}"):
                                        st.session_state["demo_mode"] = True
                                        st.success("Demo Mode enabled! Try editing again.")
                                        st.rerun()
                
                if cancel:
                    st.session_state[f"edit_{metric_type}"] = False
                    st.rerun()

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
    
    # Demo mode toggle
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        demo_mode = st.session_state.get("demo_mode", False)
        if st.checkbox("🎭 Demo Mode", value=demo_mode, help="Enable demo mode to test editing without gateway push"):
            st.session_state["demo_mode"] = True
        else:
            st.session_state["demo_mode"] = False
            # Clear demo values when disabling demo mode
            for metric in ["height", "weight"]:
                if f"demo_{metric}_value" in st.session_state:
                    del st.session_state[f"demo_{metric}_value"]
    
    # Initialize token manager for push operations
    try:
        if 'token_manager' not in st.session_state:
            st.session_state.token_manager = initialize_token_manager()
        token_manager = st.session_state.token_manager
    except Exception as e:
        st.warning(f"⚠️ Push functionality unavailable: {e}")
        token_manager = None
    
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
        
        # Editable Physical Profile Section
        st.markdown('<div class="section-title">Editable Physical Profile</div>', unsafe_allow_html=True)
        
        # Height - Editable
        create_editable_metric_card("Height", height, "m", "height", token_manager)
        
        # Weight - Editable
        create_editable_metric_card("Weight", weight, "kg", "weight", token_manager)
        
        # BMI - Calculated (non-editable)
        if weight and height and bmi:
            status_class = "status-good" if 18.5 <= bmi <= 25 else "status-warning" if bmi <= 30 else "status-info"
            st.markdown(f"""
            <div style="background: #ffffff; border: 1px solid #ecf0f1; border-radius: 8px; 
                       padding: 20px; margin: 10px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <h4><span style="width: 8px; height: 8px; border-radius: 50%; 
                          background-color: {'#27ae60' if status_class == 'status-good' else '#f39c12' if status_class == 'status-warning' else '#3498db'}; 
                          display: inline-block; margin-right: 8px;"></span>BMI (Calculated)</h4>
                <p><strong>Current:</strong> {bmi:.1f}</p>
                <p><strong>Category:</strong> {body_comp.get('bmi', {}).get('category', 'N/A')}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background: #ffffff; border: 1px solid #ecf0f1; border-radius: 8px; 
                       padding: 20px; margin: 10px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <h4><span style="width: 8px; height: 8px; border-radius: 50%; 
                          background-color: #f39c12; display: inline-block; margin-right: 8px;"></span>BMI (Calculated)</h4>
                <p><strong>No height/weight data available</strong></p>
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

def render_hospital_health_dashboard():
    """
    Render a hospital-style health dashboard with clean medical aesthetics.
    """
    # DASHBOARD DE SALUD MUY BLANCO Y MINIMALISTA
    st.markdown("""
    <style>
    /* Dashboard de salud muy limpio */
    .hospital-dashboard {
        font-family: -apple-system, BlinkMacSystemFont, 'San Francisco', 'Helvetica Neue', 'Inter', sans-serif;
        color: var(--text-primary);
        background: #ffffff !important;
        padding: 2rem;
        border-radius: 0;
    }
    
    .health-metric-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 1.5rem;
        margin-bottom: 2rem;
    }
    
    .health-metric-card {
        background: #ffffff !important;
        border-radius: 16px;
        padding: 2rem;
        border: 1px solid #f3f4f6 !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02) !important;
        transition: all 0.2s ease;
        position: relative;
    }
    
    .health-metric-card:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04) !important;
        transform: translateY(-2px);
        border-color: #e5e7eb !important;
    }
    
    .health-metric-card:focus-within {
        outline: 2px solid var(--primary-blue);
        outline-offset: 2px;
    }
    
    .metric-header {
        display: flex;
        align-items: center;
        margin-bottom: 1rem;
    }
    
    .metric-icon {
        width: 2.5rem;
        height: 2.5rem;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 0.75rem;
        font-size: 1.25rem;
        flex-shrink: 0;
    }
    
    .metric-icon.blue { 
        background: rgba(37, 99, 235, 0.1); 
        color: var(--primary-blue); 
        border: 1px solid rgba(37, 99, 235, 0.2);
    }
    .metric-icon.green { 
        background: rgba(16, 185, 129, 0.1); 
        color: var(--success-green);
        border: 1px solid rgba(16, 185, 129, 0.2);
    }
    .metric-icon.amber { 
        background: rgba(245, 158, 11, 0.1); 
        color: var(--warning-amber);
        border: 1px solid rgba(245, 158, 11, 0.2);
    }
    .metric-icon.red { 
        background: rgba(239, 68, 68, 0.1); 
        color: var(--danger-red);
        border: 1px solid rgba(239, 68, 68, 0.2);
    }
    
    .metric-title {
        font-size: 1rem;
        font-weight: 600;
        color: var(--text-primary);
        margin: 0;
        line-height: 1.3;
    }
    
    .metric-subtitle {
        font-size: 0.875rem;
        color: var(--text-secondary);
        margin: 0;
        line-height: 1.4;
    }
    
    .metric-value {
        font-size: 2.25rem;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0.75rem 0 0.5rem 0;
        line-height: 1;
    }
    
    .metric-unit {
        font-size: 0.875rem;
        color: var(--text-tertiary);
        font-weight: 500;
        margin-left: 0.25rem;
    }
    
    .metric-change {
        font-size: 0.875rem;
        font-weight: 500;
        display: flex;
        align-items: center;
        margin-top: 0.5rem;
    }
    
    .metric-change.positive { color: var(--success-green); }
    .metric-change.negative { color: var(--danger-red); }
    .metric-change.neutral { color: var(--text-tertiary); }
    
    .health-status-badge {
        position: absolute;
        top: 1rem;
        right: 1rem;
        padding: 0.375rem 0.875rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.025em;
        border: 1px solid transparent;
    }
    
    .status-excellent { 
        background: rgba(16, 185, 129, 0.1); 
        color: var(--success-green);
        border-color: rgba(16, 185, 129, 0.2);
    }
    .status-good { 
        background: rgba(37, 99, 235, 0.1); 
        color: var(--primary-blue);
        border-color: rgba(37, 99, 235, 0.2);
    }
    .status-fair { 
        background: rgba(245, 158, 11, 0.1); 
        color: var(--warning-amber);
        border-color: rgba(245, 158, 11, 0.2);
    }
    .status-poor { 
        background: rgba(239, 68, 68, 0.1); 
        color: var(--danger-red);
        border-color: rgba(239, 68, 68, 0.2);
    }
    
    .chart-container {
        background: var(--surface-elevated);
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid var(--border-primary);
        box-shadow: var(--shadow-sm);
        margin-bottom: 1.5rem;
        transition: all 0.2s ease;
    }
    
    .chart-container:hover {
        box-shadow: var(--shadow-md);
        transform: translateY(-1px);
    }
    
    .chart-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--text-primary);
        margin: 0 0 1rem 0;
        display: flex;
        align-items: center;
        line-height: 1.3;
    }
    
    .chart-icon {
        margin-right: 0.75rem;
        font-size: 1.5rem;
        color: var(--primary-blue);
        flex-shrink: 0;
    }
    
    .editable-section {
        background: var(--bg-tertiary);
        border-radius: 12px;
        padding: 1.5rem;
        border: 2px dashed var(--border-secondary);
        margin: 1.5rem 0;
        transition: all 0.2s ease;
    }
    
    .editable-section:hover {
        border-color: var(--primary-blue);
        background: rgba(37, 99, 235, 0.02);
    }
    
    .editable-title {
        font-size: 1.125rem;
        font-weight: 600;
        color: var(--text-primary);
        margin: 0 0 1rem 0;
        display: flex;
        align-items: center;
        line-height: 1.3;
    }
    
    .edit-icon {
        margin-right: 0.75rem;
        color: var(--primary-blue);
        font-size: 1.25rem;
        flex-shrink: 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize token manager for push operations
    try:
        if 'token_manager' not in st.session_state:
            st.session_state.token_manager = initialize_token_manager()
        token_manager = st.session_state.token_manager
    except Exception as e:
        st.warning(f"⚠️ Push functionality unavailable: {e}")
        token_manager = None
    
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
    
    # Demo mode toggle
    _, col2, _ = st.columns([2, 1, 2])
    with col2:
        demo_mode = st.session_state.get("demo_mode", False)
        if st.checkbox("🎭 Demo Mode", value=demo_mode, help="Enable demo mode to test editing without gateway push"):
            st.session_state["demo_mode"] = True
        else:
            st.session_state["demo_mode"] = False
            # Clear demo values when disabling demo mode
            for metric in ["height", "weight"]:
                if f"demo_{metric}_value" in st.session_state:
                    del st.session_state[f"demo_{metric}_value"]
    
    # Health metrics grid
    st.markdown('<div class="hospital-dashboard">', unsafe_allow_html=True)
    
    # Extract health data
    body_comp = health_data.get('body_composition', {})
    vital_signs = health_data.get('vital_signs', {})
    fitness = health_data.get('fitness', {})
    health_score = health_data.get('health_score', {})
    
    # Key metrics cards
    st.markdown('<div class="health-metric-grid">', unsafe_allow_html=True)
    
    # Health Score Card
    overall_score = health_score.get('overall', 0)
    if overall_score >= 80:
        status_class = "status-excellent"
        status_text = "Excellent"
        icon_class = "green"
    elif overall_score >= 60:
        status_class = "status-good"
        status_text = "Good"
        icon_class = "blue"
    elif overall_score >= 40:
        status_class = "status-fair"
        status_text = "Fair"
        icon_class = "amber"
    else:
        status_class = "status-poor"
        status_text = "Needs Attention"
        icon_class = "red"
    
    st.markdown(f"""
    <div class="health-metric-card">
        <div class="health-status-badge {status_class}">{status_text}</div>
        <div class="metric-header">
            <div class="metric-icon {icon_class}">❤️</div>
            <div>
                <h3 class="metric-title">Health Score</h3>
                <p class="metric-subtitle">Overall wellness</p>
            </div>
        </div>
        <div class="metric-value">{overall_score}<span class="metric-unit">/100</span></div>
    </div>
    """, unsafe_allow_html=True)
    
    # BMI Card
    bmi = body_comp.get('bmi', {}).get('current', 0)
    bmi_category = body_comp.get('bmi', {}).get('category', 'Unknown')
    
    if bmi:
        if 18.5 <= bmi <= 25:
            bmi_status = "status-excellent"
            bmi_icon = "green"
        elif 25 < bmi <= 30:
            bmi_status = "status-fair"
            bmi_icon = "amber"
        else:
            bmi_status = "status-poor"
            bmi_icon = "red"
        
        st.markdown(f"""
        <div class="health-metric-card">
            <div class="health-status-badge {bmi_status}">{bmi_category}</div>
            <div class="metric-header">
                <div class="metric-icon {bmi_icon}">⚖️</div>
                <div>
                    <h3 class="metric-title">Body Mass Index</h3>
                    <p class="metric-subtitle">Weight status</p>
                </div>
            </div>
            <div class="metric-value">{bmi:.1f}<span class="metric-unit">kg/m²</span></div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="health-metric-card">
            <div class="health-status-badge status-poor">No Data</div>
            <div class="metric-header">
                <div class="metric-icon amber">⚖️</div>
                <div>
                    <h3 class="metric-title">Body Mass Index</h3>
                    <p class="metric-subtitle">Weight status</p>
                </div>
            </div>
            <div class="metric-value">--<span class="metric-unit">kg/m²</span></div>
        </div>
        """, unsafe_allow_html=True)
    
    # Heart Rate Card
    hr = vital_signs.get('heartRate', {}).get('resting', 0)
    if hr:
        if 60 <= hr <= 100:
            hr_status = "status-excellent"
            hr_icon = "green"
        elif 100 < hr <= 120:
            hr_status = "status-fair"
            hr_icon = "amber"
        else:
            hr_status = "status-poor"
            hr_icon = "red"
        
        st.markdown(f"""
        <div class="health-metric-card">
            <div class="health-status-badge {hr_status}">Normal</div>
            <div class="metric-header">
                <div class="metric-icon {hr_icon}">💓</div>
                <div>
                    <h3 class="metric-title">Resting Heart Rate</h3>
                    <p class="metric-subtitle">Cardiovascular health</p>
                </div>
            </div>
            <div class="metric-value">{hr}<span class="metric-unit">bpm</span></div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="health-metric-card">
            <div class="health-status-badge status-poor">No Data</div>
            <div class="metric-header">
                <div class="metric-icon amber">💓</div>
                <div>
                    <h3 class="metric-title">Resting Heart Rate</h3>
                    <p class="metric-subtitle">Cardiovascular health</p>
                </div>
            </div>
            <div class="metric-value">--<span class="metric-unit">bpm</span></div>
        </div>
        """, unsafe_allow_html=True)
    
    # Daily Steps Card
    steps = fitness.get('steps', {}).get('daily_avg', 0)
    if steps:
        if steps >= 10000:
            steps_status = "status-excellent"
            steps_icon = "green"
        elif steps >= 7000:
            steps_status = "status-good"
            steps_icon = "blue"
        elif steps >= 5000:
            steps_status = "status-fair"
            steps_icon = "amber"
        else:
            steps_status = "status-poor"
            steps_icon = "red"
        
        st.markdown(f"""
        <div class="health-metric-card">
            <div class="health-status-badge {steps_status}">Active</div>
            <div class="metric-header">
                <div class="metric-icon {steps_icon}">👟</div>
                <div>
                    <h3 class="metric-title">Daily Steps</h3>
                    <p class="metric-subtitle">Physical activity</p>
                </div>
            </div>
            <div class="metric-value">{steps:,.0f}<span class="metric-unit">steps</span></div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="health-metric-card">
            <div class="health-status-badge status-poor">No Data</div>
            <div class="metric-header">
                <div class="metric-icon amber">👟</div>
                <div>
                    <h3 class="metric-title">Daily Steps</h3>
                    <p class="metric-subtitle">Physical activity</p>
                </div>
            </div>
            <div class="metric-value">--<span class="metric-unit">steps</span></div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)  # Close health-metric-grid
    
    # Editable Physical Profile Section
    st.markdown("""
    <div class="editable-section">
        <h3 class="editable-title"><span class="edit-icon">✏️</span>Editable Physical Profile</h3>
        <p style="color: #64748b; margin-bottom: 1.5rem;">Update your physical measurements to keep your health data current.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Editable metrics
    col1, col2 = st.columns(2)
    
    with col1:
        height = body_comp.get('height', {}).get('current')
        create_hospital_metric_card("Height", height, "m", "height", token_manager)
    
    with col2:
        weight = body_comp.get('weight', {}).get('current')
        create_hospital_metric_card("Weight", weight, "kg", "weight", token_manager)
    
    # Charts section
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<h3 class="chart-title"><span class="chart-icon">📊</span>BMI Analysis</h3>', unsafe_allow_html=True)
        fig_bmi = create_hospital_bmi_chart(health_data)
        st.plotly_chart(fig_bmi, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<h3 class="chart-title"><span class="chart-icon">📈</span>Key Metrics</h3>', unsafe_allow_html=True)
        fig_metrics = create_hospital_metrics_chart(health_data)
        st.plotly_chart(fig_metrics, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Health Score Gauge
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<h3 class="chart-title"><span class="chart-icon">🎯</span>Overall Health Score</h3>', unsafe_allow_html=True)
    fig_gauge = create_hospital_health_gauge(health_data)
    st.plotly_chart(fig_gauge, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Last update info
    last_updated = health_data.get('generated_at')
    if last_updated:
        update_time = datetime.fromisoformat(last_updated.replace('Z', '+00:00')).strftime('%B %d, %Y at %H:%M UTC')
        st.markdown(f"""
        <div style="text-align: center; color: #64748b; font-size: 0.875rem; margin-top: 2rem; padding: 1rem; background: #f8fafc; border-radius: 8px;">
            <p style="margin: 0;">Health data last updated on {update_time}</p>
            <p style="margin: 0.25rem 0 0 0;">Metrics are automatically synchronized from your connected devices</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)  # Close hospital-dashboard

def create_hospital_metric_card(title: str, current_value: float, unit: str, metric_type: str, 
                               token_manager) -> None:
    """
    Create a hospital-style editable metric card.
    
    Args:
        title: Display title for the metric
        current_value: Current value to display
        unit: Unit of measurement
        metric_type: Type of metric ('height' or 'weight')
        token_manager: Token manager for API calls
    """
    
    # Create container for the metric
    with st.container():
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Check for demo value first, then current value
            demo_value = st.session_state.get(f"demo_{metric_type}_value")
            display_value = demo_value if demo_value is not None else current_value
            is_demo = demo_value is not None
            
            # Display current value with hospital styling
            if display_value:
                demo_indicator = " (Demo)" if is_demo else ""
                status_color = "#f59e0b" if is_demo else "#2563eb"  # Amber for demo, blue for real
                st.markdown(f"""
                <div class="health-metric-card" style="margin-bottom: 1rem;">
                    <div class="metric-header">
                        <div class="metric-icon blue">📏</div>
                        <div>
                            <h3 class="metric-title">{title}{demo_indicator}</h3>
                            <p class="metric-subtitle">Physical measurement</p>
                        </div>
                    </div>
                    <div class="metric-value">{display_value:.2f}<span class="metric-unit">{unit}</span></div>
                    <div style="display: flex; align-items: center; margin-top: 0.5rem;">
                        <span class="status-dot" style="background-color: {status_color};"></span>
                        <span style="color: #64748b; font-size: 0.875rem;">
                            {'Demo data' if is_demo else 'Current measurement'}
                        </span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="health-metric-card" style="margin-bottom: 1rem;">
                    <div class="metric-header">
                        <div class="metric-icon amber">📏</div>
                        <div>
                            <h3 class="metric-title">{title}</h3>
                            <p class="metric-subtitle">Physical measurement</p>
                        </div>
                    </div>
                    <div class="metric-value">--<span class="metric-unit">{unit}</span></div>
                    <div style="display: flex; align-items: center; margin-top: 0.5rem;">
                        <span class="status-dot" style="background-color: #f59e0b;"></span>
                        <span style="color: #64748b; font-size: 0.875rem;">No data available</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            # Change button
            if st.button("✏️ Edit", key=f"change_{metric_type}", 
                        help=f"Update {title.lower()}", type="secondary"):
                st.session_state[f"edit_{metric_type}"] = True
        
        # Show edit form if button was clicked
        if st.session_state.get(f"edit_{metric_type}", False):
            with st.form(f"edit_{metric_type}_form"):
                st.markdown(f"**Update {title}**")
                
                # Input field with appropriate range and step
                demo_value = st.session_state.get(f"demo_{metric_type}_value")
                default_value = demo_value if demo_value is not None else current_value
                
                if metric_type == "height":
                    new_value = st.number_input(
                        f"New {title} ({unit})",
                        min_value=0.5,
                        max_value=2.5,
                        value=default_value if default_value else 1.70,
                        step=0.01,
                        format="%.2f"
                    )
                else:  # weight
                    new_value = st.number_input(
                        f"New {title} ({unit})",
                        min_value=20.0,
                        max_value=300.0,
                        value=default_value if default_value else 70.0,
                        step=0.1,
                        format="%.1f"
                    )
                
                col1, col2 = st.columns(2)
                with col1:
                    submit = st.form_submit_button("💾 Save & Push", type="primary")
                with col2:
                    cancel = st.form_submit_button("❌ Cancel")
                
                if submit:
                    # Check if demo mode is enabled
                    demo_mode = st.session_state.get("demo_mode", False)
                    
                    if demo_mode:
                        # Demo mode: simulate successful push
                        with st.spinner(f"Simulating {title.lower()} data push..."):
                            time.sleep(1)  # Simulate network delay
                            # Store the new value in session state for display
                            st.session_state[f"demo_{metric_type}_value"] = new_value
                            st.success(f"✅ Demo: {title} updated to {new_value} {unit} (not pushed to gateway)")
                            st.session_state[f"edit_{metric_type}"] = False
                            st.rerun()
                    else:
                        # Real mode: attempt to push to Health Connect Gateway
                        with st.spinner(f"Pushing {title.lower()} data..."):
                            try:
                                if metric_type == "height":
                                    success, message = push_height_data(new_value, token_manager)
                                else:  # weight
                                    success, message = push_weight_data(new_value, token_manager)
                                
                                if success:
                                    st.success(f"✅ {message}")
                                    st.session_state[f"edit_{metric_type}"] = False
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.error(f"❌ {message}")
                                    
                            except Exception as e:
                                error_msg = str(e)
                                st.error(f"❌ **Error**: {error_msg}")
                                
                                # Offer demo mode if FCM token error is detected
                                if "fcm token" in error_msg.lower() or "push functionality requires" in error_msg.lower():
                                    st.info("💡 **Tip**: Enable Demo Mode to test the interface without gateway push requirements")
                                    if st.button("🎭 Enable Demo Mode", key=f"enable_demo_{metric_type}"):
                                        st.session_state["demo_mode"] = True
                                        st.success("Demo Mode enabled! Try editing again.")
                                        st.rerun()
                
                if cancel:
                    st.session_state[f"edit_{metric_type}"] = False
                    st.rerun()

def create_hospital_bmi_chart(health_data: Dict[str, Any]) -> go.Figure:
    """
    Create a hospital-style BMI visualization.
    
    Args:
        health_data: Comprehensive health data dictionary
    
    Returns:
        Plotly figure with BMI analysis
    """
    theme = create_hospital_theme()
    body_comp = health_data.get('body_composition', {})
    
    fig = go.Figure()
    
    # BMI visualization
    bmi = body_comp.get('bmi', {}).get('current', 0)
    
    if bmi > 0:
        # BMI categories visualization
        categories = ['Underweight', 'Normal', 'Overweight', 'Obese']
        ranges = [18.5, 25, 30, 40]
        colors = [theme['warning'], theme['success'], theme['warning'], theme['danger']]
        
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
            name='BMI Ranges',
            textfont={'color': 'white', 'size': 12, 'family': '-apple-system, BlinkMacSystemFont, sans-serif'}
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
            font={'size': 14, 'color': theme['text'], 'family': '-apple-system, BlinkMacSystemFont, sans-serif'}
        )
    
    fig.update_layout(
        paper_bgcolor=theme['bg_color'],
        plot_bgcolor=theme['bg_color'],
        font={'color': theme['text'], 'family': '-apple-system, BlinkMacSystemFont, sans-serif'},
        showlegend=False,
        height=250,
        margin={'l': 80, 'r': 20, 't': 20, 'b': 40}
    )
    
    fig.update_xaxes(
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

def create_hospital_metrics_chart(health_data: Dict[str, Any]) -> go.Figure:
    """
    Create a hospital-style metrics overview chart.
    
    Args:
        health_data: Health data dictionary
    
    Returns:
        Plotly metrics chart figure
    """
    theme = create_hospital_theme()
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
            paper_bgcolor=theme['bg_color'],
            plot_bgcolor=theme['bg_color'],
            font={'color': theme['text'], 'family': '-apple-system, BlinkMacSystemFont, sans-serif'},
            height=250
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
            textfont={'color': theme['text'], 'size': 12, 'family': '-apple-system, BlinkMacSystemFont, sans-serif'}
        )
    ])
    
    fig.update_layout(
        paper_bgcolor=theme['bg_color'],
        plot_bgcolor=theme['bg_color'],
        font={'color': theme['text'], 'family': '-apple-system, BlinkMacSystemFont, sans-serif'},
        showlegend=False,
        height=250,
        margin={'l': 40, 'r': 40, 't': 20, 'b': 40}
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

def create_hospital_health_gauge(health_data: Dict[str, Any]) -> go.Figure:
    """
    Create a hospital-style health score gauge.
    
    Args:
        health_data: Health data dictionary
    
    Returns:
        Plotly gauge figure
    """
    theme = create_hospital_theme()
    health_score = health_data.get('health_score', {})
    overall_score = health_score.get('overall', 0)
    
    # Determine color based on score
    if overall_score >= 80:
        bar_color = theme['success']
    elif overall_score >= 60:
        bar_color = theme['primary']
    elif overall_score >= 40:
        bar_color = theme['warning']
    else:
        bar_color = theme['danger']
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=overall_score,
        domain={'x': [0, 1], 'y': [0, 1]},
        number={'font': {'size': 40, 'color': theme['text'], 'family': '-apple-system, BlinkMacSystemFont, sans-serif'}},
        gauge={
            'axis': {
                'range': [None, 100], 
                'tickcolor': theme['text'],
                'tickfont': {'color': theme['text'], 'size': 12, 'family': '-apple-system, BlinkMacSystemFont, sans-serif'}
            },
            'bar': {'color': bar_color, 'thickness': 0.3},
            'bgcolor': theme['light_gray'],
            'borderwidth': 2,
            'bordercolor': theme['border'],
            'steps': [
                {'range': [0, 40], 'color': theme['light_gray']},
                {'range': [40, 60], 'color': theme['light_gray']},
                {'range': [60, 80], 'color': theme['light_gray']},
                {'range': [80, 100], 'color': theme['light_gray']}
            ]
        }
    ))
    
    fig.update_layout(
        paper_bgcolor=theme['bg_color'],
        plot_bgcolor=theme['bg_color'],
        font={'color': theme['text'], 'family': '-apple-system, BlinkMacSystemFont, sans-serif'},
        height=300,
        margin={'l': 20, 'r': 20, 't': 20, 'b': 20}
    )
    
    return fig
