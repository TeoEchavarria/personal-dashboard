"""
Personal Dashboard - Main Streamlit Application
Frontend interface for the personal dashboard application.
"""

import streamlit as st
import sys
import os
import pandas as pd
from datetime import datetime

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import only what we need to avoid wildcard imports
from core.data_extractors.hc_collect import (
    get_method_raw_data, 
    get_method_last_update, 
    get_all_methods_status,
    collect_method_data,
    collect_all_methods_data,
    initialize_token_manager,
    METHODS
)
from core.utils.config import config

def main():
    """Main application function."""
    st.set_page_config(
        page_title="Health Portal",
        page_icon="🏥",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # DISEÑO MINIMALISTA MUY BLANCO Y LIMPIO
    st.markdown("""
    <style>
    /* Import system fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
    
    /* COLORES MINIMALISTAS - TODO MUY BLANCO */
    :root {
        /* BLANCO PRINCIPAL - MUY LIMPIO */
        --bg-primary: #ffffff;
        --bg-secondary: #ffffff;
        --bg-tertiary: #fefefe;
        --surface-elevated: #ffffff;
        
        /* AZUL SUAVE PARA ACENTOS */
        --primary-blue: #3b82f6;
        --primary-blue-light: #60a5fa;
        --primary-blue-dark: #2563eb;
        
        /* COLORES DE ESTADO MUY SUAVES */
        --success-green: #22c55e;
        --warning-amber: #f59e0b;
        --danger-red: #ef4444;
        
        /* TEXTO MUY LEGIBLE */
        --text-primary: #1f2937;
        --text-secondary: #6b7280;
        --text-tertiary: #9ca3af;
        --text-on-primary: #ffffff;
        
        /* BORDES MUY SUTILES */
        --border-primary: #f3f4f6;
        --border-secondary: #e5e7eb;
        
        /* SOMBRAS MUY SUAVES */
        --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.02);
        --shadow-md: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
        --shadow-lg: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    
    /* Global styles */
    .main .block-container {
        padding-top: 0rem;
        padding-left: 0rem;
        padding-right: 0rem;
        max-width: 100%;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Ensure proper color inheritance */
    .stApp {
        background-color: var(--bg-secondary);
        color: var(--text-primary);
    }
    
    /* SIDEBAR MUY CLARO Y VISIBLE */
    .css-1d391kg {
        background: #ffffff !important;
        border-right: 2px solid #f3f4f6 !important;
        padding: 0;
    }
    
    .sidebar .sidebar-content {
        background: #ffffff !important;
        color: var(--text-primary) !important;
        padding: 0;
    }
    
    /* HEADER DEL SIDEBAR MUY VISIBLE */
    .sidebar-header {
        background: #f8fafc !important;
        padding: 2rem 1.5rem;
        border-bottom: 2px solid #e5e7eb !important;
        margin-bottom: 1rem;
    }
    
    .sidebar-header h1 {
        color: var(--text-primary) !important;
        font-family: -apple-system, BlinkMacSystemFont, 'San Francisco', 'Helvetica Neue', 'Inter', sans-serif;
        font-size: 1.5rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.025em;
    }
    
    .sidebar-header p {
        color: var(--text-secondary) !important;
        font-size: 0.875rem;
        margin: 0.5rem 0 0 0;
        font-family: -apple-system, BlinkMacSystemFont, 'San Francisco', 'Helvetica Neue', 'Inter', sans-serif;
        font-weight: 500;
    }
    
    /* BOTONES DEL MENÚ MUY VISIBLES */
    .stButton > button {
        display: flex !important;
        align-items: center !important;
        padding: 1rem 1.5rem !important;
        margin: 0.5rem 1rem !important;
        border-radius: 8px !important;
        color: var(--text-primary) !important;
        text-decoration: none !important;
        font-family: -apple-system, BlinkMacSystemFont, 'San Francisco', 'Helvetica Neue', 'Inter', sans-serif !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
        cursor: pointer !important;
        border: 2px solid #f3f4f6 !important;
        background: #ffffff !important;
        width: calc(100% - 2rem) !important;
        text-align: left !important;
        min-height: 50px !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05) !important;
    }
    
    .stButton > button:hover {
        background: #f8fafc !important;
        color: var(--primary-blue) !important;
        transform: translateY(-1px) !important;
        border-color: var(--primary-blue) !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15) !important;
    }
    
    .stButton > button:focus {
        outline: 3px solid var(--primary-blue-light) !important;
        outline-offset: 2px !important;
        border-color: var(--primary-blue) !important;
    }
    
    .stButton > button:active {
        background: var(--primary-blue) !important;
        color: white !important;
        transform: translateY(0) !important;
        box-shadow: 0 2px 4px rgba(59, 130, 246, 0.25) !important;
    }
    
    /* ÁREA PRINCIPAL MUY BLANCA Y LIMPIA */
    .main-content {
        background: #ffffff !important;
        min-height: 100vh;
        padding: 0;
    }
    
    /* HEADER MUY LIMPIO */
    .header-bar {
        background: #ffffff !important;
        border-bottom: 1px solid #f3f4f6 !important;
        padding: 2rem 2rem 1.5rem 2rem;
        box-shadow: none !important;
    }
    
    .header-title {
        color: var(--text-primary) !important;
        font-family: -apple-system, BlinkMacSystemFont, 'San Francisco', 'Helvetica Neue', 'Inter', sans-serif;
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.025em;
    }
    
    .header-subtitle {
        color: var(--text-secondary) !important;
        font-family: -apple-system, BlinkMacSystemFont, 'San Francisco', 'Helvetica Neue', 'Inter', sans-serif;
        font-size: 1rem;
        margin: 0.5rem 0 0 0;
        font-weight: 400;
    }
    
    /* Content area */
    .content-area {
        padding: 2rem;
        max-width: 1200px;
        margin: 0 auto;
    }
    
    /* TARJETAS MÉDICAS MUY BLANCAS Y MINIMALISTAS */
    .medical-card {
        background: #ffffff !important;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03) !important;
        border: 1px solid #f3f4f6 !important;
        padding: 2rem;
        margin-bottom: 1.5rem;
        transition: all 0.2s ease;
        position: relative;
    }
    
    .medical-card:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05) !important;
        transform: translateY(-2px);
        border-color: #e5e7eb !important;
    }
    
    .medical-card:focus-within {
        outline: 2px solid var(--primary-blue);
        outline-offset: 2px;
    }
    
    .medical-card h3 {
        color: var(--text-primary) !important;
        font-family: -apple-system, BlinkMacSystemFont, 'San Francisco', 'Helvetica Neue', 'Inter', sans-serif;
        font-size: 1.25rem;
        font-weight: 700;
        margin: 0 0 1rem 0;
        display: flex;
        align-items: center;
        line-height: 1.3;
    }
    
    .medical-card .card-icon {
        margin-right: 1rem;
        color: var(--primary-blue) !important;
        font-size: 1.75rem;
        width: 1.75rem;
        text-align: center;
        flex-shrink: 0;
    }
    
    .medical-card p {
        color: var(--text-secondary) !important;
        font-family: -apple-system, BlinkMacSystemFont, 'San Francisco', 'Helvetica Neue', 'Inter', sans-serif;
        font-size: 0.95rem;
        line-height: 1.6;
        margin: 0;
        font-weight: 400;
    }
    
    /* Status indicators with better accessibility */
    .status-dot {
        width: 0.625rem;
        height: 0.625rem;
        border-radius: 50%;
        display: inline-block;
        margin-right: 0.75rem;
        flex-shrink: 0;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .status-dot.green { 
        background-color: var(--success-green); 
        border-color: var(--success-green);
    }
    .status-dot.yellow { 
        background-color: var(--warning-amber); 
        border-color: var(--warning-amber);
    }
    .status-dot.blue { 
        background-color: var(--primary-blue); 
        border-color: var(--primary-blue);
    }
    .status-dot.red { 
        background-color: var(--danger-red); 
        border-color: var(--danger-red);
    }
    
    /* Typography with theme support */
    .stMarkdown {
        font-family: -apple-system, BlinkMacSystemFont, 'San Francisco', 'Helvetica Neue', 'Inter', sans-serif;
        color: var(--text-primary);
    }
    
    /* BOTONES MINIMALISTAS Y LIMPIOS */
    .content-area .stButton > button {
        background: #ffffff !important;
        color: var(--primary-blue) !important;
        border: 2px solid var(--primary-blue) !important;
        border-radius: 8px !important;
        padding: 0.75rem 2rem !important;
        font-family: -apple-system, BlinkMacSystemFont, 'San Francisco', 'Helvetica Neue', 'Inter', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        transition: all 0.2s ease !important;
        min-height: 48px !important;
        cursor: pointer !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03) !important;
    }
    
    .content-area .stButton > button:hover {
        background: var(--primary-blue) !important;
        color: white !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2) !important;
        border-color: var(--primary-blue) !important;
    }
    
    .content-area .stButton > button:focus {
        outline: 3px solid var(--primary-blue-light) !important;
        outline-offset: 2px !important;
    }
    
    .content-area .stButton > button:active {
        transform: translateY(0) !important;
        box-shadow: 0 2px 4px rgba(59, 130, 246, 0.25) !important;
    }
    
    /* BOTÓN SECUNDARIO MINIMALISTA */
    .stButton > button[kind="secondary"] {
        background: #ffffff !important;
        color: var(--text-secondary) !important;
        border: 1px solid #e5e7eb !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02) !important;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: #f8fafc !important;
        color: var(--text-primary) !important;
        border-color: #d1d5db !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05) !important;
    }
    
    /* MÉTRICAS MUY LIMPIAS Y MINIMALISTAS */
    .metric-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 2rem;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: #ffffff !important;
        border-radius: 16px;
        padding: 2rem;
        border: 1px solid #f3f4f6 !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02) !important;
        transition: all 0.2s ease;
    }
    
    .metric-card:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04) !important;
        transform: translateY(-2px);
        border-color: #e5e7eb !important;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        color: var(--text-primary) !important;
        margin: 0;
        font-family: -apple-system, BlinkMacSystemFont, 'San Francisco', 'Helvetica Neue', 'Inter', sans-serif;
        line-height: 1;
    }
    
    .metric-label {
        font-size: 1rem;
        color: var(--text-secondary) !important;
        margin: 0.75rem 0 0 0;
        font-family: -apple-system, BlinkMacSystemFont, 'San Francisco', 'Helvetica Neue', 'Inter', sans-serif;
        font-weight: 500;
    }
    
    /* FORMULARIOS MUY LIMPIOS */
    .stSelectbox > div > div {
        background-color: #ffffff !important;
        border: 2px solid #f3f4f6 !important;
        border-radius: 8px !important;
        color: var(--text-primary) !important;
        font-family: -apple-system, BlinkMacSystemFont, 'San Francisco', 'Helvetica Neue', 'Inter', sans-serif !important;
        font-weight: 500 !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02) !important;
    }
    
    .stSelectbox > div > div:focus {
        border-color: var(--primary-blue) !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
    }
    
    .stNumberInput > div > div > input {
        background-color: #ffffff !important;
        border: 2px solid #f3f4f6 !important;
        border-radius: 8px !important;
        color: var(--text-primary) !important;
        font-family: -apple-system, BlinkMacSystemFont, 'San Francisco', 'Helvetica Neue', 'Inter', sans-serif !important;
        font-weight: 500 !important;
        font-size: 0.95rem !important;
        padding: 0.75rem !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02) !important;
    }
    
    .stNumberInput > div > div > input:focus {
        border-color: var(--primary-blue) !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
    }
    
    .stCheckbox > label {
        color: var(--text-primary) !important;
        font-family: -apple-system, BlinkMacSystemFont, 'San Francisco', 'Helvetica Neue', 'Inter', sans-serif !important;
        font-weight: 500 !important;
        font-size: 0.95rem !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Sidebar navigation
    with st.sidebar:
        # Header
        st.markdown("""
        <div class="sidebar-header">
            <h1>🏥 Health Portal</h1>
            <p>Personal Health Dashboard</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Initialize page in session state if not exists
    if 'page' not in st.session_state:
        st.session_state.page = "Home"
    
        # Navigation items
        nav_items = [
            ("Home", "🏠", "Home"),
            ("Health", "❤️", "Health"), 
            ("Life", "🌱", "Life"),
            ("Other options", "⚙️", "Settings")
        ]
        
        for label, icon, page_key in nav_items:
            if st.button(f"{icon} {label}", key=f"nav_{page_key}", 
                        help=f"Navigate to {label}",
                        use_container_width=True):
                st.session_state.page = page_key
                st.rerun()
    
    # Get current page
    page = st.session_state.page
    
    # Main content area with hospital-style layout
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    
    # Header bar
    page_titles = {
        "Home": ("¡Hola Mateo!", "Welcome to your health portal"),
        "Health": ("Health Dashboard", "Your comprehensive health overview"),
        "Life": ("Life & Wellness", "Lifestyle and wellness tracking"),
        "Settings": ("Settings", "Configure your health portal")
    }
    
    title, subtitle = page_titles.get(page, ("Health Portal", "Personal health management"))
    
    st.markdown(f"""
    <div class="header-bar">
        <h1 class="header-title">{title}</h1>
        <p class="header-subtitle">{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Content area
    st.markdown('<div class="content-area">', unsafe_allow_html=True)
    
    if page == "Home":
        show_home_page()
    elif page == "Health":
        show_health_page()
    elif page == "Life":
        show_life_page()
    elif page == "Settings":
        show_settings_page()
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def show_home_page():
    """Display the home page with hospital-style overview cards."""
    # Overview cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="medical-card">
            <h3><span class="card-icon">📅</span>Medical Appointments</h3>
            <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                <span class="status-dot green"></span>
                <span style="color: #374151; font-size: 0.875rem;">No upcoming appointments</span>
            </div>
            <p style="color: #6b7280; font-size: 0.875rem; margin: 0;">Schedule your next check-up</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="medical-card">
            <h3><span class="card-icon">🏥</span>Insurance Plans</h3>
            <div style="margin-bottom: 0.75rem;">
                <div style="display: flex; align-items: center; margin-bottom: 0.25rem;">
                    <span class="status-dot blue"></span>
                    <span style="color: #374151; font-size: 0.875rem; font-weight: 500;">ARL</span>
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 0.25rem;">
                    <span class="status-dot green"></span>
                    <span style="color: #374151; font-size: 0.875rem; font-weight: 500;">Sura Health</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="medical-card">
            <h3><span class="card-icon">💊</span>Medications</h3>
            <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                <span class="status-dot yellow"></span>
                <span style="color: #374151; font-size: 0.875rem;">No active prescriptions</span>
            </div>
            <p style="color: #6b7280; font-size: 0.875rem; margin: 0;">Add your medications</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="medical-card">
            <h3><span class="card-icon">📊</span>Health Status</h3>
            <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                <span class="status-dot green"></span>
                <span style="color: #374151; font-size: 0.875rem;">All systems normal</span>
            </div>
            <p style="color: #6b7280; font-size: 0.875rem; margin: 0;">Last updated today</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Quick actions section
    st.markdown("""
    <div style="margin: 2rem 0;">
        <h2 style="color: #1e293b; font-family: -apple-system, BlinkMacSystemFont, 'San Francisco', 'Helvetica Neue', 'Inter', sans-serif; font-size: 1.5rem; font-weight: 600; margin-bottom: 1rem;">Quick Actions</h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📋 View Health Dashboard", use_container_width=True):
            st.session_state.page = "Health"
            st.rerun()
    
    with col2:
        if st.button("📈 View Analytics", use_container_width=True):
            st.session_state.page = "Health"
            st.rerun()
    
    with col3:
        if st.button("⚙️ Settings", use_container_width=True):
            st.session_state.page = "Settings"
            st.rerun()

def show_health_page():
    """Display the health dashboard page."""
    # Check if HCG is configured
    try:
        if config.validate_hcg_config():
            # Import and render the minimal health dashboard
            try:
                from components.health_dashboard import render_hospital_health_dashboard
                render_hospital_health_dashboard()
            except Exception as e:
                st.error(f"Error loading health dashboard: {e}")
                st.info("Falling back to basic summary...")
                show_hcg_summary()
        else:
            st.warning("⚠️ Health Connect Gateway not configured. Please set up your .env file.")
            st.info("Go to Settings to configure your connection.")
    except Exception as e:
        st.error(f"Configuration error: {e}")

def show_life_page():
    """Display the life and wellness page."""
    st.markdown("""
    <div class="medical-card">
        <h3><span class="card-icon">🌱</span>Life & Wellness Tracking</h3>
        <p style="color: #6b7280; margin: 0;">This section will contain lifestyle and wellness metrics including sleep patterns, stress levels, and daily activities.</p>
    </div>
    """, unsafe_allow_html=True)

def show_hcg_summary():
    """Display Health Connect Gateway summary on home page."""
    try:
        status_data = get_all_methods_status()
        
        # Calculate summary stats
        total_methods = len(METHODS)
        methods_with_data = sum(1 for status in status_data.values() if status['has_data'])
        total_records = sum(status.get('record_count', 0) for status in status_data.values())
        
        # Get most recent update
        recent_updates = []
        for method, status in status_data.items():
            last_update = status.get('last_update', 'Never')
            if last_update != 'Never' and not last_update.startswith('Invalid'):
                recent_updates.append((method, last_update))
        
        # Sort by timestamp string (works because of YYYY-MM-DD format)
        recent_updates.sort(key=lambda x: x[1], reverse=True)
        last_update_text = recent_updates[0][1] if recent_updates else "Never"
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Health Data Stats")
            st.metric("Configured Methods", total_methods)
            st.metric("Methods with Data", methods_with_data)
            st.metric("Total Records", f"{total_records:,}")
        
        with col2:
            st.subheader("🕒 Recent Activity")
            st.info(f"Last Update: {last_update_text}")
            
            if recent_updates:
                st.success("✅ Data collection active")
                
                # Show top methods by record count
                top_methods = sorted(
                    [(method, status.get('record_count', 0)) for method, status in status_data.items()],
                    key=lambda x: x[1],
                    reverse=True
                )[:3]
                
                st.write("**Top Methods by Records:**")
                for method, count in top_methods:
                    if count > 0:
                        st.write(f"• {method}: {count:,} records")
            else:
                st.warning("⚠️ No data collected yet")
        
        # Quick actions
        st.markdown("---")
        st.subheader("🚀 Quick Actions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Update All Data", type="primary"):
                update_all_methods()
        
        with col2:
            if st.button("📊 View Data Sources"):
                st.session_state.page = "Data Sources"
                st.rerun()
        
        with col3:
            if st.button("📈 View Analytics"):
                st.session_state.page = "Analytics"
                st.rerun()
                
    except Exception as e:
        st.error(f"Error loading Health Connect data: {e}")
        st.info("Please check your configuration and try again.")

def show_data_sources_page():
    """Display the data sources page."""
    st.header("🔗 Health Connect Data Sources")
    
    # Check configuration
    try:
        if not config.validate_hcg_config():
            st.error("❌ Health Connect Gateway configuration is missing. Please check your .env file.")
            st.info("Required variables: HCG_USERNAME, HCG_PASSWORD")
            return
    except Exception as e:
        st.error(f"❌ Configuration error: {e}")
        return
    
    # Get configuration info
    hcg_config = config.get_hcg_config()
    st.info(f"📡 Connected to: {hcg_config['base_url']}")
    st.info(f"🔄 Methods mode: {hcg_config['methods_mode']} ({len(METHODS)} methods)")
    
    # Date range selector
    st.subheader("📅 Date Range Selection")
    col1, col2, col3 = st.columns([2, 2, 2])
    
    with col1:
        use_date_range = st.checkbox("Use specific date range", 
                                   help="If unchecked, will use incremental updates from last sync")
    
    start_date = None
    end_date = None
    
    if use_date_range:
        with col2:
            start_date_input = st.date_input(
                "Start Date",
                value=datetime.now().date() - pd.Timedelta(days=7),
                help="Start date for data collection"
            )
            start_date = f"{start_date_input}T00:00:00Z"
        
        with col3:
            end_date_input = st.date_input(
                "End Date", 
                value=datetime.now().date(),
                help="End date for data collection"
            )
            end_date = f"{end_date_input}T23:59:59Z"
        
        # Validate date range
        if start_date_input > end_date_input:
            st.error("❌ Start date must be before end date")
            return
        
        # Show selected range
        days_diff = (end_date_input - start_date_input).days + 1
        st.info(f"📊 Selected range: {days_diff} day(s) from {start_date_input} to {end_date_input}")
    
    st.markdown("---")
    
    # Update buttons
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        if st.button("🔄 Update All Methods", type="primary"):
            update_all_methods(start_date, end_date)
    
    with col2:
        if st.button("📊 Refresh Status"):
            st.rerun()
    
    with col3:
        st.write("")  # Spacer
    
    st.markdown("---")
    
    # Get status for all methods
    try:
        status_data = get_all_methods_status()
        
        # Display methods in tabs
        if METHODS:
            # Create tabs for different method groups
            tab1, tab2 = st.tabs(["📊 Method Status", "📋 Raw Data Viewer"])
            
            with tab1:
                show_methods_status(status_data, start_date, end_date)
            
            with tab2:
                show_raw_data_viewer()
        else:
            st.warning("No methods configured.")
            
    except Exception as e:
        st.error(f"Error loading data: {e}")

def show_methods_status(status_data, start_date=None, end_date=None):
    """Display status information for all methods."""
    st.subheader("Methods Status Overview")
    
    # Create metrics row
    total_methods = len(METHODS)
    methods_with_data = sum(1 for status in status_data.values() if status['has_data'])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Methods", total_methods)
    with col2:
        st.metric("With Data", methods_with_data)
    with col3:
        st.metric("Empty", total_methods - methods_with_data)
    
    st.markdown("---")
    
    # Display each method
    for method in METHODS:
        status = status_data.get(method, {})
        
        with st.expander(f"📊 {method}", expanded=False):
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                st.write(f"**Last Update:** {status.get('last_update', 'Never')}")
                st.write(f"**Records:** {status.get('record_count', 0):,}")
            
            with col2:
                if status.get('has_data', False):
                    st.success("✅ Has data")
                else:
                    st.warning("⚠️ No data")
            
            with col3:
                if st.button(f"🔄", key=f"update_{method}"):
                    update_single_method(method, start_date, end_date)

def show_raw_data_viewer():
    """Display raw data viewer for methods."""
    st.subheader("Raw Data Viewer")
    
    # Method selector
    selected_method = st.selectbox(
        "Select method to view raw data:",
        METHODS,
        key="raw_data_method"
    )
    
    if selected_method:
        # Get raw data
        try:
            df = get_method_raw_data(selected_method, limit=5)
            
            if not df.empty:
                st.write(f"**First 5 records from {selected_method}:**")
                st.dataframe(df, use_container_width=True)
                
                # Show column info
                with st.expander("📋 Column Information"):
                    col_info = []
                    for col in df.columns:
                        col_info.append({
                            "Column": col,
                            "Type": str(df[col].dtype),
                            "Non-null": df[col].count(),
                            "Sample": str(df[col].iloc[0]) if len(df) > 0 else "N/A"
                        })
                    st.dataframe(pd.DataFrame(col_info), use_container_width=True)
            else:
                st.info(f"No data available for {selected_method}")
                
        except Exception as e:
            st.error(f"Error loading data for {selected_method}: {e}")

def update_single_method(method, start_date=None, end_date=None):
    """Update data for a single method."""
    date_info = ""
    if start_date and end_date:
        date_info = f" (from {start_date[:10]} to {end_date[:10]})"
    
    with st.spinner(f"Updating {method}{date_info}..."):
        try:
            # Initialize token manager in session state to reuse
            if 'token_manager' not in st.session_state:
                st.session_state.token_manager = initialize_token_manager()
            
            count, since, error = collect_method_data(method, st.session_state.token_manager, start_date=start_date, end_date=end_date)
            
            if error:
                st.error(f"❌ Error updating {method}: {error}")
                # Clear token manager if there's an auth error
                if "401" in error or "Unauthorized" in error:
                    if 'token_manager' in st.session_state:
                        del st.session_state.token_manager
            else:
                st.success(f"✅ Updated {method}: {count} new records{date_info}")
                if since:
                    st.info(f"📅 Reference date: {since}")
                st.rerun()
                
        except Exception as e:
            st.error(f"❌ Failed to update {method}: {e}")
            # Clear token manager on any error to force re-authentication
            if 'token_manager' in st.session_state:
                del st.session_state.token_manager

def update_all_methods(start_date=None, end_date=None):
    """Update data for all methods."""
    date_info = ""
    if start_date and end_date:
        date_info = f" (from {start_date[:10]} to {end_date[:10]})"
    
    with st.spinner(f"Updating all methods{date_info}..."):
        try:
            # Initialize token manager in session state to reuse
            if 'token_manager' not in st.session_state:
                st.session_state.token_manager = initialize_token_manager()
            
            results = collect_all_methods_data(st.session_state.token_manager, start_date=start_date, end_date=end_date)
            
            # Display results
            success_count = 0
            error_count = 0
            total_records = 0
            
            for method, (count, since, error) in results.items():
                if error:
                    st.error(f"❌ {method}: {error}")
                    error_count += 1
                else:
                    total_records += count
                    success_count += 1
            
            if success_count > 0:
                st.success(f"✅ Updated {success_count} methods successfully. Total new records: {total_records}{date_info}")
            
            if error_count > 0:
                st.warning(f"⚠️ {error_count} methods had errors")
            
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Failed to update methods: {e}")

def show_settings_page():
    """Display the settings page with medical theme."""
    # Configuration section
    st.markdown("""
    <div class="medical-card">
        <h3><span class="card-icon">🔗</span>Health Connect Gateway</h3>
        <p style="color: #6b7280; margin-bottom: 1rem;">Configure your connection to Health Connect Gateway for data synchronization.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check configuration status
    try:
        if config.validate_hcg_config():
            st.success("✅ Health Connect Gateway is properly configured")
            
            # Show data sources management
            st.markdown("""
            <div class="medical-card">
                <h3><span class="card-icon">📊</span>Data Sources Management</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Get configuration info
            hcg_config = config.get_hcg_config()
            st.info(f"📡 Connected to: {hcg_config['base_url']}")
            st.info(f"🔄 Methods mode: {hcg_config['methods_mode']} ({len(METHODS)} methods)")
            
            # Data management section
            show_data_sources_management()
            
        else:
            st.warning("⚠️ Health Connect Gateway not configured")
            st.info("Please check your .env file and ensure HCG_USERNAME and HCG_PASSWORD are set.")
    except Exception as e:
        st.error(f"❌ Configuration error: {e}")
    
    # General settings
    st.markdown("""
    <div class="medical-card" style="margin-top: 2rem;">
        <h3><span class="card-icon">⚙️</span>General Settings</h3>
        <p style="color: #6b7280; margin: 0;">Application preferences and configuration options.</p>
    </div>
    """, unsafe_allow_html=True)

def show_data_sources_management():
    """Show data sources management within settings."""
    # Date range selector
    st.markdown("### 📅 Data Collection Settings")
    col1, col2, col3 = st.columns([2, 2, 2])
    
    with col1:
        use_date_range = st.checkbox("Use specific date range", 
                                   help="If unchecked, will use incremental updates from last sync")
    
    start_date = None
    end_date = None
    
    if use_date_range:
        with col2:
            start_date_input = st.date_input(
                "Start Date",
                value=datetime.now().date() - pd.Timedelta(days=7),
                help="Start date for data collection"
            )
            start_date = f"{start_date_input}T00:00:00Z"
        
        with col3:
            end_date_input = st.date_input(
                "End Date", 
                value=datetime.now().date(),
                help="End date for data collection"
            )
            end_date = f"{end_date_input}T23:59:59Z"
        
        # Validate date range
        if start_date_input > end_date_input:
            st.error("❌ Start date must be before end date")
            return
        
        # Show selected range
        days_diff = (end_date_input - start_date_input).days + 1
        st.info(f"📊 Selected range: {days_diff} day(s) from {start_date_input} to {end_date_input}")
    
    # Update buttons
    col1, col2 = st.columns([2, 2])
    
    with col1:
        if st.button("🔄 Update All Methods", type="primary"):
            update_all_methods(start_date, end_date)
    
    with col2:
        if st.button("📊 Refresh Status"):
            st.rerun()
    
    # Get status for all methods
    try:
        status_data = get_all_methods_status()
        
        # Display methods status
        if METHODS:
            st.markdown("### 📊 Data Sources Status")
            show_methods_status_compact(status_data, start_date, end_date)
        else:
            st.warning("No methods configured.")
            
    except Exception as e:
        st.error(f"Error loading data: {e}")

def show_methods_status_compact(status_data, start_date=None, end_date=None):
    """Display compact status information for all methods in settings."""
    # Create metrics row
    total_methods = len(METHODS)
    methods_with_data = sum(1 for status in status_data.values() if status['has_data'])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Methods", total_methods)
    with col2:
        st.metric("With Data", methods_with_data)
    with col3:
        st.metric("Empty", total_methods - methods_with_data)
    
    # Display each method in a compact format
    for method in METHODS:
        status = status_data.get(method, {})
        
        col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
        
        with col1:
            status_color = "green" if status.get('has_data', False) else "yellow"
            st.markdown(f"""
            <div style="display: flex; align-items: center;">
                <span class="status-dot {status_color}"></span>
                <span style="font-weight: 500;">{method}</span>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.write(f"{status.get('record_count', 0):,} records")
        
        with col3:
            st.write(f"{status.get('last_update', 'Never')}")
        
        with col4:
            if st.button("🔄", key=f"update_{method}_compact"):
                update_single_method(method, start_date, end_date)

if __name__ == "__main__":
    main()
