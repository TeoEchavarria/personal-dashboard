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

from core.data_extractors import *
from core.data_processors import *
from core.analytics import *
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
        page_title="Personal Dashboard",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("📊 Personal Dashboard")
    st.markdown("---")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    
    # Initialize page in session state if not exists
    if 'page' not in st.session_state:
        st.session_state.page = "Home"
    
    page = st.sidebar.selectbox(
        "Choose a page",
        ["Home", "Analytics", "Data Sources", "Settings"],
        index=["Home", "Analytics", "Data Sources", "Settings"].index(st.session_state.page),
        key="page_selector"
    )
    
    # Update session state if page changed
    if page != st.session_state.page:
        st.session_state.page = page
    
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
    
    # Check if HCG is configured
    try:
        if config.validate_hcg_config():
            show_hcg_summary()
        else:
            st.warning("⚠️ Health Connect Gateway not configured. Please set up your .env file.")
            st.info("Go to the Data Sources page to configure your connection.")
    except Exception as e:
        st.error(f"Configuration error: {e}")

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

def show_analytics_page():
    """Display the analytics page."""
    st.header("📈 Analytics")
    st.write("Analytics content will go here")

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
    
    # Update buttons
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        if st.button("🔄 Update All Methods", type="primary"):
            update_all_methods()
    
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
                show_methods_status(status_data)
            
            with tab2:
                show_raw_data_viewer()
        else:
            st.warning("No methods configured.")
            
    except Exception as e:
        st.error(f"Error loading data: {e}")

def show_methods_status(status_data):
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
                    update_single_method(method)

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

def update_single_method(method):
    """Update data for a single method."""
    with st.spinner(f"Updating {method}..."):
        try:
            # Initialize token manager in session state to reuse
            if 'token_manager' not in st.session_state:
                st.session_state.token_manager = initialize_token_manager()
            
            count, since, error = collect_method_data(method, st.session_state.token_manager)
            
            if error:
                st.error(f"❌ Error updating {method}: {error}")
                # Clear token manager if there's an auth error
                if "401" in error or "Unauthorized" in error:
                    if 'token_manager' in st.session_state:
                        del st.session_state.token_manager
            else:
                st.success(f"✅ Updated {method}: {count} new records")
                if since:
                    st.info(f"📅 Last update: {since}")
                st.rerun()
                
        except Exception as e:
            st.error(f"❌ Failed to update {method}: {e}")
            # Clear token manager on any error to force re-authentication
            if 'token_manager' in st.session_state:
                del st.session_state.token_manager

def update_all_methods():
    """Update data for all methods."""
    with st.spinner("Updating all methods..."):
        try:
            # Initialize token manager in session state to reuse
            if 'token_manager' not in st.session_state:
                st.session_state.token_manager = initialize_token_manager()
            
            results = collect_all_methods_data(st.session_state.token_manager)
            
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
                st.success(f"✅ Updated {success_count} methods successfully. Total new records: {total_records}")
            
            if error_count > 0:
                st.warning(f"⚠️ {error_count} methods had errors")
            
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Failed to update methods: {e}")

def show_settings_page():
    """Display the settings page."""
    st.header("⚙️ Settings")
    st.write("Settings configuration will go here")

if __name__ == "__main__":
    main()
