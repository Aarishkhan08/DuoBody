import streamlit as st
import io
import base64
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages
from Bio.PDB import PDBParser, PDBIO, Structure, Model, Chain
from Bio.PDB.DSSP import DSSP
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import tempfile
import os
import time
import random
from stmol import showmol
import py3Dmol
import matplotlib
matplotlib.use('Agg')

# Set page config
st.set_page_config(page_title="Bispecific Antibody Designer", layout="wide")

# CSS to hide the streamlit branding
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Title
st.title("Bispecific Antibody Designer")

# Initialize session state
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = None

if 'results' not in st.session_state:
    st.session_state.results = None

if 'report_data' not in st.session_state:
    st.session_state.report_data = {}

# File uploader section
st.header("Upload PDB Files")

col1, col2 = st.columns(2)

with col1:
    receptor_files = st.file_uploader("Upload Receptor PDB Files", type=["pdb"], accept_multiple_files=True)

with col2:
    antibody_files = st.file_uploader("Upload Antibody PDB Files", type=["pdb"], accept_multiple_files=True)

# Functions for the pipeline
def process_pdb_structure(pdb_file):
    """
    Parse PDB file and prepare structure
    """
    parser = PDBParser(QUIET=True)
    
    # Read the file content
    content = pdb_file.getvalue().decode('utf-8')
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(suffix='.pdb', delete=False) as temp_file:
        temp_file.write(pdb_file.getvalue())
        temp_path = temp_file.name
    
    # Parse the PDB file
    try:
        structure = parser.get_structure(pdb_file.name, temp_path)
        
        # Get basic structure information
        num_models = len(structure)
        chains = list(structure.get_chains())
        num_chains = len(chains)
        
        residues = list(structure.get_residues())
        num_residues = len(residues)
        
        # Calculate center of mass
        atom_coords = np.array([atom.get_coord() for atom in structure.get_atoms()])
        center_of_mass = atom_coords.mean(axis=0)
        
        # Get secondary structure
        try:
            model = structure[0]
            dssp = DSSP(model, temp_path)
            sec_struct_counts = {'H': 0, 'B': 0, 'E': 0, 'G': 0, 'I': 0, 'T': 0, 'S': 0, '-': 0}
            
            for res in dssp:
                ss = res[2]
                if ss in sec_struct_counts:
                    sec_struct_counts[ss] += 1
        except:
            sec_struct_counts = {'H': 0, 'B': 0, 'E': 0, 'G': 0, 'I': 0, 'T': 0, 'S': 0, '-': 0}
        
        # Clean up the temporary file
        os.unlink(temp_path)
        
        return {
            'name': pdb_file.name,
            'structure': structure,
            'num_models': num_models,
            'num_chains': num_chains,
            'num_residues': num_residues,
            'center_of_mass': center_of_mass,
            'sec_struct_counts': sec_struct_counts
        }
    except Exception as e:
        os.unlink(temp_path)
        raise Exception(f"Error processing PDB file {pdb_file.name}: {str(e)}")

def perform_docking(receptor_data, antibody_data):
    """
    Simulate molecular docking between receptor and antibody
    """
    # In a real application, you would use a docking tool like AutoDock or HADDOCK
    # For this demo, we'll simulate the docking with random scores
    
    # Extract coordinates for visualization
    receptor_com = receptor_data['center_of_mass']
    antibody_com = antibody_data['center_of_mass']
    
    # Calculate distance between centers of mass
    distance = np.linalg.norm(receptor_com - antibody_com)
    
    # Generate random docking scores (in a real app, these would come from actual docking)
    docking_score = -random.uniform(6.0, 12.0)  # Negative is better
    
    # Generate multiple poses (in a real app, these would be actual different conformations)
    poses = []
    for i in range(5):
        pose_score = docking_score * random.uniform(0.8, 1.2)
        poses.append({
            'pose_id': i+1,
            'score': pose_score,
            'rmsd': random.uniform(0, 5.0),
            'interface_area': random.uniform(800, 2000)
        })
    
    # Sort poses by score
    poses.sort(key=lambda x: x['score'])
    
    return {
        'receptor': receptor_data['name'],
        'antibody': antibody_data['name'],
        'top_score': poses[0]['score'],
        'distance': distance,
        'poses': poses
    }

