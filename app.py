from flask import Flask, request, render_template, redirect, flash
import os
from file_uploader import FileUploader
from resume_parser import ResumeParser
from resume_enhancer import ResumeEnhancer
from resume_downloader import ResumeDownloader

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['UPDATED_FOLDER'] = 'updated'
app.config['SECRET_KEY'] = 'a5393f60-f24f-419f-9128-0f139619460f'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

file_uploader = FileUploader(app)
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
            flash('No file uploaded', 'danger')
            return redirect(request.url)
        file = request.files['resume']
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        try:
            file.save(filepath)
            resume_parser = ResumeParser(filepath)
            content = resume_parser.extract_content()
            if content is None:
                flash('Failed to extract content from the uploaded file.', 'danger')
                return redirect(request.url)
            return render_template('edit_resume.html', content=content, original_format=file.filename.split('.')[-1], original_filename=file.filename)
        except Exception as e:
            flash(f'An error occurred while uploading the file: {e}', 'danger')
            return redirect(request.url)
    return render_template('upload.html')

# Enhance Resume Route
@app.route('/enhance', methods=['POST'])
def enhance_resume():
    content = request.form.get('content')
    ai_service = request.form.get('ai_service', 'ollama')
    objective = request.form.get('objective', None)
    original_format = request.form.get('original_format', 'pdf')
    original_filename = request.form.get('original_filename')

    if not content:
        flash("Error: No content provided for enhancement.", "danger")
        return render_template('edit_resume.html', content='', original_format=original_format, original_filename=original_filename)

    resume_enhancer = ResumeEnhancer(content, objective)
    enhanced_content = resume_enhancer.enhance(ai_service)
    return render_template('edit_resume.html', content=enhanced_content, original_format=original_format, original_filename=original_filename)

# Download Resume Route
@app.route('/download', methods=['POST'])
def download_resume():
    content = request.form['content']
    original_format = request.form.get('original_format', 'pdf')
    original_filename = request.form.get('original_filename')
    return resume_downloader.download(content, original_format, original_filename)


if __name__ == "__main__":
    app.run(debug=True)
