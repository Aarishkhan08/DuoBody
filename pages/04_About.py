import streamlit as st
import sys
import os

import Welcome

# Add the root directory to the path so we can import from the root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Welcome import is_authenticated

# Set page title
st.set_page_config(
    page_title="About - DuoDok",
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
st.title("🌟About the Author")
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
st.header("Me, Myself and I")

# Create columns for team members
col1, col2 = st.columns([1, 3])
with col1:
    st.image("aarish.jpg", caption="")
    pass
with col2:
    st.subheader("Mohmmad Aarish Khan")
    st.caption("Highschooler passionate about the world of Computational Biology")
    st.write("""
    Mohammad Aarish Khan, a 16 year old highschool, has found his passional in helping others through his knowledge in the fields of technology and biology. 
    His research for the Terra Science Fair 2026, focuses on developing an automated way for predicting and analyzing molecular interactions between protein receptors and ligands, in a attempt to make the promise of bi-specific antibodies accessible to all.
    """)

st.divider()


# Publications and Citations
st.header("Publications")
st.write("""
**RESEARCH PAPER**: Utilization of Bi-specific Antibodies for Clinical use against non small cell lung cancer
Accepted for publication by **PRINCETON IEEE**.
""")

st.header("Honors and Awards")
st.write("""
- Selected as an **EMERGING SCIENTIST OF THE YEAR** by New York Academy of Sciences.
- AP scholar award 2024
- Oracle cloud infrastructure 2024 Generative AI certified Professional
- New York Academy of Junior Sciences Winner [First Place Fall 2023, Project of Distinction in Spring 2024]
- Excellence Award in Engineering and Technology, 2024
- Buffalo State Computer Science Competition (First Place)
- TSA States (3rd Place for Coding)
- Science Olympiad Regionals 
    - Silver Medal disease detective
    - Bronze Medal Detector Building
    - Bronze Medal Flight 
- PTSA Reflections - Literature [Regional Outstanding Excellence Award, 2023]
- Excellence Award in Earth Science, 2023 
""")

st.header("Community Services")
st.write("""
- Amherst YES (Youth Engaged In Services): BRONZE Medal, 2024
- Amherst Youth Consortium
- Big Brother Big Sisters
- Sunday School Volunteer At Masjid An Noor, Getzville, NY 
""")

st.header("Extra -Curricular Activities")
st.write("""
- Computer Club: Vice President
- French Club: Treasurer
- Technology Student Association (TSA): Secretary, New York State Delegate
- National Honor Society: Member
- Science Honor Society: Member
- SIHAC - Superintendent Inter High Action Committee
    - Group A Chair 2023-2024
    - Group B Chair 2024-2025
- SDM - Shared Decision Making: Member 
""")
st.write("""
For more details about my personal achievements please refer below pdf file.
""")
st.download_button(
    label="Download My Achievements PDF",
    data=open("AARISH_RESUME.pdf", "rb").read(),
    file_name="AARISH_RESUME.pdf",
    mime="application/pdf",
    help="Click to download my achievements and resume in PDF format."
)
# Get in touch
st.header("Get in Touch")
st.write("""
We value your feedback and are continuously working to improve the platform. If you have suggestions, 
questions, or would like to report issues, please use our Contact page.

For collaboration inquiries or research partnerships, you can reach us at invisiblemr674@gmail.com.
""")

# Future developments
st.header("Future Developments")
st.write("""
We're constantly working to enhance the PDB Analysis Platform. Upcoming features include:

- Integration with molecular dynamics simulation tools
- Enhanced machine learning capabilities for structure prediction
- API access for programmatic analysis
- Additional visualization options
- Batch processing for multiple structure analysis

Stay tuned for these exciting updates!
""")
