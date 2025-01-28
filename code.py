import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from Bio.PDB import PDBParser
import subprocess
import tempfile
import requests
import time
import json

class MolecularDockingApp:
    def __init__(self):
        st.set_page_config(layout="wide", page_title="Molecular Interaction Analysis")
        self.setup_session_state()
        self.receptors = self.load_structures('receptor')
        self.antibodies = self.load_structures('antibody')
        self.HDOCK_SERVER = "http://hdock.phys.hust.edu.cn"

    def setup_session_state(self):
        if 'docking_results' not in st.session_state:
            st.session_state.docking_results = []
        if 'job_ids' not in st.session_state:
            st.session_state.job_ids = {}

    def load_structures(self, folder):
        os.makedirs(folder, exist_ok=True)
        return [f for f in os.listdir(folder) if f.endswith('.pdb')]

    def validate_structure(self, filepath):
        try:
            parser = PDBParser(QUIET=True)
            structure = parser.get_structure('protein', filepath)
            return len(list(structure.get_chains())) > 0
        except Exception:
            return False

    def submit_hdock_job(self, receptor_path, antibody_path):
        try:
            files = {
                'file1': ('receptor.pdb', open(receptor_path, 'rb')),
                'file2': ('antibody.pdb', open(antibody_path, 'rb'))
            }
            
            data = {
                'job_type': 'docking',
                'email': 'optional@example.com'  # Replace with user's email
            }
            
            response = requests.post(f"{self.HDOCK_SERVER}/submit", files=files, data=data)
            
            if response.status_code == 200:
                job_id = response.json().get('job_id')
                return job_id
            else:
                st.error(f"HDOCK submission failed: {response.text}")
                return None
                
        except Exception as e:
            st.error(f"Error submitting to HDOCK: {str(e)}")
            return None

    def check_hdock_status(self, job_id):
        try:
            response = requests.get(f"{self.HDOCK_SERVER}/status/{job_id}")
            if response.status_code == 200:
                return response.json().get('status')
            return None
        except Exception:
            return None

    def get_hdock_results(self, job_id):
        try:
            response = requests.get(f"{self.HDOCK_SERVER}/result/{job_id}")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception:
            return None

    def calculate_binding_energy(self, pdb_file):
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                output_file = os.path.join(tmpdir, 'prodigy_output.txt')
                
                command = [
                    'prodigy',
                    '-i', pdb_file,
                    '-o', output_file
                ]
                
                result = subprocess.run(command, capture_output=True, text=True)
                
                if result.returncode == 0:
                    with open(output_file, 'r') as f:
                        energy_data = json.load(f)
                    return energy_data.get('binding_energy')
                else:
                    st.error(f"PRODIGY calculation failed: {result.stderr}")
                    return None
                    
        except Exception as e:
            st.error(f"Binding energy calculation error: {str(e)}")
            return None

    def run_docking_analysis(self, receptor, antibody):
        receptor_path = os.path.join('receptor', receptor)
        antibody_path = os.path.join('antibody', antibody)

        if not (self.validate_structure(receptor_path) and self.validate_structure(antibody_path)):
            st.error("Invalid protein structures detected.")
            return None

        job_id = self.submit_hdock_job(receptor_path, antibody_path)
        
        if job_id:
            st.session_state.job_ids[(receptor, antibody)] = job_id
            return {'status': 'submitted', 'job_id': job_id}

        return None

    def check_pending_jobs(self):
        completed_jobs = []
        
        for (receptor, antibody), job_id in st.session_state.job_ids.items():
            status = self.check_hdock_status(job_id)
            
            if status == 'completed':
                results = self.get_hdock_results(job_id)
                
                if results:
                    binding_energy = self.calculate_binding_energy(results['best_model'])
                    
                    result_data = {
                        'receptor': receptor,
                        'antibody': antibody,
                        'docking_score': results['score'],
                        'binding_energy': binding_energy,
                        'job_id': job_id
                    }
                    
                    st.session_state.docking_results.append(result_data)
                    completed_jobs.append((receptor, antibody))
            
            elif status == 'failed':
                st.error(f"Docking failed for {receptor}-{antibody}")
                completed_jobs.append((receptor, antibody))

        # Remove completed jobs from pending list
        for job in completed_jobs:
            del st.session_state.job_ids[job]

    def visualize_results(self):
        if not st.session_state.docking_results:
            st.warning("No docking results available.")
            return

        df = pd.DataFrame(st.session_state.docking_results)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Binding Energy Distribution")
            fig1 = px.box(df, y='binding_energy', title='Binding Energy Distribution')
            st.plotly_chart(fig1)

        with col2:
            st.subheader("Docking Score vs Binding Energy")
            fig2 = px.scatter(df, x='docking_score', y='binding_energy',
                            hover_data=['receptor', 'antibody'])
            st.plotly_chart(fig2)

        st.subheader("Interaction Matrix")
        matrix = df.pivot_table(
            index='receptor',
            columns='antibody',
            values='binding_energy',
            aggfunc='mean'
        )
        fig3 = px.imshow(matrix, title='Binding Energy Heatmap')
        st.plotly_chart(fig3)

    def run(self):
        st.title("Molecular Docking Analysis")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            receptor = st.selectbox("Select Receptor", self.receptors)
            antibody = st.selectbox("Select Antibody", self.antibodies)
            
            if st.button("Run Docking Analysis"):
                with st.spinner('Submitting docking job...'):
                    result = self.run_docking_analysis(receptor, antibody)
                    if result:
                        st.success(f"Job submitted successfully! ID: {result['job_id']}")
        
        with col2:
            st.subheader("Upload Structures")
            uploaded_receptor = st.file_uploader("Upload Receptor (PDB)", type=['pdb'])
            uploaded_antibody = st.file_uploader("Upload Antibody (PDB)", type=['pdb'])
            
            if uploaded_receptor:
                with open(os.path.join('receptor', uploaded_receptor.name), 'wb') as f:
                    f.write(uploaded_receptor.getbuffer())
                st.success(f"Uploaded {uploaded_receptor.name}")
                
            if uploaded_antibody:
                with open(os.path.join('antibody', uploaded_antibody.name), 'wb') as f:
                    f.write(uploaded_antibody.getbuffer())
                st.success(f"Uploaded {uploaded_antibody.name}")

        # Check pending jobs
        if st.session_state.job_ids:
            st.subheader("Pending Jobs")
            st.write(f"Number of pending jobs: {len(st.session_state.job_ids)}")
            if st.button("Check Job Status"):
                with st.spinner('Checking job status...'):
                    self.check_pending_jobs()

        # Results visualization
        st.header("Results")
        self.visualize_results()

def main():
    app = MolecularDockingApp()
    app.run()

if __name__ == "__main__":
    main()
