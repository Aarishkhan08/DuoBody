import streamlit as st
import time
import os
import sys

import Welcome

# Add the root directory to the path so we can import from the root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Welcome import is_authenticated, get_user_info
from utils.pdb_analyzer import PDBAnalyzer

# Set page title
st.set_page_config(
    page_title="Analysis - PDB Analysis Platform",
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

# Initialize the PDB analyzer
analyzer = PDBAnalyzer()

# Initialize session state variables
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'comparison_result' not in st.session_state:
    st.session_state.comparison_result = None
if 'analysis_type' not in st.session_state:
    st.session_state.analysis_type = "single"

# Page content
st.image("duodok.png", width=100)
st.title("🔬PDB Structure Analysis")

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

# Create tabs for single analysis and comparison
analysis_type = st.radio(
    "Select Analysis Type:",
    ["Single PDB Analysis", "PDB Structure Comparison"],
    horizontal=True
)

if analysis_type == "Single PDB Analysis":
    st.session_state.analysis_type = "single"

    # Initialize session state for analysis mode
    if 'analysis_mode' not in st.session_state:
        st.session_state.analysis_mode = "receptor_only"

    # Create tabs for different analysis modes
    analysis_mode = st.radio(
        "Select Analysis Mode:",
        ["Receptor Only", "Antibody Only"],
        horizontal=True,
        key="analysis_mode_radio"
    )

    if analysis_mode == "Receptor Only":
        st.session_state.analysis_mode = "receptor_only"
        st.subheader("Upload a Receptor PDB File")

        # File upload widget for receptor
        receptor_file = st.file_uploader("Choose a receptor PDB file", type=["pdb"], key="receptor_file")

        # Receptor file information
        if receptor_file is not None:
            with st.container():
                st.write(f"📊 Uploaded receptor file: **{receptor_file.name}**")
                st.write(f"📁 File size: **{receptor_file.size / 1024:.2f} KB**")

            # Analyze button
            if st.button("Analyze Receptor Structure", key="analyze_receptor_btn"):
                # Validate the file
                is_valid, message = analyzer.validate_file(receptor_file)

                if not is_valid:
                    st.error(message)
                else:
                    with st.spinner("Analyzing receptor structure..."):
                        try:
                            # Reset the file pointer
                            receptor_file.seek(0)

                            # Analyze the file
                            result = analyzer.analyze_structure(receptor_file)
                            st.session_state.analysis_result = result

                            # Show success message
                            st.success("Receptor analysis completed successfully!")
                        except Exception as e:
                            st.error(f"Error during analysis: {str(e)}")

    elif analysis_mode == "Antibody Only":
        st.session_state.analysis_mode = "antibody_only"
        st.subheader("Upload an Antibody PDB File")

        # File upload widget for antibody
        antibody_file = st.file_uploader("Choose an antibody PDB file", type=["pdb"], key="antibody_file")

        # Antibody file information
        if antibody_file is not None:
            with st.container():
                st.write(f"📊 Uploaded antibody file: **{antibody_file.name}**")
                st.write(f"📁 File size: **{antibody_file.size / 1024:.2f} KB**")

            # Analyze button
            if st.button("Analyze Antibody Structure", key="analyze_antibody_btn"):
                st.balloons()
                # Validate the file
                is_valid, message = analyzer.validate_file(antibody_file)

                if not is_valid:
                    st.error(message)
                else:
                    with st.spinner("Analyzing antibody structure..."):
                        try:
                            # Reset the file pointer
                            antibody_file.seek(0)

                            # Analyze the file
                            result = analyzer.analyze_structure(antibody_file)
                            st.session_state.analysis_result = result

                            # Show success message
                            st.success("Antibody analysis completed successfully!")
                        except Exception as e:
                            st.error(f"Error during analysis: {str(e)}")

    else:  # Receptor-Antibody Analysis
        st.session_state.analysis_mode = "receptor_antibody"
        st.subheader("Upload Receptor and Antibody PDB Files")

        col1, col2 = st.columns(2)

        with col1:
            st.write("### Receptor File")
            receptor_file = st.file_uploader("Choose a receptor PDB file", type=["pdb"], key="ra_receptor_file")

            if receptor_file is not None:
                st.write(f"📊 Uploaded receptor file: **{receptor_file.name}**")
                st.write(f"📁 File size: **{receptor_file.size / 1024:.2f} KB**")

                # Validate the receptor file
                is_valid, message = analyzer.validate_file(receptor_file)
                if not is_valid:
                    st.error(message)

        with col2:
            st.write("### Antibody File")
            antibody_file = st.file_uploader("Choose an antibody PDB file", type=["pdb"], key="ra_antibody_file")

            if antibody_file is not None:
                st.write(f"📊 Uploaded antibody file: **{antibody_file.name}**")
                st.write(f"📁 File size: **{antibody_file.size / 1024:.2f} KB**")

                # Validate the antibody file
                is_valid, message = analyzer.validate_file(antibody_file)
                if not is_valid:
                    st.error(message)

        # Analyze button for both files
        if receptor_file is not None and antibody_file is not None:
            if st.button("Analyze Receptor-Antibody Interaction", key="analyze_ra_btn"):
                # Validate both files
                st.balloons()
                is_valid_receptor, message_receptor = analyzer.validate_file(receptor_file)
                is_valid_antibody, message_antibody = analyzer.validate_file(antibody_file)

                if not is_valid_receptor:
                    st.error(f"Receptor file: {message_receptor}")
                elif not is_valid_antibody:
                    st.error(f"Antibody file: {message_antibody}")
                else:
                    with st.spinner("Analyzing receptor-antibody interaction..."):
                        try:
                            # Reset file pointers
                            receptor_file.seek(0)
                            antibody_file.seek(0)

                            # Compare the structures
                            comparison = analyzer.compare_structures(receptor_file, antibody_file)
                            st.session_state.comparison_result = comparison
                            st.session_state.analysis_result = None  # Clear single analysis result

                            # Show success message
                            st.success("Receptor-Antibody analysis completed successfully!")
                        except Exception as e:
                            st.error(f"Error during analysis: {str(e)}")

    # Display analysis results
    if st.session_state.analysis_result is not None and st.session_state.analysis_type == "single":
        st.subheader("Analysis Results")

        # Basic information
        result = st.session_state.analysis_result

        col1, col2 = st.columns(2)

        with col1:
            st.write("### Basic Information")
            st.write(f"Structure ID: **{result['structure_id']}**")
            st.write(f"Number of models: **{result['number_of_models']}**")
            st.write(f"Total residues: **{result['residue_count']}**")
            st.write(f"Total atoms: **{result['atom_count']}**")

        with col2:
            st.write("### Chain Information")
            for chain_id, chain_info in result["chains"].items():
                st.write(f"Chain {chain_id}:")
                st.write(f"- Residues: **{chain_info['residue_count']}**")
                st.write(f"- Atoms: **{chain_info['atom_count']}**")

        # Residue types
        st.write("### Residue Types")
        st.write(f"Number of unique residue types: **{len(result['residue_types'])}**")
        st.write(f"Residue types: **{', '.join(sorted(result['residue_types']))}**")

        # Bond information
        if result["bond_lengths"]:
            st.write("### Bond Statistics")

            # Calculate average bond length
            avg_bond_length = sum(bond["distance"] for bond in result["bond_lengths"]) / len(result["bond_lengths"])

            # Find min and max bond lengths
            min_bond = min(result["bond_lengths"], key=lambda x: x["distance"])
            max_bond = max(result["bond_lengths"], key=lambda x: x["distance"])

            st.write(f"Average bond length: **{avg_bond_length:.3f} Å**")
            st.write(f"Minimum bond length: **{min_bond['distance']:.3f} Å** "
                     f"({min_bond['atom1']}-{min_bond['atom2']} in {min_bond['residue']} of chain {min_bond['chain']})")
            st.write(f"Maximum bond length: **{max_bond['distance']:.3f} Å** "
                     f"({max_bond['atom1']}-{max_bond['atom2']} in {max_bond['residue']} of chain {max_bond['chain']})")

        # Add download button for report
        report = f"""
        # PDB Structure Analysis Report

        ## Basic Information
        - Structure ID: {result['structure_id']}
        - Number of models: {result['number_of_models']}
        - Total residues: {result['residue_count']}
        - Total atoms: {result['atom_count']}

        ## Chain Information
        """

        for chain_id, chain_info in result["chains"].items():
            report += f"""
        ### Chain {chain_id}
        - Residues: {chain_info['residue_count']}
        - Atoms: {chain_info['atom_count']}
            """

        report += f"""
        ## Residue Types
        - Number of unique residue types: {len(result['residue_types'])}
        - Residue types: {', '.join(sorted(result['residue_types']))}
        """

        if result["bond_lengths"]:
            avg_bond_length = sum(bond["distance"] for bond in result["bond_lengths"]) / len(result["bond_lengths"])
            min_bond = min(result["bond_lengths"], key=lambda x: x["distance"])
            max_bond = max(result["bond_lengths"], key=lambda x: x["distance"])

            report += f"""
        ## Bond Statistics
        - Average bond length: {avg_bond_length:.3f} Å
        - Minimum bond length: {min_bond['distance']:.3f} Å ({min_bond['atom1']}-{min_bond['atom2']} in {min_bond['residue']} of chain {min_bond['chain']})
        - Maximum bond length: {max_bond['distance']:.3f} Å ({max_bond['atom1']}-{max_bond['atom2']} in {max_bond['residue']} of chain {max_bond['chain']})
            """

        st.download_button(
            label="Download Report",
            data=report,
            file_name="pdb_analysis_report.md",
            mime="text/markdown"
        )

else:  # Comparison analysis
    st.session_state.analysis_type = "comparison"
    st.subheader("Upload Two PDB Files for Comparison")

    col1, col2 = st.columns(2)

    with col1:
        st.write("### First PDB File")
        file1 = st.file_uploader("Choose first PDB file", type=["pdb"], key="file1")

        if file1 is not None:
            st.write(f"Uploaded file: **{file1.name}**")
            st.write(f"File size: **{file1.size / 1024:.2f} KB**")

            # Validate the first file
            is_valid1, message1 = analyzer.validate_file(file1)
            if not is_valid1:
                st.error(message1)

    with col2:
        st.write("### Second PDB File")
        file2 = st.file_uploader("Choose second PDB file", type=["pdb"], key="file2")

        if file2 is not None:
            st.write(f"Uploaded file: **{file2.name}**")
            st.write(f"File size: **{file2.size / 1024:.2f} KB**")

            # Validate the second file
            is_valid2, message2 = analyzer.validate_file(file2)
            if not is_valid2:
                st.error(message2)

    # Compare button
    if file1 is not None and file2 is not None:
        if st.button("Compare Structures"):
            st.balloons()
            # Validate both files
            is_valid1, message1 = analyzer.validate_file(file1)
            is_valid2, message2 = analyzer.validate_file(file2)

            if not is_valid1:
                st.error(f"First file: {message1}")
            elif not is_valid2:
                st.error(f"Second file: {message2}")
            else:
                with st.spinner("Comparing PDB structures..."):
                    try:
                        # Reset file pointers
                        file1.seek(0)
                        file2.seek(0)

                        # Compare the structures
                        comparison = analyzer.compare_structures(file1, file2)
                        st.session_state.comparison_result = comparison

                        # Show success message
                        st.success("Comparison completed successfully!")
                    except Exception as e:
                        st.error(f"Error during comparison: {str(e)}")

    # Display comparison results
    if st.session_state.comparison_result is not None and st.session_state.analysis_type == "comparison":
        st.subheader("Comparison Results")

        comparison = st.session_state.comparison_result

        # Basic comparison
        st.write("### Basic Comparison")
        st.write(f"Structure 1 ID: **{comparison['structure1_id']}**")
        st.write(f"Structure 2 ID: **{comparison['structure2_id']}**")

        # Structural differences
        st.write("### Structural Differences")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Model Count Difference", comparison['model_count_diff'])

        with col2:
            st.metric("Residue Count Difference", comparison['residue_count_diff'])

        with col3:
            st.metric("Atom Count Difference", comparison['atom_count_diff'])

        # Chain analysis
        st.write("### Chain Analysis")
        st.write(
            f"Common chains: **{', '.join(comparison['common_chains']) if comparison['common_chains'] else 'None'}**")
        st.write(
            f"Unique chains in structure 1: **{', '.join(comparison['unique_chains_1']) if comparison['unique_chains_1'] else 'None'}**")
        st.write(
            f"Unique chains in structure 2: **{', '.join(comparison['unique_chains_2']) if comparison['unique_chains_2'] else 'None'}**")

        # Residue type analysis
        st.write("### Residue Type Analysis")
        st.write(
            f"Unique residue types in structure 1: **{', '.join(comparison['unique_residue_types_1']) if comparison['unique_residue_types_1'] else 'None'}**")
        st.write(
            f"Unique residue types in structure 2: **{', '.join(comparison['unique_residue_types_2']) if comparison['unique_residue_types_2'] else 'None'}**")

        # Chain comparison
        if comparison["chain_comparison"]:
            st.write("### Chain Comparison")

            for chain_id, chain_data in comparison["chain_comparison"].items():
                st.write(f"#### Chain {chain_id}")

                col1, col2 = st.columns(2)

                with col1:
                    st.metric("Residue Count Difference", chain_data['residue_count_diff'])

                with col2:
                    st.metric("Atom Count Difference", chain_data['atom_count_diff'])

        # Generate and download report
        report = analyzer.generate_report(comparison)

        st.download_button(
            label="Download Comparison Report",
            data=report,
            file_name="pdb_comparison_report.md",
            mime="text/markdown"
        )

# Add help information
with st.expander("Need help with PDB analysis?"):
    st.write("""
    ### Understanding PDB Analysis Results

    The analysis provides information about the structure of proteins stored in PDB format:

    - **Models**: Some PDB files contain multiple models of the same structure (e.g., from NMR experiments)
    - **Chains**: Separate polypeptide chains in the protein
    - **Residues**: Amino acid building blocks that make up the protein
    - **Atoms**: Individual atoms that make up the residues

    ### Tips for Effective Analysis

    - Compare proteins with similar sequences for meaningful results
    - For large proteins, focus on specific chains or domains
    - When analyzing mutations, pay attention to side chain conformations

    ### Common Issues

    - Missing residues or atoms in the PDB file can affect analysis
    - Some PDB files may contain non-standard residues
    - Older PDB files may have formatting differences
    """)

# Add custom content section below analysis results
st.markdown("---")
st.subheader("💡 Insights & Interpretations")

# Check if any analysis has been performed
if st.session_state.analysis_result is not None or st.session_state.comparison_result is not None:
    # Custom content tabs
    custom_tabs = st.tabs(["Structure Insights", "Visualization Tips", "Research Applications", "Notes"])

    with custom_tabs[0]:
        st.write("""
        ### Key Structure Insights

        Protein structures offer valuable insights into their function. Here are some key points to consider:

        - **Binding Pockets**: Look for cavities or pockets in the structure where ligands might bind
        - **Secondary Structure**: Analyze the distribution of α-helices and β-sheets
        - **Conserved Domains**: Identify evolutionarily conserved regions
        - **Active Sites**: Locate residues involved in catalytic activity
        - **Protein-Protein Interfaces**: Examine potential interaction surfaces

        Identifying these features can help you understand the biological function of your protein.
        """)

        # Add interactive elements
        st.info(
            "💡 **Pro Tip**: Secondary structures often correlate with protein function. α-helices are common in membrane proteins, while β-sheets are prevalent in structural proteins.")

    with custom_tabs[1]:
        st.write("""
        ### Effective Structure Visualization

        To better visualize your PDB structures, consider these tips:

        1. **Color by Property**: Color residues by hydrophobicity, charge, or conservation
        2. **Surface Representation**: Use surface views to identify binding pockets
        3. **Highlight Domains**: Emphasize functional domains with different colors
        4. **Side-by-Side Comparison**: Compare related structures to identify differences
        5. **Electrostatic Surface**: Calculate and visualize electrostatic potential

        External visualization tools like PyMOL, ChimeraX, or online viewers can provide additional insights.
        """)

        # Add a color scheme picker mockup
        st.write("#### Color Scheme Preferences")
        col1, col2 = st.columns(2)
        with col1:
            st.color_picker("Structure Color", "#6A39D0")
        with col2:
            st.selectbox("Coloring Method", ["Chain", "Residue Type", "B-factor", "Secondary Structure"])

    with custom_tabs[2]:
        st.write("""
        ### Research Applications

        PDB structure analysis is valuable for various research applications:

        - **Drug Discovery**: Identify potential binding sites for drug candidates
        - **Protein Engineering**: Guide modifications to enhance protein stability or function
        - **Disease Mechanisms**: Understand how mutations lead to disease phenotypes
        - **Evolutionary Studies**: Compare structures across species to trace evolutionary relationships
        - **Antibody-Antigen Interactions**: Analyze the molecular basis of immune recognition

        Your analysis results can inform experimental design and hypothesis generation.
        """)

    with custom_tabs[3]:
        st.write("### Your Analysis Notes")
        st.text_area("Add your notes and observations here", height=150, key="analysis_notes")
        st.button("Save Notes", key="save_notes_btn")

        # Add tags
        st.write("#### Add Tags")
        tag_cols = st.columns(3)
        with tag_cols[0]:
            st.checkbox("Receptor", key="tag_receptor")
        with tag_cols[1]:
            st.checkbox("Antibody", key="tag_antibody")
        with tag_cols[2]:
            st.checkbox("Interaction", key="tag_interaction")

        # Add custom tag
        st.text_input("Add custom tag", placeholder="Enter custom tag here", key="custom_tag")
else:
    # If no analysis has been performed
    st.info("🔍 Upload and analyze PDB files to access insights and interpretation tools.")

    # Show example insight
    with st.expander("See example insights"):
        st.write("""
        ### Example Analysis Insights

        When you analyze a PDB structure, you'll receive detailed information about:

        - Protein composition and size
        - Secondary structure elements
        - Bond statistics and atomic interactions
        - Chain organization and relationships

        Upload your PDB files to get started with your analysis!
        """)

# Add a feedback section
st.markdown("---")
st.subheader("📊 Feedback & Improvement")
feedback_col1, feedback_col2 = st.columns(2)
with feedback_col1:
    st.selectbox("How useful was this analysis?", ["Select an option", "Very useful", "Somewhat useful", "Not useful"])
with feedback_col2:
    st.text_input("Suggest improvements", placeholder="Share your ideas to improve the platform")
st.button("Submit Feedback", key="submit_feedback_btn")