def calculate_binding_energy(docking_result):
    """
    Estimate binding energy for the docked complex
    """
    # In a real application, this would use molecular mechanics or more sophisticated methods
    # For this demo, we'll generate simulated binding energies
    
    # Base energy from docking score
    base_energy = docking_result['top_score'] * 1.5
    
    # Add components that would normally be calculated
    energy_components = {
        'van_der_waals': random.uniform(-20, -5),
        'electrostatic': random.uniform(-15, 5),
        'desolvation': random.uniform(0, 10),
        'hydrogen_bonding': random.uniform(-10, -2),
        'entropy': random.uniform(5, 15)
    }
    
    # Calculate total energy
    total_energy = base_energy + sum(energy_components.values())
    
    # Return energy details
    return {
        'receptor': docking_result['receptor'],
        'antibody': docking_result['antibody'],
        'total_energy': total_energy,
        'components': energy_components
    }

def analyze_interactions(receptor_data, antibody_data, docking_result):
    """
    Profile the interactions between receptor and antibody
    """
    # In a real application, this would analyze the actual molecular interactions
    # For this demo, we'll simulate the interaction profile
    
    # Generate random counts for different interaction types
    interaction_counts = {
        'hydrogen_bonds': random.randint(3, 12),
        'salt_bridges': random.randint(0, 5),
        'hydrophobic': random.randint(5, 20),
        'pi_stacking': random.randint(0, 3),
        'cation_pi': random.randint(0, 2)
    }
    
    # Generate interface residues
    interface_residues = {
        'receptor': [f"{random.choice(['ALA', 'GLY', 'THR', 'SER', 'ASP', 'GLU'])}{random.randint(10, 300)}" for _ in range(random.randint(10, 20))],
        'antibody': [f"{random.choice(['ALA', 'GLY', 'THR', 'SER', 'ASP', 'GLU'])}{random.randint(10, 300)}" for _ in range(random.randint(10, 20))]
    }
    
    # CDR regions involved (for antibodies)
    cdr_involvement = {
        'CDR-H1': random.uniform(0, 1),
        'CDR-H2': random.uniform(0, 1),
        'CDR-H3': random.uniform(0, 1),
        'CDR-L1': random.uniform(0, 1),
        'CDR-L2': random.uniform(0, 1),
        'CDR-L3': random.uniform(0, 1)
    }
    
    # Generate epitope classification (for receptor)
    epitope_types = ['conformational', 'linear', 'mixed']
    epitope_classification = random.choice(epitope_types)
    
    return {
        'receptor': docking_result['receptor'],
        'antibody': docking_result['antibody'],
        'interaction_counts': interaction_counts,
        'interface_residues': interface_residues,
        'cdr_involvement': cdr_involvement,
        'epitope_classification': epitope_classification,
        'buried_surface_area': random.uniform(800, 2000),
        'shape_complementarity': random.uniform(0.6, 0.9)
    }

