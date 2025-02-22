import streamlit as st
import os
import subprocess
import itertools
import pandas as pd
import base64

def get_pdb_files(folder):
    return [f for f in os.listdir(folder) if f.endswith('.pdb')]

def ensure_executable(file_path):
    if os.path.exists(file_path):
        subprocess.run(["chmod", "+x", file_path])

def run_command(command):
    result = subprocess.run(["/bin/bash", "-c", command], capture_output=True, text=True)
    return result.stdout + result.stderr

def run_hdock(receptor, antibody, results_folder):
    output_file = f"{results_folder}/{receptor}_{antibody}_hdock.out"
    ensure_executable("./hdock")
    command = f"./hdock receptor/{receptor} antibody/{antibody} -out {output_file}"
    return run_command(command)

def run_createpl(results_folder, receptor, antibody):
    output_pdb = f"{results_folder}/{receptor}_{antibody}_complex.pdb"
    ensure_executable("./createpl")
    command = f"./createpl {results_folder}/{receptor}_{antibody}_hdock.out {output_pdb} -nmax 1 -complex -models"
    run_command(command)
    return output_pdb

def run_prodigy(input_file, protein_chains, ligand_chain, results_folder, receptor, antibody):
    output_file = f"{results_folder}/{receptor}_{antibody}_prodigy.out"
    command = f"prodigy_lig -c {protein_chains} {ligand_chain} -i {input_file} -o > {output_file}"
    return run_command(command)

def run_plip(input_file, results_folder, receptor, antibody):
    output_pse = f"{results_folder}/{receptor}_{antibody}_plip.pse"
    command = f"plip -i {input_file} -o {results_folder}"
    return run_command(command)

def main():
    st.title("🔬 HDOCK, PRODIGY & PLIP Automation Tool")
    receptor_folder, antibody_folder, results_folder = "receptor", "antibody", "results"
    os.makedirs(results_folder, exist_ok=True)
    receptors, antibodies = get_pdb_files(receptor_folder), get_pdb_files(antibody_folder)
    pairs = list(itertools.product(receptors, antibodies))
    
    st.sidebar.write(f"🔍 Found {len(receptors)} receptors and {len(antibodies)} antibodies.")
    
    if st.button("Run Docking, Analysis & PLIP 🚀"):
        for receptor, antibody in pairs:
            with st.spinner(f"Processing: {receptor} with {antibody}..."):
                st.text(run_hdock(receptor, antibody, results_folder))
                result_pdb = run_createpl(results_folder, receptor, antibody)
                st.text(run_prodigy(result_pdb, "A,B", "C", results_folder, receptor, antibody))
                st.text(run_plip(result_pdb, results_folder, receptor, antibody))
                st.success(f"✅ Completed: {receptor} with {antibody}")
        st.balloons()
        st.success("🎉 All tasks completed! Check the results folder.")

if __name__ == "__main__":
    main()
