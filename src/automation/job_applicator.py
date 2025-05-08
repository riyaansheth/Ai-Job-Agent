from playwright.sync_api import sync_playwright
from typing import Dict, Optional
import logging
import os
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JobApplicator:
    def __init__(self):
        """Initialize job applicator."""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=True)
        self.context = self.browser.new_context()
        self.page = self.context.new_page()

    def apply_to_job(self, job_data: Dict, resume_path: str, cover_letter: str) -> bool:
        """Apply to a job using Playwright automation."""
        try:
            # Map platform to application URL
            platform_urls = {
                'LinkedIn': f"https://www.linkedin.com/jobs/view/{job_data['id']}",
                'Indeed': f"https://www.indeed.com/viewjob?jk={job_data['id']}",
                'Internshala': f"https://internshala.com/job/{job_data['id']}"
            }

            if job_data['platform'] not in platform_urls:
                raise ValueError(f"Unsupported platform: {job_data['platform']}")

            # Navigate to job page
            self.page.goto(platform_urls[job_data['platform']])
            
            # Wait for page to load
            self.page.wait_for_load_state('networkidle')

            # Handle different platforms
            if job_data['platform'] == 'LinkedIn':
                return self._apply_linkedin(resume_path, cover_letter)
            elif job_data['platform'] == 'Indeed':
                return self._apply_indeed(resume_path, cover_letter)
            elif job_data['platform'] == 'Internshala':
                return self._apply_internshala(resume_path, cover_letter)

        except Exception as e:
            logger.error(f"Error applying to job: {str(e)}")
            return False

    def _apply_linkedin(self, resume_path: str, cover_letter: str) -> bool:
        """Apply to LinkedIn job."""
        try:
            # Click apply button
            self.page.click('button[data-control-name="jobdetails_topcard_inapply"]')
            
            # Wait for application form
            self.page.wait_for_selector('input[type="file"]')
            
            # Upload resume
            self.page.set_input_files('input[type="file"]', resume_path)
            
            # Fill cover letter
            self.page.fill('textarea[name="coverLetter"]', cover_letter)
            
            # Submit application
            self.page.click('button[data-control-name="submit_unify"]')
            
            # Wait for confirmation
            self.page.wait_for_selector('.artdeco-inline-feedback--success')
            return True
        except Exception as e:
            logger.error(f"Error applying to LinkedIn: {str(e)}")
            return False

    def _apply_indeed(self, resume_path: str, cover_letter: str) -> bool:
        """Apply to Indeed job."""
        try:
            # Click apply button
            self.page.click('button[data-tn-element="apply-button"]')
            
            # Wait for application form
            self.page.wait_for_selector('input[type="file"]')
            
            # Upload resume
            self.page.set_input_files('input[type="file"]', resume_path)
            
            # Fill cover letter
            self.page.fill('textarea[name="coverLetter"]', cover_letter)
            
            # Submit application
            self.page.click('button[data-tn-element="submit-button"]')
            
            # Wait for confirmation
            self.page.wait_for_selector('.success-message')
            return True
        except Exception as e:
            logger.error(f"Error applying to Indeed: {str(e)}")
            return False

    def _apply_internshala(self, resume_path: str, cover_letter: str) -> bool:
        """Apply to Internshala job."""
        try:
            # Click apply button
            self.page.click('button[data-tn-element="apply-button"]')
            
            # Wait for application form
            self.page.wait_for_selector('input[type="file"]')
            
            # Upload resume
            self.page.set_input_files('input[type="file"]', resume_path)
            
            # Fill cover letter
            self.page.fill('textarea[name="coverLetter"]', cover_letter)
            
            # Submit application
            self.page.click('button[data-tn-element="submit-button"]')
            
            # Wait for confirmation
            self.page.wait_for_selector('.success-message')
            return True
        except Exception as e:
            logger.error(f"Error applying to Internshala: {str(e)}")
            return False

    def close(self):
        """Close browser and cleanup."""
        try:
            self.context.close()
            self.browser.close()
            self.playwright.stop()
        except Exception as e:
            logger.error(f"Error closing browser: {str(e)}")
            raise 