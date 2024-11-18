import requests
import json
import os
import openai

OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"
HEADERS = {"Content-Type": "application/json"}

class ResumeEnhancer:

    def __init__(self, content, objective=None):
        self.content = content
        self.prompt = "You are a professional resume writer.\n"
        if objective:
            self.prompt += f"Objective: {objective}\n"
        self.prompt += f"Enhance the following resume content to make it more effective and impactful:\n\n{content}"
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        if not self.GEMINI_API_KEY:
            print("No Gemini API key found. Please set the GEMINI_API_KEY environment variable.")
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        if not self.OPENAI_API_KEY:
            print("No OpenAI API key found. Please set the OPENAI_API_KEY environment variable.")
        openai.api_key = self.OPENAI_API_KEY


    def enhance(self, ai_service):
        if ai_service == "ollama":
            return self.enhance_with_ollama()
        elif ai_service == "gemini":
            return self.enhance_with_gemini()
        elif ai_service == "openai":
            return self.enhance_with_openai()
        else:
            return "Error: Unsupported AI service selected."

    def enhance_with_ollama(self):
        
        payload = {
            "model": "llama3.2",  # Replace with the actual model name if different
            "prompt": self.prompt,
            "stream": False
        }
        try:
            response = requests.post(OLLAMA_ENDPOINT, headers=HEADERS, json=payload)
            response.raise_for_status()  # Raise an error for bad status codes
            response_data = response.json()
            return response_data.get('response', self.content)
        except requests.exceptions.RequestException as e:
            print(f"Ollama API Error: {e}")
            return "Error: Failed to enhance resume using Ollama."
        except ValueError:
            print("Ollama API returned non-JSON response.")
            return "Error: Invalid response from Ollama."

    def enhance_with_gemini(self):
        GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"

        headers = {
            "Content-Type": "application/json",
        }
        payload = {
            "contents": [{"parts": [{"text": self.prompt}]}]
        }

        params = {
            "key": self.GEMINI_API_KEY
        }

        try:
            response = requests.post(GEMINI_ENDPOINT, headers=headers, params=params, json=payload)
            response.raise_for_status()  # Raise an error for bad status codes
            response_data = response.json()
            print(json.dumps(response_data['candidates'][0]['content']))
            
            # Parse the response based on Gemini's API structure
            enhanced_text = ""
            if 'content' in response_data.get('candidates', [{}])[0]:
                for part in response_data['candidates'][0]['content']['parts']:
                    enhanced_text += part.get('text', '')
            
            return enhanced_text if enhanced_text else "Error: No enhanced content received from Gemini."

        except requests.exceptions.RequestException as e:
            print(f"Gemini API Error: {e}")
            return "Error: Failed to enhance resume using Gemini."
        except ValueError as e:
            print(f"Invalid response from Gemini: {e}")
            return "Error: Invalid response from Gemini."

    def enhance_with_openai(self):
        try:
            response = openai.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": self.prompt
                        }
                        ],
                        model="gpt-4o"
                        )
            enhanced_text = response.choices[0].text.strip()
            return enhanced_text if enhanced_text else "Error: No enhanced content received from OpenAI."

        except Exception as e:
            print(f"OpenAI API Error: {e}")
            return "Error: Failed to enhance resume using OpenAI."
