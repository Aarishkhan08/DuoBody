import time
from collections import defaultdict
import streamlit as st
from config import RATE_LIMIT_REQUESTS, RATE_LIMIT_PERIOD

# Initialize the rate limiter as a global object
_rate_limiter = None


def get_rate_limiter():
    """Get or create a RateLimiter instance"""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter


def check_rate_limit(identifier):
    """Wrapper function to check if a request is allowed based on rate limits"""
    limiter = get_rate_limiter()
    return limiter.is_allowed(identifier)


class RateLimiter:
    """Rate limiter to prevent abuse of the API"""

    def __init__(self):
        # Initialize the rate limiter
        self._initialize_session_state()

    def _initialize_session_state(self):
        """Initialize the rate limiter in session state if not already present"""
        if 'rate_limiter' not in st.session_state:
            st.session_state.rate_limiter = {
                'requests': defaultdict(list),
                'blocked': defaultdict(int)
            }

    def is_allowed(self, identifier):
        """Check if a request is allowed based on rate limits"""
        # Ensure session state is initialized
        self._initialize_session_state()

        current_time = time.time()
        requests = st.session_state.rate_limiter['requests'][identifier]

        # If the identifier is blocked, check if the block has expired
        if st.session_state.rate_limiter['blocked'][identifier] > current_time:
            return False

        # Remove requests that are outside the rate limit period
        requests = [req_time for req_time in requests if current_time - req_time < RATE_LIMIT_PERIOD]

        # Update the requests list
        st.session_state.rate_limiter['requests'][identifier] = requests

        # If the number of requests exceeds the limit, block the identifier
        if len(requests) >= RATE_LIMIT_REQUESTS:
            # Block for 1 hour
            st.session_state.rate_limiter['blocked'][identifier] = current_time + RATE_LIMIT_PERIOD
            return False

        # Add the current request
        st.session_state.rate_limiter['requests'][identifier].append(current_time)
        return True

    def get_remaining_requests(self, identifier):
        """Get the number of remaining requests for the identifier"""
        # Ensure session state is initialized
        self._initialize_session_state()

        current_time = time.time()
        requests = st.session_state.rate_limiter['requests'][identifier]

        # Remove requests that are outside the rate limit period
        requests = [req_time for req_time in requests if current_time - req_time < RATE_LIMIT_PERIOD]

        # Update the requests list
        st.session_state.rate_limiter['requests'][identifier] = requests

        return RATE_LIMIT_REQUESTS - len(requests)
