import streamlit as st
import sys
import os

import Welcome

# Add the root directory to the path so we can import from the root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Welcome import is_authenticated

# Set page title
st.set_page_config(
    page_title="Tutorial - PDB Analysis Platform",
    page_icon="🧬",
    layout="wide"
)

def load_custom_css():
    with open(".streamlit/custom.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Call the function at the beginning
load_custom_css()

# Check if user is authenticated
if not is_authenticated():
    st.warning("Please log in to access this page.")
    st.stop()

# Page content
st.image("duodok.png", width=100)
st.title("🎓Tutorial: How to Use the PDB Analysis Platform")
if is_authenticated():
    # Get user information
    user_info = Welcome.get_user_info()

    # Display user information and logout button in the sidebar
    with st.sidebar:
        if user_info:
            st.write(f"Welcome, {user_info.get('name', 'User')}!")
            st.write(f"Email: {user_info.get('email', 'N/A')}")
            st.write("© 2025 DuoDok")

        else:
            st.write("Welcome, User! © 2025 DuoDok")

        # Logout button
        if st.button("Logout"):
            Welcome.logout()
            st.rerun()
st.write("""
Welcome to the PDB Analysis Platform tutorial. This guide will help you understand how to use 
our platform effectively to analyze and compare protein structures using PDB files.
""")

# Tutorial sections
st.header("1. Getting Started")
st.subheader("What are PDB Files?")
st.write("""
PDB (Protein Data Bank) files contain atomic coordinate data for biological macromolecules like proteins and nucleic acids. 
These files store information about the 3D structure of molecules, including:

- Atomic coordinates
- Chemical bonds
- Secondary structure assignments
- Experimental details

PDB files typically have a `.pdb` extension and follow a standardized format established by the Worldwide Protein Data Bank.
""")

st.subheader("Where to Find PDB Files")
st.write("""
You can obtain PDB files from several sources:

1. **RCSB Protein Data Bank** (https://www.rcsb.org/) - The primary repository for protein structures
2. **PDBe** (https://www.ebi.ac.uk/pdbe/) - European resource for collection, organization, and dissemination of PDB data
3. **PDBj** (https://pdbj.org/) - Japanese resource for PDB data
4. **AlphaFold DB** (https://alphafold.ebi.ac.uk/) - For AI-predicted protein structures

Simply search for proteins of interest and download the PDB files for analysis on our platform.
""")

# Analysis tutorial
st.header("2. Duodok Analysis")
st.subheader("a. Uploading Files")
st.write("""
You can upload your own PDB files or use our default structures:

- Navigate to the DuoDok page
- Use the "Upload Receptor" or "Upload Antibody" buttons
- Select a .pdb file from your computer
- Your file will be added to the list of available structures

""")

st.subheader("b. Running Analysis")
st.write("""
To analyze receptor-antibody interactions:

- Select at least one receptor and one antibody
- Click "Run Analysis"
- The system will create all possible combinations
- Each pair will be processed through HDOCK, PRODIGY, and PLIP
- Results will be sent to your email address

""")

st.subheader("c. Interpreting Results")
st.write("""
Your results email will contain:

- A summary CSV file with binding energies for each pair
- A ZIP archive with detailed results for each analysis
- Visualization files that can be opened with PyMOL

""")


st.header("3. Single PDB File Analysis")
st.write("""
To analyze a single PDB file:

1. Navigate to the **Analysis** page from the sidebar
2. Click on the file upload area or drag and drop your PDB file
3. Ensure your file has a `.pdb` extension
4. Click the "Analyze" button
5. View the generated report with structural information

The analysis provides details about:
- Number of models, chains, residues, and atoms
- Chain composition
- Residue types
- Bond statistics
""")

# Compare tutorial
st.header("4. Comparing Two PDB Files")
st.write("""
To compare two PDB structures:

1. Navigate to the **Analysis** page
2. Upload two PDB files using the provided upload areas
3. Click the "Compare Structures" button
4. Review the comparison report highlighting the differences between the structures

This feature is particularly useful for:
- Comparing wild-type and mutant proteins
- Analyzing conformational changes
- Studying ligand binding effects
- Evaluating experimental vs. predicted structures
""")

# Interpreting results
st.header("5. Interpreting Results")
st.write("""
Our analysis reports provide several key metrics:

- **Basic Statistics**: Chain, residue, and atom counts
- **Chain Analysis**: Composition of each chain in the structure
- **Residue Analysis**: Distribution of amino acid types
- **Structural Features**: Secondary structure elements, bond lengths

When comparing structures, pay special attention to:
- Differences in residue and atom counts
- Unique residues or chains in each structure
- RMSD values between corresponding atoms (when available)
- Significant changes in bond lengths or angles
""")

# Tips and best practices
st.header("6. Tips and Best Practices")
st.write("""
- **Clean Your PDB Files**: Remove heteroatoms, water molecules, or alternative conformations if they're not relevant to your analysis
- **Consistent Comparison**: When comparing structures, ensure they represent the same protein or region
- **File Size Limit**: Files should be under 10MB for optimal performance
- **Troubleshooting**: If you encounter errors, check your PDB file format and ensure it follows standard conventions
""")

# Video tutorials
st.header("7. Video Tutorials")

# First video tutorial
st.subheader("Basic PDB File Analysis")
st.write("<< **Coming Soon** >>")
st.write("This video explains how to perform basic analysis of a single PDB file.")


# Help and support
st.header("8. Getting Help")
st.write("""
If you need assistance or have questions about using the platform:

1. Check our detailed documentation
2. Use the **Contact** page to reach out to our support team
3. Report any bugs or issues you encounter
""")

# Closing note
st.success("""
Now that you're familiar with the platform, head to the **Analysis** page to start analyzing your PDB files!

For any further help, feel free to reach out through the **Contact** page or our support email.
""")
