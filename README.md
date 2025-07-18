# 🧠 Resume Doctor

A **Flask-based Resume Upload Web App**  
This project allows users to upload their resumes securely and prepares the backend system for future AI analysis (skill extraction, scoring, suggestions, etc.).

## ✅ Phase 1 Features:
- Resume Upload Form
- File Upload Handling
- Dark-themed UI
- Flask Backend Setup

---

## 🛠️ Tech Used
- HTML, CSS
- Python (Flask)
- JavaScript (in future phase)


---

## 🚀 Phase 2 – Resume Text Extraction + Email & Phone Detection

### 🔧 Features Implemented:
- Extracts full resume text using `PyMuPDF`
- Automatically detects and displays:
  - 📧 Email address
  - 📞 Phone number
- Clean and scrollable resume preview
- Beautiful UI using custom CSS inside `summary.html`

### 🖥️ How It Works:
- Upload any `.pdf` resume
- The app extracts and displays:
  - Email
  - Phone
  - Full resume text

### 📁 Files Added / Modified:
- `app.py` – Added PyMuPDF logic, email & phone extract
- `summary.html` – Output UI for resume details

---

✅ Phase-2 makes our app smarter and user-friendly.  
Get ready for Phase-2.5 where we extract **Name, Education, and Skills**!




### ✅ Phase-2.5: Smart Resume Data Extraction

In this phase, we added real-time extraction of:

- 📛 Name
- 📧 Email
- 📞 Phone Number
- 🎓 Education Details
- 🛠️ Skills
- 📃 Full Resume Text

🧠 Built using PyMuPDF, Regular Expressions, and Flask.

💡 Outputs cleanly rendered on a summary page after resume upload.
