import os
import json
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
import base64
from datetime import datetime

class PortfolioGenerator:
    def __init__(self):
        self.template_dir = Path(__file__).parent / 'templates'
        self.output_dir = Path(__file__).parent.parent / 'static' / 'portfolios'
        self.env = Environment(loader=FileSystemLoader(self.template_dir))
        
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_portfolio(self, profile_data: dict) -> str:
        """Generate a portfolio website from profile data."""
        try:
            # Load the base template
            template = self.env.get_template('portfolio.html')
            
            # Process profile data for the template
            portfolio_data = self._process_profile_data(profile_data)
            
            # Generate unique filename based on name and timestamp
            safe_name = "".join(c for c in profile_data.get('full_name', 'portfolio') if c.isalnum()).lower()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_filename = f"{safe_name}_{timestamp}.html"
            output_path = self.output_dir / output_filename
            
            # Render the template
            html_content = template.render(**portfolio_data)
            
            # Save the generated portfolio
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return str(output_path)
        except Exception as e:
            print(f"Error generating portfolio: {str(e)}")
            return None
    
    def _process_profile_data(self, data: dict) -> dict:
        """Process profile data for the portfolio template."""
        # Ensure all required sections exist
        processed_data = {
            'full_name': data.get('full_name', ''),
            'tagline': data.get('tagline', 'Professional Portfolio'),
            'about_me': data.get('about_me', ''),
            'email': data.get('email', ''),
            'phone': data.get('phone', ''),
            'location': data.get('location', ''),
            'linkedin': data.get('linkedin', ''),
            'profile_photo': data.get('profile_photo', ''),
            'experience': self._format_experience(data.get('experience', [])),
            'education': self._format_education(data.get('education', [])),
            'skills': self._format_skills(data.get('skills', [])),
            'projects': self._format_projects(data.get('projects', [])),
            'certifications': self._format_certifications(data.get('certifications', [])),
            'testimonials': data.get('testimonials', []),
            'generated_date': datetime.now().strftime('%B %d, %Y')
        }
        return processed_data
    
    def _format_experience(self, experience: list) -> list:
        """Format experience data for the template."""
        if isinstance(experience, str):
            # If experience is a string (from manual entry), try to parse it
            try:
                # Simple parsing - split by newlines and process each entry
                entries = [entry.strip() for entry in experience.split('\n') if entry.strip()]
                return [{'title': entry, 'company': '', 'dates': '', 'responsibilities': []} for entry in entries]
            except:
                return []
        return experience
    
    def _format_education(self, education: list) -> list:
        """Format education data for the template."""
        if isinstance(education, str):
            return [entry.strip() for entry in education.split('\n') if entry.strip()]
        return education
    
    def _format_skills(self, skills: list) -> list:
        """Format skills data for the template."""
        if isinstance(skills, str):
            return [skill.strip() for skill in skills.split(',') if skill.strip()]
        return skills
    
    def _format_projects(self, projects: list) -> list:
        """Format projects data for the template."""
        if isinstance(projects, str):
            return [project.strip() for project in projects.split('\n') if project.strip()]
        return projects
    
    def _format_certifications(self, certifications: list) -> list:
        """Format certifications data for the template."""
        if isinstance(certifications, str):
            return [cert.strip() for cert in certifications.split('\n') if cert.strip()]
        return certifications 