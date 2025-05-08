import streamlit as st
import os
from dotenv import load_dotenv
from resume_parser.parser import ResumeParser
from job_search.job_search import JobSearch
from rag_system.rag import RAGSystem
from database.operations import Database
from automation.job_applicator import JobApplicator
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize components
resume_parser = ResumeParser(os.getenv('GEMINI_API_KEY'))
job_search = JobSearch()
rag_system = RAGSystem(os.getenv('GEMINI_API_KEY'))
database = Database(os.getenv('DATABASE_URL'))
job_applicator = JobApplicator()

def main():
    st.title("AI Job Application Agent")
    
    # Sidebar for navigation
    page = st.sidebar.selectbox(
        "Navigation",
        ["Login", "Register", "Upload Resume", "Search Jobs", "Generate Cover Letter", "My Applications"]
    )
    
    if page == "Login":
        show_login_page()
    elif page == "Register":
        show_register_page()
    elif page == "Upload Resume":
        show_upload_resume_page()
    elif page == "Search Jobs":
        show_search_jobs_page()
    elif page == "Generate Cover Letter":
        show_cover_letter_page()
    elif page == "My Applications":
        show_applications_page()

def show_login_page():
    st.header("Login")
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        user = database.authenticate_user(username, password)
        if user:
            st.session_state['user'] = user
            st.success("Login successful!")
        else:
            st.error("Invalid credentials")

def show_register_page():
    st.header("Register")
    
    username = st.text_input("Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    
    if st.button("Register"):
        if password != confirm_password:
            st.error("Passwords do not match")
        else:
            try:
                user = database.create_user(username, email, password)
                st.success("Registration successful! Please login.")
            except Exception as e:
                st.error(f"Registration failed: {str(e)}")

def show_upload_resume_page():
    st.header("Upload Resume")
    
    if 'user' not in st.session_state:
        st.warning("Please login first")
        return
    
    uploaded_file = st.file_uploader("Choose a resume file", type=['pdf', 'docx', 'txt'])
    
    if uploaded_file:
        # Save uploaded file
        file_path = os.path.join("data", "resumes", uploaded_file.name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Parse resume
        try:
            resume_data = resume_parser.parse_resume(file_path)
            st.session_state['resume_data'] = resume_data
            st.session_state['resume_path'] = file_path
            st.success("Resume parsed successfully!")
            
            # Display parsed data
            st.subheader("Parsed Resume Data")
            st.json(resume_data)
        except Exception as e:
            st.error(f"Error parsing resume: {str(e)}")

def show_search_jobs_page():
    st.header("Search Jobs")
    
    if 'user' not in st.session_state:
        st.warning("Please login first")
        return
    
    if 'resume_data' not in st.session_state:
        st.warning("Please upload your resume first")
        return
    
    # Search form
    query = st.text_input("Job Title or Keywords")
    location = st.text_input("Location")
    
    if st.button("Search"):
        try:
            # Search jobs
            jobs = job_search.search_jobs(query, location)
            logger.info(f"Found {len(jobs)} jobs from search")
            
            if not jobs:
                st.warning("No jobs found matching your criteria")
                return
            
            # Build RAG index
            rag_system.build_index(jobs)
            logger.info("Built RAG index")
            
            # Find similar jobs
            similar_jobs = rag_system.find_similar_jobs(st.session_state['resume_data'])
            logger.info(f"Found {len(similar_jobs)} similar jobs")
            
            # Display results
            st.subheader("Matching Jobs")
            for job in similar_jobs:
                with st.expander(f"{job['title']} at {job['company']}"):
                    st.write(f"**Location:** {job['location']}")
                    st.write(f"**Salary:** {job['salary_range']}")
                    st.write("**Description:**")
                    st.write(job['description'])
                    st.write("**Requirements:**")
                    for req in job['requirements']:
                        st.write(f"- {req}")
                    
                    # Check if already applied
                    try:
                        existing_apps = database.get_user_applications(st.session_state['user'].id)
                        already_applied = any(app.job_id == job['id'] for app in existing_apps)
                    except Exception as e:
                        logger.error(f"Error checking existing applications: {str(e)}")
                        already_applied = False
                    
                    if already_applied:
                        st.info("You have already applied to this job")
                    else:
                        if st.button(f"Apply to {job['title']}", key=f"apply_{job['id']}"):
                            try:
                                # Generate cover letter
                                cover_letter = rag_system.generate_cover_letter(
                                    job,
                                    st.session_state['resume_data']
                                )
                                
                                # Save application
                                application = database.add_job_application(
                                    st.session_state['user'].id,
                                    job,
                                    cover_letter,
                                    st.session_state.get('resume_path', '')
                                )
                                
                                st.success(f"Successfully applied to {job['title']} at {job['company']}!")
                                st.experimental_rerun()
                                
                            except Exception as e:
                                st.error(f"Error applying to job: {str(e)}")
        except Exception as e:
            st.error(f"Error searching jobs: {str(e)}")

def show_cover_letter_page():
    st.header("Generate Cover Letter")
    
    if 'user' not in st.session_state:
        st.warning("Please login first")
        return
    
    if 'resume_data' not in st.session_state:
        st.warning("Please upload your resume first")
        return
    
    # Job details form
    st.subheader("Job Details")
    job_title = st.text_input("Job Title")
    company = st.text_input("Company Name")
    job_description = st.text_area("Job Description")
    requirements = st.text_area("Job Requirements (one per line)")
    
    if st.button("Generate Cover Letter"):
        try:
            # Create job data
            job_data = {
                "title": job_title,
                "company": company,
                "description": job_description,
                "requirements": [req.strip() for req in requirements.split('\n') if req.strip()]
            }
            
            # Generate cover letter
            cover_letter = rag_system.generate_cover_letter(
                job_data,
                st.session_state['resume_data']
            )
            
            # Display cover letter
            st.subheader("Generated Cover Letter")
            st.write(cover_letter)
            
            # Save to database
            if st.button("Save Cover Letter"):
                database.add_job_application(
                    st.session_state['user'].id,
                    job_data,
                    cover_letter,
                    st.session_state.get('resume_path', '')
                )
                st.success("Cover letter saved!")
        except Exception as e:
            st.error(f"Error generating cover letter: {str(e)}")

def show_applications_page():
    st.header("My Applications")
    
    if 'user' not in st.session_state:
        st.warning("Please login first")
        return
    
    try:
        # Get user's applications
        applications = database.get_user_applications(st.session_state['user'].id)
        
        if not applications:
            st.info("No applications yet")
            return
        
        # Display applications
        for app in applications:
            with st.expander(f"{app.job_title} at {app.company}"):
                st.write(f"**Status:** {app.status}")
                st.write(f"**Applied Date:** {app.applied_date}")
                st.write("**Cover Letter:**")
                st.write(app.cover_letter)
                
                # Update status
                new_status = st.selectbox(
                    "Update Status",
                    ["applied", "interviewed", "rejected", "accepted"],
                    key=f"status_{app.id}"
                )
                
                if st.button("Update", key=f"update_{app.id}"):
                    try:
                        database.update_application_status(app.id, new_status)
                        st.success("Status updated!")
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(f"Error updating status: {str(e)}")
    except Exception as e:
        st.error(f"Error loading applications: {str(e)}")

if __name__ == "__main__":
    main() 