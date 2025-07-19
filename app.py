from flask import Flask, render_template, request, send_file, make_response
import fitz  # PyMuPDF
import openai
import re
import os
from dotenv import load_dotenv
from xhtml2pdf import pisa
from io import BytesIO

app = Flask(__name__)

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Helper function to extract sections
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

# ---------- ATS Optimization Functions ----------
def clean_html(html):
    """Remove unwanted tags/attributes while preserving essential formatting"""
    allowed_tags = ['h1', 'h2', 'h3', 'p', 'ul', 'li', 'strong', 'a']
    for tag in re.findall(r'<(/?\w+)', html):
        if tag.strip('/') not in allowed_tags:
            html = re.sub(fr'<{tag}[^>]*>', '', html)
    # Remove empty paragraphs
    html = re.sub(r'<p>\s*</p>', '', html)
    # Normalize whitespace
    html = re.sub(r'\s+', ' ', html).strip()
    return html

def validate_ats_structure(html):
    """Check for required sections"""
    required_sections = [
        "Professional Summary",
        "Technical Skills",
        "Work Experience",
        "Education"
    ]
    missing = []
    for section in required_sections:
        if f"<h2>{section}</h2>" not in html:
            missing.append(section)
    return missing

def enforce_ats_formatting(html):
    """Standardize resume formatting"""
    # Fix dates
    html = re.sub(r"(\d{4})\s*-\s*(\d{4}|Present)", r"\1–\2", html)
    # Capitalize bullet points
    html = re.sub(r"<li>\s*([a-z])", lambda m: f"<li>{m.group(1).upper()}", html)
    return html

# ---------- Routes ----------
@app.route('/')
def home():
    return render_template('dashboard.html')

@app.route('/upload', methods=['POST'])
def upload():
    """Resume Analyzer"""
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
    Analyze this resume and provide:
    1. Key strengths
    2. Improvement areas
    3. Suggested job roles
    4. Skills to develop

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
            max_tokens=700
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

@app.route('/match', methods=['POST'])
def match():
    """Job Matcher"""
    file = request.files['resume']
    job_desc = request.form['job_description']
    text = ""

    if file and file.filename.endswith('.pdf'):
        doc = fitz.open(stream=file.read(), filetype="pdf")
        for page in doc:
            text += page.get_text()

    prompt = f"""
    Compare this resume with the job description:

    Resume:
    {text}

    Job Description:
    {job_desc}

    Provide:
    1. Match score (0-100)
    2. Missing keywords
    3. Improvement suggestions
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert resume-job matcher."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=700
        )
        match_feedback = response.choices[0].message['content'].strip()
    except Exception as e:
        match_feedback = f"Error matching resume: {e}"

    return render_template('match_summary.html', feedback=match_feedback)

@app.route('/generate-resume')
def generate_resume_form():
    return render_template('generate_resume.html')

@app.route('/generate-resume', methods=['POST'])
def generate_resume():
    """ATS-Optimized Resume Generator"""
    file = request.files['resume']
    resume_text = ""

    if file and file.filename.endswith('.pdf'):
        doc = fitz.open(stream=file.read(), filetype="pdf")
        for page in doc:
            resume_text += page.get_text()

    prompt = f"""
    Create an ATS-optimized resume (90+ score) using this template:

    <h1>Full Name</h1>
    <p class="contact-info">Phone | Email | Location | LinkedIn | GitHub</p>

    <h2>Professional Summary</h2>
    <p>3-5 sentence summary highlighting key skills</p>

    <h2>Technical Skills</h2>
    <ul>
      <li><strong>Languages:</strong> Python, Java</li>
      <li><strong>Tools:</strong> Git, AWS</li>
    </ul>

    <h2>Work Experience</h2>
    <h3>Job Title | Company</h3>
    <p>Month YYYY–Month YYYY</p>
    <ul>
      <li>Action verb + quantified achievement (e.g., "Increased X by 40%")</li>
    </ul>

    <h2>Education</h2>
    <h3>Degree, University</h3>
    <p>YYYY–YYYY | GPA/Percentage</p>

    Rules:
    1. Use ONLY these HTML tags: h1, h2, h3, p, ul, li, strong
    2. Never invent information
    3. Quantify achievements
    4. Standardize dates as "Month YYYY–Month YYYY"

    Resume Data:
    {resume_text}
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an ATS resume expert. Use only verified information."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2000
        )
        generated_resume = response.choices[0].message['content']
        generated_resume = clean_html(generated_resume)
        generated_resume = enforce_ats_formatting(generated_resume)
        
        # Validate structure
        missing_sections = validate_ats_structure(generated_resume)
        if missing_sections:
            generated_resume += f"\n<!-- Missing sections: {', '.join(missing_sections)} -->"

    except Exception as e:
        generated_resume = f"<h1>Error</h1><p>{str(e)}</p>"

    return render_template('generated_result.html', ai_resume=generated_resume)

@app.route('/download-resume', methods=['POST'])
def download_resume():
    """Generate PDF with perfect ATS formatting"""
    try:
        raw_html = request.form['resume_html']
        
        # Clean HTML before PDF conversion
        cleaned_html = re.sub(r'<\!\-\-.*?\-\->', '', raw_html)  # Remove comments
        cleaned_html = re.sub(r'\s+', ' ', cleaned_html).strip()  # Normalize whitespace

        full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="description" content="ATS-optimized resume">
    <title>Professional Resume</title>
    <style>
        /* ATS-optimized styling */
        body {{
            font-family: Arial, sans-serif;
            font-size: 11pt;
            line-height: 1.5;
            margin: 0.75in;
            color: #000;
            -webkit-print-color-adjust: exact;
            print-color-adjust: exact;
        }}
        h1 {{
            font-size: 18pt;
            margin: 0 0 10px 0;
            text-align: center;
            color: #2c3e50;
        }}
        h2 {{
            font-size: 14pt;
            border-bottom: 1px solid #2c3e50;
            margin: 18pt 0 6pt 0;
            padding-bottom: 3px;
            color: #2c3e50;
            page-break-after: avoid;
        }}
        h3 {{
            font-size: 12pt;
            margin: 12pt 0 4pt 0;
            page-break-after: avoid;
        }}
        ul {{
            margin: 6pt 0;
            padding-left: 20px;
        }}
        li {{
            margin-bottom: 4pt;
            page-break-inside: avoid;
        }}
        p {{
            margin: 4pt 0;
        }}
        .contact-info {{
            text-align: center;
            margin-bottom: 12pt;
        }}
        @media print {{
            body {{
                margin: 0.5in;
            }}
            a {{
                text-decoration: none;
                color: #000;
            }}
        }}
    </style>
</head>
<body>
    {cleaned_html}
</body>
</html>"""

        result = BytesIO()
        pisa_status = pisa.CreatePDF(
            full_html,
            dest=result,
            encoding='UTF-8',
            link_callback=lambda uri, _: uri  # Handle external links
        )

        if pisa_status.err:
            return render_template('error.html', message="Failed to generate PDF"), 500

        result.seek(0)
        return send_file(
            result,
            mimetype='application/pdf',
            download_name='ATS_Optimized_Resume.pdf',
            as_attachment=True
        )

    except Exception as e:
        return render_template('error.html', message=str(e)), 500

if __name__ == '__main__':
    app.run(debug=True)