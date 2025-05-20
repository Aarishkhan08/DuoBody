# DuoDok - Bispecific Antibody Design Platform

DuoDok is a comprehensive platform for designing and analyzing bispecific antibodies using molecular visualization and computational methods. The platform provides an intuitive interface for protein structure analysis, molecular docking, and bispecific antibody design.

## Features

- **Molecular Visualization**: Interactive 3D visualization of protein structures using py3Dmol
- **Structure Analysis**: Detailed analysis of receptor and antibody structures
- **Molecular Docking**: Simulation of protein-protein interactions
- **Binding Energy Calculation**: Estimation of binding energies and interaction profiles
- **Bispecific Design**: Automated design of bispecific antibodies with compatibility scoring
- **Report Generation**: Comprehensive PDF reports of analysis results

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd DuoDok
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install required packages:
```bash
pip install streamlit biopython pandas numpy matplotlib seaborn py3Dmol stmol reportlab
```

## Usage

1. Start the Streamlit application:
```bash
streamlit run DuoBody/pages/03_DuoBody.py
```

2. Upload PDB files:
   - Upload receptor PDB files
   - Upload antibody PDB files

3. Run the analysis pipeline:
   - Click "Run Analysis Pipeline" to start the analysis
   - View results in the interactive interface
   - Generate and download PDF reports

## Project Structure

```
DuoDok/
├── DuoBody/
│   ├── pages/
│   │   └── 03_DuoBody.py    # Main application file
│   └── ...
└── README.md
```

## Dependencies

- Python 3.x
- Streamlit
- BioPython
- pandas
- numpy
- matplotlib
- seaborn
- py3Dmol
- stmol
- reportlab

## Features in Detail

### Molecular Visualization
- Interactive 3D visualization of protein structures
- Customizable visualization styles
- Support for multiple structure viewing

### Structure Analysis
- Secondary structure analysis
- Chain and residue counting
- Center of mass calculation
- Interface analysis

### Molecular Docking
- Automated docking simulation
- Multiple pose generation
- RMSD calculation
- Interface area estimation

### Binding Energy Analysis
- Van der Waals interactions
- Electrostatic interactions
- Hydrogen bonding
- Desolvation effects
- Entropy calculations

### Bispecific Design
- Compatibility scoring
- CDR usage analysis
- Format suggestions
- Interference prediction

### Report Generation
- Comprehensive PDF reports
- Detailed analysis summaries
- Visualization exports
- Downloadable PDB structures

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License
