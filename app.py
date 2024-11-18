from flask import Flask, request, jsonify, render_template, redirect, url_for, send_file
import os
import fitz  # For PDF handling
import requests
import json

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"
HEADERS = {"Content-Type": "application/json"}
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("No Gemini API key found. Please set the GEMINI_API_KEY environment variable.")

# Home Route
@app.route('/')
def home():
    return render_template('index.html')

# Upload Route
@app.route('/upload', methods=['GET', 'POST'])
def upload_resume():
    if request.method == 'POST':
        if 'resume' not in request.files:
            return 'No file uploaded', 400
        file = request.files['resume']
        if file.filename == '':
            return 'No selected file', 400
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        content = extract_content(filepath)
        return render_template('edit_resume.html', content=content)
    return render_template('upload.html')

@app.route("/resume", methods=["POST"])
def create_resume():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filename)
    generated_resume = generate_resume(filename)
    generated_resume_path = os.path.join(app.config['UPLOAD_FOLDER'], 'generated_resume.txt')
    with open(generated_resume_path, 'w') as f:
        f.write(generated_resume)
    return jsonify({"message": "File uploaded successfully", "filename": file.filename, "generated_resume": generated_resume_path}), 200

# Enhance Resume Route
@app.route('/enhance', methods=['POST'])
def enhance_resume():
    content = request.form['content']
    ai_service = request.form.get('ai_service', 'ollama')  # Default to 'ollama' if not provided
    enhanced_content = enhance_with_ai(content, ai_service)
    return render_template('edit_resume.html', content=enhanced_content)

# Download Resume Route
@app.route('/download', methods=['POST'])
def download_resume():
    content = request.form['content']
    output_format = request.form.get('format', 'pdf')
    output_filepath = os.path.join(app.config['UPLOAD_FOLDER'], f'enhanced_resume.{output_format}')
    
    if output_format == 'pdf':
        # Generate PDF using ReportLab or WeasyPrint
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        
        c = canvas.Canvas(output_filepath, pagesize=letter)
        textobject = c.beginText(40, 730)
        for line in content.split('\n'):
            textobject.textLine(line)
        c.drawText(textobject)
        c.save()
    elif output_format == 'docx':
        from docx import Document
        doc = Document()
        for line in content.split('\n'):
            doc.add_paragraph(line)
        doc.save(output_filepath)
    else:
        # Default to plain text
        with open(output_filepath, 'w') as f:
            f.write(content)
    
    return send_file(output_filepath, as_attachment=True)

def generate_resume(file_path):
    # Extract text from PDF
    doc = fitz.open(file_path)
    content = ""
    for page in doc:
        content += page.get_text()

    # Call LLM to parse content into neat sections
    payload = {
        "model": "llama3.2",
        "prompt": f"Parse the following resume content into neat sections:\n\n{content}"
    }
    response = requests.post(OLLAMA_ENDPOINT, headers=HEADERS, json=payload)
    response_data = response.json()
    generated_resume = response_data['text']

    return generated_resume

def extract_content(filepath):
    if filepath.endswith('.pdf'):
        # Extract text from PDF
        doc = fitz.open(filepath)
        content = ''
        for page in doc:
            content += page.get_text()
        return content
    elif filepath.endswith('.docx'):
        # Extract text from Word document
        from docx import Document
        doc = Document(filepath)
        content = '\n'.join([para.text for para in doc.paragraphs])
        return content
    else:
        return ''

def enhance_with_ai(content, ai_service):
    if ai_service == "ollama":
        return enhance_with_ollama(content)
    elif ai_service == "gemini":
        return enhance_with_gemini(content)
    else:
        return "Error: Unsupported AI service selected."

def enhance_with_ollama(content):
    prompt = f"""
    You are a professional resume writer. Enhance the following resume content to make it more effective and impactful:

    {content}

    Provide the improved resume content.
    """
    payload = {
        "model": "llama3.2",  # Replace with the actual model name if different
        "prompt": prompt
    }
    try:
        response = requests.post(OLLAMA_ENDPOINT, headers=HEADERS, json=payload)
        response.raise_for_status()  # Raise an error for bad status codes
        response_data = response.json()
        return response_data.get('text', content)
    except requests.exceptions.RequestException as e:
        print(f"Ollama API Error: {e}")
        return "Error: Failed to enhance resume using Ollama."
    except ValueError:
        print("Ollama API returned non-JSON response.")
        return "Error: Invalid response from Ollama."

def enhance_with_gemini(content):
    GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # Ensure this is set

    if not GEMINI_API_KEY:
        print("Gemini API key is not set.")
        return "Error: Gemini API key is missing."

    headers = {
        "Content-Type": "application/json",
    }

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": f"Enhance the following resume content to make it more effective and impactful:\n\n{content}"
                    }
                ]
            }
        ]
    }

    params = {
        "key": GEMINI_API_KEY
    }

    try:
        response = requests.post(GEMINI_ENDPOINT, headers=headers, params=params, json=payload)
        response.raise_for_status()  # Raise an error for bad status codes
        response_data = response.json()
        # print(json.dumps(response_data))
        
        # Parse the response based on Gemini's API structure
        enhanced_text = ""
        if 'contents' in response_data.get('candidates', {}):
            for item in response_data.get['candidates']['contents']:
                for part in item.get('parts', []):
                    enhanced_text += part.get('text', '')
        
        return enhanced_text if enhanced_text else "Error: No enhanced content received from Gemini."

    except requests.exceptions.RequestException as e:
        print(f"Gemini API Error: {e}")
        return "Error: Failed to enhance resume using Gemini."
    except ValueError:
        print("Gemini API returned non-JSON response.")
        return "Error: Invalid response from Gemini."

if __name__ == "__main__":
    app.run(debug=True)
