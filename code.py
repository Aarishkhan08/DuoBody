# app.py - Main Streamlit application
import streamlit as st
import os
import subprocess
import glob
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import itertools
import shutil
import re
import time
import base64
import smtplib
import smth.py

def send_email(name, email, subject, message):
    try:
        # Set up the SMTP server and sender credentials
        sender_email = "invisiblemr674@gmail.com"  
        sender_password = "someone123"  
        recipient_email = "invisiblemr674@gmail.com" 
        # Create the MIME message
        msg = MIMEMultipart()
        msg['From'] = email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        
        # The body of the email
        body = f"Message from {name} ({email}):\n\n{message}"
        msg.attach(MIMEText(body, 'plain'))
        
        # Connect to the SMTP server
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:  # For Gmail
            server.login(sender_email, sender_password)
            server.sendmail(email, recipient_email, msg.as_string())
        
        return True
    
    except Exception as e:
        return str(e)  # Return the error message if something goes wrong

# Configuration
UPLOAD_FOLDER = 'uploads'
RECEPTOR_FOLDER = 'receptors'
ANTIBODY_FOLDER = 'antibodies'
RESULTS_FOLDER = 'results'
DEFAULT_RECEPTOR_FOLDER = 'receptors/default'
DEFAULT_ANTIBODY_FOLDER = 'antibodies/default'

# Ensure all directories exist
for directory in [UPLOAD_FOLDER, RECEPTOR_FOLDER, ANTIBODY_FOLDER, RESULTS_FOLDER, 
                 DEFAULT_RECEPTOR_FOLDER, DEFAULT_ANTIBODY_FOLDER]:
    os.makedirs(directory, exist_ok=True)

# Helper function to validate email
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@gmail\.com$'
    return re.match(pattern, email) is not None

# Function to get files from directory
def get_files_from_directory(directory):
    return [os.path.basename(f) for f in glob.glob(f"{directory}/*.pdb")]

# Function to run analysis
def run_analysis(selected_receptors, selected_antibodies, user_email):
    if not selected_receptors or not selected_antibodies:
        st.error('Please select at least one receptor and one antibody.')
        return
    
    # Create a unique results folder for this run
    user_results_folder = os.path.join(RESULTS_FOLDER, user_email.replace('@', '_').replace('.', '_'))
    os.makedirs(user_results_folder, exist_ok=True)
    
    # Set up progress tracking
    total_combinations = len(selected_receptors) * len(selected_antibodies)
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Process all combinations
    results_data = []
    
    for i, (receptor_name, antibody_name) in enumerate(itertools.product(selected_receptors, selected_antibodies)):
        # Update progress
        progress = int((i / total_combinations) * 100)
        progress_bar.progress(progress)
        status_text.text(f"Processing {receptor_name} with {antibody_name}... ({i+1}/{total_combinations})")
        
        # Determine file paths
        if receptor_name.startswith('default_'):
            receptor_path = os.path.join(DEFAULT_RECEPTOR_FOLDER, receptor_name[8:])
        else:
            receptor_path = os.path.join(RECEPTOR_FOLDER, receptor_name)
            
        if antibody_name.startswith('default_'):
            antibody_path = os.path.join(DEFAULT_ANTIBODY_FOLDER, antibody_name[8:])
        else:
            antibody_path = os.path.join(ANTIBODY_FOLDER, antibody_name)
        
        # Create pair directory
        pair_name = f"{os.path.splitext(receptor_name)[0]}_{os.path.splitext(antibody_name)[0]}"
        pair_dir = os.path.join(user_results_folder, pair_name)
        os.makedirs(pair_dir, exist_ok=True)
        
        # Run HDOCK
        hdock_out = os.path.join(pair_dir, "hdock.out")
        try:
            subprocess.run("chmod +x hdock")
            subprocess.run(["./hdock", receptor_path, antibody_path, "-out", hdock_out], 
                          check=True, capture_output=True)
            
            # Run createpl
            complex_pdb = os.path.join(pair_dir, "Protein_Peptide.pdb")
            subprocess.run(["./createpl", hdock_out, complex_pdb, "-nmax", "1", "-complex", "-models"],
                          check=True, capture_output=True)
            
            # Run PRODIGY
            prodigy_output = os.path.join(pair_dir, "prodigy_results.txt")
            subprocess.run(["prodigy", complex_pdb], 
                          check=True, capture_output=True, text=True, 
                          stdout=open(prodigy_output, 'w'))
            
            # Run PLIP
            plip_command = f"python ~/plip/plip/plipcmd.py -i {complex_pdb} -yv"
            subprocess.run(plip_command, shell=True, check=True, capture_output=True)
            
            # Try to run PyMOL (note: this might not work in a web environment)
            pymol_command = f"pymol {os.path.splitext(complex_pdb)[0]}_NFT_A_283.pse"
            try:
                subprocess.run(pymol_command, shell=True, check=True, capture_output=True)
            except:
                # PyMOL might not be available or might require GUI
                pass
            
            # Parse PRODIGY results
            binding_energy = "N/A"
            with open(prodigy_output, 'r') as f:
                for line in f:
                    if "Predicted binding affinity" in line:
                        binding_energy = line.split(':')[1].strip()
            
            # Add to results data
            results_data.append({
                'Receptor': receptor_name,
                'Antibody': antibody_name,
                'Binding Energy': binding_energy,
                'Result Folder': pair_dir
            })
            
        except subprocess.CalledProcessError as e:
            st.error(f"Error processing {receptor_name} with {antibody_name}: {str(e)}")
            continue
    
    # Complete progress
    progress_bar.progress(100)
    status_text.text("Analysis complete!")
    
    # Create a summary table
    if results_data:
        results_df = pd.DataFrame(results_data)
        results_csv = os.path.join(user_results_folder, "results_summary.csv")
        results_df.to_csv(results_csv, index=False)
        
        # Email results to user
        send_results_email(user_email, user_results_folder)
        
        st.success('Analysis complete! Results have been emailed to you.')
        
        # Display results summary
        st.subheader("Results Summary")
        st.dataframe(results_df)
        
        # Create download link for results
        shutil.make_archive(user_results_folder, 'zip', user_results_folder)
        with open(f"{user_results_folder}.zip", "rb") as file:
            btn = st.download_button(
                label="Download Results (ZIP)",
                data=file,
                file_name=f"{os.path.basename(user_results_folder)}_results.zip",
                mime="application/zip"
            )
    else:
        st.error('No results were generated. Please check the logs for errors.')

