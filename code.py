import streamlit as st
import os
import subprocess
import itertools
import pandas as pd

def get_pdb_files(folder):
    return [f for f in os.listdir(folder) if f.endswith('.pdb')]

def run_hdock(receptor, antibody, results_folder):
    output_file = f"{results_folder}/{receptor}_{antibody}_hdock.out"
    command = f"./hdock receptor/{receptor} antibody/{antibody} -out {output_file}"
    subprocess.run(command, shell=True)

def run_createpl(results_folder, receptor, antibody):
    output_pdb = f"{results_folder}/{receptor}_{antibody}_complex.pdb"
    command = f"./createpl {results_folder}/{receptor}_{antibody}_hdock.out {output_pdb} -nmax 1 -complex -models"
    subprocess.run(command, shell=True)
    return output_pdb

def run_prodigy(input_file, protein_chains, ligand_chain, results_folder, receptor, antibody):
    output_file = f"{results_folder}/{receptor}_{antibody}_prodigy.out"
    command = f"prodigy_lig -c {protein_chains} {ligand_chain} -i {input_file} -o > {output_file}"
    subprocess.run(command, shell=True)
    return output_file

def run_plip(input_file, results_folder, receptor, antibody):
    output_pse = f"{results_folder}/{receptor}_{antibody}_plip.pse"
    command = f"plip -i {input_file} -o {results_folder}"
    subprocess.run(command, shell=True)
    return output_pse

def generate_summary(results_folder, pairs):
    summary_data = []
    for receptor, antibody in pairs:
        prodigy_file = f"{results_folder}/{receptor}_{antibody}_prodigy.out"
        plip_file = f"{results_folder}/{receptor}_{antibody}_plip.pse"
        summary_data.append([receptor, antibody, os.path.exists(prodigy_file), os.path.exists(plip_file)])
    df = pd.DataFrame(summary_data, columns=["Receptor", "Antibody", "Prodigy Results", "PLIP Results"])
    return df

def main():
    st.set_page_config(page_title="HDOCK, PRODIGY & PLIP Automation", layout="wide")
    st.title("🔬 HDOCK, PRODIGY & PLIP Automation Tool")
    st.markdown("""
    <style>
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            padding: 10px 24px;
            font-size: 16px;
            border-radius: 5px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.sidebar.header("Configuration")
    receptor_folder = "receptor"
    antibody_folder = "antibody"
    results_folder = "results"
    os.makedirs(results_folder, exist_ok=True)
    
    receptors = get_pdb_files(receptor_folder)
    antibodies = get_pdb_files(antibody_folder)
    
    pairs = list(itertools.product(receptors, antibodies))
    st.sidebar.write(f"🔍 Found {len(receptors)} receptors and {len(antibodies)} antibodies.")
    st.sidebar.write(f"🔗 Total pairs to process: {len(pairs)}")
    
    if st.sidebar.button("Run Docking, Analysis & PLIP 🚀"):
        for receptor, antibody in pairs:
            with st.spinner(f"Processing: {receptor} with {antibody}..."):
                run_hdock(receptor, antibody, results_folder)
                result_pdb = run_createpl(results_folder, receptor, antibody)
                run_prodigy(result_pdb, "A,B", "C", results_folder, receptor, antibody)  # Modify chains accordingly
                run_plip(result_pdb, results_folder, receptor, antibody)
                st.success(f"✅ Completed: {receptor} with {antibody}")
        
        st.balloons()
        st.sidebar.success("🎉 All tasks completed! Check the results folder.")
    
    st.header("📊 Results Summary")
    df_summary = generate_summary(results_folder, pairs)
    st.dataframe(df_summary)
    
if __name__ == "__main__":
    main()
