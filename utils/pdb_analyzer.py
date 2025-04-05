import Bio.PDB
import streamlit as st
import os
import tempfile
from io import StringIO
import pandas as pd
import numpy as np
from config import ALLOWED_EXTENSIONS, MAX_FILE_SIZE

# Initialize the analyzer as a global object
_analyzer = None


def get_analyzer():
    """Get or create a PDBAnalyzer instance"""
    global _analyzer
    if _analyzer is None:
        _analyzer = PDBAnalyzer()
    return _analyzer


def validate_pdb_file(file):
    """Wrapper function to validate a PDB file"""
    analyzer = get_analyzer()
    is_valid, _ = analyzer.validate_file(file)
    return is_valid


def analyze_pdb_structure(file):
    """Wrapper function to analyze a PDB file"""
    analyzer = get_analyzer()
    try:
        # Save the file position and reset it after reading
        pos = file.tell()
        file.seek(0)

        # Run the analysis
        result = analyzer.analyze_structure(file)

        # Add filename to results
        result['filename'] = file.name

        # Reset file position
        file.seek(pos)

        return result
    except Exception as e:
        st.error(f"Error analyzing PDB file: {str(e)}")
        return None


def compare_pdb_structures(file1, file2):
    """Wrapper function to compare two PDB files"""
    analyzer = get_analyzer()
    try:
        # Save the file positions and reset them after reading
        pos1, pos2 = file1.tell(), file2.tell()
        file1.seek(0)
        file2.seek(0)

        # Run the comparison
        result = analyzer.compare_structures(file1, file2)

        # Add filenames to results
        result['filenames'] = [file1.name, file2.name]

        # Reset file positions
        file1.seek(pos1)
        file2.seek(pos2)

        return result
    except Exception as e:
        st.error(f"Error comparing PDB files: {str(e)}")
        return None


