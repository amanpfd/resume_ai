import fitz  # For PDF handling
import requests
import json
import os

OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"
HEADERS = {"Content-Type": "application/json"}

class ResumeParser:

    def __init__(self, filepath):
        self.filepath = filepath

    def extract_content(self):
        if self.filepath.endswith('.pdf'):
            # Extract text from PDF
            doc = fitz.open(self.filepath)
            content = ''
            for page in doc:
                content += page.get_text()
            return content
        elif self.filepath.endswith('.docx'):
            from docx import Document
            doc = Document(self.filepath)
            content = ''
            for para in doc.paragraphs:
                content += para.text + '\n'
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        content += cell.text + '\n'
            # Iterate through paragraphs and identify list items based on formatting
            for para in doc.paragraphs:
                if para.style.name.startswith('List'):
                    content += para.text + '\n'

            return content
        else:
            return ''
