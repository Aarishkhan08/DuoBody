import streamlit as st
import os
import subprocess
import itertools
import pandas as pd
import base64

def get_pdb_files(folder):
    return [f for f in os.listdir(folder) if f.endswith('.pdb')]

def download_file(file_path):
    with open(file_path, "rb") as f:
        bytes = f.read()
        b64 = base64.b64encode(bytes).decode()
        href = f'<a href="data:file/txt;base64,{b64}" download="{os.path.basename(file_path)}">Download {os.path.basename(file_path)}</a>'
        return href

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
    
    # Custom CSS
    st.markdown("""
    <style>
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            padding: 10px 24px;
            font-size: 16px;
            border-radius: 5px;
        }
        .file-browser {
            background-color: #f5f5f5;
            padding: 20px;
            border-radius: 5px;
            margin: 10px 0;
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
    
    # Results Browser Section
    st.header("📂 Results Browser")
    if os.path.exists(results_folder):
        results_files = os.listdir(results_folder)
        if results_files:
            st.write(f"Found {len(results_files)} files in results folder:")
            
            # File filtering
            file_filter = st.text_input("Filter files (type to search):")
            file_type = st.selectbox("Filter by file type:", 
                                   ["All", ".pdb", ".out", ".pse"])
            
            filtered_files = results_files
            if file_filter:
                filtered_files = [f for f in filtered_files if file_filter.lower() in f.lower()]
            if file_type != "All":
                filtered_files = [f for f in filtered_files if f.endswith(file_type)]
            
            # Display files in a table with download links
            if filtered_files:
                file_data = []
                for file in filtered_files:
                    file_path = os.path.join(results_folder, file)
                    file_size = os.path.getsize(file_path) / 1024  # Size in KB
                    file_data.append({
                        "File Name": file,
                        "Size (KB)": f"{file_size:.2f}",
                        "Download": download_file(file_path)
                    })
                
                df = pd.DataFrame(file_data)
                st.write(df.to_html(escape=False, index=False), unsafe_allow_html=True)
            else:
                st.warning("No files match the current filters.")
        else:
            st.info("No files in results folder yet. Run the analysis to generate results.")
    else:
        st.error("Results folder not found!")
    
    # Original Processing Section
    st.header("⚙️ Processing")
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
    
    # Results Summary Section
    st.header("📊 Results Summary")
    df_summary = generate_summary(results_folder, pairs)
    st.dataframe(df_summary)

if __name__ == "__main__":
    main()