def send_results_email(email, results_folder):
    # Set up email
    msg = MIMEMultipart()
    msg['From'] = 'invisiblemr674@gmail.com'  # Replace with actual email
    msg['To'] = email
    msg['Subject'] = 'Your DuoDok Analysis Results'
    
    body = "Please find attached your DuoDok analysis results."
    msg.attach(MIMEText(body, 'plain'))
    
    # Attach results summary
    summary_file = os.path.join(results_folder, "results_summary.csv")
    if os.path.exists(summary_file):
        with open(summary_file, 'rb') as f:
            attachment = MIMEApplication(f.read(), _subtype="csv")
            attachment.add_header('Content-Disposition', 'attachment', filename="results_summary.csv")
            msg.attach(attachment)
    
    # Create a zip of all results and attach
    shutil.make_archive(results_folder, 'zip', results_folder)
    with open(f"{results_folder}.zip", 'rb') as f:
        attachment = MIMEApplication(f.read(), _subtype="zip")
        attachment.add_header('Content-Disposition', 'attachment', 
                             filename=f"{os.path.basename(results_folder)}_results.zip")
        msg.attach(attachment)
    
    # Send email - note: in a real app, configure proper SMTP settings
    try:
        # This is a placeholder - in a real app, you'd use proper SMTP settings
        server = smtplib.SMTP('smtp.example.com', 587)  # Replace with actual SMTP server
        server.starttls()
        server.login('user', 'password')  # Replace with actual credentials
        server.send_message(msg)
        server.quit()
    except Exception as e:
        st.error(f"Failed to send email: {str(e)}")
        st.warning("Note: Email functionality requires proper SMTP configuration. Please download results directly from the app.")

# App components for different pages
def login_page():
    st.title("Welcome to DuoDok")
    st.write("Please enter your Gmail address to continue")
    
    email = st.text_input("Gmail Address", placeholder="youremail@gmail.com")
    login_button = st.button("Access DuoDok")
    
    if login_button:
        if is_valid_email(email):
            st.session_state.email = email
            st.session_state.page = "intro"
            st.rerun()
        else:
            st.error("Please enter a valid Gmail address.")

def intro_page():
    st.title("Welcome to DuoDok")
    
    st.header("About DuoDok")
    st.write("""
    DuoDok is a powerful web application designed for molecular docking analysis of receptor-antibody interactions.
    Our platform integrates several computational biology tools to provide comprehensive analysis of protein-protein interactions.
    """)
    
    st.subheader("Key Features:")
    st.markdown("""
    - Upload and manage your own PDB files for receptors and antibodies
    - Access to a library of default receptor and antibody structures
    - Automated docking using HDOCK algorithm
    - Binding energy prediction using PRODIGY
    - Detailed interaction analysis with PLIP
    - Results delivered directly to your email
    """)
    
    st.header("How to Get Started")
    st.markdown("""
    1. Visit the **Tutorial** page to watch a video guide on using DuoDok
    2. Navigate to the **DuoDok** page
    3. Upload your PDB files or select from our default library
    4. Run the analysis to get comprehensive results
    5. Receive your results via email
    """)

