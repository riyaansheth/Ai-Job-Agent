from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import List, Dict, Optional
from datetime import datetime
import logging
from .models import Base, User, JobApplication, JobSearch
import bcrypt
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_url: str):
        """Initialize database connection."""
        try:
            # Create database directory if it doesn't exist
            db_path = db_url.replace('sqlite:///', '')
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            
            # Initialize database with echo=True for debugging
            self.engine = create_engine(db_url, echo=True)
            
            # Create tables if they don't exist
            Base.metadata.create_all(self.engine)
            logger.info("Database tables created successfully")
            
            self.Session = sessionmaker(bind=self.engine)
            
            # Create test user if no users exist
            self._create_test_user()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise

    def _create_test_user(self):
        """Create a test user if no users exist."""
        try:
            session = self.Session()
            if not session.query(User).first():
                # Create test user
                password_hash = bcrypt.hashpw("test123".encode('utf-8'), bcrypt.gensalt())
                test_user = User(
                    username="test",
                    email="test@example.com",
                    password_hash=password_hash.decode('utf-8')
                )
                session.add(test_user)
                session.commit()
                logger.info("Created test user: test@example.com / test123")
        except Exception as e:
            logger.error(f"Error creating test user: {str(e)}")
            session.rollback()
        finally:
            session.close()

    def create_user(self, username: str, email: str, password: str) -> User:
        """Create a new user."""
        try:
            session = self.Session()
            # Hash password
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            user = User(
                username=username,
                email=email,
                password_hash=password_hash.decode('utf-8')
            )
            session.add(user)
            session.commit()
            return user
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user."""
        try:
            session = self.Session()
            user = session.query(User).filter(User.username == username).first()
            
            if user and bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
                return user
            return None
        except Exception as e:
            logger.error(f"Error authenticating user: {str(e)}")
            raise
        finally:
            session.close()

    def add_job_application(self, user_id: int, job_data: Dict, cover_letter: str, resume_path: str) -> JobApplication:
        """Add a new job application."""
        session = None
        try:
            session = self.Session()
            
            # Create new application
            application = JobApplication(
                user_id=user_id,
                job_id=job_data['id'],
                job_title=job_data['title'],
                company=job_data['company'],
                platform=job_data['platform'],
                cover_letter=cover_letter,
                resume_path=resume_path,
                status='applied',
                applied_date=datetime.utcnow()
            )
            
            # Add and commit
            session.add(application)
            session.commit()
            
            return application
        except Exception as e:
            if session:
                session.rollback()
            logger.error(f"Error adding job application: {str(e)}")
            raise
        finally:
            if session:
                session.close()

    def update_application_status(self, application_id: int, status: str, notes: str = None) -> JobApplication:
        """Update job application status."""
        try:
            session = self.Session()
            application = session.query(JobApplication).filter(JobApplication.id == application_id).first()
            if application:
                application.status = status
                if notes:
                    application.notes = notes
                session.commit()
                return application
            raise ValueError(f"Application with ID {application_id} not found")
        except Exception as e:
            logger.error(f"Error updating application status: {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()

    def get_user_applications(self, user_id: int) -> List[JobApplication]:
        """Get all applications for a user."""
        session = None
        try:
            session = self.Session()
            applications = session.query(JobApplication)\
                .filter(JobApplication.user_id == user_id)\
                .order_by(JobApplication.applied_date.desc())\
                .all()
            return applications
        except Exception as e:
            logger.error(f"Error getting user applications: {str(e)}")
            raise
        finally:
            if session:
                session.close()

    def save_job_search(self, user_id: int, query: str, location: str, results_count: int) -> JobSearch:
        """Save job search history."""
        try:
            session = self.Session()
            search = JobSearch(
                user_id=user_id,
                query=query,
                location=location,
                results_count=results_count
            )
            session.add(search)
            session.commit()
            return search
        except Exception as e:
            logger.error(f"Error saving job search: {str(e)}")
            session.rollback()
            raise
        finally:
            session.close() 