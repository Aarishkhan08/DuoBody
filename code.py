import streamlit as st
import os
import subprocess
import pandas as pd
from pathlib import Path
import time
from Bio.PDB import *
import glob

def run_hdock(receptor_path, antibody_path, output_dir):
    output_path = os.path.join(output_dir, f"hdock_{Path(receptor_path).stem}_{Path(antibody_path).stem}.out")
    subprocess.run(['./hdock', receptor_path, antibody_path, '-out', output_path], check=True)
    return output_path

def run_createpl(hdock_output, output_dir):
    complex_path = os.path.join(output_dir, f"complex_{Path(hdock_output).stem}.pdb")
    subprocess.run(['./createpl', hdock_output, complex_path, '-nmax', '1', '-complex', '-models'], check=True)
    return complex_path

def run_prodigy(complex_path):
    try:
        result = subprocess.run(['prodigy', complex_path], 
                              capture_output=True, 
                              text=True, 
                              check=True)
        
        output_lines = result.stdout.split('\n')
        binding_affinity = None
        dissociation_constant = None
        contacts = {}
        
        for line in output_lines:
            if 'Predicted binding affinity' in line:
                binding_affinity = float(line.split(':')[-1].strip())
            elif 'Predicted dissociation constant' in line:
                dissociation_constant = line.split(':')[-1].strip()
            elif 'No. of' in line and 'contacts:' in line:
                contact_type = line.split('No. of ')[-1].split('contacts:')[0].strip()
                count = int(line.split(':')[-1].strip())
                contacts[contact_type] = count
        
        return {
            'binding_affinity': binding_affinity,
            'dissociation_constant': dissociation_constant,
            'contacts': contacts
        }
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"PRODIGY analysis failed: {e.stderr}")

def create_results_df(results):
    df_data = []
    for result in results:
        row = {
            'Receptor': result['Receptor'],
            'Antibody': result['Antibody'],
            'Binding Affinity': result['Binding Affinity'],
            'Dissociation Constant': result['Dissociation Constant']
        }
        row.update({f"Contacts_{k}": v for k, v in result['Contacts'].items()})
        df_data.append(row)
    return pd.DataFrame(df_data)

def main():
    st.set_page_config(page_title="Receptor-Antibody Docking Analysis", layout="wide")
    
    st.title("🧬 Receptor-Antibody Docking Analysis")
    st.markdown("Upload receptor and antibody files for docking analysis using HDOCK and PRODIGY")

    with st.sidebar:
        st.header("📁 Input Files")
        receptor_folder = st.file_uploader("Upload Receptor Files", accept_multiple_files=True, type=['pdb'])
        antibody_folder = st.file_uploader("Upload Antibody Files", accept_multiple_files=True, type=['pdb'])
        
        if st.button("Start Analysis", type="primary"):
            if not receptor_folder or not antibody_folder:
                st.error("Please upload both receptor and antibody files.")
                return

            temp_dir = Path("temp")
            results_dir = Path("results")
            for dir_path in [temp_dir, results_dir]:
                dir_path.mkdir(exist_ok=True)

            receptor_paths = []
            antibody_paths = []
            
            for receptor in receptor_folder:
                path = temp_dir / f"receptor_{receptor.name}"
                with open(path, "wb") as f:
                    f.write(receptor.getvalue())
                receptor_paths.append(path)

            for antibody in antibody_folder:
                path = temp_dir / f"antibody_{antibody.name}"
                with open(path, "wb") as f:
                    f.write(antibody.getvalue())
                antibody_paths.append(path)

            total_combinations = len(receptor_paths) * len(antibody_paths)
            progress_bar = st.progress(0)
            status_text = st.empty()
            results = []
            
            for i, receptor in enumerate(receptor_paths):
                for j, antibody in enumerate(antibody_paths):
                    current_progress = (i * len(antibody_paths) + j + 1) / total_combinations
                    status_text.text(f"Processing {receptor.name} with {antibody.name}...")
                    
                    try:
                        hdock_output = run_hdock(receptor, antibody, temp_dir)
                        complex_path = run_createpl(hdock_output, temp_dir)
                        prodigy_results = run_prodigy(complex_path)
                        
                        results.append({
                            'Receptor': receptor.stem,
                            'Antibody': antibody.stem,
                            'Binding Affinity': prodigy_results['binding_affinity'],
                            'Dissociation Constant': prodigy_results['dissociation_constant'],
                            'Contacts': prodigy_results['contacts']
                        })
                        
                        final_complex_path = results_dir / f"complex_{receptor.stem}_{antibody.stem}.pdb"
                        os.rename(complex_path, final_complex_path)
                        
                    except Exception as e:
                        st.error(f"Error processing {receptor.name} with {antibody.name}: {str(e)}")
                    
                    progress_bar.progress(current_progress)

            if results:
                df = create_results_df(results)
                
                csv_path = results_dir / "analysis_results.csv"
                df.to_csv(csv_path, index=False)
                
                st.header("📊 Analysis Results")
                st.dataframe(df)
                
                with open(csv_path, 'rb') as f:
                    st.download_button(
                        label="Download Results CSV",
                        data=f,
                        file_name="analysis_results.csv",
                        mime="text/csv"
                    )
                
                st.header("📈 Results Visualization")
                
                st.subheader("Binding Affinity Heatmap")
                heatmap_data = df.pivot(index='Receptor', columns='Antibody', values='Binding Affinity')
                st.write(heatmap_data.style.background_gradient(cmap='viridis'))
                
                st.subheader("Binding Affinity Distribution")
                hist_values = pd.DataFrame(df['Binding Affinity'].values)
                st.bar_chart(hist_values)

            for file_path in temp_dir.glob("*"):
                file_path.unlink()
            temp_dir.rmdir()

if __name__ == "__main__":
    main()