def tutorial_page():
    st.title("Tutorial")
    
    st.header("Video Tutorial")
    #st.image("temp/me.jpg", caption="Tutorial Video")
    st.write("Coming Soon")
    st.header("Step-by-Step Guide")
    
    st.subheader("1. Uploading Files")
    st.write("You can upload your own PDB files or use our default structures:")
    st.markdown("""
    - Navigate to the DuoDok page
    - Use the "Upload Receptor" or "Upload Antibody" buttons
    - Select a .pdb file from your computer
    - Your file will be added to the list of available structures
    """)
    
    st.subheader("2. Running Analysis")
    st.write("To analyze receptor-antibody interactions:")
    st.markdown("""
    - Select at least one receptor and one antibody
    - Click "Run Analysis"
    - The system will create all possible combinations
    - Each pair will be processed through HDOCK, PRODIGY, and PLIP
    - Results will be sent to your email address
    """)
    
    st.subheader("3. Interpreting Results")
    st.write("Your results email will contain:")
    st.markdown("""
    - A summary CSV file with binding energies for each pair
    - A ZIP archive with detailed results for each analysis
    - Visualization files that can be opened with PyMOL
    """)

def duodok_page():
    st.title("DuoDok Analysis")
    st.write("Note: You must install the files from Github to run its.")
    
    # Set up columns for receptor and antibody
    col1, col2 = st.columns(2)
    
    with col1:
        st.header("Receptor Files")
        
        # Upload receptor
        uploaded_receptor = st.file_uploader("Upload Receptor File (.pdb)", type=["pdb"], key="receptor_uploader")
        if uploaded_receptor is not None:
            # Save the uploaded file
            file_path = os.path.join(RECEPTOR_FOLDER, uploaded_receptor.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_receptor.getbuffer())
            st.success(f"Receptor file {uploaded_receptor.name} uploaded successfully!")
        
        # Get available receptor files
        default_receptors = get_files_from_directory(DEFAULT_RECEPTOR_FOLDER)
        user_receptors = get_files_from_directory(RECEPTOR_FOLDER)
        
        # Remove default files from user files list to avoid duplicates
        user_receptors = [f for f in user_receptors if f not in default_receptors]
        
        # Display receptor selection
        st.subheader("Default Receptors")
        default_receptor_selections = [st.checkbox(receptor, key=f"def_rec_{receptor}") for receptor in default_receptors]
        selected_default_receptors = [f"default_{receptor}" for receptor, selected in zip(default_receptors, default_receptor_selections) if selected]
        
        st.subheader("Your Uploaded Receptors")
        if user_receptors:
            user_receptor_selections = [st.checkbox(receptor, key=f"user_rec_{receptor}") for receptor in user_receptors]
            selected_user_receptors = [receptor for receptor, selected in zip(user_receptors, user_receptor_selections) if selected]
        else:
            st.write("No uploaded receptors")
            selected_user_receptors = []
    
    with col2:
        st.header("Antibody Files")
        
        # Upload antibody
        uploaded_antibody = st.file_uploader("Upload Antibody File (.pdb)", type=["pdb"], key="antibody_uploader")
        if uploaded_antibody is not None:
            # Save the uploaded file
            file_path = os.path.join(ANTIBODY_FOLDER, uploaded_antibody.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_antibody.getbuffer())
            st.success(f"Antibody file {uploaded_antibody.name} uploaded successfully!")
        
        # Get available antibody files
        default_antibodies = get_files_from_directory(DEFAULT_ANTIBODY_FOLDER)
        user_antibodies = get_files_from_directory(ANTIBODY_FOLDER)
        
        # Remove default files from user files list to avoid duplicates
        user_antibodies = [f for f in user_antibodies if f not in default_antibodies]
        
        # Display antibody selection
        st.subheader("Default Antibodies")
        default_antibody_selections = [st.checkbox(antibody, key=f"def_ab_{antibody}") for antibody in default_antibodies]
        selected_default_antibodies = [f"default_{antibody}" for antibody, selected in zip(default_antibodies, default_antibody_selections) if selected]
        
        st.subheader("Your Uploaded Antibodies")
        if user_antibodies:
            user_antibody_selections = [st.checkbox(antibody, key=f"user_ab_{antibody}") for antibody in user_antibodies]
            selected_user_antibodies = [antibody for antibody, selected in zip(user_antibodies, user_antibody_selections) if selected]
        else:
            st.write("No uploaded antibodies")
            selected_user_antibodies = []
    
    # Combine selections
    selected_receptors = selected_default_receptors + selected_user_receptors
    selected_antibodies = selected_default_antibodies + selected_user_antibodies
    
    # Run analysis button
    if st.button("Run Analysis", type="primary"):
        if not selected_receptors:
            st.error("Please select at least one receptor")
        elif not selected_antibodies:
            st.error("Please select at least one antibody")
        else:
            run_analysis(selected_receptors, selected_antibodies, st.session_state.email)
    
    # Information section
    st.header("About DuoDok Analysis")
    st.write("""
    DuoDok performs comprehensive analysis of receptor-antibody interactions using multiple computational tools:
    """)
    st.markdown("""
    - **HDOCK** - A protein-protein docking algorithm
    - **PRODIGY** - Predicts binding affinity of protein-protein complexes
    - **PLIP** - Analyzes protein-ligand interactions
    """)
    st.write(f"""
    The system will analyze all possible combinations of selected receptors and antibodies. Results will be
    emailed to your address ({st.session_state.email}) once processing is complete.
    """)
    
    st.image("workflow.png", caption="DuoDok workflow diagram")