class PDBAnalyzer:
    """Class for analyzing PDB files"""

    def __init__(self):
        self.parser = Bio.PDB.PDBParser(QUIET=True)

    def validate_file(self, file):
        """Validate that the file is a PDB file"""
        # Check file extension
        _, file_extension = os.path.splitext(file.name)
        if file_extension.lower() not in ALLOWED_EXTENSIONS:
            return False, f"Invalid file format. Only PDB files ({', '.join(ALLOWED_EXTENSIONS)}) are allowed."

        # Check file size
        if file.size > MAX_FILE_SIZE:
            return False, f"File size exceeds the maximum allowed size ({MAX_FILE_SIZE / (1024 * 1024):.1f} MB)."

        # Try to parse the file to ensure it's a valid PDB file
        temp_file_path = None
        try:
            # Create a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdb") as temp_file:
                temp_file.write(file.getbuffer())
                temp_file_path = temp_file.name

            # Parse the PDB file
            self.parser.get_structure("temp", temp_file_path)

            # Clean up
            if temp_file_path and os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

            return True, "File is valid."
        except Exception as e:
            # Clean up
            if temp_file_path and os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

            return False, f"Invalid PDB file: {str(e)}"

    def analyze_structure(self, file):
        """Analyze the structure of a PDB file"""
        temp_file_path = None
        try:
            # Create a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdb") as temp_file:
                temp_file.write(file.getbuffer())
                temp_file_path = temp_file.name

            # Parse the PDB file
            structure = self.parser.get_structure("structure", temp_file_path)

            # Get structure information
            info = {
                "structure_id": structure.id,
                "number_of_models": len(structure),
                "chains": {},
                "residue_count": 0,
                "atom_count": 0,
                "residue_types": set(),
                "bond_lengths": []
            }

            # Process models, chains, residues, and atoms
            for model in structure:
                for chain in model:
                    chain_id = chain.id
                    info["chains"][chain_id] = {
                        "residue_count": 0,
                        "atom_count": 0
                    }

                    for residue in chain:
                        if Bio.PDB.is_aa(residue):
                            info["residue_types"].add(residue.get_resname())

                        info["residue_count"] += 1
                        info["chains"][chain_id]["residue_count"] += 1

                        for atom in residue:
                            info["atom_count"] += 1
                            info["chains"][chain_id]["atom_count"] += 1

            # Calculate bond lengths for the first model
            if len(structure) > 0:
                model = structure[0]
                for chain in model:
                    for residue in chain:
                        atoms = list(residue.get_atoms())
                        for i in range(len(atoms)):
                            for j in range(i + 1, len(atoms)):
                                atom1 = atoms[i]
                                atom2 = atoms[j]
                                # Calculate distance between atoms
                                distance = atom1 - atom2
                                info["bond_lengths"].append({
                                    "atom1": atom1.get_name(),
                                    "atom2": atom2.get_name(),
                                    "residue": residue.get_resname(),
                                    "chain": chain.id,
                                    "distance": distance
                                })

            # Clean up
            if temp_file_path and os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

            return info
        except Exception as e:
            # Clean up
            if temp_file_path and os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

            raise Exception(f"Error analyzing PDB file: {str(e)}")

    def compare_structures(self, file1, file2):
        """Compare two PDB structures"""
        # Analyze both structures
        info1 = self.analyze_structure(file1)
        info2 = self.analyze_structure(file2)

        # Compare basic statistics
        comparison = {
            "structure1_id": info1["structure_id"],
            "structure2_id": info2["structure_id"],
            "model_count_diff": info1["number_of_models"] - info2["number_of_models"],
            "residue_count_diff": info1["residue_count"] - info2["residue_count"],
            "atom_count_diff": info1["atom_count"] - info2["atom_count"],
            "common_chains": set(info1["chains"].keys()).intersection(set(info2["chains"].keys())),
            "unique_chains_1": set(info1["chains"].keys()) - set(info2["chains"].keys()),
            "unique_chains_2": set(info2["chains"].keys()) - set(info1["chains"].keys()),
            "common_residue_types": info1["residue_types"].intersection(info2["residue_types"]),
            "unique_residue_types_1": info1["residue_types"] - info2["residue_types"],
            "unique_residue_types_2": info2["residue_types"] - info1["residue_types"]
        }

        # For common chains, compare residue and atom counts
        chain_comparison = {}
        for chain_id in comparison["common_chains"]:
            chain_comparison[chain_id] = {
                "residue_count_diff": info1["chains"][chain_id]["residue_count"] - info2["chains"][chain_id][
                    "residue_count"],
                "atom_count_diff": info1["chains"][chain_id]["atom_count"] - info2["chains"][chain_id]["atom_count"]
            }

        comparison["chain_comparison"] = chain_comparison

        return comparison

    def generate_report(self, comparison):
        """Generate a report from the comparison results"""
        report = f"""
        # PDB Structure Comparison Report

        ## Basic Information
        - Structure 1 ID: {comparison['structure1_id']}
        - Structure 2 ID: {comparison['structure2_id']}

        ## Structure Differences
        - Model Count Difference: {comparison['model_count_diff']}
        - Residue Count Difference: {comparison['residue_count_diff']}
        - Atom Count Difference: {comparison['atom_count_diff']}

        ## Chain Analysis
        - Common Chains: {', '.join(comparison['common_chains']) if comparison['common_chains'] else 'None'}
        - Unique Chains in Structure 1: {', '.join(comparison['unique_chains_1']) if comparison['unique_chains_1'] else 'None'}
        - Unique Chains in Structure 2: {', '.join(comparison['unique_chains_2']) if comparison['unique_chains_2'] else 'None'}

        ## Residue Type Analysis
        - Unique Residue Types in Structure 1: {', '.join(comparison['unique_residue_types_1']) if comparison['unique_residue_types_1'] else 'None'}
        - Unique Residue Types in Structure 2: {', '.join(comparison['unique_residue_types_2']) if comparison['unique_residue_types_2'] else 'None'}

        ## Chain Comparison
        """

        for chain_id, chain_data in comparison["chain_comparison"].items():
            report += f"""
        ### Chain {chain_id}
        - Residue Count Difference: {chain_data['residue_count_diff']}
        - Atom Count Difference: {chain_data['atom_count_diff']}
            """

        return report
