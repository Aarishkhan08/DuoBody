import streamlit as st
import os
import subprocess
import itertools

def get_pdb_files(folder):
    return [f for f in os.listdir(folder) if f.endswith('.pdb')]

def run_hdock(receptor, antibody):
    command = f"./hdock receptor/{receptor} antibody/{antibody} -out hdock.out"
    subprocess.run(command, shell=True)

def run_createpl():
    command = "./createpl hdock.out Protein_Peptide.pdb -nmax 1 -complex -models"
    subprocess.run(command, shell=True)

def run_prodigy(input_file, protein_chains, ligand_chain):
    command = f"prodigy_lig -c {protein_chains} {ligand_chain} -i {input_file} -o"
    subprocess.run(command, shell=True)

def run_plip(input_file):
    command = f"plip -i {input_file} -yv"
    subprocess.run(command, shell=True)

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
                run_hdock(receptor, antibody)
                run_createpl()
                result_pdb = "Protein_Peptide.pdb"
                run_prodigy(result_pdb, "A,B", "C")  # Modify chains accordingly
                run_plip(result_pdb)
                subprocess.run(f"mv hdock.out {results_folder}/{receptor}_{antibody}_hdock.out", shell=True)
                subprocess.run(f"mv Protein_Peptide.pdb {results_folder}/{receptor}_{antibody}_complex.pdb", shell=True)
                subprocess.run(f"mv *pse {results_folder}/{receptor}_{antibody}_plip.pse", shell=True)
                st.success(f"✅ Completed: {receptor} with {antibody}")
        
        st.balloons()
        st.sidebar.success("🎉 All tasks completed! Check the results folder.")
    
if __name__ == "__main__":
    main()
