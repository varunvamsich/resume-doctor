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

# ✅ Route: Homepage
@app.route('/')
def index():
    return render_template('index.html')

# ✅ Route: Handle Resume Upload
@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['resume']

    # ✅ Extract text from PDF
    text = ""
    if file.filename.endswith('.pdf'):
        doc = fitz.open(stream=file.read(), filetype="pdf")
        for page in doc:
            text += page.get_text()

    lines = text.strip().split('\n')

    # ✅ Extract Basic Info
    email_match = re.search(r'[\w\.-]+@[\w\.-]+', text)
    phone_match = re.search(r'\+?\d[\d\s\-]{8,}\d', text)

    name = lines[0] if lines else "Not found"
    email = email_match.group() if email_match else "Not found"
    phone = phone_match.group() if phone_match else "Not found"

    # ✅ Extract Education & Skills Sections
    education = extract_section(lines, "education", ["skills", "projects", "experience", "certifications"])
    skills = extract_section(lines, "skills", ["projects", "experience", "certifications", "summary"])

    # ✅ Prepare Prompt for AI
    prompt = f"""
    Analyze the following resume and provide:
    1. Strengths of the candidate
    2. Areas of improvement
    3. Suitable job roles
    4. Skills to learn for better job prospects

    Resume:
    {text}
    """

    # ✅ Generate AI Feedback
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

    # ✅ Render Summary Page
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

if __name__ == '__main__':
    app.run(debug=True)
