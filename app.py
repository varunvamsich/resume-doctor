from flask import Flask, render_template, request
import os
import fitz  # PyMuPDF for reading PDF files
import re    # Regular expressions for email & phone extraction

# Initialize Flask app
app = Flask(__name__)

# Folder to save uploaded resumes
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Home route to display upload form
@app.route('/')
def index():
    return render_template('index.html')

# Route that handles resume upload
@app.route('/upload', methods=['POST'])
def upload_resume():
    if 'resume' not in request.files:
        return "No file uploaded."

    file = request.files['resume']
    
    if file.filename == '':
        return "No file selected."

    if file:
        # Save the file in uploads folder
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        # Extract information from PDF
        resume_text = extract_text_from_pdf(file_path)
        email = extract_email(resume_text)
        phone = extract_phone(resume_text)

        # Pass data to summary.html for display
        return render_template(
            'summary.html',
            text=resume_text,
            email=email,
            phone=phone
        )

# Function to read PDF content
def extract_text_from_pdf(pdf_path):
    text = ''
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

# Function to extract email using regex
def extract_email(text):
    match = re.search(r'[\w\.-]+@[\w\.-]+', text)
    return match.group(0) if match else 'Not found'

# Function to extract phone number using regex
def extract_phone(text):
    match = re.search(r'(\+91[\-\s]?)?[0]?[6789]\d{9}', text)
    return match.group(0) if match else 'Not found'

# Start the server
if __name__ == '__main__':
    app.run(debug=True)
