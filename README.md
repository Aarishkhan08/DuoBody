
**DuoDok**

![Blue White Modern and Professional Technology Company Logo](https://github.com/user-attachments/assets/3182c8a3-3d05-4d05-bc87-f50fe7bfbee5)

# 🔬 Receptor-Antibody Docking Analysis  

This repository provides a **Streamlit-based web application** for analyzing docking interactions between receptor and antibody molecules. The application leverages **HDOCK, PRODIGY, and CREATEPL** to predict binding affinities, dissociation constants, and contact points between molecular structures.  

---

## ✨ Features  

✅ **Upload PDB files** for receptor and antibody molecules.  
✅ **Automated docking simulations** using **HDOCK**.  
✅ **Complex generation** with **CREATEPL**.  
✅ **Predict binding affinities** and **dissociation constants** using **PRODIGY**.  
✅ **Interactive visualizations** – heatmaps & distribution charts.  
✅ **Download analysis results** as a CSV file.  

---

## 🚀 Installation  

### 1️⃣ Clone the Repository  
```bash
git clone https://github.com/Aarishkhan08/DuoBody/
cd DuoDok
```
###2️⃣ Install Required Dependencies
```bash
pip install streamlit pandas smtplib itertools shutil re base64 plip
```
3️⃣ Ensure Required Tools are Installed
Make sure the following tools are installed and accessible from the command line:

HDOCK
CREATEPL (included in the HDOCK package)
PRODIGY
###▶️ Usage
Start the Streamlit app:

```bash
streamlit run app.py
```
###📌 Requirements
Python 3.8+
Streamlit
pandas
Biopython
HDOCK, CREATEPL, PRODIGY (installed separately)

###🛠 Troubleshooting
If you encounter issues:
✅ Ensure all dependencies & tools are correctly installed.
✅ Verify that uploaded PDB files are properly formatted.
✅ Check file paths & permissions for temp/ and results/ directories.

###🤝 Contributing
Contributions are welcome! Feel free to:

Submit Issues for bugs & feature requests.
Create Pull Requests to improve the repository.
Suggest Enhancements via discussions.

###📜 License
This project is licensed under the MIT License. See the LICENSE file for details.

