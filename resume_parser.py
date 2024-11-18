import fitz  # For PDF handling
import requests
import json
import os

OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"
HEADERS = {"Content-Type": "application/json"}

class ResumeParser:

    def __init__(self):
        pass

    def generate_resume(self, file_path):
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

    def extract_content(self, filepath):
        if filepath.endswith('.pdf'):
            # Extract text from PDF
            doc = fitz.open(filepath)
            content = ''
            for page in doc:
                content += page.get_text()
            sections = content #.split('\n\n')  # Simple split, adjust as needed
            return sections
        elif filepath.endswith('.docx'):
            from docx import Document
            doc = Document(filepath)
            sections = []
            current_section = ''
            for para in doc.paragraphs:
                text = para.text.strip()
                if text == '':
                    if current_section:
                        sections.append(current_section)
                        current_section = ''
                else:
                    current_section += text + '\n'
            if current_section:
                sections.append(current_section)
            return sections
        else:
            return []
