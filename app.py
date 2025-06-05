import streamlit as st
import sys
import os
from pathlib import Path

# Import AIProcessor directly from main.py in root directory
from main import AIProcessor

from backend.file_utils import FileUtils
import json
import base64
from datetime import datetime
from backend.portfolio_generator import PortfolioGenerator

# Add the project root directory to Python path
project_root = Path(__file__).parent.absolute()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Initialize session state
if 'profile_data' not in st.session_state:
    st.session_state.profile_data = {}
if 'current_step' not in st.session_state:
    st.session_state.current_step = 'landing'
if 'extracted_data' not in st.session_state:
    st.session_state.extracted_data = None

# Initialize AI processor
ai_processor = AIProcessor()

# Initialize portfolio generator
portfolio_generator = PortfolioGenerator()

def show_landing_page():
    st.title("Portfolio and Resume Generator Mockup- AI Tool")
    st.markdown("""
    Transform your professional profile into a complete career package:
    - Professional Portfolio Website
    - ATS-Ready Resume
    - Tailored Cover Letter
    """)
    
    if st.button("Get Started", type="primary", use_container_width=True):
        st.session_state.current_step = 'profile_builder'
        st.rerun()

def show_profile_builder():
    st.title("Profile Builder")
    
    # Check if extracted data is available and move to preview if in profile_builder step
    if st.session_state.get('extracted_data') is not None and st.session_state.current_step == 'profile_builder':
        # This means data was extracted and 'Use Extracted Data' was clicked
        # We should now set profile_data and move to preview
        st.session_state.profile_data = st.session_state.extracted_data
        st.session_state.current_step = 'preview'
        st.rerun()

    # Input method selection
    input_method = st.radio(
        "Choose how to provide your information:",
        ["Upload Resume", "LinkedIn URL", "Enter Data Manually"],
        horizontal=True
    )
    
    if input_method == "Upload Resume":
        uploaded_file = st.file_uploader(
            "Upload your resume (PDF or DOCX)",
            type=["pdf", "docx"],
            help="Upload your existing resume to extract information"
        )
        
        if uploaded_file:
            file_content = uploaded_file.read()
            text, error = FileUtils.process_uploaded_file(file_content, uploaded_file.type)
            
            if error:
                st.error(error)
            elif text:
                with st.spinner("Extracting information from your resume..."):
                    extracted_data = ai_processor.extract_resume_data(text)
                    
                    if not extracted_data:
                        st.error("Failed to extract information from your resume. Please try manual entry or upload a different file.")
                        if st.button("Try Manual Entry Instead"):
                            st.session_state.current_step = 'manual_entry'
                            st.rerun()
                    else:
                        st.session_state.extracted_data = extracted_data
                        st.success("Information extracted successfully!")
                        
                        # Show extracted data for review
                        st.subheader("Extracted Information")
                        
                        # Basic Information
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write("**Full Name:**")
                            st.write(extracted_data.get('full_name', 'Not found'))
                            st.write("**Contact Information:**")
                            st.write(f"📧 {extracted_data.get('email', 'Not found')}")
                            st.write(f"📱 {extracted_data.get('phone', 'Not found')}")
                            st.write(f"📍 {extracted_data.get('location', 'Not found')}")
                        
                        with col2:
                            st.write("**Professional Summary:**")
                            st.write(extracted_data.get('summary', 'Not found'))
                        
                        # Experience
                        st.write("**Work Experience:**")
                        if extracted_data.get('experience'):
                            for exp in extracted_data['experience']:
                                st.write(f"**{exp.get('title', '')} at {exp.get('company', '')}** ({exp.get('dates', '')})")
                                for resp in exp.get('responsibilities', []):
                                    st.write(f"- {resp}")
                        else:
                            st.write("No experience found")
                        
                        # Education
                        st.write("**Education:**")
                        if extracted_data.get('education'):
                            for edu in extracted_data['education']:
                                st.write(f"- {edu}")
                        else:
                            st.write("No education found")
                        
                        # Skills
                        st.write("**Skills:**")
                        if extracted_data.get('skills'):
                            st.write(", ".join(extracted_data['skills']))
                        else:
                            st.write("No skills found")
                        
                        # Projects
                        st.write("**Projects:**")
                        if extracted_data.get('projects'):
                            for project in extracted_data['projects']:
                                st.write(f"- {project}")
                        else:
                            st.write("No projects found")
                        
                        # Certifications
                        st.write("**Certifications:**")
                        if extracted_data.get('certifications'):
                            for cert in extracted_data['certifications']:
                                st.write(f"- {cert}")
                        else:
                            st.write("No certifications found")
                        
                        # Action buttons
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("Use Extracted Data", type="primary", use_container_width=True):
                                st.session_state.profile_data = extracted_data
                                st.session_state.current_step = 'preview'
                                st.rerun()
                        with col2:
                            if st.button("Enter Data Manually", use_container_width=True):
                                st.session_state.current_step = 'manual_entry'
                                st.rerun()
    
    elif input_method == "LinkedIn URL":
        st.subheader("Extract from LinkedIn Profile")
        st.markdown("Due to technical and policy restrictions, direct extraction from a LinkedIn URL is limited. Please paste the text content of your LinkedIn profile below, or provide the URL and we will attempt a basic extraction if possible.")

        linkedin_url = st.text_input(
            "Enter your LinkedIn profile URL (Optional)",
            help="Provide your LinkedIn URL if you'd like, but pasting the text is more reliable."
        )
        
        linkedin_text = st.text_area(
            "Paste your LinkedIn Profile Text Here (Recommended)",
            height=300,
            help="Copy and paste the relevant sections from your LinkedIn profile (About, Experience, Education, Skills, etc.)"
        )
        
        if st.button("Extract from LinkedIn", type="primary", use_container_width=True):
            if linkedin_text or linkedin_url:
                text_to_process = ""
                if linkedin_text:
                    text_to_process = linkedin_text
                elif linkedin_url:
                    # Basic attempt with URL (might not work due to scraping restrictions)
                    # For a real application, consider using a third-party API for LinkedIn data
                    st.warning("Attempting basic extraction from URL... results may vary.")
                    # In a real scenario, you would call a backend function that might use a service
                    # that can handle LinkedIn URLs. For this example, we'll just use the URL as text input for the AI.
                    text_to_process = f"LinkedIn Profile URL: {linkedin_url}"
                    
                if text_to_process:
                    with st.spinner("Extracting information from your LinkedIn profile..."):
                        extracted_data = ai_processor.extract_resume_data(text_to_process)

                        if not extracted_data or not any(extracted_data.values()):
                             st.error("Failed to extract information from LinkedIn profile. Please try pasting the text content or enter data manually.")
                             if st.button("Try Manual Entry Instead", key="linkedin_manual_entry"):
                                 st.session_state.current_step = 'manual_entry'
                                 st.rerun()
                        else:
                            st.session_state.extracted_data = extracted_data
                            st.success("Information extracted successfully!")
                            
                            # Show extracted data for review (similar to resume flow)
                            st.subheader("Extracted Information")
                            
                            # Basic Information
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write("**Full Name:**")
                                st.write(extracted_data.get('full_name', 'Not found'))
                                st.write("**Contact Information:**")
                                st.write(f"📧 {extracted_data.get('email', 'Not found')}")
                                st.write(f"📱 {extracted_data.get('phone', 'Not found')}")
                                st.write(f"📍 {extracted_data.get('location', 'Not found')}")
                            
                            with col2:
                                st.write("**Professional Summary:**")
                                st.write(extracted_data.get('summary', 'Not found'))
                            
                            # Experience
                            st.write("**Work Experience:**")
                            if extracted_data.get('experience'):
                                for exp in extracted_data['experience']:
                                    st.write(f"**{exp.get('title', '')} at {exp.get('company', '')}** ({exp.get('dates', '')})")
                                    for resp in exp.get('responsibilities', []):
                                        st.write(f"- {resp}")
                            else:
                                st.write("No experience found")
                            
                            # Education
                            st.write("**Education:**")
                            if extracted_data.get('education'):
                                for edu in extracted_data['education']:
                                    st.write(f"- {edu}")
                            else:
                                st.write("No education found")
                            
                            # Skills
                            st.write("**Skills:**")
                            if extracted_data.get('skills'):
                                st.write(", ".join(extracted_data['skills']))
                            else:
                                st.write("No skills found")
                            
                            # Projects
                            st.write("**Projects:**")
                            if extracted_data.get('projects'):
                                for project in extracted_data['projects']:
                                    st.write(f"- {project}")
                            else:
                                st.write("No projects found")
                            
                            # Certifications
                            st.write("**Certifications:**")
                            if extracted_data.get('certifications'):
                                for cert in extracted_data['certifications']:
                                    st.write(f"- {cert}")
                            else:
                                st.write("No certifications found")
                                
                            # Action buttons
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button("Use Extracted Data", type="primary", use_container_width=True, key="use_linkedin_extracted"):
                                    st.session_state.profile_data = extracted_data
                                    st.session_state.current_step = 'preview'
                                    st.rerun()
                            with col2:
                                if st.button("Enter Data Manually", use_container_width=True, key="manual_entry_linkedin"):
                                    st.session_state.current_step = 'manual_entry'
                                    st.rerun()
            else:
                 st.warning("Please enter a LinkedIn URL or paste your profile text.")

    else:  # Manual Entry
        st.session_state.current_step = 'manual_entry'
        st.rerun()