def design_bispecific_antibody(receptor_antibody_pairs, binding_energies, interaction_profiles):
    """
    Design bispecific antibody based on best binders
    """
    # Sort pairs by binding energy
    sorted_pairs = sorted(binding_energies, key=lambda x: x['total_energy'])
    
    # Get top pairs for each receptor
    receptors = set(pair['receptor'] for pair in receptor_antibody_pairs)
    antibodies = set(pair['antibody'] for pair in receptor_antibody_pairs)
    
    # Find best antibody for each receptor
    best_pairs = {}
    for receptor in receptors:
        receptor_pairs = [pair for pair in sorted_pairs if pair['receptor'] == receptor]
        if receptor_pairs:
            best_pairs[receptor] = receptor_pairs[0]
    
    # Find potential combinations for bispecific antibodies
    bispecific_combinations = []
    
    # In a real application, this would involve sophisticated engineering rules
    # For this demo, we'll consider all possible pairs of antibodies
    
    processed_antibodies = {}
    for receptor, pair in best_pairs.items():
        # Find antibody info
        antibody_name = pair['antibody']
        interaction_profile = next((p for p in interaction_profiles if p['receptor'] == receptor and p['antibody'] == antibody_name), None)
        
        processed_antibodies[antibody_name] = {
            'receptor': receptor,
            'binding_energy': pair['total_energy'],
            'cdr_usage': interaction_profile['cdr_involvement'] if interaction_profile else None
        }
    
    # Create potential bispecific combinations
    antibody_list = list(processed_antibodies.keys())
    for i in range(len(antibody_list)):
        for j in range(i+1, len(antibody_list)):
            ab1 = antibody_list[i]
            ab2 = antibody_list[j]
            ab1_data = processed_antibodies[ab1]
            ab2_data = processed_antibodies[ab2]
            
            # Check if they target different receptors
            if ab1_data['receptor'] != ab2_data['receptor']:
                # Calculate compatibility score (in a real app, this would be based on sequence and structural analysis)
                compatibility = random.uniform(0, 1)
                
                # Calculate potential interference
                interference = 0
                if ab1_data['cdr_usage'] and ab2_data['cdr_usage']:
                    # Check if both antibodies heavily use the same CDRs
                    for cdr, usage1 in ab1_data['cdr_usage'].items():
                        usage2 = ab2_data['cdr_usage'][cdr]
                        if usage1 > 0.5 and usage2 > 0.5:
                            interference += 0.2
                
                # Calculate combined score
                combined_score = (abs(ab1_data['binding_energy']) + abs(ab2_data['binding_energy'])) * compatibility * (1 - interference)
                
                bispecific_combinations.append({
                    'antibody1': ab1,
                    'antibody2': ab2,
                    'receptor1': ab1_data['receptor'],
                    'receptor2': ab2_data['receptor'],
                    'compatibility': compatibility,
                    'interference': interference,
                    'combined_score': combined_score,
                    'format_suggestions': random.choice(['IgG-scFv', 'Diabody', 'CrossMAb', 'DVD-Ig', 'TandAb'])
                })
    
    # Sort by combined score
    bispecific_combinations.sort(key=lambda x: x['combined_score'], reverse=True)
    
    return bispecific_combinations

def generate_report_data(receptor_data, antibody_data, docking_results, binding_energies, interaction_profiles, bispecific_designs):
    """
    Compile all analysis results into a report format
    """
    report = {
        'receptors': receptor_data,
        'antibodies': antibody_data,
        'docking_results': docking_results,
        'binding_energies': binding_energies,
        'interaction_profiles': interaction_profiles,
        'bispecific_designs': bispecific_designs
    }
    
    return report

