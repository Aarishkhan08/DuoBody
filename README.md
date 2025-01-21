Receptor-Antibody Docking Analysis
This repository provides a **Streamlit**-based web application for analyzing docking interactions between receptor and antibody molecules. The application utilizes **HDOCK**, **PRODIGY**, and **CREATEPL** tools to predict binding affinities, dissociation constants, and contact points between molecular structures.
Features

- Upload **PDB** files for receptors and antibodies.
- Perform automated docking simulations using **HDOCK**.
- Generate protein complexes with **CREATEPL**.
- Predict binding affinities and dissociation constants with **PRODIGY**.
- Visualize results as heatmaps and distribution charts.
- Download analysis results as a CSV file.

Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your_username/receptor-antibody-docking.git
   cd receptor-antibody-docking
   ```
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Ensure the following tools are installed and accessible from the command line:
   - [HDOCK](http://hdock.phys.hust.edu.cn/)
   - CREATEPL (included in the HDOCK package)
   - [PRODIGY](https://bianca.science.uu.nl/prodigy/)

Usage

1. Start the Streamlit app:
   ```bash
   streamlit run app.py
   ```
2. Open the app in your web browser at `http://localhost:8501`.
3. Upload receptor and antibody **PDB** files through the sidebar.
4. Click **Start Analysis** to process the files.
5. View results, download the CSV, and visualize binding affinities.

File Organization

- **`app.py`**: The main Streamlit application.
- **`requirements.txt`**: Python dependencies.
- **`temp/`**: Temporary storage for input and output files during analysis.
- **`results/`**: Directory where final analysis outputs (PDB and CSV files) are saved.

Key Functions

- **`run_hdock`**: Runs HDOCK to perform docking simulations.
- **`run_createpl`**: Generates protein complexes from HDOCK outputs.
- **`run_prodigy`**: Predicts binding affinities, dissociation constants, and contacts.
- **`create_results_df`**: Converts analysis results into a pandas DataFrame.

Outputs

- **Binding Affinity Heatmap**: Displays binding affinities between receptor-antibody pairs.
- **Binding Affinity Distribution**: Shows the frequency distribution of affinities.
- **Analysis Results CSV**: Contains detailed docking metrics for all receptor-antibody combinations.

Example Workflow

1. **Input Files**: Upload receptor and antibody PDB files.
2. **Docking Process**:
   - HDOCK computes the docking.
   - CREATEPL generates the docked complex.
   - PRODIGY predicts interaction metrics.
3. **Results**: View and download results, including binding affinities and dissociation constants.
4. **Visualizations**: Analyze heatmaps and distribution charts for insights.

Requirements

- Python 3.8+
- Streamlit
- pandas
- Biopython
- HDOCK, CREATEPL, PRODIGY (installed separately)

Troubleshooting

If you encounter issues during the analysis:
- Ensure all dependencies and tools are correctly installed.
- Verify that the uploaded PDB files are valid and properly formatted.
- Check file paths and permissions for temporary and results directories.

Contributing

Contributions are welcome! Feel free to submit issues, pull requests, or suggestions to improve this repository.

License

This project is licensed under the MIT License. See the `LICENSE` file for details.

