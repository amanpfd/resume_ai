import os
from flask import Flask, request, jsonify

class FileUploader:
    def __init__(self, app: Flask, upload_folder: str = 'uploads'):
        self.app = app
        self.app.config['UPLOAD_FOLDER'] = upload_folder
        os.makedirs(self.app.config['UPLOAD_FOLDER'], exist_ok=True)

    def upload(self):
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        filename = os.path.join(self.app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)
        return filename