def create_pdf_report(report_data):
    """
    Generate PDF report from the analysis results
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []
    
    # Add title
    title_style = styles['Heading1']
    elements.append(Paragraph("Bispecific Antibody Design Report", title_style))
    elements.append(Spacer(1, 0.25*inch))
    
    # Add timestamp
    date_style = styles['Normal']
    date_style.alignment = 1  # Right alignment
    elements.append(Paragraph(f"Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}", date_style))
    elements.append(Spacer(1, 0.25*inch))
    
    # Add summary
    elements.append(Paragraph("Summary", styles['Heading2']))
    summary_text = f"""
    This report summarizes the analysis of {len(report_data['receptors'])} receptor(s) and {len(report_data['antibodies'])} antibody(s),
    with {len(report_data['docking_results'])} docking simulations performed. The analysis identified {len(report_data['bispecific_designs'])} 
    potential bispecific antibody designs.
    """
    elements.append(Paragraph(summary_text, styles['Normal']))
    elements.append(Spacer(1, 0.25*inch))
    
    # Add receptor information
    elements.append(Paragraph("Receptor Analysis", styles['Heading2']))
    for i, receptor in enumerate(report_data['receptors']):
        elements.append(Paragraph(f"Receptor {i+1}: {receptor['name']}", styles['Heading3']))
        receptor_text = f"""
        Chains: {receptor['num_chains']}
        Residues: {receptor['num_residues']}
        """
        elements.append(Paragraph(receptor_text, styles['Normal']))
        
        # Add secondary structure information
        sec_struct = receptor['sec_struct_counts']
        ss_text = f"Secondary Structure: α-helix: {sec_struct['H']}, β-sheet: {sec_struct['E']}, Loop: {sec_struct['-']}"
        elements.append(Paragraph(ss_text, styles['Normal']))
        elements.append(Spacer(1, 0.15*inch))
    
    elements.append(Spacer(1, 0.25*inch))
    
    # Add antibody information
    elements.append(Paragraph("Antibody Analysis", styles['Heading2']))
    for i, antibody in enumerate(report_data['antibodies']):
        elements.append(Paragraph(f"Antibody {i+1}: {antibody['name']}", styles['Heading3']))
        antibody_text = f"""
        Chains: {antibody['num_chains']}
        Residues: {antibody['num_residues']}
        """
        elements.append(Paragraph(antibody_text, styles['Normal']))
        
        # Add secondary structure information
        sec_struct = antibody['sec_struct_counts']
        ss_text = f"Secondary Structure: α-helix: {sec_struct['H']}, β-sheet: {sec_struct['E']}, Loop: {sec_struct['-']}"
        elements.append(Paragraph(ss_text, styles['Normal']))
        elements.append(Spacer(1, 0.15*inch))
    
    elements.append(Spacer(1, 0.25*inch))
    
    # Add docking results
    elements.append(Paragraph("Molecular Docking Analysis", styles['Heading2']))
    
    # Create docking results table
    docking_data = []
    docking_data.append(["Receptor", "Antibody", "Docking Score", "Top Pose RMSD"])
    
    for result in report_data['docking_results']:
        docking_data.append([
            result['receptor'],
            result['antibody'],
            f"{result['top_score']:.2f}",
            f"{result['poses'][0]['rmsd']:.2f}"
        ])
    
    docking_table = Table(docking_data)
    docking_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(docking_table)
    elements.append(Spacer(1, 0.25*inch))
    
    # Add binding energy analysis
    elements.append(Paragraph("Binding Energy Analysis", styles['Heading2']))
    
    # Create binding energy table
    energy_data = []
    energy_data.append(["Receptor", "Antibody", "Total Energy", "vdW", "Electrostatic", "H-Bond"])
    
    for energy in report_data['binding_energies']:
        energy_data.append([
            energy['receptor'],
            energy['antibody'],
            f"{energy['total_energy']:.2f}",
            f"{energy['components']['van_der_waals']:.2f}",
            f"{energy['components']['electrostatic']:.2f}",
            f"{energy['components']['hydrogen_bonding']:.2f}"
        ])
    
    energy_table = Table(energy_data)
    energy_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(energy_table)
    elements.append(Spacer(1, 0.25*inch))
    
    # Add interaction analysis
    elements.append(Paragraph("Interaction Profile Analysis", styles['Heading2']))
    
    # Create interaction table
    interaction_data = []
    interaction_data.append(["Receptor", "Antibody", "H-Bonds", "Salt Bridges", "Hydrophobic", "Interface Area"])
    
    for profile in report_data['interaction_profiles']:
        interaction_data.append([
            profile['receptor'],
            profile['antibody'],
            profile['interaction_counts']['hydrogen_bonds'],
            profile['interaction_counts']['salt_bridges'],
            profile['interaction_counts']['hydrophobic'],
            f"{profile['buried_surface_area']:.1f}"
        ])
    
    interaction_table = Table(interaction_data)
    interaction_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(interaction_table)
    elements.append(Spacer(1, 0.25*inch))
    
    # Add bispecific antibody designs
    elements.append(Paragraph("Bispecific Antibody Design Results", styles['Heading2']))
    
    if report_data['bispecific_designs']:
        # Create bispecific design table
        bispecific_data = []
        bispecific_data.append(["Antibody 1", "Antibody 2", "Target 1", "Target 2", "Compatibility", "Format"])
        
        for design in report_data['bispecific_designs']:
            bispecific_data.append([
                design['antibody1'],
                design['antibody2'],
                design['receptor1'],
                design['receptor2'],
                f"{design['compatibility']:.2f}",
                design['format_suggestions']
            ])
        
        bispecific_table = Table(bispecific_data)
        bispecific_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(bispecific_table)
        elements.append(Spacer(1, 0.25*inch))
        
        # Add top recommendations
        elements.append(Paragraph("Top Bispecific Antibody Recommendations", styles['Heading2']))
        
        for i, design in enumerate(report_data['bispecific_designs'][:3]):
            elements.append(Paragraph(f"Recommendation {i+1}", styles['Heading3']))
            
            recommendation_text = f"""
            Bispecific Format: {design['format_suggestions']}
            Component 1: {design['antibody1']} targeting {design['receptor1']}
            Component 2: {design['antibody2']} targeting {design['receptor2']}
            Compatibility Score: {design['compatibility']:.2f}
            Predicted Interference: {design['interference']:.2f}
            Combined Score: {design['combined_score']:.2f}
            """
            elements.append(Paragraph(recommendation_text, styles['Normal']))
            elements.append(Spacer(1, 0.15*inch))
    else:
        elements.append(Paragraph("No viable bispecific designs found.", styles['Normal']))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

def create_visualization(receptor_data, antibody_data, docking_result=None):
    """
    Create a visualization of the receptor, antibody, and optionally the docked complex
    """
    view = py3Dmol.view(width=600, height=400)
    
    # Add receptor structure
    if receptor_data and 'structure' in receptor_data:
        io = PDBIO()
        io.set_structure(receptor_data['structure'])
        
        with tempfile.NamedTemporaryFile(suffix='.pdb', delete=False) as temp_file:
            io.save(temp_file.name)
            with open(temp_file.name, 'r') as f:
                receptor_pdb = f.read()
            temp_path = temp_file.name
        
        view.addModel(receptor_pdb, 'pdb')
        view.setStyle({'model': 0}, {'cartoon': {'color': 'blue'}})
        
        try:
            os.unlink(temp_path)
        except:
            pass
    
    # Add antibody structure
    if antibody_data and 'structure' in antibody_data:
        io = PDBIO()
        io.set_structure(antibody_data['structure'])
        
        with tempfile.NamedTemporaryFile(suffix='.pdb', delete=False) as temp_file:
            io.save(temp_file.name)
            with open(temp_file.name, 'r') as f:
                antibody_pdb = f.read()
            temp_path = temp_file.name
        
        view.addModel(antibody_pdb, 'pdb')
        view.setStyle({'model': 1}, {'cartoon': {'color': 'green'}})
        
        try:
            os.unlink(temp_path)
        except:
            pass
    
    # Show binding interface if docking result is provided
    if docking_result:
        if 'poses' in docking_result and docking_result['poses']:
            top_pose = docking_result['poses'][0]
            if 'interface_area' in top_pose:
                # In a real application, this would highlight the actual interface residues
                # For this demo, we'll just show a sphere at the midpoint
                if receptor_data and antibody_data:
                    midpoint = (receptor_data['center_of_mass'] + antibody_data['center_of_mass']) / 2
                    view.addSphere({
                        'center': {'x': midpoint[0], 'y': midpoint[1], 'z': midpoint[2]},
                        'radius': 3,
                        'color': 'red',
                        'opacity': 0.5
                    })
    
    view.zoomTo()
    view.setBackgroundColor('white')
    return view

def run_pipeline():
    """
    Execute the complete analysis pipeline
    """
    if not receptor_files or not antibody_files:
        st.error("Please upload at least one receptor and one antibody PDB file.")
        return
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Process receptor files
    status_text.text("Processing receptor structures...")
    receptor_data = []
    for i, receptor_file in enumerate(receptor_files):
        try:
            receptor_info = process_pdb_structure(receptor_file)
            receptor_data.append(receptor_info)
            progress_bar.progress((i + 1) / len(receptor_files) * 0.2)
        except Exception as e:
            st.error(f"Error processing receptor {receptor_file.name}: {str(e)}")
            return
    
    # Process antibody files
    status_text.text("Processing antibody structures...")
    antibody_data = []
    for i, antibody_file in enumerate(antibody_files):
        try:
            antibody_info = process_pdb_structure(antibody_file)
            antibody_data.append(antibody_info)
            progress_bar.progress(0.2 + (i + 1) / len(antibody_files) * 0.2)
        except Exception as e:
            st.error(f"Error processing antibody {antibody_file.name}: {str(e)}")
            return
    
    # Perform docking for all receptor-antibody pairs
    status_text.text("Performing molecular docking...")
    docking_results = []
    pair_count = 0
    total_pairs = len(receptor_data) * len(antibody_data)
    
    for receptor in receptor_data:
        for antibody in antibody_data:
            try:
                docking_result = perform_docking(receptor, antibody)
                docking_results.append(docking_result)
                pair_count += 1
                progress_bar.progress(0.4 + pair_count / total_pairs * 0.2)
            except Exception as e:
                st.error(f"Error docking {receptor['name']} with {antibody['name']}: {str(e)}")
                return
    
    # Calculate binding energies
    status_text.text("Estimating binding energies...")
    binding_energies = []
    for i, docking_result in enumerate(docking_results):
        try:
            energy = calculate_binding_energy(docking_result)
            binding_energies.append(energy)
            progress_bar.progress(0.6 + (i + 1) / len(docking_results) * 0.1)
        except Exception as e:
            st.error(f"Error calculating binding energy for {docking_result['receptor']} - {docking_result['antibody']}: {str(e)}")
            return
    
    # Analyze interactions
    status_text.text("Profiling molecular interactions...")
    interaction_profiles = []
    for i, (receptor, antibody, docking_result) in enumerate(zip(
        [r for r in receptor_data for _ in range(len(antibody_data))],
        [a for _ in range(len(receptor_data)) for a in antibody_data],
        docking_results
    )):
        try:
            profile = analyze_interactions(receptor, antibody, docking_result)
            interaction_profiles.append(profile)
            progress_bar.progress(0.7 + (i + 1) / len(docking_results) * 0.1)
        except Exception as e:
            st.error(f"Error analyzing interactions for {docking_result['receptor']} - {docking_result['antibody']}: {str(e)}")
            return
    
    # Design bispecific antibodies
    status_text.text("Designing bispecific antibodies...")
    try:
        receptor_antibody_pairs = [{'receptor': result['receptor'], 'antibody': result['antibody']} for result in docking_results]
        bispecific_designs = design_bispecific_antibody(receptor_antibody_pairs, binding_energies, interaction_profiles)
        progress_bar.progress(0.9)
    except Exception as e:
        st.error(f"Error designing bispecific antibodies: {str(e)}")
        return
    
    # Generate report data
    status_text.text("Generating report...")
    try:
        report_data = generate_report_data(receptor_data, antibody_data, docking_results, binding_energies, interaction_profiles, bispecific_designs)
        progress_bar.progress(0.95)
    except Exception as e:
        st.error(f"Error generating report: {str(e)}")
        return
    
    # Complete
    progress_bar.progress(1.0)
    status_text.text("Analysis complete!")
    
    return {
        'receptor_data': receptor_data,
        'antibody_data': antibody_data,
        'docking_results': docking_results,
        'binding_energies': binding_energies,
        'interaction_profiles': interaction_profiles,
        'bispecific_designs': bispecific_designs,
        'report_data': report_data
    }

def generate_bispecific_pdb(design, receptor_data, antibody_data):
    """
    Generate a PDB file for the designed bispecific antibody
    """
    # In a real application, this would perform actual protein engineering
    # For this demo, we'll simulate by combining the two antibody structures
    
    # Find the two antibodies
    antibody1 = next((a for a in antibody_data if a['name'] == design['antibody1']), None)
    antibody2 = next((a for a in antibody_data if a['name'] == design['antibody2']), None)
    
    if not antibody1 or not antibody2:
        return None
    
    # Create a new structure
    new_structure = Structure.Structure("bispecific")
    model = Model.Model(0)
    new_structure.add(model)
    
    # Add first antibody
    for i, chain in enumerate(antibody1['structure'].get_chains()):
        new_chain = Chain.Chain(f"A{i+1}")
        for residue in chain:
            new_chain.add(residue)
        model.add(new_chain)
    
    # Add second antibody with offset
    # In a real application, this would be a sophisticated engineering step
    offset = np.array([50.0, 0.0, 0.0])  # Arbitrary offset for visualization
    for i, chain in enumerate(antibody2['structure'].get_chains()):
        new_chain = Chain.Chain(f"B{i+1}")
        for residue in chain:
            # Create a copy of the residue with offset coordinates
            new_residue = residue.copy()
            for atom in new_residue:
                atom.set_coord(atom.get_coord() + offset)
            new_chain.add(new_residue)
        model.add(new_chain)
    
    # Save to PDB format
    io = PDBIO()
    io.set_structure(new_structure)
    
    with tempfile.NamedTemporaryFile(suffix='.pdb', delete=False) as temp_file:
        io.save(temp_file.name)
        with open(temp_file.name, 'r') as f:
            pdb_content = f.read()
        os.unlink(temp_file.name)
    
    return pdb_content

# Run pipeline button
if st.button("Run Analysis Pipeline"):
    # Clear any previous results
    st.session_state.processed_data = None
    st.session_state.results = None
    
    # Run the pipeline and store results in session state
    with st.spinner("Running analysis pipeline..."):
        results = run_pipeline()
        if results:
            st.session_state.processed_data = results
            st.session_state.report_data = results['report_data']
            st.success("Analysis completed successfully!")

# Display results if available
if st.session_state.processed_data:
    st.header("Analysis Results")
    
    # Show tabs for different result sections
    tabs = st.tabs(["Overview", "Docking Results", "Binding Energies", "Interaction Profiles", "Bispecific Designs"])
    
    with tabs[0]:
        st.subheader("Analysis Overview")
        results = st.session_state.processed_data
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Receptors Analyzed:** {len(results['receptor_data'])}")
            st.write(f"**Antibodies Analyzed:** {len(results['antibody_data'])}")
        
        with col2:
            st.write(f"**Docking Simulations:** {len(results['docking_results'])}")
            st.write(f"**Bispecific Designs:** {len(results['bispecific_designs'])}")
        
        # Show a sample visualization
        if results['receptor_data'] and results['antibody_data']:
            st.subheader("Sample Visualization")
            view = create_visualization(results['receptor_data'][0], results['antibody_data'][0])
            showmol(view, height=400, width=600)
    
    with tabs[1]:
        st.subheader("Molecular Docking Results")
        
        # Create a DataFrame for docking results
        docking_df = pd.DataFrame([
            {
                'Receptor': result['receptor'],
                'Antibody': result['antibody'],
                'Docking Score': result['top_score'],
                'RMSD': result['poses'][0]['rmsd'],
                'Interface Area': result['poses'][0]['interface_area']
            }
            for result in results['docking_results']
        ])
        
        # Show the table
        st.dataframe(docking_df)
        
        # Create a bar chart of docking scores
        st.subheader("Top Docking Scores")
        top_docking = docking_df.sort_values('Docking Score').head(10)
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(x='Docking Score', y='Receptor + Antibody', 
                   data=top_docking.assign(**{'Receptor + Antibody': top_docking['Receptor'] + ' + ' + top_docking['Antibody']}),
                   ax=ax)
        ax.set_title('Top 10 Docking Scores')
        st.pyplot(fig)
    
    with tabs[2]:
        st.subheader("Binding Energy Analysis")
        
        # Create a DataFrame for binding energies
        energy_df = pd.DataFrame([
            {
                'Receptor': energy['receptor'],
                'Antibody': energy['antibody'],
                'Total Energy': energy['total_energy'],
                'vdW': energy['components']['van_der_waals'],
                'Electrostatic': energy['components']['electrostatic'],
                'H-Bond': energy['components']['hydrogen_bonding'],
                'Desolvation': energy['components']['desolvation'],
                'Entropy': energy['components']['entropy']
            }
            for energy in results['binding_energies']
        ])
        
        # Show the table
        st.dataframe(energy_df)
        
        # Create a stacked bar chart of energy components
        st.subheader("Energy Components for Top Complexes")
        top_energy = energy_df.sort_values('Total Energy').head(5)
        
        # Prepare data for stacked bar chart
        energy_components = top_energy[['Receptor', 'Antibody', 'vdW', 'Electrostatic', 'H-Bond', 'Desolvation', 'Entropy']]
        energy_components['Complex'] = energy_components['Receptor'] + ' + ' + energy_components['Antibody']
        
        # Create stacked bar chart
        fig, ax = plt.subplots(figsize=(10, 6))
        energy_components.set_index('Complex')[['vdW', 'Electrostatic', 'H-Bond', 'Desolvation', 'Entropy']].plot(kind='bar', stacked=True, ax=ax)
        ax.set_title('Energy Components of Top 5 Complexes')
        ax.set_ylabel('Energy (kcal/mol)')
        st.pyplot(fig)
    
    with tabs[3]:
        st.subheader("Interaction Profile Analysis")
        
        # Create a DataFrame for interaction profiles
        interaction_df = pd.DataFrame([
            {
                'Receptor': profile['receptor'],
                'Antibody': profile['antibody'],
                'H-Bonds': profile['interaction_counts']['hydrogen_bonds'],
                'Salt Bridges': profile['interaction_counts']['salt_bridges'],
                'Hydrophobic': profile['interaction_counts']['hydrophobic'],
                'Pi-Stacking': profile['interaction_counts']['pi_stacking'],
                'Buried Surface Area': profile['buried_surface_area'],
                'Shape Complementarity': profile['shape_complementarity'],
                'Epitope Type': profile['epitope_classification']
            }
            for profile in results['interaction_profiles']
        ])
        
        # Show the table
        st.dataframe(interaction_df)
        
        # Create a heatmap of CDR involvement for a selected complex
        st.subheader("CDR Involvement Analysis")
        
        # Create complex name list
        complex_names = [f"{profile['receptor']} + {profile['antibody']}" for profile in results['interaction_profiles']]
        selected_complex = st.selectbox("Select Complex", complex_names)
        
        if selected_complex:
            # Find the selected profile
            receptor_name, antibody_name = selected_complex.split(" + ")
            selected_profile = next((p for p in results['interaction_profiles'] 
                                   if p['receptor'] == receptor_name and p['antibody'] == antibody_name), None)
            
            if selected_profile and 'cdr_involvement' in selected_profile:
                # Create heatmap of CDR involvement
                cdr_data = pd.DataFrame([selected_profile['cdr_involvement']])
                
                fig, ax = plt.subplots(figsize=(8, 2))
                sns.heatmap(cdr_data, annot=True, cmap="YlGnBu", cbar=False, ax=ax)
                ax.set_title('CDR Involvement in Receptor Binding')
                st.pyplot(fig)
    
    with tabs[4]:
        st.subheader("Bispecific Antibody Designs")
        
        # Create a DataFrame for bispecific designs
        if results['bispecific_designs']:
            bispecific_df = pd.DataFrame([
                {
                    'Antibody 1': design['antibody1'],
                    'Antibody 2': design['antibody2'],
                    'Target 1': design['receptor1'],
                    'Target 2': design['receptor2'],
                    'Compatibility': design['compatibility'],
                    'Interference': design['interference'],
                    'Combined Score': design['combined_score'],
                    'Format': design['format_suggestions']
                }
                for design in results['bispecific_designs']
            ])
            
            # Show the table
            st.dataframe(bispecific_df)
            
            # Show top recommendations
            st.subheader("Top Bispecific Recommendations")
            
            for i, design in enumerate(results['bispecific_designs'][:3]):
                with st.expander(f"Recommendation {i+1}: {design['antibody1']} + {design['antibody2']}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Format:** {design['format_suggestions']}")
                        st.write(f"**Compatibility Score:** {design['compatibility']:.2f}")
                        st.write(f"**Interference:** {design['interference']:.2f}")
                        st.write(f"**Combined Score:** {design['combined_score']:.2f}")
                    
                    with col2:
                        st.write(f"**Targets:**")
                        st.write(f"- {design['receptor1']} (via {design['antibody1']})")
                        st.write(f"- {design['receptor2']} (via {design['antibody2']})")
                    
                    # Generate PDB file for bispecific
                    if st.button(f"Generate Structure for Design {i+1}"):
                        with st.spinner("Generating bispecific structure..."):
                            pdb_content = generate_bispecific_pdb(design, results['receptor_data'], results['antibody_data'])
                            if pdb_content:
                                # Show visualization
                                view = py3Dmol.view(width=600, height=400)
                                view.addModel(pdb_content, 'pdb')
                                view.setStyle({'chain': 'A1'}, {'cartoon': {'color': 'blue'}})
                                view.setStyle({'chain': 'B1'}, {'cartoon': {'color': 'green'}})
                                view.zoomTo()
                                view.setBackgroundColor('white')
                                showmol(view, height=400, width=600)
                                
                                # Provide download link
                                st.download_button(
                                    label=f"Download PDB for Design {i+1}",
                                    data=pdb_content,
                                    file_name=f"bispecific_{design['antibody1']}_{design['antibody2']}.pdb",
                                    mime="chemical/x-pdb"
                                )
        else:
            st.info("No viable bispecific designs were found.")

    # Generate and download report
    st.header("Generate Report")
    
    if st.button("Generate PDF Report"):
        with st.spinner("Generating PDF report..."):
            pdf_buffer = create_pdf_report(st.session_state.report_data)
            
            # Create download button for PDF
            st.download_button(
                label="Download PDF Report",
                data=pdf_buffer,
                file_name="Bispecific_Antibody_Report.pdf",
                mime="application/pdf"
            )
            
            st.success("PDF report generated successfully!")