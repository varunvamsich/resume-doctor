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


## 🔥 Phase-3: AI Feedback Integration using OpenAI

In this phase, we added powerful AI features to our Resume Doctor project using **OpenAI GPT-4**. Now, after a resume is uploaded, the system performs:

- ✅ Extraction of name, email, phone, education, and skills
- ✅ Full resume text extraction using PyMuPDF
- ✅ Real-time AI feedback with GPT-4:
  - Strengths of the candidate
  - Areas of improvement
  - Suitable job roles
  - Recommended skills to learn

### 🔐 API Key Protection

To keep the API key secure and production-ready:
- The key is stored in a `.env` file (not in the code)
- `python-dotenv` is used to load the `.env` file
- `.env` is added to `.gitignore` so it's never pushed to GitHub

# 🧠 Resume Doctor – AI-Powered Resume Analyzer

Resume Doctor is a web app that allows users to upload a resume (PDF) and receive smart AI feedback using OpenAI GPT-4.

---

## ✅ Live Project

🌐 [Live Demo – Resume Doctor](https://resume-doctor.onrender.com)

---

## ⚙️ Features

- Upload resume as PDF
- Extracts: Name, Email, Phone, Education, Skills
- AI Feedback includes:
  - ✅ Strengths
  - 🛠 Areas of Improvement
  - 🎯 Suitable Job Roles
  - 📚 Skills to Learn
- GPT-4 powered analysis
- .env file for secure API key handling
- Hosted using Render.com
- UptimeRobot keeps app always alive

---

## 🚀 Technologies Used

- **Frontend:** HTML, CSS (Jinja2 Templates)
- **Backend:** Flask (Python)
- **AI Engine:** OpenAI GPT-4
- **PDF Parsing:** PyMuPDF (`fitz`)
- **Deployment:** Render (Free Tier)
- **Monitoring:** UptimeRobot

---

## 🧾 Deployment Steps (Phase-4 Completed)

1. Created `requirements.txt` using:  
   `pip freeze > requirements.txt`

2. Installed Gunicorn and added to requirements:  
   `pip install gunicorn`

3. Created `Procfile` with:  
   `web: gunicorn app:app`

4. Used `.env` file to securely store OpenAI API key  
   and added `.env` to `.gitignore`

5. Deployed on Render.com:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`

6. Added Environment Variable on Render:  
   `OPENAI_API_KEY=your_openai_api_key_here`

7. Setup UptimeRobot to ping every 5 mins  
   ✅ Keeps the app awake 24/7

---

## 🧪 Run Locally
---

## 📸 Screenshots

### 🔹 Upload Page
![Upload Page](screenshots/upload_page.png)

### 🔹 Summary Output
![Summary Output](screenshots/summary_output.png)


```bash
git clone https://github.com/CH-Varun-Vamsi/resume-doctor.git
cd resume-doctor
pip install -r requirements.txt
# Add your OpenAI key to .env
echo "OPENAI_API_KEY=your_openai_api_key" > .env
python app.py
