from flask import Flask, request, render_template, redirect, url_for, jsonify
import os
from file_uploader import FileUploader
from resume_parser import ResumeParser
from resume_enhancer import ResumeEnhancer
from resume_downloader import ResumeDownloader

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

file_uploader = FileUploader(app)
resume_parser = ResumeParser()
resume_downloader = ResumeDownloader(app)

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
        content = resume_parser.extract_content(filepath)
        return render_template('edit_resume.html', content=content, original_format=file.filename.split('.')[-1])
    return render_template('upload.html')

@app.route("/resume", methods=["POST"])
def create_resume():
    filename = file_uploader.upload()
    if isinstance(filename, tuple):
        return filename # This is an error
    generated_resume = resume_parser.generate_resume(filename)
    generated_resume_path = os.path.join(app.config['UPLOAD_FOLDER'], 'generated_resume.txt')
    with open(generated_resume_path, 'w') as f:
        f.write(generated_resume)
    return jsonify({"message": "File uploaded successfully", "filename": filename, "generated_resume": generated_resume_path}), 200

# Enhance Resume Route
@app.route('/enhance', methods=['POST'])
def enhance_resume():
    content = request.form.get('content')
    ai_service = request.form.get('ai_service', 'ollama')
    objective = request.form.get('objective', None)
    original_format = request.form.get('original_format', 'pdf')
    
    if not content:
        return "Error: No content provided", 400
    
    resume_enhancer = ResumeEnhancer(content, objective)
    
    enhanced_content = resume_enhancer.enhance(ai_service)
    return render_template('edit_resume.html', content=enhanced_content, original_format=original_format)

# Download Resume Route
@app.route('/download', methods=['POST'])
def download_resume():
    content = request.form['content']
    original_format = request.form.get('original_format', 'pdf')
    return resume_downloader.download(content, original_format)


if __name__ == "__main__":
    app.run(debug=True)
