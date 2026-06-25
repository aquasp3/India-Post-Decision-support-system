![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-App-red?logo=streamlit)
![License](https://img.shields.io/badge/License-Educational-green)

# 🇮🇳 India Post Decision Support System (IPDSS)

> Transforming Village Data into Actionable Rural Outreach Intelligence

A comprehensive **Decision Support System (DSS)** built for **India Post** to assist postal officers in identifying suitable government schemes, prioritizing outreach campaigns, and generating structured annual campaign plans using demographic and environmental village data.

> 🎓 Capstone Project | Inspired by a Smart India Hackathon (SIH) Problem Statement

---

## 📌 Overview

The India Post Decision Support System (IPDSS) is an intelligent platform designed to help regional postal officers make **data-driven rural outreach decisions**.

Instead of manually analyzing demographic datasets and selecting welfare schemes, officers can upload village data and receive:

- Intelligent scheme recommendations
- Priority classification
- Village insights
- Annual campaign planning
- Government-ready reports

The system is designed to work **offline**, making it suitable for deployment in regions with limited internet connectivity.

---

## ✨ Features

### 📂 Regional Data Upload
- Upload village demographic datasets
- Optional environmental datasets
- CSV validation
- Automatic preprocessing

### ✅ Data Validation Engine
- Missing value detection
- Schema validation
- Data normalization
- Error reporting

### 🏘 Village Intelligence
- Demographic analysis
- Population insights
- Risk identification
- Community profiling

### 🎯 Scheme Recommendation Engine
- Intelligent matching of villages with government schemes
- Priority-based recommendations
- Confidence scoring

### 📅 Campaign Planning
Generate structured 12-month outreach plans including:

- Awareness campaigns
- Seasonal planning
- Target groups
- Recommended timelines

### 🌐 Localization
Supports multiple languages:

- English
- Hindi
- Telugu
- Tamil
- Kannada

### 📄 Report Generation
Export recommendations and planning reports for government use.

---

# 🏗 System Workflow

```text
Village CSV Upload
        │
        ▼
Validation Engine
        │
        ▼
Data Cleaning
        │
        ▼
Village Analysis
        │
        ▼
Scheme Recommendation
        │
        ▼
Priority Classification
        │
        ▼
Campaign Planning
        │
        ▼
Report Generation
```

---

# 🛠 Tech Stack

| Category | Technology |
|----------|------------|
| Language | Python |
| Framework | Streamlit |
| Data Processing | Pandas, NumPy |
| Visualization | Plotly |
| File Handling | CSV |
| Export | PDF, Excel |
| UI | Streamlit Custom Components |

---

# 📁 Project Structure

```
IndiaPostDSS/
│
├── app.py
├── pages/
│
├── recommendation_engine.py
├── planning_generator.py
├── validator.py
├── preprocessing.py
├── anomaly_detector.py
├── export_service.py
│
├── datasets/
│
├── assets/
│
├── requirements.txt
└── README.md
```

---

# 🚀 Getting Started

## Clone Repository

```bash
git clone https://github.com/yourusername/IndiaPostDSS.git

cd IndiaPostDSS
```

---

## Create Virtual Environment

```bash
python -m venv venv
```

Activate

Windows

```bash
venv\Scripts\activate
```

Linux/Mac

```bash
source venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Run

```bash
streamlit run app.py
```

---

# 📷 Screenshots

### Dashboard


---

### Upload & Validation

(Add Screenshot)

---

### Scheme Recommendation

(Add Screenshot)

---

### Campaign Planning

(Add Screenshot)

---

# 🎯 Key Highlights

- Offline-first architecture
- Modular design
- Data validation pipeline
- Rule-based recommendation engine
- Campaign planning generator
- Government-inspired UI
- Multilingual support

---

# 📚 What I Learned

This project helped me understand that building reliable software goes beyond writing algorithms.

Some key learnings include:

- Data validation is the foundation of intelligent systems.
- Simple architectures are often more reliable than complex ones.
- Building for real users requires thoughtful UX and predictable workflows.
- Engineering is about solving practical problems, not just implementing features.

---

# 🔮 Future Improvements

- Cloud deployment
- GIS map integration
- ML-based recommendation engine
- Admin dashboard
- Authentication
- Real-time analytics
- Database integration
- Mobile application

---

# 🤝 Contributing

Contributions, suggestions, and feedback are welcome.

Feel free to open an issue or submit a pull request.

---

# 📄 License

This project was developed for educational and demonstration purposes.

---

# 👨‍💻 Author

**Sathvik Konduri**

B.Tech Computer Science (AI & ML)

Methodist College of Engineering & Technology

📧 Email: sathvikkonduri2@gmail.com

💼 LinkedIn: https://www.linkedin.com/in/sathvik-konduri/

🌐 Portfolio: https://sathvikkonduri.vercel.app/

📝 Medium: https://medium.com/@sathvikkonduri14

⭐ If you found this project interesting, consider giving it a star!
