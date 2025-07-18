WellnessWise is a smart, web-based medical decision support system that predicts possible diseases based on user symptoms and personal health factors like age, gender, and pregnancy status. Built using machine learning, it also provides treatment protocols, comorbidity insights, and lifestyle recommendations—making it a powerful tool for both education and early self-assessment.

> ⚠️ Disclaimer: This tool is for *educational and informational* purposes only and is *not a substitute for professional medical advice, diagnosis, or treatment*.

---

## 📋 Features

- 🔎 *Symptom Checker:* Predict likely diseases by entering symptoms in natural language or as selections.
- 📊 *Smart Filtering:* Get personalized results based on *age, **gender, and **pregnancy status*.
- 📈 *Detailed Disease Profiles:* View treatments, medications, comorbidities, precautions, and safety information.
- 🏃‍♀️ *Lifestyle Recommendations:* Tailored *diet* and *workout* suggestions for each disease.
- 🏷 *Category Browsing:* Explore diseases grouped by type or system (e.g., respiratory, cardiovascular).
- 🔐 *User Authentication:* Simple *signup/login* system with Flask and SQLite for data security.
- 🎨 *Responsive UI:* Clean, user-friendly interface for desktop and mobile.

---

## 🛠️ Tech Stack

- *Backend:* Python, Flask  
- *Machine Learning:* Scikit-learn, Pandas, NumPy  
- *Models:*  
  - *TF-IDF + Cosine Similarity* for symptom mapping  
  - *Multinomial Naive Bayes* for disease prediction  
- *Frontend:* HTML, CSS, Jinja2 Templates  
- *Database:* SQLite + SQLAlchemy  
- *Data:* augmented_diseases_extended.csv – A curated dataset with symptoms, diseases, treatments, comorbidities, and more

---

## 📁 Project Structure


WellnessWise/
├── app.py                        # Main Flask application
├── model.py                      # Core ML logic and symptom matching
├── models.py                     # (Optional) Extended models or helper classes
├── Models.ipynb                  # Jupyter notebook for training and testing
├── augmented_diseases_extended.csv # Main dataset
├── templates/                    # HTML templates (Jinja2)
├── static/                       # Static files (CSS, JS, images)
├── Model Details/                # Documentation and model explanations
├── requirements.txt              # Python dependencies
└── README.md                     # Project documentation


---

## 🚀 Setup Instructions

1. *Clone the repository:*
   bash
   git clone <repo-url>
   cd WellnessWise
   

2. *Install dependencies:*
   bash
   pip install -r requirements.txt
   
   If requirements.txt is missing, manually install:
   bash
   pip install flask pandas scikit-learn numpy
   

3. *Ensure dataset is available:*
   - File: augmented_diseases_extended.csv should be in the project root.

4. *Run the application:*
   bash
   python app.py
   

   (Alternatively, use Models.ipynb for interactive exploration in Jupyter Notebook.)

---

## 🧪 Usage Guide

1. Launch the web application (localhost:5000 by default).
2. Select your symptoms  from dropdowns.
3. Input age, gender, and pregnancy status.
4. View:
   - Predicted diseases with similarity scores
   - Disease-specific precautions and comorbidities
   - Personalized treatment and lifestyle suggestions

---

## 👨‍💻 Authors

- *Mahipal Chauhan*
- *Dhruv Jani*  
BTech CSE Students, Batch 2022–2026

---

## 📜 License & Copyright


© 2025 Dhruv Jani and Mahipal Chauhan  
All rights reserved.  
Unauthorized use, reproduction, or distribution is strictly prohibited.
