# ---------- Import Dependencies ----------
from flask import Flask, render_template, request, send_file
import fitz  # PyMuPDF for PDF reading
import openai
import re
import os
from dotenv import load_dotenv
from xhtml2pdf import pisa
from io import BytesIO

# ---------- Flask App ----------
app = Flask(__name__)

# ---------- Load Environment Variables ----------
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# ---------- Helper: Extract Section ----------
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

# ---------- ATS Cleanup ----------
def clean_html(html):
    # Allowed ATS-safe tags
    allowed_tags = ['h1', 'h2', 'h3', 'p', 'ul', 'li', 'strong', 'a']

    # Remove script, style, comments
    html = re.sub(r'<script.*?>.*?</script>', '', html, flags=re.DOTALL)
    html = re.sub(r'<style.*?>.*?</style>', '', html, flags=re.DOTALL)
    html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)

    # Remove disallowed tags but preserve content inside
    html = re.sub(r'</?(?!' + '|'.join(allowed_tags) + r')\b[^>]*>', '', html)

    # Remove specific unwanted tags and HTML entities
    html = re.sub(r'<br\s*/?>', '', html)
    html = re.sub(r'<div[^>]*>', '', html)
    html = re.sub(r'</div>', '', html)
    html = re.sub(r'&nbsp;', ' ', html)

    # Remove extra attributes inside allowed tags
    html = re.sub(r'(<(?:' + '|'.join(allowed_tags) + r'))\b[^>]*>', r'\1>', html)

    # Remove empty tags and excessive spaces
    html = re.sub(r'<(p|h1|h2|h3|ul)>\s*</\1>', '', html)
    html = re.sub(r'\s+', ' ', html)
    html = re.sub(r'>\s+<', '><', html)  # Collapse spaces between tags

    return html.strip()


# ---------- ATS Validation ----------
def validate_ats_structure(html):
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

# ---------- ATS Formatting Fix ----------
def enforce_ats_formatting(html):
    html = re.sub(r"(\d{4})\s*-\s*(\d{4}|Present)", r"\1–\2", html)
    html = re.sub(r"<li>\s*([a-z])", lambda m: f"<li>{m.group(1).upper()}", html)
    return html

# ---------- Home Route ----------
@app.route('/')
def home():
    return render_template('dashboard.html')

# ---------- Resume Upload Route ----------
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

# ---------- Job Matcher ----------
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

# ---------- Form to Generate Resume ----------
@app.route('/generate-resume', methods=['POST'])
def generate_resume():
    """ATS-Optimized Resume Generator"""
    file = request.files['resume']
    resume_text = ""
    hyperlinks = []

    if file and file.filename.endswith('.pdf'):
        doc = fitz.open(stream=file.read(), filetype="pdf")
        for page in doc:
            resume_text += page.get_text()

            # ✅ Extract all real hyperlinks (e.g., LinkedIn, GitHub, Email, Projects, etc.)
            links = page.get_links()
            for link in links:
                if 'uri' in link:
                    url = link['uri']
                    if url not in hyperlinks:
                        hyperlinks.append(url)

    # ✅ Create the prompt for GPT (use clean user resume + AI guidance)
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
    1. Use ONLY these HTML tags: h1, h2, h3, p, ul, li, strong, a
    2. Do NOT invent any hyperlinks or fake info
    3. Only use verified links from the uploaded resume (LinkedIn, GitHub, Projects, etc.)
    4. Use AI feedback and job matcher insights if available
    5. Ensure resume formatting guarantees 90+ ATS score
    6. Keep resume concise and remove extra spacing

    Resume Data:
    {resume_text}
    """

    try:
        # 🔍 Generate optimized resume using GPT
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an ATS resume expert. Only use verified user data and hyperlinks."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2000
        )
        generated_resume = response.choices[0].message['content']

        # 🧹 Clean HTML and enforce formatting
        generated_resume = clean_html(generated_resume)
        generated_resume = enforce_ats_formatting(generated_resume)

        # 🔗 Replace placeholder hyperlinks with real ones
        for url in hyperlinks:
            domain = url.split('//')[-1].split('/')[0].lower()
            label = ""
            if "linkedin" in domain:
                label = "LinkedIn"
            elif "github" in domain:
                label = "GitHub"
            elif "mailto" in url:
                label = "Email"
            elif "project" in domain or "vercel" in domain:
                label = "Project"
            elif "resume" in domain or "portfolio" in domain:
                label = "Portfolio"
            else:
                label = domain

            # ✅ Insert href link in the contact-info or wherever label found
            link_tag = f'<a href="{url}" target="_blank">{label}</a>'
            generated_resume = re.sub(rf'\b{label}\b', link_tag, generated_resume, flags=re.IGNORECASE)

        # ✅ Check if any important sections are missing
        missing_sections = validate_ats_structure(generated_resume)
        if missing_sections:
            generated_resume += f"\n<!-- Missing sections: {', '.join(missing_sections)} -->"

    except Exception as e:
        generated_resume = f"<h1>Error</h1><p>{str(e)}</p>"

    selected_template = request.form.get("selected_template_name", "Default AI Template")

    return render_template(
        'generated_result.html',
        ai_resume=generated_resume,
        template_name=selected_template
    )

    




# ---------- PDF Download ----------
@app.route('/download-resume', methods=['POST'])
def download_resume():
    try:
        raw_html = request.form['resume_html']
        cleaned_html = re.sub(r'<\!\-\-.*?\-\->', '', raw_html)
        cleaned_html = re.sub(r'\s+', ' ', cleaned_html).strip()

        full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="description" content="ATS-optimized resume">
    <title>Professional Resume</title>
    <style>
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
            link_callback=lambda uri, _: uri
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
# ---------- Template Selector ----------
@app.route('/select-template', methods=['GET', 'POST'])
def select_template():
    templates = {
        "harvard": "Harvard (Modern ATS-Optimized)",
        "princeton": "Princeton (Chronological Resume)",
        "google": "Google UX Resume (Minimal + Effective)",
        "ibm": "IBM Technical Resume Template",
        "stanford": "Stanford ATS Resume Template"
    }
    if request.method == 'POST':
        selected = request.form.get('template')
        return render_template(f'templates/{selected}.html')
    return render_template('template_selector.html', templates=templates)

# ---------- ATS Score Visualizer ----------
@app.route('/ats-score-visualizer', methods=['POST'])
def ats_score_visualizer():
    resume_html = request.form['resume_html']
    selected_template_name = request.form.get('template_name', 'Unknown Template')  # Safely get template

    # Scoring logic based on section presence
    sections = {
        "Professional Summary": 25,
        "Technical Skills": 20,
        "Work Experience": 30,
        "Education": 15,
        "Hyperlinks (LinkedIn, GitHub)": 10
    }

    ats_score = 0
    missing_sections = []

    for section, weight in sections.items():
        if section == "Hyperlinks (LinkedIn, GitHub)":
            if "linkedin.com" in resume_html.lower() or "github.com" in resume_html.lower():
                ats_score += weight
            else:
                missing_sections.append(section)
        else:
            if f"<h2>{section}</h2>" in resume_html:
                ats_score += weight
            else:
                missing_sections.append(section)

    ats_score = min(ats_score, 100)

    return render_template(
        "ats_score.html",
        score=ats_score,
        missing=missing_sections,
        template_name=selected_template_name
    )





# ---------- Run App ----------
if __name__ == '__main__':
    app.run(debug=True)