def show_manual_entry():
    st.subheader("Enter Your Information Manually (Interactive Interview)")

    # Initialize session state for interview progress
    if 'interview_step' not in st.session_state:
        st.session_state.interview_step = 'basic_info'
    if 'work_history' not in st.session_state:
        st.session_state.work_history = []
    if 'current_job' not in st.session_state:
        st.session_state.current_job = {}
    if 'skills' not in st.session_state:
        st.session_state.skills = []
    if 'metrics' not in st.session_state:
        st.session_state.metrics = []
    
    # Progress bar
    steps = ['basic_info', 'work_history', 'skills', 'education', 'projects', 'review']
    current_step_index = steps.index(st.session_state.interview_step)
    st.progress((current_step_index + 1) / len(steps))
    
    # Basic Information Section
    if st.session_state.interview_step == 'basic_info':
        st.subheader("Let's start with your basic information")
        
        with st.form("basic_info_form"):
            col1, col2 = st.columns(2)
            with col1:
                full_name = st.text_input(
                    "What's your full name?",
                    value=st.session_state.profile_data.get('full_name', ''),
                    help="Enter your full name as it should appear on your resume"
                )
                email = st.text_input(
                    "What's your professional email?",
                    value=st.session_state.profile_data.get('email', ''),
                    help="Use a professional email address"
                )
                phone = st.text_input(
                    "What's your contact number?",
                    value=st.session_state.profile_data.get('phone', ''),
                    help="Include country code if applying internationally"
                )
            
            with col2:
                location = st.text_input(
                    "Where are you located?",
                    value=st.session_state.profile_data.get('location', ''),
                    help="City, State/Province, Country"
                )
                linkedin = st.text_input(
                    "What's your LinkedIn profile URL?",
                    value=st.session_state.profile_data.get('linkedin', ''),
                    help="Optional: Add your LinkedIn profile"
                )
            
            # Professional Summary
            st.subheader("Professional Summary")
            about_me = st.text_area(
                "Tell us about yourself professionally",
                value=st.session_state.profile_data.get('about_me', ''),
                help="Write a compelling 3-4 sentence summary of your professional background and career goals",
                height=150
            )
            
            # Profile Photo
            st.subheader("Profile Photo")
            profile_photo = st.file_uploader(
                "Upload a professional headshot",
                type=["jpg", "jpeg", "png"],
                help="Upload a professional photo (max 800x800px)"
            )
            
            if profile_photo:
                photo_content = profile_photo.read()
                processed_photo, error = FileUtils.process_profile_image(photo_content)
                if error:
                    st.error(error)
                else:
                    st.session_state.profile_data['profile_photo'] = base64.b64encode(processed_photo).decode()
            
            if st.form_submit_button("Next: Work History", type="primary"):
                # Save basic information
                st.session_state.profile_data.update({
                    'full_name': full_name,
                    'email': email,
                    'phone': phone,
                    'location': location,
                    'linkedin': linkedin,
                    'about_me': about_me
                })
                st.session_state.interview_step = 'work_history'
                st.rerun()
    
    # Work History Section
    elif st.session_state.interview_step == 'work_history':
        st.subheader("Work Experience")
        
        # Show existing work history
        if st.session_state.work_history:
            st.write("Your work history:")
            for i, job in enumerate(st.session_state.work_history):
                with st.expander(f"{job.get('title', '')} at {job.get('company', '')}"):
                    st.write(f"**Dates:** {job.get('dates', '')}")
                    st.write("**Responsibilities:**")
                    for resp in job.get('responsibilities', []):
                        st.write(f"- {resp}")
                    if st.button("Remove", key=f"remove_{i}"):
                        st.session_state.work_history.pop(i)
                        st.rerun()
        
        # Add new job experience
        st.write("Add a new position:")
        with st.form("work_history_form"):
            col1, col2 = st.columns(2)
            with col1:
                job_title = st.text_input("Job Title", help="Your role or position")
                company = st.text_input("Company Name")
                dates = st.text_input("Employment Dates", help="e.g., Jan 2020 - Present")
            
            with col2:
                responsibilities = st.text_area(
                    "Key Responsibilities & Achievements",
                    help="List your main responsibilities and achievements. Use action verbs and include metrics where possible.",
                    height=150
                )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("Add Position"):
                    if job_title and company:
                        # Process responsibilities into bullet points
                        resp_list = [r.strip() for r in responsibilities.split('\n') if r.strip()]
                        st.session_state.work_history.append({
                            'title': job_title,
                            'company': company,
                            'dates': dates,
                            'responsibilities': resp_list
                        })
                        st.rerun()
            
            with col2:
                if st.form_submit_button("Next: Skills", type="primary"):
                    st.session_state.profile_data['experience'] = st.session_state.work_history
                    st.session_state.interview_step = 'skills'
                    st.rerun()
    
    # Skills Section
    elif st.session_state.interview_step == 'skills':
        st.subheader("Skills & Expertise")

        # Ensure skills data is in dictionary format with expected categories
        if 'skills' in st.session_state.profile_data and isinstance(st.session_state.profile_data['skills'], list):
            # If skills is a list (e.g., from extraction), convert to dictionary with a default category
            st.session_state.profile_data['skills'] = {'General Skills': st.session_state.profile_data['skills']}
        elif 'skills' not in st.session_state.profile_data or not isinstance(st.session_state.profile_data['skills'], dict):
             # If skills is missing or not a dict, initialize with empty categories
             st.session_state.profile_data['skills'] = {
                 'Technical Skills': [],
                 'Soft Skills': [],
                 'Tools & Technologies': [],
                 'Languages': []
             }


        # Define the skill categories to display in the form
        # Use the categories already in profile_data if it's a dictionary, otherwise use defaults
        current_skill_categories = st.session_state.profile_data['skills'].keys()
        default_skill_categories = ['Technical Skills', 'Soft Skills', 'Tools & Technologies', 'Languages', 'General Skills']
        # Combine existing and default categories, ensuring unique and desired order
        skill_categories_order = [cat for cat in default_skill_categories if cat in current_skill_categories] + [cat for cat in current_skill_categories if cat not in default_skill_categories]


        with st.form("skills_form"):
            st.write("Add your skills in each category:")

            # Use the potentially updated categories
            edited_skill_data = {}
            for category in skill_categories_order:
                # Use the skills data from the potentially updated session state
                skills_list = st.session_state.profile_data['skills'].get(category, [])
                skills_input = st.text_area(
                    f"{category}",
                    value=", ".join(skills_list),
                    help=f"Enter {category.lower()} separated by commas",
                    key=f"skills_input_{category}"
                )
                # Temporarily store edited skills outside session state until form submit
                edited_skill_data[category] = [s.strip() for s in skills_input.split(',') if s.strip()]

            # Metrics and Achievements
            st.subheader("Key Metrics & Achievements")
            edited_metrics = st.text_area(
                "List your key metrics and achievements",
                value="\n".join(st.session_state.metrics), # Assuming metrics is already a list in session_state
                help="Enter one achievement per line. Include specific numbers and results where possible.",
                height=150,
                key="metrics_input"
            )

            col1, col2 = st.columns(2)
            with col1:
                # Adjusted button to work within the form
                if st.form_submit_button("Previous: Work History"):
                    st.session_state.interview_step = 'work_history'
                    st.rerun()

            with col2:
                # Add the submit button for the skills form
                if st.form_submit_button("Next: Education", type="primary"):
                    # Save the edited skill data and metrics to session state
                    st.session_state.profile_data['skills'] = edited_skill_data
                    st.session_state.metrics = [m.strip() for m in edited_metrics.split('\n') if m.strip()]
                    st.session_state.interview_step = 'education'
                    st.rerun()
    
    # Education Section
    elif st.session_state.interview_step == 'education':
        st.subheader("Education & Certifications")
        
        with st.form("education_form"):
            # Education
            st.write("Education History:")
            education = st.text_area(
                "List your educational background",
                value=st.session_state.profile_data.get('education', ''),
                help="Enter one education entry per line. Include degree, major, institution, and graduation date.",
                height=150
            )
            
            # Certifications
            st.write("Professional Certifications:")
            certifications = st.text_area(
                "List your certifications",
                value=st.session_state.profile_data.get('certifications', ''),
                help="Enter one certification per line. Include certification name, issuing organization, and date.",
                height=150
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("Previous: Skills"):
                    st.session_state.interview_step = 'skills'
                    st.rerun()
            
            with col2:
                if st.form_submit_button("Next: Projects", type="primary"):
                    st.session_state.profile_data.update({
                        'education': [edu.strip() for edu in education.split('\n') if edu.strip()],
                        'certifications': [cert.strip() for cert in certifications.split('\n') if cert.strip()]
                    })
                    st.session_state.interview_step = 'projects'
                    st.rerun()
    
    # Projects Section
    elif st.session_state.interview_step == 'projects':
        st.subheader("Projects & Portfolio")
        
        with st.form("projects_form"):
            projects = st.text_area(
                "Describe your key projects",
                value=st.session_state.profile_data.get('projects', ''),
                help="""Enter one project per line. For each project, include:
                - Project name
                - Your role
                - Technologies used
                - Key outcomes or results
                - Impact on the organization""",
                height=200
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("Previous: Education"):
                    st.session_state.interview_step = 'education'
                    st.rerun()
            
            with col2:
                if st.form_submit_button("Review Profile", type="primary"):
                    st.session_state.profile_data['projects'] = [proj.strip() for proj in projects.split('\n') if proj.strip()]
                    st.session_state.interview_step = 'review'
                    st.rerun()
    
    # Review Section
    elif st.session_state.interview_step == 'review':
        st.subheader("Review Your Profile")
        
        # Display all collected information
        st.write("### Basic Information")
        st.write(f"**Name:** {st.session_state.profile_data.get('full_name', '')}")
        st.write(f"**Email:** {st.session_state.profile_data.get('email', '')}")
        st.write(f"**Phone:** {st.session_state.profile_data.get('phone', '')}")
        st.write(f"**Location:** {st.session_state.profile_data.get('location', '')}")
        st.write(f"**LinkedIn:** {st.session_state.profile_data.get('linkedin', '')}")
        
        st.write("### Professional Summary")
        st.write(st.session_state.profile_data.get('about_me', ''))
        
        st.write("### Work Experience")
        for job in st.session_state.profile_data.get('experience', []):
            st.write(f"**{job.get('title', '')} at {job.get('company', '')}** ({job.get('dates', '')})")
            for resp in job.get('responsibilities', []):
                st.write(f"- {resp}")
        
        st.write("### Skills")
        for category, skills in st.session_state.profile_data.get('skills', {}).items():
            if skills:
                st.write(f"**{category}:**")
                st.write(", ".join(skills))
        
        st.write("### Education")
        for edu in st.session_state.profile_data.get('education', []):
            st.write(f"- {edu}")
        
        st.write("### Certifications")
        for cert in st.session_state.profile_data.get('certifications', []):
            st.write(f"- {cert}")
        
        st.write("### Projects")
        for project in st.session_state.profile_data.get('projects', []):
            st.write(f"- {project}")
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Edit Profile", use_container_width=True):
                st.session_state.interview_step = 'basic_info'
                st.rerun()
        
        with col2:
            if st.button("Generate Resume", type="primary", use_container_width=True):
                with st.spinner("Generating your ATS-friendly resume..."):
                    resume_text = ai_processor.generate_resume(st.session_state.profile_data)
                    if resume_text:
                        # Save resume to temporary file
                        resume_path = FileUtils.save_temp_file(
                            resume_text.encode(),
                            'pdf'
                        )
                        if resume_path:
                            with open(resume_path, 'rb') as f:
                                st.download_button(
                                    "Download Resume PDF",
                                    f,
                                    file_name=f"resume_{datetime.now().strftime('%Y%m%d')}.pdf",
                                    mime="application/pdf",
                                    use_container_width=True
                                )
        
        with col3:
            if st.button("Generate Portfolio", use_container_width=True):
                with st.spinner("Generating your portfolio website..."):
                    portfolio_path = portfolio_generator.generate_portfolio(st.session_state.profile_data)
                    if portfolio_path:
                        # Read the generated portfolio file
                        with open(portfolio_path, 'rb') as f:
                            portfolio_html = f.read()

                        # Create a download button for the portfolio
                        st.download_button(
                            "Download Portfolio HTML",
                            portfolio_html,
                            file_name=f"portfolio_{datetime.now().strftime('%Y%m%d')}.html",
                            mime="text/html",
                            use_container_width=True
                        )

                        # Add subdomain text input
                        st.text_input(
                            "Enter desired subdomain for hosting (Optional)",
                            value="your-name",
                            help="e.g., 'your-name.your-domain.com'. This is for your reference and doesn't automatically host the site."
                        )

                        st.success("Portfolio generated successfully! Download the HTML file above.")
                    else:
                        st.error("Failed to generate portfolio. Please try again.")

def show_preview():
    st.title("Profile Preview")
    
    # Display profile information
    col1, col2 = st.columns([1, 2])
    
    with col1:
        if 'profile_photo' in st.session_state.profile_data:
            st.image(base64.b64decode(st.session_state.profile_data['profile_photo']))
        st.write(f"**{st.session_state.profile_data.get('full_name', '')}**")
        st.write(st.session_state.profile_data.get('location', ''))
        st.write(f"📧 {st.session_state.profile_data.get('email', '')}")
        st.write(f"📱 {st.session_state.profile_data.get('phone', '')}")
    
    with col2:
        st.subheader("Professional Summary")
        st.write(st.session_state.profile_data.get('about_me', ''))
        
        st.subheader("Experience")
        st.write(st.session_state.profile_data.get('experience', ''))
        
        st.subheader("Education")
        st.write(st.session_state.profile_data.get('education', ''))
        
        st.subheader("Skills")
        st.write(st.session_state.profile_data.get('skills', ''))
        
        st.subheader("Projects")
        st.write(st.session_state.profile_data.get('projects', ''))
        
        st.subheader("Certifications")
        st.write(st.session_state.profile_data.get('certifications', ''))
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Edit Profile", use_container_width=True):
            st.session_state.current_step = 'manual_entry'
            st.rerun()
    
    with col2:
        if st.button("Generate Resume", type="primary", use_container_width=True):
            with st.spinner("Generating your resume..."):
                resume_text = ai_processor.generate_resume(st.session_state.profile_data)
                if resume_text:
                    # Save resume to temporary file
                    resume_path = FileUtils.save_temp_file(
                        resume_text.encode(),
                        'pdf'
                    )
                    if resume_path:
                        with open(resume_path, 'rb') as f:
                            st.download_button(
                                "Download Resume",
                                f,
                                file_name=f"resume_{datetime.now().strftime('%Y%m%d')}.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )
    
    with col3:
        if st.button("Generate Portfolio", use_container_width=True):
            with st.spinner("Generating your portfolio website..."):
                portfolio_path = portfolio_generator.generate_portfolio(st.session_state.profile_data)
                if portfolio_path:
                    # Read the generated portfolio file
                    with open(portfolio_path, 'rb') as f:
                        portfolio_html = f.read()

                    # Create a download button for the portfolio
                    st.download_button(
                        "Download Portfolio HTML",
                        portfolio_html,
                        file_name=f"portfolio_{datetime.now().strftime('%Y%m%d')}.html",
                        mime="text/html",
                        use_container_width=True
                    )

                    # Add subdomain text input
                    st.text_input(
                        "Enter desired subdomain for hosting (Optional)",
                        value="your-name",
                        help="e.g., 'your-name.your-domain.com'. This is for your reference and doesn't automatically host the site."
                    )

                    st.success("Portfolio generated successfully! Download the HTML file above.")

                else:
                    st.error("Failed to generate portfolio. Please try again.")

def show_cover_letter_generator():
    st.title("Cover Letter Generator")
    st.markdown("""
    Generate a tailored cover letter for your job applications.
    - Upload a job description or paste it directly
    - Choose your preferred tone and style
    - Edit the generated cover letter
    - Download in multiple formats
    """)
    
    # Check if profile exists
    if not st.session_state.profile_data:
        st.warning("Please complete your profile first!")
        if st.button("Go to Profile Builder", type="primary"):
            st.session_state.current_step = 'profile_builder'
            st.rerun()
        return
    
    # Job Description Input
    st.subheader("1. Job Description")
    job_desc_method = st.radio(
        "How would you like to provide the job description?",
        ["Upload Job Description", "Paste Job Description"],
        horizontal=True
    )
    
    if job_desc_method == "Upload Job Description":
        uploaded_file = st.file_uploader(
            "Upload job description (PDF, DOCX, or TXT)",
            type=["pdf", "docx", "txt"]
        )
        if uploaded_file:
            file_content = uploaded_file.read()
            text, error = FileUtils.process_uploaded_file(file_content, uploaded_file.type)
            if error:
                st.error(error)
            elif text:
                st.session_state.job_description = text
                st.success("Job description uploaded successfully!")
    else:
        job_description = st.text_area(
            "Paste the job description here",
            value=st.session_state.get('job_description', ''),
            height=300,
            help="Copy and paste the complete job description"
        )
        if job_description:
            st.session_state.job_description = job_description
    
    # Tone Selection
    st.subheader("2. Cover Letter Style")
    # Get the list of available tones from the backend
    available_tones_list = ai_processor.get_cover_letter_templates()

    # Define tone details with icons and descriptions (can be expanded)
    tone_details = {
        "Professional": {"name": "Professional", "icon": "💼", "description": "Balanced, confident tone"},
        "Formal": {"name": "Formal", "icon": "🎩", "description": "Traditional, respectful tone"},
        "Friendly": {"name": "Friendly", "icon": "🤝", "description": "Friendly, approachable tone"},
        # Add other tones here as needed
    }

    # Display tone options in a grid with icons and descriptions
    cols = st.columns(len(available_tones_list))
    # Get the current selected tone from session state, default to the first available tone if not set
    selected_tone = st.session_state.get('selected_tone', available_tones_list[0] if available_tones_list else None)

    for i, tone_name in enumerate(available_tones_list):
        if tone_name in tone_details:
            template = tone_details[tone_name]
            with cols[i]:
                st.markdown(f"### {template['icon']}")
                if st.button(
                    template['name'],
                    key=f"tone_button_{tone_name}", # Use a unique key
                    use_container_width=True,
                    type="primary" if tone_name == selected_tone else "secondary"
                ):
                    selected_tone = tone_name
                    st.session_state.selected_tone = tone_name
                    st.rerun()
                st.markdown(f"*{template['description']}*", help=template['description'])

    # If no tones are available, display a warning
    if not available_tones_list:
        st.warning("No cover letter tones available from the backend.")
        # Set selected_tone to None if no tones are available
        st.session_state.selected_tone = None

    # Generate Cover Letter
    st.subheader("3. Generate & Edit")
    # Disable generate button if no tone is selected
    if st.button("Generate Cover Letter", type="primary", use_container_width=True, disabled=selected_tone is None):
        if not st.session_state.get('job_description'):
            st.warning("Please provide a job description!")
        elif selected_tone is None:
             st.warning("Please select a cover letter tone.")
        else:
            with st.spinner("Generating your cover letter..."):
                cover_letter = ai_processor.generate_cover_letter(
                    st.session_state.profile_data,
                    st.session_state.job_description,
                    selected_tone
                )
                if cover_letter:
                    st.session_state.cover_letter = cover_letter
                    st.success("Cover letter generated successfully!")
                else:
                    st.error("Failed to generate cover letter. Please try again.")

    # Display and Edit Cover Letter
    # Only show review/edit/download if a cover letter has been generated
    if st.session_state.get('cover_letter'):
        st.subheader("4. Review & Edit")
        
        # Tabs for different views
        preview_tab, edit_tab, html_tab = st.tabs(["Preview", "Edit", "HTML"])
        
        with preview_tab:
            # Add custom CSS for better preview
            st.markdown("""
                <style>
                .cover-letter-preview {
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 40px;
                    background-color: white;
                    border: 1px solid #e0e0e0;
                    border-radius: 5px;
                    color: #333333; /* Dark grey for main text for visibility */
                    font-size: 14px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                .cover-letter-preview * {
                    color: #333333; /* Ensure all elements inherit a darker color */
                }
                .cover-letter-preview strong {
                    color: #000000; /* Black for emphasis for high contrast */
                    font-weight: 600;
                }
                </style>
            """, unsafe_allow_html=True)
            
            # Wrap the cover letter in a styled container
            preview_html = f"""
            <div class="cover-letter-preview">
                {st.session_state.cover_letter}
            </div>
            """
            
            # Display the preview
            st.components.v1.html(
                preview_html,
                height=600,
                scrolling=True
            )
        
        with edit_tab:
            edited_letter = st.text_area(
                "Edit your cover letter",
                value=st.session_state.cover_letter,
                height=600,
                help="Make any necessary changes to your cover letter. The text will be preserved when you download."
            )
            if edited_letter != st.session_state.cover_letter:
                st.session_state.cover_letter = edited_letter
                st.success("Changes saved!")
        
        with html_tab:
            st.code(st.session_state.cover_letter, language="html")
            st.markdown("""
            **HTML Tips:**
            - Use `<div>` for paragraphs
            - Use `<strong>` for emphasis
            - Use `<br>` for line breaks
            - Use `<ul>` and `<li>` for lists
            """)
        
        # Download Options
        st.subheader("5. Download")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Save as PDF
            pdf_path = FileUtils.save_temp_file(
                st.session_state.cover_letter.encode(),
                'pdf'
            )
            if pdf_path:
                with open(pdf_path, 'rb') as f:
                    st.download_button(
                        "📄 Download as PDF",
                        f,
                        file_name=f"cover_letter_{datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
        
        with col2:
            # Save as DOCX
            docx_path = FileUtils.save_temp_file(
                st.session_state.cover_letter.encode(),
                'docx'
            )
            if docx_path:
                with open(docx_path, 'rb') as f:
                    st.download_button(
                        "📝 Download as DOCX",
                        f,
                        file_name=f"cover_letter_{datetime.now().strftime('%Y%m%d')}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True
                    )
        
        with col3:
            # Save as HTML
            st.download_button(
                "🌐 Download as HTML",
                st.session_state.cover_letter,
                file_name=f"cover_letter_{datetime.now().strftime('%Y%m%d')}.html",
                mime="text/html",
                use_container_width=True
            )

def show_profile_optimizer():
    st.title("Résumé/PortfolioOptimizer")
    st.markdown("""
    Real-time score, keyword gap analysis vs. target job description, and auto-rewrite suggestions.
    """)
    
    if not st.session_state.profile_data:
        st.warning("Please complete your profile first!")
        if st.button("Go to Profile Builder", type="primary"):
            st.session_state.current_step = 'profile_builder'
            st.rerun()
        return
        
    # Job Description Input
    st.subheader("1. Target Job Description")
    job_desc_method = st.radio(
        "How would you like to provide the job description?",
        ["Upload Job Description", "Paste Job Description"],
        horizontal=True,
        key="optimizer_job_desc_method"
    )
    
    job_description_text = st.session_state.get('optimizer_job_description', '')

    if job_desc_method == "Upload Job Description":
        uploaded_file = st.file_uploader(
            "Upload job description (PDF, DOCX, or TXT)",
            type=["pdf", "docx", "txt"],
            key="optimizer_job_desc_uploader"
        )
        if uploaded_file:
            file_content = uploaded_file.read()
            text, error = FileUtils.process_uploaded_file(file_content, uploaded_file.type)
            if error:
                st.error(error)
            elif text:
                st.session_state.optimizer_job_description = text
                job_description_text = text
                st.success("Job description uploaded successfully!")
    else: # Paste Job Description
        job_description_text = st.text_area(
            "Paste the job description here",
            value=st.session_state.get('optimizer_job_description', ''),
            height=200,
            help="Copy and paste the complete job description",
            key="optimizer_job_desc_text"
        )
        if job_description_text:
            st.session_state.optimizer_job_description = job_description_text

    # Proceed with analysis if job description is available
    if job_description_text:
        st.subheader("2. Analysis Results")
        
        # ATS Score
        st.subheader("ATS Compatibility Score")
        ats_score = ai_processor.calculate_ats_score(st.session_state.profile_data, job_description_text)
        st.progress(ats_score / 100)
        st.write(f"Your profile has an estimated ATS compatibility score of {ats_score}%")
        st.info("Note: This is an estimated score based on keyword matching and basic structure. Real ATS systems use more complex criteria.")
        
        # Optimization Suggestions
        st.subheader("Optimization Suggestions")
        suggestions = ai_processor.get_optimization_suggestions(st.session_state.profile_data, job_description_text)
        
        if suggestions:
            for category, items in suggestions.items():
                with st.expander(f"{category} Suggestions"): # Use expander for cleaner view
                    for item in items:
                        st.write(f"- {item}")
        else:
            st.info("No specific optimization suggestions based on the job description at this time.")
        
        # Keyword Analysis
        st.subheader("Keyword Gap Analysis")
        keywords = ai_processor.analyze_keywords(st.session_state.profile_data, job_description_text)
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Strong Keywords (Found in Profile)**")
            if keywords.get('strong'):
                 for keyword in keywords.get('strong', []):
                     st.success(f"✓ {keyword}")
            else:
                st.info("No strong keywords identified based on this job description.")
        
        with col2:
            st.write("**Missing Keywords (From Job Description)**")
            if keywords.get('missing'):
                 for keyword in keywords.get('missing', []):
                     st.warning(f"⚠ {keyword}")
            else:
                 st.info("No missing keywords identified based on this job description.")

        # Auto-rewrite Suggestions (Simulated)
        st.subheader("Auto-rewrite Suggestions")
        st.info("Auto-rewrite suggestions would appear here, offering improved phrasing for your profile based on the job description.")
        # TODO: Implement actual auto-rewrite suggestion generation if needed later

        # Action Buttons
        st.subheader("3. Actions")
        col1, col2 = st.columns(2)
        with col1:
            # This button would ideally apply the rewrite suggestions
            if st.button("Apply Suggestions", type="primary", use_container_width=True, key="apply_optimizer_suggestions"):
                 # Call the backend to apply suggestions (currently placeholder)
                 optimized_profile = ai_processor.apply_optimization_suggestions(
                     st.session_state.profile_data,
                     suggestions # Pass suggestions if backend needs them
                 )
                 st.session_state.profile_data = optimized_profile
                 st.session_state.current_step = 'preview'
                 st.rerun()
        
        with col2:
            # This button navigates back to manual entry to allow manual edits based on suggestions
            if st.button("Update Profile Manually", use_container_width=True, key="update_profile_manual_optimizer"):
                st.session_state.current_step = 'manual_entry'
                # Removed temporary success message
                st.rerun()

    else:
        st.info("Please provide a target job description to get optimization analysis.")

def show_mock_interviewer():
    st.title("AI Mock Interviewer Role")
    st.markdown("Role aware questions set to help prepare for this Job interview")

    if not st.session_state.profile_data:
        st.warning("Please complete your profile first in the Profile Builder section to get personalized interview questions.")
        if st.button("Go to Profile Builder", type="primary", key="mock_interviewer_go_to_profile"):
            st.session_state.current_step = 'profile_builder'
            st.rerun()
        return

    st.subheader("1. Provide Job Description")
    job_desc_method = st.radio(
        "How would you like to provide the job description?",
        ["Upload Job Description", "Paste Job Description"],
        horizontal=True,
        key="interviewer_job_desc_method"
    )

    job_description_text = st.session_state.get('interviewer_job_description', '')

    if job_desc_method == "Upload Job Description":
        uploaded_file = st.file_uploader(
            "Upload job description (PDF, DOCX, or TXT)",
            type=["pdf", "docx", "txt"],
            key="interviewer_job_desc_uploader"
        )
        if uploaded_file:
            file_content = uploaded_file.read()
            text, error = FileUtils.process_uploaded_file(file_content, uploaded_file.type)
            if error:
                st.error(error)
            elif text:
                st.session_state.interviewer_job_description = text
                job_description_text = text
                st.success("Job description uploaded successfully!")
    else: # Paste Job Description
        job_description_text = st.text_area(
            "Paste the job description here",
            value=st.session_state.get('interviewer_job_description', ''),
            height=200,
            help="Copy and paste the complete job description",
            key="interviewer_job_desc_text"
        )
        if job_description_text:
            st.session_state.interviewer_job_description = job_description_text

    st.subheader("2. Generate Questions")
    if st.button("Generate Interview Questions", type="primary", use_container_width=True):
        if not job_description_text:
            st.warning("Please provide a job description first!")
        else:
            with st.spinner("Generando preguntas..."):
                # This will call the backend method (to be implemented next)
                
                # Add a check for Groq client before calling the backend
                import sys
                print(f"Python Path: {sys.path}")
                print(f"AIProcessor instance: {ai_processor}")
                print(f"Groq client initialized in AIProcessor: {ai_processor.groq_client is not None}")
                
                if ai_processor.groq_client is None:
                    st.error("AI Processor is not initialized. Please ensure GROQ_API_KEY is set correctly.")
                    questions = [] # Ensure questions is empty if client is None
                else:
                    questions = ai_processor.generate_mock_interview_questions(
                        job_description_text,
                        st.session_state.profile_data # Pass profile data for context
                    )

                # Save the generated questions to session state
                st.session_state.mock_interview_questions = questions

    # Display and Download Questions
    if st.session_state.get('mock_interview_questions'):
        st.subheader("3. Your Mock Interview Questions")
        questions_list = st.session_state.mock_interview_questions

        if questions_list:
            for i, question in enumerate(questions_list):
                st.markdown(f"**Q{i+1}:** {question}")

            # Download Button
            questions_text = "\n".join([f"Q{i+1}: {q}" for i, q in enumerate(questions_list)])
            st.download_button(
                label="Download Questions List",
                data=questions_text,
                file_name=f"mock_interview_questions_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        else:
             st.info("No questions available.")

def main():
    # Set page config
    st.set_page_config(
        page_title="Portfolio and Resume Generator - AI Tool",
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
        <style>
        .stButton>button {
            width: 100%;
        }
        .sidebar .sidebar-content {
            background-color: #f0f2f6;
        }
        .sidebar-nav {
            padding: 1rem;
        }
        .sidebar-nav-item {
            padding: 0.5rem 1rem;
            margin: 0.5rem 0;
            border-radius: 0.5rem;
            cursor: pointer;
        }
        .sidebar-nav-item:hover {
            background-color: #e0e2e6;
        }
        .sidebar-nav-item.active {
            background-color: #4CAF50;
            color: white;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Sidebar Navigation
    with st.sidebar:
        st.title("Navigation")
        st.markdown("---")
        
        # Navigation options
        nav_option = st.radio(
            "Select a section:",
            ["Profile Builder", "Cover Letter Generator", "Résumé/PortfolioOptimizer", "AI Mock Interviewer"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        st.markdown("### About")
        st.markdown("""
        This AI-powered tool helps you create:
        - Professional profiles
        - ATS-friendly resumes
        - Tailored cover letters
        - Portfolio websites
        """)
    
    # Main content based on navigation
    if nav_option == "Profile Builder":
        if st.session_state.current_step == 'landing':
            show_landing_page()
        elif st.session_state.current_step == 'profile_builder':
            show_profile_builder()
        elif st.session_state.current_step == 'manual_entry':
            show_manual_entry()
        elif st.session_state.current_step == 'preview':
            show_preview()
    elif nav_option == "Cover Letter Generator":
        show_cover_letter_generator()
    elif nav_option == "Résumé/PortfolioOptimizer":
        show_profile_optimizer()
    elif nav_option == "AI Mock Interviewer":
        show_mock_interviewer()
    
    # Cleanup temporary files when session ends
    if st.session_state.current_step == 'landing':
        FileUtils.cleanup_temp_files()

if __name__ == "__main__":
    main() 