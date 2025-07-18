from flask import Flask, render_template, request
import re
import fitz  # PyMuPDF

app = Flask(__name__)

def extract_text_from_pdf(path):
    doc = fitz.open(path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def extract_email(text):
    match = re.search(r'[\w\.-]+@[\w\.-]+', text)
    return match.group(0) if match else "Not found"

def extract_phone(text):
    match = re.search(r'(\+91[\-\s]?)?[789]\d{9}', text)
    return match.group(0) if match else "Not found"

def extract_name(text):
    lines = text.split('\n')
    for line in lines:
        if line.strip() and len(line.strip().split()) <= 4:
            return line.strip()
    return "Not found"

def extract_education(text):
    edu_keywords = ["B.Tech", "Bachelor", "Master", "Degree", "Graduation", "Engineering"]
    education = []
    lines = text.split('\n')
    for line in lines:
        for keyword in edu_keywords:
            if keyword.lower() in line.lower():
                education.append(line.strip())
    return education if education else ["Not found"]

def extract_skills(text):
    skills_keywords = ["Python", "Java", "HTML", "CSS", "JavaScript", "SQL", "C++", "React", "Node.js"]
    found_skills = [skill for skill in skills_keywords if skill.lower() in text.lower()]
    return found_skills if found_skills else ["Not found"]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    resume = request.files['resume']
    resume_path = "uploaded_resume.pdf"
    resume.save(resume_path)

    text = extract_text_from_pdf(resume_path)
    email = extract_email(text)
    phone = extract_phone(text)
    name = extract_name(text)
    education = extract_education(text)
    skills = extract_skills(text)

    return render_template(
        'summary.html',
        text=text,
        email=email,
        phone=phone,
        name=name,
        education=education,
        skills=skills
    )

if __name__ == '__main__':
    app.run(debug=True)
