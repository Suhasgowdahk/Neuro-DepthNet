# 🧠 NEURODEPTHNET PROJECT

## 🧩 Overview
**NeuroDepthNet** is an advanced AI-based system designed to **classify brain tumor types** and **estimate tumor depth** using **3D reconstruction** techniques.  
This project combines deep learning, medical imaging, and visualization technologies to assist in better tumor analysis and diagnosis.

---

## ⚙️ Technologies Used

| Technology | Purpose |
|-------------|----------|
| 🧠 **CNN (Convolutional Neural Network)** | For brain tumor detection and classification |
| 🧭 **SimpleITK** | For spatial image recognition and medical image processing |
| 🧱 **VTK (Visualization Toolkit)** | For 3D reconstruction and visualization of tumor depth |

---

## 🛠️ Prerequisites

Before running the project, make sure you have installed:

- **Python 3.8+**
- **Node.js and npm**
- **VS Code or any preferred IDE**

---

## 🚀 How to Run the Project

### 🧩 Step 1 — Extract Files
- Download and **extract the project zip file**.

---

### 🧠 Step 2 — Open the Project
- Open the **project folder** in **VS Code**.

---

### ⚙️ Step 3 — Set Up Backend (Python)

1. Open a new terminal and run the following commands:

   ```bash
   cd backend
   python -m venv venv
   venv/Scripts/Activate
   pip install -r requirements.txt
   python main.py
✅ This will start the backend server.

### 💻 Step 4 — Set Up Frontend (React)

Open another terminal and run:

cd frontend
npm install
npm start

✅ This will launch the frontend React app in your browser.

### 🧬 Project Workflow

Upload MRI/CT brain images.

The system uses CNN to classify the tumor type.

SimpleITK processes spatial image data.

VTK generates a 3D reconstructed model to estimate tumor depth.

### 📸 Output

Tumor Type (e.g., Meningioma, Glioma, Pituitary)

3D Reconstruction Model with Depth Estimation

Visual and Statistical Analysis Reports

### 🧠 Key Features

✅ Brain tumor classification using Deep Learning

✅ Depth estimation with 3D reconstruction

✅ Interactive and user-friendly UI

✅ Modular design with separate backend and frontend

🧑‍💻 Developed By
Team NeuroDepthNet
👤 Suhas H K
📧 suhashk778@gmail.com

📜 License
This project is open-source and distributed under the MIT License.

🌟 Future Enhancements
]
Integration with DICOM file support

Real-time MRI visualization

Cloud-based tumor analysis API

Improved model accuracy with additional datasets