def authors_page():
    st.title("About the Author")
    
    st.header("Me, Myself and I")
    
    # Author 1
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
    
def contact_page():
    st.title("Contact Us")
    
    st.write("""
    I'd love to hear from you! If you have any questions, suggestions, or feedback about DuoDok,
    please don't hesitate to get in touch.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.header("Send a Message")
        name = st.text_input("Your Name")
        email = st.text_input("Your Email")
        subject = st.text_input("Subject")
        message = st.text_area("Message", height=200)
        
        if st.button("Send Message"):
            if name and email and subject and message:
                result = send_email(name, email, subject, message)
                if result == True:
                    st.success("Your message has been sent successfully!")
                else:
                    st.error(f"Failed to send message: {result}")
            else:
                st.warning("Please fill out all fields before sending.")
    
    with col2:
        st.header("Contact Information")
        st.markdown("""
        **Email:** invisiblemr674@gmail.com
        
        **Phone:** (716) - 998 - 2757
        """)

def privacy_page():
    st.title("Privacy Policy")
    
    st.write("""
    Thank you for using DuoDok. This Privacy Policy explains how the collection, use, disclosure, 
    and safeguarding of your information when you use our service.
    """)
    
    st.header("Information Collected")
    st.write("""
    The information you directly provide to us is collected but not stored by our program, including:
    - Email address (used for account identification and to send analysis results)
    - Uploaded PDB files and analysis results
    """)
    
    st.header("How Your Information is Used")
    st.write("""
    Your collected information is used to:
    - Provide, maintain, and improve our services
    - Send you analysis results
    - Respond to comments, questions, and requests
    """)
    
    st.header("Information Sharing")
    st.write("""
    Your personally identifiable information is not sold, traded, or otherwise transfered to 
    outside parties.
    """)
    
    st.header("Contact Us")
    st.write("""
    If you have any questions about this Privacy Policy, please contact me at:
    invisiblemr674@gmail.com
    """)

# Main app
def main():
    # Set page configuration
    st.set_page_config(
        page_title="DuoDok - Molecular Docking Analysis",
        page_icon="🧬",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    if "page" not in st.session_state:
        st.session_state.page = "login"
    if "email" not in st.session_state:
        st.session_state.email = None
    
    # Check login status
    if st.session_state.email is None and st.session_state.page != "login":
        st.session_state.page = "login"
    
    # Sidebar navigation (only shown if logged in)
    if st.session_state.email is not None:
        st.sidebar.title("DuoDok")
        st.sidebar.markdown(f"Logged in as: {st.session_state.email}")
        
        pages = {
            "Introduction": "intro",
            "Tutorial": "tutorial",
            "DuoDok Analysis": "duodok",
            "About the Author": "authors",
            "Contact Us": "contact",
            "Privacy Policy": "privacy"
            "Something": "smth"
        }
        
        selection = st.sidebar.radio("Navigation", list(pages.keys()))
        st.session_state.page = pages[selection]
        
        if st.sidebar.button("Logout"):
            st.session_state.email = None
            st.session_state.page = "login"
            st.rerun()
        
        st.sidebar.divider()
        st.sidebar.caption("© 2025 DuoDok")
    
    # Display the selected page
    if st.session_state.page == "login":
        login_page()
    elif st.session_state.page == "intro":
        intro_page()
    elif st.session_state.page == "tutorial":
        tutorial_page()
    elif st.session_state.page == "duodok":
        duodok_page()
    elif st.session_state.page == "authors":
        authors_page()
    elif st.session_state.page == "contact":
        contact_page()
    elif st.session_state.page == "privacy":
        privacy_page()
    elif st.session_state.page == "smth":
        smth.py();

if __name__ == "__main__":
    main()
