from flask import Flask, render_template, request
import fitz  # PyMuPDF
import openai
import re
import os
from dotenv import load_dotenv

app = Flask(__name__)

# ✅ Load environment variables from .env
load_dotenv()

# ✅ Set OpenAI API key securely
openai.api_key = os.getenv("OPENAI_API_KEY")

# ✅ Helper function to extract sections
def extract_section(lines, start_keyword, stop_keywords):
    extracted = []
    started = False
    for line in lines:
        if start_keyword in line.lower():
            started = True
            continue
        if started:
            if any(stop in line.lower() for stop in stop_keywords):
                break
            if line.strip():
                extracted.append(line.strip())
    return extracted

# ✅ Route: Combined Homepage (Phase-6)
@app.route('/')
def home():
    return render_template('dashboard.html')  # new combined UI page

# ✅ Route: Resume Analyzer (Phase-3)
@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['resume']
    text = ""
    if file and file.filename.endswith('.pdf'):
        doc = fitz.open(stream=file.read(), filetype="pdf")
        for page in doc:
            text += page.get_text()

    lines = text.strip().split('\n')
    email_match = re.search(r'[\w\.-]+@[\w\.-]+', text)
    phone_match = re.search(r'\+?\d[\d\s\-]{8,}\d', text)

    name = lines[0] if lines else "Not found"
    email = email_match.group() if email_match else "Not found"
    phone = phone_match.group() if phone_match else "Not found"

    education = extract_section(lines, "education", ["skills", "projects", "experience", "certifications"])
    skills = extract_section(lines, "skills", ["projects", "experience", "certifications", "summary"])

    prompt = f"""
    Analyze the following resume and provide:
    1. Strengths of the candidate
    2. Areas of improvement
    3. Suitable job roles
    4. Skills to learn for better job prospects

    Resume:
    {text}
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional career counselor."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=700,
            temperature=0.7
        )
        ai_feedback = response.choices[0].message['content'].strip()
    except Exception as e:
        ai_feedback = f"Error analyzing resume: {e}"

    return render_template(
        'summary.html',
        name=name,
        email=email,
        phone=phone,
        education=education,
        skills=skills,
        text=text,
        ai_feedback=ai_feedback
    )

# ✅ Route: Job Matcher (Phase-5)
@app.route('/match', methods=['POST'])
def match():
    file = request.files['resume']
    job_desc = request.form['job_description']
    text = ""

    if file and file.filename.endswith('.pdf'):
        doc = fitz.open(stream=file.read(), filetype="pdf")
        for page in doc:
            text += page.get_text()

    prompt = f"""
You are a resume reviewer. Compare the resume below with the job description and give:

1. ✅ Match Score (0-100)
2. 🔍 Missing Keywords from resume
3. 💡 Suggestions to improve match

Resume:
{text}

Job Description:
{job_desc}
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert resume-job matcher."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=700,
            temperature=0.7
        )
        match_feedback = response.choices[0].message['content'].strip()
    except Exception as e:
        match_feedback = f"Error matching resume: {e}"

    return render_template('match_summary.html', feedback=match_feedback)
# ✅ Route: Resume Rebuilder Form (Phase-7)
@app.route('/generate-resume')
def generate_resume_form():
    return render_template('generate_resume.html')

# ✅ Route: Handle Resume Rebuilding (Phase-7)
@app.route('/generate-resume', methods=['POST'])
def generate_resume():
    file = request.files['resume']
    resume_text = ""

    if file and file.filename.endswith('.pdf'):
        doc = fitz.open(stream=file.read(), filetype="pdf")
        for page in doc:
            resume_text += page.get_text()

    prompt = f"""
You're an expert resume writer. Rewrite the following resume in a professional, clean format suitable for modern ATS systems. Use strong action verbs, bullet points, clear section headers, and optimize it for readability.

Resume Text:
{resume_text}
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional resume writer."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        generated_resume = response.choices[0].message['content'].strip()
    except Exception as e:
        generated_resume = f"Error generating resume: {e}"
    # NEW fixed line
    return render_template('generated_result.html', ai_resume=generated_resume)


# ✅ Run the app
if __name__ == '__main__':
    app.run(debug=True)
