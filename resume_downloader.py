import os
from flask import send_file
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from docx import Document


class ResumeDownloader:

    def __init__(self, app):
        self.app = app
        self.UPLOAD_FOLDER = app.config['UPLOAD_FOLDER']

    def download(self, content, original_format):
        output_filepath = os.path.join(self.UPLOAD_FOLDER, f'enhanced_resume.{original_format}')
        
        if original_format == 'pdf':
            c = canvas.Canvas(output_filepath, pagesize=letter)
            width, height = letter
            textobject = c.beginText(40, height - 50)
            for line in content.split('\n'):
                textobject.textLine(line)
            c.drawText(textobject)
            c.save()
        elif original_format == 'docx':
            doc = Document()
            for line in content.split('\n'):
                doc.add_paragraph(line)
            doc.save(output_filepath)
        else:
            with open(output_filepath, 'w') as f:
                f.write(content)
        
        return send_file(output_filepath, as_attachment=True)
