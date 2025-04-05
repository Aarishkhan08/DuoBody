import streamlit as st
import os
import sys
import time
import Welcome
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from io import BytesIO

# Add the root directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Welcome import is_authenticated, get_user_info, logout
from utils.pdb_analyzer import PDBAnalyzer

# Set page configuration
st.set_page_config(
    page_title="DuoDok",
    page_icon="🧬",
    layout="wide"
)


# Custom CSS for styling
def load_custom_css():
    with open(".streamlit/custom.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_custom_css()

# Authentication check
if not is_authenticated():
    st.warning("Please log in to access this page.")
    st.stop()

# Initialize analyzer
analyzer = PDBAnalyzer()

# Session state management
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'comparison_result' not in st.session_state:
    st.session_state.comparison_result = None
if 'analysis_type' not in st.session_state:
    st.session_state.analysis_type = "single"


# Visualization functions
def create_residue_chart(chain_data):
    """Create interactive residue count bar chart"""
    df = pd.DataFrame([(k, v['residue_count']) for k, v in chain_data.items()],
                      columns=['Chain', 'Residues'])
    fig = px.bar(df, x='Chain', y='Residues',
                 title='Residue Distribution Across Chains',
                 color='Chain', text_auto=True)
    fig.update_layout(showlegend=False)
    return fig


def create_bond_histogram(bond_data):
    """Create bond length distribution histogram"""
    bond_lengths = [bond['distance'] for bond in bond_data]
    fig = px.histogram(bond_lengths, nbins=20,
                       labels={'value': 'Bond Length (Å)'},
                       title='Bond Length Distribution')
    fig.update_layout(showlegend=False)
    return fig


def create_residue_pie(residue_counts):
    """Create residue type distribution pie chart"""
    df = pd.DataFrame(list(residue_counts.items()), columns=['Residue', 'Count'])
    fig = px.pie(df, names='Residue', values='Count',
                 title='Residue Type Distribution')
    return fig


def create_comparison_visualizations(comparison_data):
    """Create comparison visualizations using available data"""
    # Bar chart for differences
    differences = {
        'Models': comparison_data.get('model_count_diff', 0),
        'Residues': comparison_data.get('residue_count_diff', 0),
        'Atoms': comparison_data.get('atom_count_diff', 0)
    }

    fig1 = px.bar(
        x=list(differences.keys()),
        y=list(differences.values()),
        labels={'x': 'Metric', 'y': 'Difference'},
        title='Structural Differences',
        color=list(differences.keys())
    )
    fig1.update_layout(showlegend=False)

    # Chain comparison chart
    chain_diffs = []
    for chain_id, data in comparison_data.get('chain_comparison', {}).items():
        chain_diffs.append({
            'Chain': chain_id,
            'Residue Diff': data['residue_count_diff'],
            'Atom Diff': data['atom_count_diff']
        })

    if chain_diffs:
        df = pd.DataFrame(chain_diffs)
        fig2 = px.bar(df, x='Chain', y=['Residue Diff', 'Atom Diff'],
                      title='Chain-wise Differences', barmode='group')
    else:
        fig2 = None

    return fig1, fig2


# Main application layout
st.image("duodok.png", width=100)
st.title("🔬PDB Structure Analysis Visualization")

if is_authenticated():
    # Get user information
    user_info = Welcome.get_user_info()

# User sidebar
with st.sidebar:
    if user_info:
        st.write(f"Welcome, {user_info.get('name', 'User')}!")
        st.write(f"Email: {user_info.get('email', '')}")
        st.write("© 2025 DuoDok")
    else:
        st.write("Welcome, User! © 2025 DuoDok")
    if st.button("Logout"):
        logout()
        st.rerun()

# Analysis type selection
analysis_type = st.radio(
    "Select Analysis Mode:",
    ["Single Structure Analysis", "Structure Comparison"],
    horizontal=True,
    key="analysis_type_selector"
)

# Single structure analysis
if analysis_type == "Single Structure Analysis":
    st.header("Single Structure Analysis")

    uploaded_file = st.file_uploader("Upload PDB File", type=["pdb"])

    if uploaded_file:
        st.subheader("File Details")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**File Name:** {uploaded_file.name}")
            st.write(f"**Size:** {uploaded_file.size / 1024:.2f} KB")

        if st.button("Analyze Structure"):
            with st.spinner("Analyzing structure..."):
                try:
                    result = analyzer.analyze_structure(uploaded_file)
                    st.session_state.analysis_result = result
                    st.success("Analysis completed!")
                except Exception as e:
                    st.error(f"Analysis failed: {str(e)}")

    if st.session_state.analysis_result:
        result = st.session_state.analysis_result
        st.header("Analysis Results")

        # Visualization section
        st.subheader("Interactive Visualizations")
        viz_col1, viz_col2 = st.columns(2)

        with viz_col1:
            if result.get("chains"):
                st.plotly_chart(create_residue_chart(result["chains"]), use_container_width=True)
            if result.get("residue_counts"):
                st.plotly_chart(create_residue_pie(result["residue_counts"]), use_container_width=True)

        with viz_col2:
            if result.get("bond_lengths"):
                st.plotly_chart(create_bond_histogram(result["bond_lengths"]), use_container_width=True)

        # Textual results
        st.subheader("Structural Details")
        col1, col2 = st.columns(2)

        with col1:
            st.write("### Basic Information")
            st.metric("Total Chains", len(result["chains"]))
            st.metric("Total Residues", result["residue_count"])
            st.metric("Total Atoms", result["atom_count"])

        with col2:
            st.write("### Chain Breakdown")
            for chain_id, chain_info in result["chains"].items():
                st.write(f"**Chain {chain_id}**:")
                st.write(f"- Residues: {chain_info['residue_count']}")
                st.write(f"- Atoms: {chain_info['atom_count']}")

        # Download report
        st.subheader("Export Results")
        report = f"""
        # PDB Analysis Report
        ## Basic Information
        - Total Chains: {len(result["chains"])}
        - Total Residues: {result["residue_count"]}
        - Total Atoms: {result["atom_count"]}

        ## Residue Types
        {', '.join(result["residue_types"])}
        """

        st.download_button(
            label="Download Report (PDF)",
            data=report,
            file_name="pdb_analysis_report.md",
            mime="text/markdown"
        )
# Structure comparison analysis
else:
    st.header("Structure Comparison")

    col1, col2 = st.columns(2)
    with col1:
        file1 = st.file_uploader("Upload First PDB", type=["pdb"], key="file1")
    with col2:
        file2 = st.file_uploader("Upload Second PDB", type=["pdb"], key="file2")

    if file1 and file2:
        if st.button("Compare Structures"):
            with st.spinner("Comparing structures..."):
                try:
                    comparison = analyzer.compare_structures(file1, file2)
                    st.session_state.comparison_result = comparison
                    st.success("Comparison completed!")
                except Exception as e:
                    st.error(f"Comparison failed: {str(e)}")

    if st.session_state.comparison_result:
        comp = st.session_state.comparison_result
        st.header("Comparison Results")

        # Visualizations
        st.subheader("Interactive Comparison")
        fig1, fig2 = create_comparison_visualizations(comp)
        st.plotly_chart(fig1, use_container_width=True)
        if fig2:
            st.plotly_chart(fig2, use_container_width=True)

        # Textual results
#        st.subheader("Detailed Comparison")
#        col1, col2 = st.columns(2)

#        with col1:
#            st.write("### Structure 1")
#            st.write(f"**ID:** {comp.get('structure1_id', 'N/A')}")
#            st.write(f"**Residues:** {comp.get('structure1_residue_count', 'N/A')}")
#            st.write(f"**Atoms:** {comp.get('structure1_atom_count', 'N/A')}")

#        with col2:
#            st.write("### Structure 2")
#            st.write(f"**ID:** {comp.get('structure2_id', 'N/A')}")
#            st.write(f"**Residues:** {comp.get('structure2_residue_count', 'N/A')}")
#            st.write(f"**Atoms:** {comp.get('structure2_atom_count', 'N/A')}")

        # Download report
        st.subheader("Export Comparison")
        report = f"""
        # PDB Comparison Report
        ## Structure 1
        - ID: {comp.get('structure1_id', 'N/A')}
        - Residues: {comp.get('structure1_residue_count', 'N/A')}
        - Atoms: {comp.get('structure1_atom_count', 'N/A')}

        ## Structure 2
        - ID: {comp.get('structure2_id', 'N/A')}
        - Residues: {comp.get('structure2_residue_count', 'N/A')}
        - Atoms: {comp.get('structure2_atom_count', 'N/A')}

        ## Differences
        - Model Count Difference: {comp.get('model_count_diff', 'N/A')}
        - Residue Count Difference: {comp.get('residue_count_diff', 'N/A')}
        - Atom Count Difference: {comp.get('atom_count_diff', 'N/A')}
        """

        st.download_button(
            label="Download Comparison Report",
            data=report,
            file_name="pdb_comparison_report.md",
            mime="text/markdown"
        )

# Help section
with st.expander("Analysis Guide"):
    st.markdown("""
    ## Using DuoDok PDB Analyzer

    1. **Upload Files**: Use the file uploaders to select PDB files
    2. **Run Analysis**: Click the analysis/comparison button
    3. **View Results**: Interactive visualizations and detailed statistics
    4. **Export**: Download reports in markdown format

    ## Interpretation Tips
    - Residue distribution shows chain composition
    - Bond length histogram helps identify unusual bonds
    - Radar chart in comparisons visualizes structural differences
    - Use exported reports for further analysis
    """)
