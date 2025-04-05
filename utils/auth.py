import os
import streamlit as st
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import json
import time
import secrets
from utils.rate_limiter import check_rate_limit

# Load environment variables
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI', 'http://localhost:8501')

# OAuth2 configuration
SCOPES = ['https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile']


def create_oauth_flow():
    """Create and return a Google OAuth2 flow object."""
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [REDIRECT_URI]
            }
        },
        scopes=SCOPES
    )
    flow.redirect_uri = REDIRECT_URI
    return flow


def authenticate_user():
    """Authenticate the user with Google OAuth2."""
    if check_rate_limit('login_attempts'):
        st.warning("Too many login attempts. Please try again later.")
        return

    if 'auth_state' not in st.session_state:
        st.session_state.auth_state = secrets.token_urlsafe(32)

    if 'code' not in st.session_state:
        flow = create_oauth_flow()
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            state=st.session_state.auth_state,
            prompt='consent'
        )

        st.markdown(f"[Login with Gmail](javascript:window.open('{auth_url}', '_self'))", unsafe_allow_html=True)

        # For local development (can be used with query parameters)
        code = st.text_input("Or enter the authorization code:", "")
        if code:
            st.session_state.code = code
            st.rerun()
    else:
        try:
            flow = create_oauth_flow()
            flow.fetch_token(code=st.session_state.code)
            credentials = flow.credentials

            # Get user information
            user_info_service = build('oauth2', 'v2', credentials=credentials)
            user_info = user_info_service.userinfo().get().execute()

            # Save user information and credentials to session state
            st.session_state.user_email = user_info.get('email')
            st.session_state.user_name = user_info.get('name')
            st.session_state.user_picture = user_info.get('picture')
            st.session_state.authenticated = True
            st.session_state.credentials = {
                'token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_uri': credentials.token_uri,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scopes': credentials.scopes,
                'expiry': credentials.expiry.isoformat() if credentials.expiry else None
            }

            # Clear code after successful authentication
            del st.session_state.code
            st.rerun()
        except Exception as e:
            st.error(f"Authentication failed: {str(e)}")
            if 'code' in st.session_state:
                del st.session_state.code


def is_authenticated():
    """Check if user is authenticated."""
    return st.session_state.get('authenticated', False)


def get_user_email():
    """Get the authenticated user's email."""
    return st.session_state.get('user_email', None)


def logout_user():
    """Log out the authenticated user."""
    # Clear all authentication-related session state
    auth_keys = ['authenticated', 'user_email', 'user_name', 'user_picture', 'credentials', 'code', 'auth_state']
    for key in auth_keys:
        if key in st.session_state:
            del st.session_state[key]
