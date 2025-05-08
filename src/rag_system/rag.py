import faiss
import numpy as np
import google.generativeai as genai
from typing import List, Dict, Tuple
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGSystem:
    def __init__(self, api_key: str):
        """Initialize RAG system with Gemini API."""
        try:
            genai.configure(api_key=api_key)
            # Use the latest stable Gemini model
            self.model = genai.GenerativeModel('gemini-pro')
            logger.info("Using Gemini model: gemini-pro")
            self.index = None
            self.job_documents = []
        except Exception as e:
            logger.error(f"Error initializing Gemini API: {str(e)}")
            raise
        
    def create_embeddings(self, text: str) -> np.ndarray:
        """Create embeddings for text using Gemini API."""
        try:
            # Create a simple embedding by converting text to a fixed-size vector
            # This is a placeholder until we implement proper embeddings
            words = text.lower().split()
            unique_words = list(set(words))
            embedding = np.zeros(100)  # Fixed size of 100
            for i, word in enumerate(unique_words[:100]):
                embedding[i] = hash(word) % 100
            return embedding.astype(np.float32)
        except Exception as e:
            logger.error(f"Error creating embeddings: {str(e)}")
            raise

    def build_index(self, jobs: List[Dict]):
        """Build FAISS index from job descriptions."""
        try:
            if not jobs:
                logger.warning("No jobs provided to build index")
                return

            # Create embeddings for each job
            embeddings = []
            for job in jobs:
                # Combine relevant job information
                job_text = f"{job['title']} {job['description']} {' '.join(job['requirements'])}"
                embedding = self.create_embeddings(job_text)
                embeddings.append(embedding)
                self.job_documents.append(job)

            if not embeddings:
                logger.warning("No embeddings created")
                return

            # Convert to numpy array
            embeddings_array = np.array(embeddings, dtype=np.float32)
            
            # Create FAISS index
            dimension = embeddings_array.shape[1]
            self.index = faiss.IndexFlatL2(dimension)
            self.index.add(embeddings_array)
            
            logger.info(f"Built FAISS index with {len(jobs)} jobs")
        except Exception as e:
            logger.error(f"Error building index: {str(e)}")
            raise

    def find_similar_jobs(self, resume_data: Dict, k: int = 5) -> List[Dict]:
        """Find similar jobs based on resume content."""
        try:
            if not self.index:
                logger.warning("Index not built. Returning all jobs.")
                return self.job_documents[:k]

            # Create embedding for resume
            resume_text = f"{resume_data['skills']} {' '.join([exp['description'] for exp in resume_data['experience']])}"
            resume_embedding = self.create_embeddings(resume_text)
            
            # Search for similar jobs
            distances, indices = self.index.search(
                np.array([resume_embedding], dtype=np.float32), k
            )
            
            # Get matching jobs
            similar_jobs = [self.job_documents[idx] for idx in indices[0]]
            return similar_jobs
        except Exception as e:
            logger.error(f"Error finding similar jobs: {str(e)}")
            return self.job_documents[:k]  # Return first k jobs as fallback

    def generate_cover_letter(self, job: Dict, resume_data: Dict) -> str:
        """Generate personalized cover letter using Gemini API."""
        try:
            # Create header with candidate's information
            header = f"""
            {resume_data.get('name', 'Your Name')}
            {resume_data.get('contact', {}).get('email', 'your.email@example.com')}
            {resume_data.get('contact', {}).get('phone', '')}
            
            {datetime.now().strftime('%B %d, %Y')}
            
            Hiring Manager
            {job.get('company', 'Company Name')}
            {job.get('location', 'Location')}
            
            Dear Hiring Manager,
            """

            # Prepare resume information
            skills = resume_data.get('skills', [])
            experience = resume_data.get('experience', [])
            education = resume_data.get('education', [])
            
            # Format experience and education
            exp_text = "\n".join([f"- {exp.get('role', '')} at {exp.get('company', '')}: {exp.get('description', '')}" 
                                for exp in experience])
            edu_text = "\n".join([f"- {edu.get('degree', '')} from {edu.get('institution', '')}" 
                                for edu in education])

            prompt = f"""Write a professional cover letter for the following job application:

Job Details:
- Position: {job.get('title', 'Job Title')}
- Company: {job.get('company', 'Company Name')}
- Description: {job.get('description', 'Job Description')}
- Requirements: {', '.join(job.get('requirements', ['Job Requirements']))}

Candidate Information:
- Name: {resume_data.get('name', 'Your Name')}
- Skills: {', '.join(skills)}
- Experience:
{exp_text}
- Education:
{edu_text}

Guidelines:
1. Be professional and engaging
2. Highlight relevant skills and experience
3. Show enthusiasm for the role
4. Keep it concise (max 300 words)
5. End with a professional closing

Write the cover letter body only, without any headers or signatures."""

            try:
                response = self.model.generate_content(prompt)
                if response and response.text:
                    # Combine header with generated content
                    cover_letter = header + "\n\n" + response.text + "\n\nSincerely,\n" + resume_data.get('name', 'Your Name')
                    return cover_letter
                else:
                    raise Exception("Empty response from Gemini API")
            except Exception as api_error:
                logger.error(f"Error from Gemini API: {str(api_error)}")
                # Return a basic cover letter if API fails
                return f"""{header}

I am writing to express my interest in the {job.get('title', 'position')} at {job.get('company', 'your company')}. With my background in {', '.join(skills[:3])}, I believe I would be a valuable addition to your team.

{exp_text[:200]}...

I am excited about the opportunity to contribute to {job.get('company', 'your company')} and would welcome the chance to discuss how my skills and experience align with your needs.

Sincerely,
{resume_data.get('name', 'Your Name')}"""

        except Exception as e:
            logger.error(f"Error generating cover letter: {str(e)}")
            return f"""Error generating cover letter. Please try again.

Job: {job.get('title', 'Job Title')} at {job.get('company', 'Company Name')}
Error: {str(e)}""" 