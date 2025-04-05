import streamlit as st
import os
from datetime import datetime, timedelta


def init_session():
    """Initialize session state variables."""
    # User authentication state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

    # User information
    if 'user_email' not in st.session_state:
        st.session_state.user_email = None

    if 'user_name' not in st.session_state:
        st.session_state.user_name = None

    if 'user_picture' not in st.session_state:
        st.session_state.user_picture = None

    # Session timing for security purposes
    if 'session_start_time' not in st.session_state:
        st.session_state.session_start_time = datetime.now()

    # Check for session timeout (4 hours)
    if 'session_start_time' in st.session_state:
        current_time = datetime.now()
        session_duration = current_time - st.session_state.session_start_time

        # If session is older than 4 hours, reset it
        if session_duration > timedelta(hours=4):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.session_state.session_start_time = current_time

    # Rate limiting
    if 'rate_limit_counters' not in st.session_state:
        st.session_state.rate_limit_counters = {}

    # Analysis results state
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None

    if 'comparison_results' not in st.session_state:
        st.session_state.comparison_results = None
