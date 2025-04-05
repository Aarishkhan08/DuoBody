import streamlit as st
import os
import time
import hashlib
import secrets
from utils.rate_limiter import check_rate_limit


# Set page configuration
st.set_page_config(
    page_title="PDB Analysis Platform",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

def load_custom_css():
    with open(".streamlit/custom.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Call the function at the beginning
load_custom_css()

# Initialize session state variables
if 'auth' not in st.session_state:
    st.session_state.auth = {
        'is_authenticated': False,
        'user_email': None,
        'login_time': None,
        'last_activity': None,
        'login_error': None
    }


def is_valid_email(email_str):
    """Validate email format"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email_str) is not None


def simple_authenticate(email, password):
    """Simplified authentication for development"""
    # For development, we'll use a simple hashing mechanism
    # In production, you would use a more secure method
    if email and password:
        # Temporarily disable rate limiting for debugging
        # In production, you would want to enable this
        # if not check_rate_limit('login_attempts'):
        #     return False, "Rate limit exceeded. Please try again later."

        # For demo purposes, accept any valid email with password "demo123"
        # In a real app, you would check against a secure database
        if password == "demo123":
            st.session_state.auth['is_authenticated'] = True
            st.session_state.auth['user_email'] = email
            st.session_state.auth['login_time'] = time.time()
            st.session_state.auth['last_activity'] = time.time()

            return True, None
        else:
            return False, "Invalid credentials. For this demo, use password 'demo123'"

    return False, "Email and password are required"


def is_authenticated():
    """Check if user is authenticated"""
    if not st.session_state.auth['is_authenticated']:
        return False

    # Update last activity time
    st.session_state.auth['last_activity'] = time.time()

    # Check session expiration (4 hours)
    if st.session_state.auth['login_time'] and time.time() - st.session_state.auth['login_time'] > 14400:
        logout()
        st.session_state.auth['login_error'] = "Your session has expired. Please log in again."
        return False

    # Check inactivity timeout (30 minutes)
    if st.session_state.auth['last_activity'] and time.time() - st.session_state.auth['last_activity'] > 1800:
        logout()
        st.session_state.auth['login_error'] = "Your session has timed out due to inactivity. Please log in again."
        return False

    return True


def get_user_info():
    """Get user information"""
    if is_authenticated():
        return {
            'email': st.session_state.auth['user_email'],
            'name': st.session_state.auth['user_email'].split('@')[0]  # Simple name extraction from email
        }
    return None


def logout():
    """Log out the user"""
    st.session_state.auth = {
        'is_authenticated': False,
        'user_email': None,
        'login_time': None,
        'last_activity': None,
        'login_error': None
    }


def main():
    # Display header
    st.image("duodok.png", width=100)
    st.title("🧬PDB Analysis Platform")
    # Check if user is authenticated
    if is_authenticated():
        # Get user information
        user_info = get_user_info()

        # Display user information and logout button in the sidebar
        with st.sidebar:
            if user_info:
                st.write(f"Welcome, {user_info.get('name', 'User')}!")
                st.write(f"Email: {user_info.get('email', 'N/A')}")
                st.write("© 2025 DuoDok")

            else:
                st.write("Welcome, User! © 2025 DuoDok")


            # Logout button
            if st.button("Logout"):
                logout()
                st.rerun()

        # Display main content
        st.write("""
        ## Welcome to the PDB Analysis Platform

        This platform allows you to analyze and compare Protein Data Bank (PDB) files. 

        Use the navigation sidebar to access different features:
        - **Introduction**: Learn about the platform
        - **Tutorial**: Watch tutorials on how to use the platform
        - **Analysis**: Upload and analyze PDB files
        - **DuoBody**: Uploadn and analyze PDB files
        - **About**: Information about the developers
        - **Contact**: Get in touch with us
        - **Privacy Policy**: View our privacy policy
        """)

        # Additional information
        with st.expander("What is a PDB file?"):
            st.write("""
            A PDB (Protein Data Bank) file is a standardized file format for the representation of 
            three-dimensional structural data of biological macromolecules like proteins and nucleic acids. 

            The PDB format was created in the 1970s and is still widely used in structural biology and 
            bioinformatics. Each PDB file contains atomic coordinates, observed sidechain rotamers, 
            secondary structure assignments, and atomic connectivity.

            This platform helps you analyze and compare PDB files to derive insights about protein structures.
            """)
    else:
        # Display login page
        st.write("""
        ## Welcome to the PDB Analysis Platform

        Please log in to access the platform.
        """)

        # Create columns for centering
        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            # Login form
            with st.form("login_form"):
                email = st.text_input("Email Address", placeholder="your.email@gmail.com")
                password = st.text_input("Password", type="password", placeholder="For demo use: demo123")

                submit_button = st.form_submit_button("Login")

                if submit_button:
                    if is_valid_email(email):
                        success, error = simple_authenticate(email, password)
                        if success:
                            st.session_state.auth['login_error'] = None
                            st.rerun()
                        else:
                            st.error(error)
                    else:
                        st.error("Please enter a valid email address format (example@gmail.com)")

            # Display error message if login failed
            if st.session_state.auth.get('login_error'):
                st.error(st.session_state.auth['login_error'])

            # Add notice about demo mode
            st.info("**Demo Mode**: Use any email with password 'demo123'")

        # Additional information
        with st.expander("Why do I need to log in?"):
            st.write("""
            Logging in allows us to:
            1. Provide a personalized experience
            2. Save your analysis history
            3. Protect your data
            4. Send you notifications about your analyses

            In this demo version, we use a simple authentication system. 
            In production, we would use a more secure authentication method.
            """)

        with st.expander("About this platform"):
            st.write("""
            The PDB Analysis Platform is a tool for scientists, researchers, and students to analyze 
            and compare protein structures using PDB files.

            Key features:
            - Upload and validate PDB files
            - Analyze structural properties
            - Compare multiple PDB files
            - Generate comprehensive reports

            Created by bioinformatics experts to simplify the analysis of complex protein structures.
            """)


if __name__ == "__main__":
    main()
