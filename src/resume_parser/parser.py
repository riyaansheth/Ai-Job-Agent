import os
import PyPDF2
import docx
import google.generativeai as genai
from typing import Dict, List, Optional
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResumeParser:
    def __init__(self, api_key: str):
        """Initialize the resume parser with Gemini API key."""
        try:
            if not api_key:
                raise ValueError("Gemini API key is required")
            
            genai.configure(api_key=api_key)
            # List available models
            models = [m for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            logger.info(f"Available models: {[m.name for m in models]}")
            
            # Use the correct Gemini model
            self.model = genai.GenerativeModel('models/gemini-1.5-pro')
            logger.info("Using Gemini model: models/gemini-1.5-pro")
        except Exception as e:
            logger.error(f"Error initializing Gemini API: {str(e)}")
            raise

    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file."""
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()
                return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            raise

    def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file."""
        try:
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            logger.error(f"Error extracting text from DOCX: {str(e)}")
            raise

    def parse_resume(self, file_path: str) -> Dict:
        """Parse resume and extract structured information using Gemini API."""
        try:
            # Determine file type and extract text
            file_extension = os.path.splitext(file_path)[1].lower()
            if file_extension == '.pdf':
                text = self.extract_text_from_pdf(file_path)
            elif file_extension == '.docx':
                text = self.extract_text_from_docx(file_path)
            else:
                with open(file_path, 'r') as file:
                    text = file.read()

            logger.info(f"Extracted text from resume: {text[:200]}...")  # Log first 200 chars

            # Prepare prompt for Gemini
            prompt = f"""
            You are a resume parser. Extract the following information from this resume and return it in JSON format:
            
            Resume text:
            {text}
            
            Required JSON structure:
            {{
                "name": "Full Name",
                "contact": {{
                    "email": "Email address",
                    "phone": "Phone number"
                }},
                "skills": ["Skill 1", "Skill 2", ...],
                "experience": [
                    {{
                        "company": "Company name",
                        "role": "Job title",
                        "duration": "Time period",
                        "description": "Key responsibilities and achievements"
                    }}
                ],
                "education": [
                    {{
                        "degree": "Degree name",
                        "institution": "School/University name",
                        "year": "Graduation year"
                    }}
                ],
                "projects": [
                    {{
                        "name": "Project name",
                        "description": "Project description",
                        "technologies": ["Tech 1", "Tech 2", ...]
                    }}
                ]
            }}
            
            Important:
            1. Return ONLY the JSON object, no other text
            2. Ensure all fields are properly filled
            3. If a field is not found, use empty string or empty list
            4. Format dates consistently
            """

            # Get response from Gemini
            try:
                response = self.model.generate_content(prompt)
                logger.info(f"Raw Gemini response: {response.text}")  # Log the raw response
            except Exception as e:
                logger.error(f"Error getting response from Gemini: {str(e)}")
                raise
            
            # Parse the response
            try:
                # Try to parse as JSON first
                parsed_data = json.loads(response.text)
                logger.info("Successfully parsed JSON response")
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {str(e)}")
                # If not valid JSON, try to evaluate as Python dict
                try:
                    # Clean the response text to ensure it's valid Python
                    cleaned_text = response.text.strip()
                    if cleaned_text.startswith('```json'):
                        cleaned_text = cleaned_text[7:]
                    if cleaned_text.endswith('```'):
                        cleaned_text = cleaned_text[:-3]
                    parsed_data = eval(cleaned_text)
                    logger.info("Successfully parsed Python dict response")
                except Exception as e:
                    logger.error(f"Error parsing response as Python dict: {str(e)}")
                    # Return a basic structure if parsing fails
                    parsed_data = {
                        "name": "Unknown",
                        "contact": {"email": "", "phone": ""},
                        "skills": [],
                        "experience": [],
                        "education": [],
                        "projects": []
                    }

            # Validate and clean the parsed data
            if not isinstance(parsed_data, dict):
                logger.error("Parsed data is not a dictionary")
                parsed_data = {
                    "name": "Unknown",
                    "contact": {"email": "", "phone": ""},
                    "skills": [],
                    "experience": [],
                    "education": [],
                    "projects": []
                }

            # Ensure all required fields exist
            required_fields = ['name', 'contact', 'skills', 'experience', 'education', 'projects']
            for field in required_fields:
                if field not in parsed_data:
                    parsed_data[field] = [] if field in ['skills', 'experience', 'education', 'projects'] else {"email": "", "phone": ""} if field == 'contact' else "Unknown"

            logger.info(f"Final parsed data: {json.dumps(parsed_data, indent=2)}")
            return parsed_data

        except Exception as e:
            logger.error(f"Error parsing resume: {str(e)}")
            raise

    def validate_parsed_data(self, data: Dict) -> bool:
        """Validate the parsed resume data."""
        required_fields = ['name', 'contact', 'skills', 'experience', 'education']
        return all(field in data for field in required_fields) 