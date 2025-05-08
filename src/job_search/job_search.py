from typing import List, Dict
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JobSearch:
    def __init__(self):
        """Initialize job search with mock data."""
        self.mock_jobs = self._generate_mock_jobs()
        logger.info(f"Initialized with {len(self.mock_jobs)} mock jobs")

    def _generate_mock_jobs(self) -> List[Dict]:
        """Generate mock job data for testing."""
        return [
            {
                "id": 1,
                "title": "Senior Python Developer",
                "company": "TechCorp",
                "location": "San Francisco, CA",
                "description": "Looking for an experienced Python developer with expertise in web development and AI/ML.",
                "requirements": [
                    "5+ years of Python experience",
                    "Experience with FastAPI/Django",
                    "Knowledge of ML frameworks",
                    "Strong problem-solving skills"
                ],
                "salary_range": "$120,000 - $150,000",
                "posted_date": datetime.now().isoformat(),
                "platform": "LinkedIn"
            },
            {
                "id": 2,
                "title": "AI Engineer",
                "company": "AI Solutions Inc",
                "location": "Remote",
                "description": "Join our AI team to build cutting-edge machine learning solutions.",
                "requirements": [
                    "MS/PhD in Computer Science or related field",
                    "Experience with TensorFlow/PyTorch",
                    "Strong background in NLP",
                    "Research experience"
                ],
                "salary_range": "$130,000 - $160,000",
                "posted_date": datetime.now().isoformat(),
                "platform": "Indeed"
            },
            {
                "id": 3,
                "title": "Full Stack Developer",
                "company": "WebTech",
                "location": "New York, NY",
                "description": "Full stack developer position focusing on modern web technologies.",
                "requirements": [
                    "3+ years of full stack development",
                    "React/Node.js experience",
                    "Database design skills",
                    "Agile methodology"
                ],
                "salary_range": "$100,000 - $130,000",
                "posted_date": datetime.now().isoformat(),
                "platform": "Internshala"
            },
            {
                "id": 4,
                "title": "Data Scientist",
                "company": "DataWorks",
                "location": "Boston, MA",
                "description": "Data scientist position focusing on predictive analytics and machine learning.",
                "requirements": [
                    "Strong statistical background",
                    "Python/R programming",
                    "Experience with big data tools",
                    "Data visualization skills"
                ],
                "salary_range": "$110,000 - $140,000",
                "posted_date": datetime.now().isoformat(),
                "platform": "LinkedIn"
            },
            {
                "id": 5,
                "title": "DevOps Engineer",
                "company": "CloudTech",
                "location": "Seattle, WA",
                "description": "DevOps engineer position focusing on cloud infrastructure and automation.",
                "requirements": [
                    "AWS/Azure experience",
                    "Kubernetes/Docker",
                    "CI/CD pipeline experience",
                    "Infrastructure as Code"
                ],
                "salary_range": "$115,000 - $145,000",
                "posted_date": datetime.now().isoformat(),
                "platform": "Indeed"
            },
            {
                "id": 6,
                "title": "Machine Learning Engineer",
                "company": "ML Innovations",
                "location": "Austin, TX",
                "description": "ML engineer position focusing on developing and deploying ML models.",
                "requirements": [
                    "Strong ML fundamentals",
                    "Python programming",
                    "Model deployment experience",
                    "Cloud platform knowledge"
                ],
                "salary_range": "$125,000 - $155,000",
                "posted_date": datetime.now().isoformat(),
                "platform": "LinkedIn"
            },
            {
                "id": 7,
                "title": "Software Engineer",
                "company": "CodeMasters",
                "location": "Chicago, IL",
                "description": "Software engineer position focusing on scalable applications.",
                "requirements": [
                    "Strong algorithms knowledge",
                    "Java/Python experience",
                    "System design skills",
                    "Agile development"
                ],
                "salary_range": "$95,000 - $125,000",
                "posted_date": datetime.now().isoformat(),
                "platform": "Internshala"
            },
            {
                "id": 8,
                "title": "Senior Software Engineer",
                "company": "TechMahindra",
                "location": "Bangalore, India",
                "description": "Looking for a senior software engineer to join our growing team in Bangalore.",
                "requirements": [
                    "5+ years of software development experience",
                    "Strong Java/Python skills",
                    "Experience with microservices architecture",
                    "Cloud platform experience (AWS/Azure)"
                ],
                "salary_range": "₹25,00,000 - ₹35,00,000",
                "posted_date": datetime.now().isoformat(),
                "platform": "LinkedIn"
            },
            {
                "id": 9,
                "title": "AI/ML Engineer",
                "company": "Infosys",
                "location": "Hyderabad, India",
                "description": "Join our AI/ML team to work on cutting-edge projects in natural language processing and computer vision.",
                "requirements": [
                    "3+ years of ML experience",
                    "Strong Python programming",
                    "Experience with TensorFlow/PyTorch",
                    "Published research papers (preferred)"
                ],
                "salary_range": "₹20,00,000 - ₹30,00,000",
                "posted_date": datetime.now().isoformat(),
                "platform": "Indeed"
            },
            {
                "id": 10,
                "title": "Full Stack Developer",
                "company": "TCS",
                "location": "Mumbai, India",
                "description": "Full stack developer position focusing on modern web technologies and cloud platforms.",
                "requirements": [
                    "4+ years of full stack development",
                    "React/Angular experience",
                    "Node.js/Python backend",
                    "Cloud platform knowledge"
                ],
                "salary_range": "₹18,00,000 - ₹28,00,000",
                "posted_date": datetime.now().isoformat(),
                "platform": "LinkedIn"
            },
            {
                "id": 11,
                "title": "DevOps Engineer",
                "company": "Wipro",
                "location": "Pune, India",
                "description": "DevOps engineer position focusing on cloud infrastructure and automation.",
                "requirements": [
                    "3+ years of DevOps experience",
                    "AWS/Azure certification",
                    "Kubernetes/Docker expertise",
                    "CI/CD pipeline implementation"
                ],
                "salary_range": "₹22,00,000 - ₹32,00,000",
                "posted_date": datetime.now().isoformat(),
                "platform": "Indeed"
            },
            {
                "id": 12,
                "title": "Data Scientist",
                "company": "HCL Technologies",
                "location": "Chennai, India",
                "description": "Data scientist position focusing on predictive analytics and machine learning solutions.",
                "requirements": [
                    "Strong statistical background",
                    "Python/R programming",
                    "Experience with big data tools",
                    "Data visualization skills"
                ],
                "salary_range": "₹20,00,000 - ₹30,00,000",
                "posted_date": datetime.now().isoformat(),
                "platform": "LinkedIn"
            }
        ]

    def search_jobs(self, query: str = None, location: str = None) -> List[Dict]:
        """Search for jobs based on query and location."""
        try:
            filtered_jobs = self.mock_jobs
            logger.info(f"Searching jobs with query: {query}, location: {location}")

            if query:
                query = query.lower()
                filtered_jobs = [
                    job for job in filtered_jobs
                    if query in job["title"].lower() or
                    query in job["description"].lower() or
                    query in job["company"].lower()
                ]
                logger.info(f"Found {len(filtered_jobs)} jobs matching query")

            if location:
                location = location.lower()
                filtered_jobs = [
                    job for job in filtered_jobs
                    if location in job["location"].lower()
                ]
                logger.info(f"Found {len(filtered_jobs)} jobs matching location")

            return filtered_jobs

        except Exception as e:
            logger.error(f"Error searching jobs: {str(e)}")
            raise

    def get_job_details(self, job_id: int) -> Dict:
        """Get detailed information about a specific job."""
        try:
            for job in self.mock_jobs:
                if job["id"] == job_id:
                    return job
            raise ValueError(f"Job with ID {job_id} not found")
        except Exception as e:
            logger.error(f"Error getting job details: {str(e)}")
            raise 