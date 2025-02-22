import streamlit as st
import os
import subprocess
import itertools
import pandas as pd
import base64

def get_pdb_files(folder):
    return [f for f in os.listdir(folder) if f.endswith('.pdb')]

def ensure_executable(file_path):
    if os.path.exists(file_path) and not os.access(file_path, os.X_OK):
        os.chmod(file_path, 0o755)  # Grant execute permissions

def run_command(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, executable='/bin/bash')
        if result.returncode != 0:
            st.error(f"Error running command: {command}\n{result.stderr}")
        return result.stdout
    except Exception as e:
        st.error(f"Exception running command: {command}\n{str(e)}")

def run_hdock(receptor, antibody, results_folder):
    ensure_executable("./hdock")
    output_file = f"{results_folder}/{receptor}_{antibody}_hdock.out"
    command = f"./hdock receptor/{receptor} antibody/{antibody} -out {output_file}"
    run_command(command)

def run_createpl(results_folder, receptor, antibody):
    ensure_executable("./createpl")
    output_pdb = f"{results_folder}/{receptor}_{antibody}_complex.pdb"
    command = f"./createpl {results_folder}/{receptor}_{antibody}_hdock.out {output_pdb} -nmax 1 -complex -models"
    run_command(command)
    return output_pdb

def run_prodigy(input_file, protein_chains, ligand_chain, results_folder, receptor, antibody):
    output_file = f"{results_folder}/{receptor}_{antibody}_prodigy.out"
    command = f"prodigy_lig -c {protein_chains} {ligand_chain} -i {input_file} -o > {output_file}"
    run_command(command)
    return output_file

def run_plip(input_file, results_folder, receptor, antibody):
    output_pse = f"{results_folder}/{receptor}_{antibody}_plip.pse"
    command = f"plip -i {input_file} -o {results_folder}"
    run_command(command)
    return output_pse

def main():
    st.title("🔬 HDOCK, PRODIGY & PLIP Automation Tool")
    receptor_folder, antibody_folder, results_folder = "receptor", "antibody", "results"
    os.makedirs(results_folder, exist_ok=True)
    
    receptors, antibodies = get_pdb_files(receptor_folder), get_pdb_files(antibody_folder)
    pairs = list(itertools.product(receptors, antibodies))
    st.sidebar.write(f"🔗 Total pairs to process: {len(pairs)}")
    
    if st.button("Run Docking, Analysis & PLIP 🚀"):
        for receptor, antibody in pairs:
            with st.spinner(f"Processing: {receptor} with {antibody}..."):
                run_hdock(receptor, antibody, results_folder)
                result_pdb = run_createpl(results_folder, receptor, antibody)
                run_prodigy(result_pdb, "A,B", "C", results_folder, receptor, antibody)
                run_plip(result_pdb, results_folder, receptor, antibody)
                st.success(f"✅ Completed: {receptor} with {antibody}")
        st.balloons()
        st.success("🎉 All tasks completed! Check the results browser above.")

if __name__ == "__main__":
    main()
