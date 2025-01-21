Receptor-Antibody Docking Analysis
This repository provides a Streamlit-based web application to analyze docking interactions between receptor and antibody molecules. The application utilizes HDOCK, PRODIGY, and CREATEPL tools to predict binding affinities, dissociation constants, and contact points between molecular structures.

Features
Upload PDB files for receptors and antibodies.
Perform automated docking simulations using HDOCK.
Generate protein complexes with CREATEPL.
Predict binding affinities and dissociation constants with PRODIGY.
Visualize results as heatmaps and distribution charts.
Download analysis results as a CSV file.
Installation
Clone the repository:
bash
Copy
Edit
git clone https://github.com/your_username/receptor-antibody-docking.git
cd receptor-antibody-docking
Install the required dependencies:
bash
Copy
Edit
pip install -r requirements.txt
Ensure that the following tools are installed and accessible from the command line:
HDOCK
CREATEPL (included in the HDOCK package)
PRODIGY
Usage
Start the Streamlit app:
bash
Copy
Edit
streamlit run app.py
Open the app in your web browser at http://localhost:8501.
Upload receptor and antibody PDB files through the sidebar.
Click Start Analysis to process the files.
View results, download CSV, and visualize binding affinities.
File Organization
app.py: The main Streamlit application.
requirements.txt: Python dependencies.
temp/: Temporary storage for input and output files during analysis.
results/: Directory where final analysis outputs (PDB and CSV files) are saved.
Key Functions
run_hdock: Runs HDOCK to perform docking simulations.
run_createpl: Generates protein complexes from HDOCK outputs.
run_prodigy: Predicts binding affinities, dissociation constants, and contacts.
create_results_df: Converts analysis results into a pandas DataFrame.
Outputs
Binding Affinity Heatmap: Displays binding affinities between receptor-antibody pairs.
Binding Affinity Distribution: Shows the frequency distribution of affinities.
Analysis Results CSV: Contains detailed docking metrics for all receptor-antibody combinations.
Example Workflow
Input Files: Upload receptor and antibody PDB files.
Docking Process:
HDOCK computes the docking.
CREATEPL generates the docked complex.
PRODIGY predicts interaction metrics.
Results: View and download results, including binding affinities and dissociation constants.
Visualizations: Analyze heatmaps and distribution charts for insights.
Requirements
Python 3.8+
Streamlit
pandas
Biopython
HDOCK, CREATEPL, PRODIGY (installed separately)
Troubleshooting
If you encounter issues during the analysis:

Ensure all dependencies and tools are correctly installed.
Verify that the uploaded PDB files are valid and properly formatted.
Check file paths and permissions for temporary and results directories.
