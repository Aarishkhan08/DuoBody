import glob
import streamlit as st
import sys
import os
import itertools
import subprocess
import shutil
import pandas as pd
import Welcome
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger()

# Add the root directory to the path so we can import from the root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Welcome import is_authenticated

# Set page title
st.set_page_config(
    page_title="Tutorial - PDB Analysis Platform",
    page_icon="🧬",
    layout="wide"
)

def load_custom_css():
    with open(".streamlit/custom.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Call the function at the beginning
load_custom_css()

# Ensure user is authenticated before proceeding
if not is_authenticated():
    st.warning("Please log in to access this page.")
    st.stop()

# Page content
st.image("duodok.png", width=100)
st.title("🧬DuoDok Analysis")
st.write("Note: You must install the files from Github to run it.")

# Fetch user info
user_info = Welcome.get_user_info()

# Sidebar: User Info & Logout
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

# Folder setup
#BASE_DIR = os.path.dirname(os.path.abspath(__file__))
#UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
#RECEPTOR_FOLDER = os.path.join(BASE_DIR, 'receptors')
#ANTIBODY_FOLDER = os.path.join(BASE_DIR, 'antibodies')
#RESULTS_FOLDER = os.path.join(BASE_DIR, 'results')
#DEFAULT_RECEPTOR_FOLDER = os.path.join(RECEPTOR_FOLDER, 'default')
#DEFAULT_ANTIBODY_FOLDER = os.path.join(ANTIBODY_FOLDER, 'default')
#HDOCK_DIR = os.path.join(BASE_DIR, 'HDOCKlite')

# Ensure all directories exist
#for directory in [UPLOAD_FOLDER, RECEPTOR_FOLDER, ANTIBODY_FOLDER,
#                  RESULTS_FOLDER, DEFAULT_RECEPTOR_FOLDER,
#                  DEFAULT_ANTIBODY_FOLDER, HDOCK_DIR]:
#    os.makedirs(directory, exist_ok=True)


#def get_files_from_directory(directory):
#    logger.debug(f"Getting files from directory: {directory}")
#    files = [os.path.basename(f) for f in glob.glob(f"{directory}/*.pdb")]
#    logger.debug(f"Found {len(files)} files: {files}")
#    return files


#def send_results_email(user_email, results_folder):
#    logger.debug(f"Sending results email to {user_email}, results folder: {results_folder}")
    # Placeholder function for email sending
#    pass


#def check_hdock_installed():
    """Check if HDOCK is properly installed"""
#    try:
#        hdock_path = os.path.join(HDOCK_DIR, 'hdock')
#        createpl_path = os.path.join(HDOCK_DIR, 'createpl')

#        if not os.path.exists(hdock_path):
#            raise FileNotFoundError(f"HDOCK not found at: {hdock_path}")
#        if not os.path.exists(createpl_path):
#            raise FileNotFoundError(f"createpl not found at: {createpl_path}")

        # Set execute permissions
#        os.chmod(hdock_path, 0o755)
#        os.chmod(createpl_path, 0o755)

#        return True
#    except Exception as e:
#        st.error(f"HDOCK setup failed: {str(e)}")
#        st.info(f"Please ensure HDOCKlite directory exists at {HDOCK_DIR} with executables")
#        return False


#def run_analysis(selected_receptors, selected_antibodies, user_email):
#    if not selected_receptors or not selected_antibodies:
#        st.error('Please select at least one receptor and one antibody.')
#        return

#    if not check_hdock_installed():
#        return

    # Create a unique results folder for this run
#    user_results_folder = os.path.join(RESULTS_FOLDER, user_email.replace('@', '_').replace('.', '_'))
#    os.makedirs(user_results_folder, exist_ok=True)
#    logger.debug(f"Results will be saved in: {user_results_folder}")

    # Set up progress tracking
#    total_combinations = len(selected_receptors) * len(selected_antibodies)
#    progress_bar = st.progress(0)
#    status_text = st.empty()

    # Process all combinations
#    results_data = []

#    for i, (receptor_name, antibody_name) in enumerate(itertools.product(selected_receptors, selected_antibodies)):
#        progress = int((i / total_combinations) * 100)
#        progress_bar.progress(progress)
#        status_text.text(f"Processing {receptor_name} with {antibody_name}... ({i + 1}/{total_combinations})")

        # Get absolute paths
#        receptor_path = os.path.join(
#            DEFAULT_RECEPTOR_FOLDER if receptor_name.startswith('default_') else RECEPTOR_FOLDER,
#            receptor_name[8:] if receptor_name.startswith('default_') else receptor_name
#        )
 #       antibody_path = os.path.join(
 #           DEFAULT_ANTIBODY_FOLDER if antibody_name.startswith('default_') else ANTIBODY_FOLDER,
 #           antibody_name[8:] if antibody_name.startswith('default_') else antibody_name
 #       )

 #       pair_name = f"{os.path.splitext(receptor_name)[0]}_{os.path.splitext(antibody_name)[0]}"
 #       pair_dir = os.path.join(user_results_folder, pair_name)
 #       os.makedirs(pair_dir, exist_ok=True)

  #      try:
            # HDOCK paths
  #          hdock_exec = os.path.join(HDOCK_DIR, 'hdock')
  #          createpl_exec = os.path.join(HDOCK_DIR, 'createpl')
  #          hdock_out = os.path.join(pair_dir, "hdock.out")
  #          complex_pdb = os.path.join(pair_dir, "Protein_Peptide.pdb")

            # Run HDOCK
  #          logger.debug(f"Running HDOCK: {hdock_exec} {receptor_path} {antibody_path}")
  #          subprocess.run(
  #              [hdock_exec, receptor_path, antibody_path, "-out", hdock_out],
  #              check=True,
  #              cwd=HDOCK_DIR
  #          )

            # Run createpl
  #          logger.debug(f"Running createpl: {createpl_exec} {hdock_out}")
  #          subprocess.run(
  #              [createpl_exec, hdock_out, complex_pdb, "-nmax", "1", "-complex", "-models"],
  #              check=True,
  #              cwd=HDOCK_DIR
  #          )

            # Run PRODIGY
  #          prodigy_output = os.path.join(pair_dir, "prodigy_results.txt")
  #          logger.debug(f"Running PRODIGY: {complex_pdb}")
  #          subprocess.run(
  #              ["prodigy", complex_pdb],
  #              check=True,
  #              stdout=open(prodigy_output, 'w')
  #          )

            # Run PLIP
  #          plip_output = os.path.join(pair_dir, "plip_results")
  #          os.makedirs(plip_output, exist_ok=True)
  #          logger.debug(f"Running PLIP: {complex_pdb}")
  #          subprocess.run(
  #              ["plip", "-f", complex_pdb, "-o", plip_output, "-x"],
  #              check=True
  #          )

            # Parse PRODIGY results
 #           binding_energy = "N/A"
 #           with open(prodigy_output, 'r') as f:
 #               for line in f:
 #                   if "Predicted binding affinity" in line:
 #                       binding_energy = line.split(':')[1].strip()

 #           results_data.append({
 #               'Receptor': receptor_name,
 #               'Antibody': antibody_name,
 #               'Binding Energy': binding_energy,
 #               'Result Folder': pair_dir
 #           })

  #      except subprocess.CalledProcessError as e:
  #          logger.error(f"Error processing {receptor_name} with {antibody_name}: {str(e)}")
  #          st.error(f"Error processing {receptor_name} with {antibody_name}: {str(e)}")
  #          continue

    # Complete progress
  #  progress_bar.progress(100)
  #  status_text.text("Analysis complete!")

    # Create summary
  #  if results_data:
  #      results_df = pd.DataFrame(results_data)
  #      results_csv = os.path.join(user_results_folder, "results_summary.csv")
  #      results_df.to_csv(results_csv, index=False)

   #     send_results_email(user_email, user_results_folder)
   #     st.success('Analysis complete! Results have been emailed to you.')

   #     st.subheader("Results Summary")
   #     st.dataframe(results_df)

        # Create download link
  #      shutil.make_archive(user_results_folder, 'zip', user_results_folder)
  #      with open(f"{user_results_folder}.zip", "rb") as file:
  #          btn = st.download_button(
  #              label="Download Results (ZIP)",
  #              data=file,
  #              file_name=f"{os.path.basename(user_results_folder)}_results.zip",
  #              mime="application/zip"
  #          )
  #  else:
  #      st.error('No results were generated. Please check the logs for errors.')


# Upload and Selection UI
#col1, col2 = st.columns(2)

#with col1:
#    st.header("Receptor Files")
#    uploaded_receptor = st.file_uploader("Upload Receptor File (.pdb)", type=["pdb"], key="receptor_uploader")
#    if uploaded_receptor:
#        file_path = os.path.join(RECEPTOR_FOLDER, uploaded_receptor.name)
#        with open(file_path, "wb") as f:
#            f.write(uploaded_receptor.getbuffer())
#        st.success(f"Receptor file {uploaded_receptor.name} uploaded successfully!")

#    default_receptors = get_files_from_directory(DEFAULT_RECEPTOR_FOLDER)
#    user_receptors = get_files_from_directory(RECEPTOR_FOLDER)
#    user_receptors = [f for f in user_receptors if f not in default_receptors]

#    st.subheader("Default Receptors")
#    default_receptor_selections = [st.checkbox(receptor, key=f"def_rec_{receptor}") for receptor in default_receptors]
#    selected_default_receptors = [f"default_{receptor}" for receptor, selected in
#                                  zip(default_receptors, default_receptor_selections) if selected]

#    st.subheader("Your Uploaded Receptors")
#    if user_receptors:
#        user_receptor_selections = [st.checkbox(receptor, key=f"user_rec_{receptor}") for receptor in user_receptors]
#        selected_user_receptors = [receptor for receptor, selected in zip(user_receptors, user_receptor_selections) if
#                                   selected]
#    else:
#        st.write("No uploaded receptors")
#        selected_user_receptors = []

#with col2:
#    st.header("Antibody Files")
#    uploaded_antibody = st.file_uploader("Upload Antibody File (.pdb)", type=["pdb"], key="antibody_uploader")
#    if uploaded_antibody:
#        file_path = os.path.join(ANTIBODY_FOLDER, uploaded_antibody.name)
#        with open(file_path, "wb") as f:
#            f.write(uploaded_antibody.getbuffer())
#        st.success(f"Antibody file {uploaded_antibody.name} uploaded successfully!")

#    default_antibodies = get_files_from_directory(DEFAULT_ANTIBODY_FOLDER)
#    user_antibodies = get_files_from_directory(ANTIBODY_FOLDER)
#    user_antibodies = [f for f in user_antibodies if f not in default_antibodies]

#    st.subheader("Default Antibodies")
#    default_antibody_selections = [st.checkbox(antibody, key=f"def_ab_{antibody}") for antibody in default_antibodies]
#    selected_default_antibodies = [f"default_{antibody}" for antibody, selected in
#                                   zip(default_antibodies, default_antibody_selections) if selected]

#    st.subheader("Your Uploaded Antibodies")
#    if user_antibodies:
#        user_antibody_selections = [st.checkbox(antibody, key=f"user_ab_{antibody}") for antibody in user_antibodies]
#        selected_user_antibodies = [antibody for antibody, selected in zip(user_antibodies, user_antibody_selections) if
#                                    selected]
#    else:
#        st.write("No uploaded antibodies")
#        selected_user_antibodies = []

# Combine selections and run
#selected_receptors = selected_default_receptors + selected_user_receptors
#selected_antibodies = selected_default_antibodies + selected_user_antibodies

#if st.button("Run Analysis", type="primary"):
#    if not selected_receptors:
#        st.error("Please select at least one receptor")
#    elif not selected_antibodies:
#        st.error("Please select at least one antibody")
#    else:
#        if user_info and 'email' in user_info:
#            run_analysis(selected_receptors, selected_antibodies, user_info['email'])
#        else:
#            st.error("User authentication failed. Please log in again.")
#            Welcome.logout()
#            st.rerun()

def run_command(command):
    try:
        result = subprocess.run(command, shell=True, text=True, capture_output=True)
        return result.stdout, result.stderr
    except Exception as e:
        return None, str(e)


# Streamlit app UI
st.title("Protein Complex Docking Pipeline")

st.header("Step 1: Upload Receptor and Antibody PDB Files")
receptor_file = st.file_uploader("Upload Receptor PDB", type=["pdb"])
antibody_file = st.file_uploader("Upload Antibody PDB", type=["pdb"])

if receptor_file and antibody_file:
    st.write("Receptor and Antibody files uploaded successfully!")

    # Save files locally for processing
    receptor_path = "./receptor.pdb"
    antibody_path = "./antibody.pdb"

    with open(receptor_path, "wb") as f:
        f.write(receptor_file.getbuffer())

    with open(antibody_path, "wb") as f:
        f.write(antibody_file.getbuffer())

    st.header("Step 2: Run Docking with hDock")

    # Run the hDock command to create the complex
    hdock_command = f"./hdock {receptor_path} {antibody_path} -out hdock.out"
    stdout, stderr = run_command(hdock_command)

    if stderr:
        st.error(f"Error running hDock: {stderr}")
    else:
        st.success("hDock completed successfully!")
        st.write("hDock Output:", stdout)

        # Now create the complex file
        createpl_command = f"./createpl Hdock.out complex_name -nmax 1 -complex -models"
        stdout, stderr = run_command(createpl_command)

        if stderr:
            st.error(f"Error running createpl: {stderr}")
        else:
            st.success("Complex file created successfully!")
            st.write("Createpl Output:", stdout)

            # Step 3: Run Prodigy for Binding Energy Calculation
            st.header("Step 3: Run Prodigy Binding Energy Calculator")
            complex_pdb_path = "./complex_name_complex.pdb"  # Assuming the complex is saved with this name
            chain_one = st.text_input("Enter Chain Name for Receptor (e.g., A)")
            chain_two = st.text_input("Enter Chain Name for Antibody (e.g., B)")

            if chain_one and chain_two:
                prodigy_command = f"prodigy {complex_pdb_path} --selection {chain_one} {chain_two}"
                stdout, stderr = run_command(prodigy_command)

                if stderr:
                    st.error(f"Error running Prodigy: {stderr}")
                else:
                    st.success("Prodigy calculation completed!")
                    st.write("Prodigy Output:", stdout)

                    # Step 4: Run PLIP Analysis
                    st.header("Step 4: Run PLIP Analysis")
                    plip_command = f"plip -i {complex_pdb_path} -o plip_results/"
                    stdout, stderr = run_command(plip_command)

                    if stderr:
                        st.error(f"Error running PLIP: {stderr}")
                    else:
                        st.success("PLIP analysis completed!")
                        st.write("PLIP Output:", stdout)

                        # Step 5: Show Results
                        st.header("Final Results")
                        # Optionally, you can parse the outputs and display them in a more structured way
                        # For example, parsing Prodigy binding energy results or PLIP interactions
                        st.write("Binding Energy and PLIP Results are ready!")
else:
    st.warning("Please upload both the Receptor and Antibody PDB files.")

# Information section
st.header("About DuoDok Analysis")
st.write("""
DuoDok performs comprehensive analysis of receptor-antibody interactions using multiple computational tools:
""")
st.markdown("""
- **HDOCK** - An algorithm for protein–protein and protein–DNA/RNA docking based on a hybrid strategy
- **PRODIGY** - Predicts binding affinity of in biological complexes
- **PLIP** - Analyzes protein-ligand interactions 
""")
st.write("The system will analyze all possible combinations of selected receptors and antibodies. Results will be emailed to your email once processing is complete.")
st.write("This platform facilitates an efficient workflow for antibody research and development.")

st.image("workflow.png", use_container_width=True, caption="DuoDok workflow diagram")