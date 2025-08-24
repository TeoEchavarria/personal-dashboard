"""
Personal Dashboard - Main Streamlit Application
Frontend interface for the personal dashboard application.
"""

import streamlit as st
import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.data_extractors import *
from core.data_processors import *
from core.analytics import *

def main():
    """Main application function."""
    st.set_page_config(
        page_title="Personal Dashboard",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("📊 Personal Dashboard")
    st.markdown("---")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page",
        ["Home", "Analytics", "Data Sources", "Settings"]
    )
    
    # Main content area
    if page == "Home":
        show_home_page()
    elif page == "Analytics":
        show_analytics_page()
    elif page == "Data Sources":
        show_data_sources_page()
    elif page == "Settings":
        show_settings_page()

def show_home_page():
    """Display the home page."""
    st.header("🏠 Welcome to Your Personal Dashboard")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Quick Stats")
        st.metric("Data Sources", "3")
        st.metric("Last Update", "2 hours ago")
    
    with col2:
        st.subheader("Recent Activity")
        st.info("Dashboard updated successfully")
        st.success("New data processed")

def show_analytics_page():
    """Display the analytics page."""
    st.header("📈 Analytics")
    st.write("Analytics content will go here")

def show_data_sources_page():
    """Display the data sources page."""
    st.header("🔗 Data Sources")
    st.write("Data sources configuration will go here")

def show_settings_page():
    """Display the settings page."""
    st.header("⚙️ Settings")
    st.write("Settings configuration will go here")

if __name__ == "__main__":
    main()
