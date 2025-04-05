import streamlit as st
import subprocess
import os


# Function to run shell commands
def run_command(command):
    try:
        result = subprocess.run(command, shell=True, text=True, capture_output=True)
        return result.stdout, result.stderr
    except Exception as e:
        return None, str(e)

def app():
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
    
                prodigy_command = f"prodigy {complex_pdb_path}"
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
                        st.write("Binding Energy and PLIP Results are ready!")
    else:
        st.warning("Please upload both the Receptor and Antibody PDB files.")
