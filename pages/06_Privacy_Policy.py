import streamlit as st
import sys
import os

import Welcome

# Add the root directory to the path so we can import from the root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Welcome import is_authenticated

# Set page title
st.set_page_config(
    page_title="Privacy Policy - DuoDok",
    page_icon="🧬",
    layout="wide"
)
def load_custom_css():
    with open(".streamlit/custom.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Call the function at the beginning
load_custom_css()
# Check if user is authenticated
if not is_authenticated():
    st.warning("Please log in to access this page.")
    st.stop()

# Page content
st.image("duodok.png", width=100)
st.title("🕵️Privacy Policy")
if is_authenticated():
    # Get user information
    user_info = Welcome.get_user_info()

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
            Welcome.logout()
            st.rerun()
st.write("""
**Last Updated: January 1, 2025**

This Privacy Policy describes how DuoDok collects, uses, and 
shares your personal information when you use our platform.

Please read this Privacy Policy carefully. By using DuoDok, you agree to the practices 
described in this policy.
""")

# Data collection section
st.header("Information Collected")


st.write("""
The information you directly provide to us is collected but not stored by our program, including:

- Email address (used for account identification, to send  any forms and to send analysis results)
- Uploaded PDB files and analysis results

""")

st.subheader("How Your Information is Used")
st.write("""
Your personal information is not stored anywhere. The information you provide is used solely for the 
purpose of providing the services you request.
""")

# Data sharing section
st.header("How We Share Your Information")
st.write("""
Your personally identifiable information is not sold, traded, or otherwise transferred to outside parties.
""")
# Changes to policy section
st.header("Changes to This Privacy Policy")
st.write("""
This Privacy Policy mey be updated from time to time. 
 """)

# Contact information section
st.header("Contact Us")
st.write("""
If you have any questions, concerns, or requests regarding this Privacy Policy or our privacy practices, please contact us at:

**Email**: invisiblemr674@gmail.com
**Address**: Buffalo, New York, United States

If you have an unresolved privacy concern that we have not addressed satisfactorily, please contact your local data protection authority.
""")
# Consent acknowledgment
st.info("""
By using the PDB Analysis Platform, you acknowledge that you have read and understood this Privacy Policy.
""")
