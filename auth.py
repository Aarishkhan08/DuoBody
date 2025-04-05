import streamlit as st
from requests_oauthlib import OAuth2Session
import json
import time
import base64
import hashlib
import os
import secrets
from urllib.parse import urlencode
from config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI, GOOGLE_AUTH_SCOPE, SECRET_KEY
from utils.rate_limiter import RateLimiter

# Initialize rate limiter
rate_limiter = RateLimiter()


def init_auth_state():
    """Initialize authentication state if not already present"""
    if 'auth_state' not in st.session_state:
        st.session_state.auth_state = {
            'is_authenticated': False,
            'user_info': None,
            'oauth_state': None,
            'code_verifier': None,
            'login_time': None,
            'last_activity': time.time(),
            'login_email': None
        }


def generate_code_verifier():
    """Generate a code verifier for PKCE"""
    code_verifier = secrets.token_urlsafe(64)
    return code_verifier


def generate_code_challenge(code_verifier):
    """Generate a code challenge for PKCE"""
    code_challenge = hashlib.sha256(code_verifier.encode('utf-8')).digest()
    code_challenge = base64.urlsafe_b64encode(code_challenge).decode('utf-8').rstrip('=')
    return code_challenge


def get_login_url(email=None):
    """Generate a login URL for Google OAuth"""
    init_auth_state()

    code_verifier = generate_code_verifier()
    code_challenge = generate_code_challenge(code_verifier)

    # Store the email in session state if provided
    if email:
        st.session_state.auth_state['login_email'] = email

    # Additional parameters for the authorization URL
    extra_params = {
        'code_challenge': code_challenge,
        'code_challenge_method': 'S256'
    }

    # Add login_hint parameter if email is provided
    if email:
        extra_params['login_hint'] = email

    oauth = OAuth2Session(GOOGLE_CLIENT_ID, scope=GOOGLE_AUTH_SCOPE, redirect_uri=GOOGLE_REDIRECT_URI)
    authorization_url, state = oauth.authorization_url(
        'https://accounts.google.com/o/oauth2/auth',
        **extra_params
    )

    st.session_state.auth_state['oauth_state'] = state
    st.session_state.auth_state['code_verifier'] = code_verifier

    return authorization_url


def handle_callback():
    """Handle the OAuth callback"""
    init_auth_state()

    # Get the authorization code from the URL query parameters
    query_params = st.query_params

    if 'code' in query_params and 'state' in query_params:
        code = query_params['code']
        state = query_params['state']

        # Verify the state to prevent CSRF
        if state != st.session_state.auth_state['oauth_state']:
            st.error("State verification failed. Authentication attempt may be compromised.")
            return

        # Exchange the authorization code for an access token
        oauth = OAuth2Session(
            GOOGLE_CLIENT_ID,
            redirect_uri=GOOGLE_REDIRECT_URI,
            state=st.session_state.auth_state['oauth_state']
        )

        try:
            token = oauth.fetch_token(
                'https://oauth2.googleapis.com/token',
                code=code,
                client_secret=GOOGLE_CLIENT_SECRET,
                code_verifier=st.session_state.auth_state['code_verifier']
            )

            # Get user info
            response = oauth.get('https://www.googleapis.com/oauth2/v1/userinfo')
            user_info = response.json()

            # Apply rate limiting
            ip_address = os.environ.get('REMOTE_ADDR', 'unknown')
            if not rate_limiter.is_allowed(ip_address):
                st.error("Rate limit exceeded. Please try again later.")
                return

            # Store user information in the session
            st.session_state.auth_state['is_authenticated'] = True
            st.session_state.auth_state['user_info'] = user_info
            st.session_state.auth_state['login_time'] = time.time()
            st.session_state.auth_state['last_activity'] = time.time()

            # Clear query parameters to prevent reloading issues
            st.query_params.clear()

            # Redirect to the main page
            st.rerun()

        except Exception as e:
            st.error(f"Authentication error: {str(e)}")

    # Check if we're in an error state
    elif 'error' in query_params:
        error = query_params['error']
        st.error(f"Authentication error: {error}")
        st.query_params.clear()


def is_authenticated():
    """Check if the user is authenticated"""
    init_auth_state()

    # Update last activity time
    if st.session_state.auth_state['is_authenticated']:
        st.session_state.auth_state['last_activity'] = time.time()

    # Check session expiration (4 hours)
    if st.session_state.auth_state['login_time'] and time.time() - st.session_state.auth_state['login_time'] > 14400:
        logout()
        st.error("Your session has expired. Please log in again.")
        return False

    # Check inactivity timeout (30 minutes)
    if st.session_state.auth_state['last_activity'] and time.time() - st.session_state.auth_state['last_activity'] > 1800:
        logout()
        st.error("Your session has timed out due to inactivity. Please log in again.")
        return False

    return st.session_state.auth_state['is_authenticated']


def get_user_info():
    """Get the authenticated user's information"""
    init_auth_state()
    return st.session_state.auth_state['user_info']


def logout():
    """Log the user out"""
    init_auth_state()
    st.session_state.auth_state = {
        'is_authenticated': False,
        'user_info': None,
        'oauth_state': None,
        'code_verifier': None,
        'login_time': None,
        'last_activity': None,
        'login_email': None
    }
