import streamlit as st
import sys
import os

import Welcome

# Add the root directory to the path so we can import from the root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Welcome import is_authenticated, get_user_info
from utils.email_sender import EmailSender

# Set page title
st.set_page_config(
    page_title="Contact - DuoDok",
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

# Initialize email sender
email_sender = EmailSender()

# Initialize session state variables
if 'form_submitted' not in st.session_state:
    st.session_state.form_submitted = False
if 'submission_result' not in st.session_state:
    st.session_state.submission_result = None
if 'submission_message' not in st.session_state:
    st.session_state.submission_message = None

# Get user info for pre-filling form
user_info = get_user_info()
user_email = ''
user_name = ''
if user_info is not None:
    user_email = user_info.get('email', '')
    user_name = user_info.get('name', '')

# Page content
st.image("duodok.png", width=100)
st.title("📨Contact Us")
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
We value your feedback and are here to help with any questions or concerns you may have about DuoDok.
Please fill out the form below, and I will get back to you as soon as possible.
""")

# Contact form
st.subheader("Send us a message")

# Create a form
with st.form("contact_form", clear_on_submit=False):
    # Contact form fields
    name = st.text_input("Name", value=user_name)
    email = st.text_input("Email", value=user_email)
    subject = st.text_input("Subject")
    category = st.selectbox(
        "Message Category",
        [
            "General Inquiry",
            "Technical Support",
            "Feature Request",
            "Bug Report",
            "Collaboration Opportunity",
            "Other"
        ]
    )
    message = st.text_area("Message", height=150)

    # Checkbox for receiving updates
    receive_updates = st.checkbox("I would like to receive updates about new features and improvements")

    # Terms and conditions
    agree_terms = st.checkbox("I agree to the privacy policy and terms of service")

    # Submit button
    submitted = st.form_submit_button("Send Message")

    # Form validation and submission
    if submitted:
        # Validate the form
        errors = email_sender.validate_form(name, email, subject, message)

        if not agree_terms:
            errors.append("You must agree to the privacy policy and terms of service.")

        if errors:
            for error in errors:
                st.error(error)
        else:
            # Send the email
            try:
                # Add category to the message
                full_message = f"Category: {category}\n\n{message}"
                if receive_updates:
                    full_message += "\n\nThe user has opted to receive updates."

                # Send the email
                success, message_result = email_sender.send_contact_email(name, email, subject, full_message)

                if success:
                    st.session_state.form_submitted = True
                    st.session_state.submission_result = True
                    st.session_state.submission_message = message_result
                    st.rerun()
                else:
                    st.session_state.form_submitted = True
                    st.session_state.submission_result = False
                    st.session_state.submission_message = message_result
                    st.rerun()
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

# Display submission result
if st.session_state.form_submitted:
    if st.session_state.submission_result:
        st.success(st.session_state.submission_message)

        # Option to reset form
        if st.button("Send Another Message"):
            st.session_state.form_submitted = False
            st.session_state.submission_result = None
            st.session_state.submission_message = None
            st.rerun()
    else:
        st.error(st.session_state.submission_message)

        # Option to try again
        if st.button("Try Again"):
            st.session_state.form_submitted = False
            st.session_state.submission_result = None
            st.session_state.submission_message = None
            st.rerun()

# Alternative contact methods
if not st.session_state.form_submitted:
    st.subheader("Other Ways to Reach Us")

    col1, col2 = st.columns(2)

    with col1:
        st.write("### Email")
        st.write("For general inquiries: invisiblemr674@gmail.com")
        st.write("For technical support: invisiblemr674@gmail.com")


    with col2:
        st.write("### Social Media")
        st.write("Twitter: [@DuoBody](https://twitter.com)")
        st.write("LinkedIn: [DuoBody](https://linkedin.com/in/mak08)")

# FAQ section
with st.expander("Frequently Asked Questions"):
    st.write("""
    ### Can I request a new feature for the platform?
    Absolutely! I welcome feature requests and will consider them for future updates.

    ### How can I report a bug?
    You can report bugs through this contact form by selecting "Bug Report" as the category.

    """)

