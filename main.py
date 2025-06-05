import os
import groq
from typing import Dict, List, Optional
import json
from dotenv import load_dotenv
import re # Import re for clean_and_tokenize
import streamlit as st

load_dotenv()

class AIProcessor:
    def __init__(self, model_name="deepseek-r1-distill-llama-70b"):
        # Import Groq here to avoid issues if the API key is not set immediately
        try:
            from groq import Groq
            self.groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
            self.model_name = model_name
        except ImportError:
            st.error("The Groq library is not installed. Please install it using 'pip install groq'.")
            self.groq_client = None
        except Exception as e:
            st.error(f"Failed to initialize Groq client: {e}")
            self.groq_client = None

    # Add a list of common English stop words as a class attribute
    STOP_WORDS = set([
        'a', 'an', 'the', 'and', 'or', 'but', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', 'as', 'at', 'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by', 'can', 'did', 'do', 'does', 'doing', 'down', 'during', 'each', 'few', 'for', 'from', 'further', 'had', 'has', 'have', 'having', 'he', 'her', 'here', 'hers', 'herself', 'him', 'himself', 'his', 'how', 'i', 'if', 'in', 'into', 'is', 'it', 'its', 'itself', 'just', 'me', 'more', 'most', 'my', 'myself', 'no', 'nor', 'not', 'now', 'of', 'off', 'on', 'once', 'only', 'or', 'other', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 's', 'same', 'she', 'should', 'so', 'some', 'such', 't', 'than', 'that', 'their', 'theirs', 'them', 'themselves', 'then', 'there', 'these', 'they', 'this', 'those', 'through', 'to', 'too', 'under', 'until', 'up', 'very', 'was', 'we', 'were', 'what', 'when', 'where', 'which', 'while', 'who', 'whom', 'why', 'will', 'with', 'you', 'your', 'yours', 'yourself', 'yourselves'])

    # Move clean_and_tokenize to be a class method for reusability
    def clean_and_tokenize(self, text):
        """Remove punctuation, split into words, and filter out stop words, short words, and digits."""
        if not isinstance(text, str): # Ensure input is string
            return []
        text = text.lower()
        # Replace non-alphanumeric (excluding some like #, +, .) with space, then clean further
        text = re.sub(r'[^a-z0-9+#.-]+', ' ', text) # Keep some technical chars
        words = text.split()
        # Filter out stop words, words that are purely digits, and short words
        return [word for word in words if word not in self.STOP_WORDS and len(word) > 1 and not word.isdigit()]

    def extract_resume_data(self, text):
        if not self.groq_client:
            return None
        try:
            prompt = f"""
            You are an AI assistant designed to extract key information from a resume text.
            Extract the following information and return it as a JSON object:
            - full_name
            - email
            - phone
            - location
            - summary (professional summary or objective)
            - experience (list of jobs, each with title, company, dates, and list of responsibilities/achievements)
            - education (list of degrees, institutions, dates)
            - skills (list of key skills)
            - projects (list of significant projects)
            - certifications (list of certifications)

            If a section is not present, use an empty string or empty list as appropriate.

            Resume Text:
            {text}

            Return only the JSON object.
            """
            chat_completion = self.groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that extracts resume data into a JSON object."
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=self.model_name,
                response_format={"type": "json_object"}
            )
            content = chat_completion.choices[0].message.content
            # Clean the content to ensure it's valid JSON
            content = content.strip()
            # Attempt to parse the JSON string
            try:
                extracted_data = json.loads(content)
                return extracted_data
            except json.JSONDecodeError as e:
                print(f"JSON decoding error: {e}")
                print(f"Content received: {content}")
                return None

        except Exception as e:
            print(f"Error during resume data extraction: {e}")
            return None

    def generate_profile_summary(self, profile_data):
        if not self.groq_client:
            return "AI Processor not initialized."
        try:
            # Construct a prompt using the profile data
            prompt = f"""
            Based on the following profile data, generate a concise professional summary (3-5 sentences).

            Profile Data:
            {json.dumps(profile_data, indent=2)}

            Professional Summary:
            """
            chat_completion = self.groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are an AI assistant that generates professional summaries."
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=self.model_name,
                temperature=0.7,
            )
            return chat_completion.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating profile summary: {e}")
            return "Failed to generate summary."

    def optimize_bullet_points(self, bullet_points, job_description=""):
        if not self.groq_client:
            return bullet_points # Return original if no client
        try:
            # Join bullet points with newlines, properly escaped
            bullet_points_text = "\n- ".join(bullet_points)
            prompt = f"""
            Optimize the following resume bullet points for a resume, making them concise, action-oriented, and quantifiable where possible.
            If a job description is provided, tailor the bullet points to be relevant to that description.

            Job Description:
            {job_description if job_description else "N/A"}

            Bullet Points:
            - {bullet_points_text}

            Optimized Bullet Points (as a numbered or bulleted list):
            """
            chat_completion = self.groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are an AI assistant that optimizes resume bullet points."
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=self.model_name,
                temperature=0.7,
            )
            optimized_text = chat_completion.choices[0].message.content.strip()
            # Simple split by lines for now, assuming each line is an optimized bullet point
            return [line.strip() for line in optimized_text.split('\n') if line.strip()]
        except Exception as e:
            print(f"Error optimizing bullet points: {e}")
            return bullet_points # Return original on error

    def generate_resume(self, profile_data, job_description=""):
        if not self.groq_client:
            return "AI Processor not initialized. Cannot generate resume."
        try:
            # Construct a detailed prompt for resume generation
            prompt = f"""
            Generate a professional resume in a standard text format based on the following profile data.
            Include sections for Contact Information, Summary, Experience, Education, Skills, Projects, and Certifications.
            Format the experience and education sections clearly with dates and details.
            If a job description is provided, subtly tailor the resume content (especially summary and skills) for relevance without fabricating information.

            Profile Data:
            {json.dumps(profile_data, indent=2)}

            Job Description (for tailoring):
            {job_description if job_description else "N/A"}

            Generate the resume text below:
            """
            chat_completion = self.groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are an AI assistant that generates professional resumes in text format."
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=self.model_name,
                temperature=0.8,
            )
            return chat_completion.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating resume: {e}")
            return "Failed to generate resume."

    def generate_cover_letter(self, profile_data, job_description, tone="Professional"):
        if not self.groq_client:
            return "AI Processor not initialized. Cannot generate cover letter."
        try:
            prompt = f"""
            Generate a cover letter based on the provided profile data and job description.
            Adopt a {tone} tone.
            The cover letter should highlight relevant skills and experiences from the profile data that match the job description requirements.
            Format the cover letter in standard business letter format, including placeholders for recipient details (e.g., [Hiring Manager Name]), and conclude with a professional closing.
            Return the cover letter content in HTML format, suitable for rendering directly in a web browser or email. Ensure the HTML is clean and basic, primarily using paragraphs and line breaks.

            Profile Data:
            {json.dumps(profile_data, indent=2)}

            Job Description:
            {job_description}

            Cover Letter ({tone} Tone, HTML format):
            """
            chat_completion = self.groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": f"You are an AI assistant that generates cover letters in HTML format with a {tone} tone."
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=self.model_name,
                temperature=0.7,
            )
            cover_letter_html = chat_completion.choices[0].message.content.strip()

            # Basic cleanup: remove any leading/trailing text outside of the main HTML structure
            # This is a simple approach and might need refinement based on model output
            # Look for the first '<' character and the last '>' character
            start_index = cover_letter_html.find('<')
            end_index = cover_letter_html.rfind('>')

            if start_index != -1 and end_index != -1 and end_index > start_index:
                cleaned_html = cover_letter_html[start_index : end_index + 1]
            else:
                # If no HTML tags found, assume the whole response is the letter and wrap in <p>
                cleaned_html = "<p>" + cover_letter_html.replace('\\n', '<br>') + "</p>"

            # --- Start of added cleanup for <think> tags --
            # Remove content within <think>...</think> tags
            cleaned_html = re.sub(r'<think>.*?<\/think>', '', cleaned_html, flags=re.DOTALL)

            # Further cleanup: ensure it starts with a tag and remove any leading/trailing whitespace
            cleaned_html = cleaned_html.strip()
            # --- End of added cleanup for <think> tags --

            return cleaned_html

        except Exception as e:
            print(f"Error generating cover letter: {e}")
            return "<p>Failed to generate cover letter.</p>"

    def get_cover_letter_templates(self):
        # In a real application, this might load templates from files or a database
        return ["Professional", "Formal", "Friendly"] # Example tones/templates

    # --- Profile Optimizer Methods ---

    def calculate_ats_score(self, profile_data: Dict, job_description: str = "") -> int:
        """Simulate calculating an ATS compatibility score based on relevant profile sections and job description."""
        # Placeholder: Implement actual ATS scoring logic here
        
        score = 0
        
        # --- Score based on Profile Data Completeness (basic) ---
        if profile_data.get('full_name'): score += 5
        if profile_data.get('email'): score += 2
        if profile_data.get('phone'): score += 2
        if profile_data.get('location'): score += 3
        if profile_data.get('summary') or profile_data.get('about_me'): score += 15
        if profile_data.get('experience'): score += 10 # Reduced weight as keywords focus moves elsewhere
        if profile_data.get('education'): score += 5    # Reduced weight
        
        # Adjust skills score based on presence and format (list/dict)
        skills_data = profile_data.get('skills')
        if skills_data:
            if isinstance(skills_data, list) and skills_data:
                 score += 10
            elif isinstance(skills_data, dict) and any(skills_data.values()):
                 score += 10

        # --- Keyword Overlap Score (Focus on Skills and Summary) ---
        profile_relevant_text = ""
        
        # Add Summary/About Me text
        if profile_data.get('summary'):
            profile_relevant_text += profile_data['summary'] + " "
        elif profile_data.get('about_me'):
             profile_relevant_text += profile_data['about_me'] + " "
             
        # Add Skills text (focus on Technical and Soft Skills if dictionary)
        if skills_data:
            if isinstance(skills_data, list): # Case: Skills extracted as a list
                profile_relevant_text += ", ".join(skills_data) + " "
            elif isinstance(skills_data, dict): # Case: Skills entered manually as a dictionary
                # Focus on Technical Skills and Soft Skills categories
                technical_skills = ", ".join(skills_data.get('Technical Skills', []))
                soft_skills = ", ".join(skills_data.get('Soft Skills', []))
                profile_relevant_text += f"{technical_skills}, {soft_skills}" + " "

        # Clean and tokenize the relevant profile text and job description
        profile_relevant_words = set(self.clean_and_tokenize(profile_relevant_text))
        job_keywords_cleaned = set(self.clean_and_tokenize(job_description))

        # Calculate overlap based on cleaned, relevant words
        if job_keywords_cleaned: # Only calculate keyword score if job description has keywords
             matched_keywords = job_keywords_cleaned.intersection(profile_relevant_words)
             # Assign score based on percentage of job keywords found in relevant profile sections
             keyword_score_percentage = (len(matched_keywords) / len(job_keywords_cleaned)) * 100
             score += min(int(keyword_score_percentage * 0.4), 40) # Keyword match contributes up to 40 points

        return min(score, 100) # Cap score at 100

    def get_optimization_suggestions(self, profile_data: Dict, job_description: str = "") -> Dict[str, List[str]]:
        """Generate intelligent optimization suggestions using LLM based on profile and job description."""
        if not self.groq_client:
            return {"General": ["AI suggestions unavailable. Please check your API key."]}
        
        try:
            # Prepare profile data for the prompt
            profile_summary = {
                "summary": profile_data.get('summary', profile_data.get('about_me', '')),
                "experience": profile_data.get('experience', []),
                "skills": profile_data.get('skills', {}),
                "education": profile_data.get('education', []),
                "projects": profile_data.get('projects', [])
            }
            
            prompt = f"""
            Analyze the following profile data and job description to provide specific, actionable suggestions for improving the profile/resume.
            Focus on making the profile more competitive for the target role.
            Return the suggestions in JSON format with categories: Summary, Experience, Skills, and General.
            Each category should contain a list of specific, actionable suggestions.

            Profile Data:
            {json.dumps(profile_summary, indent=2)}

            Job Description:
            {job_description}

            Provide suggestions in this JSON format:
            {{
                "Summary": ["suggestion1", "suggestion2"],
                "Experience": ["suggestion1", "suggestion2"],
                "Skills": ["suggestion1", "suggestion2"],
                "General": ["suggestion1", "suggestion2"]
            }}
            """
            
            chat_completion = self.groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert resume and profile optimizer. Provide specific, actionable suggestions to improve the profile for the target role."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model_name,
                temperature=0.7,
            )
            
            suggestions_text = chat_completion.choices[0].message.content.strip()
            
            # Extract JSON from the response
            try:
                # Find JSON in the response (it might be wrapped in markdown code blocks)
                json_match = re.search(r'```json\n(.*?)\n```', suggestions_text, re.DOTALL)
                if json_match:
                    suggestions_text = json_match.group(1)
                
                suggestions = json.loads(suggestions_text)
                return {k: v for k, v in suggestions.items() if v}  # Return only categories with suggestions
            except json.JSONDecodeError:
                print(f"Error parsing suggestions JSON: {suggestions_text}")
                return {"General": ["Error processing suggestions. Please try again."]}
                
        except Exception as e:
            print(f"Error generating optimization suggestions: {e}")
            return {"General": ["Error generating suggestions. Please try again."]}

    def analyze_keywords(self, profile_data: Dict, job_description: str = "") -> Dict[str, List[str]]:
        """Analyze keywords using LLM to identify strong matches and gaps between profile and job description."""
        if not self.groq_client:
            return {"strong": [], "missing": ["AI analysis unavailable. Please check your API key."]}
        
        try:
            # Prepare profile data for the prompt
            profile_summary = {
                "summary": profile_data.get('summary', profile_data.get('about_me', '')),
                "skills": profile_data.get('skills', {}),
                "experience": profile_data.get('experience', []),
                "projects": profile_data.get('projects', [])
            }
            
            prompt = f"""
            Analyze the following profile data and job description to identify:
            1. Strong keyword matches (skills, technologies, and qualifications that are clearly present in the profile)
            2. Missing keywords (important skills, technologies, or qualifications from the job description that are not clearly present in the profile)

            Profile Data:
            {json.dumps(profile_summary, indent=2)}

            Job Description:
            {job_description}

            Return the analysis in this JSON format:
            {{
                "strong": ["keyword1", "keyword2", ...],
                "missing": ["keyword1", "keyword2", ...]
            }}

            Guidelines:
            - Include only relevant technical skills, tools, methodologies, and key qualifications
            - Exclude generic terms and common words
            - Focus on specific, actionable keywords that would be important for the role
            - For strong matches, only include keywords that are clearly demonstrated in the profile
            - For missing keywords, prioritize the most important requirements from the job description
            """
            
            chat_completion = self.groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at analyzing resumes and job descriptions to identify key skills and qualifications."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model_name,
                temperature=0.5,  # Lower temperature for more focused analysis
            )
            
            analysis_text = chat_completion.choices[0].message.content.strip()
            
            # Extract JSON from the response
            try:
                # Find JSON in the response (it might be wrapped in markdown code blocks)
                json_match = re.search(r'```json\n(.*?)\n```', analysis_text, re.DOTALL)
                if json_match:
                    analysis_text = json_match.group(1)
                
                keywords = json.loads(analysis_text)
                return {
                    "strong": sorted(keywords.get("strong", [])),
                    "missing": sorted(keywords.get("missing", []))
                }
            except json.JSONDecodeError:
                print(f"Error parsing keywords JSON: {analysis_text}")
                return {"strong": [], "missing": ["Error processing keyword analysis. Please try again."]}
                
        except Exception as e:
            print(f"Error analyzing keywords: {e}")
            return {"strong": [], "missing": ["Error analyzing keywords. Please try again."]}

    def apply_optimization_suggestions(self, profile_data: Dict, suggestions: Dict[str, List[str]]) -> Dict:
        """Simulate applying optimization suggestions (no actual changes made in this placeholder)."""
        # Placeholder: In a real implementation, this would modify profile_data
        print("Simulating applying suggestions. No actual data changes made.")
        return profile_data # Return original data for now

    # --- Mock Interviewer Method ---

    def generate_mock_interview_questions(self, job_description, profile_data):
        """
        Generates mock interview questions based on the provided job description and profile data.
        """
        if not self.groq_client:
            print("AI Processor not initialized. Cannot generate interview questions.")
            return []
        try:
            prompt = f"""
            You are an AI interviewer. Generate a list of 5-10 relevant mock interview questions based on the following job description and candidate profile.
            Focus on questions that assess skills and experiences mentioned in the profile that are relevant to the job description.
            Format the output as a numbered list of questions.

            Job Description:
            {job_description}

            Candidate Profile Summary/Keywords:
            {json.dumps(profile_data.get('summary', '') + ' ' + ', '.join(profile_data.get('skills', [])), indent=2)}

            Generate 5-10 Mock Interview Questions (numbered list):
            """
            print("Sending prompt to LLM for interview question generation...")
            chat_completion = self.groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are an AI that generates mock interview questions."
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=self.model_name,
                temperature=0.7,
            )
            questions_text = chat_completion.choices[0].message.content.strip()
            print(f"Received response from LLM:\n{questions_text}")

            # --- Start of refined question extraction logic ---
            questions_list = []
            # Split the text into lines
            lines = questions_text.split('\n')

            # Iterate through lines and extract numbered questions, ignoring lines within <think> tags
            in_think_block = False
            for line in lines:
                stripped_line = line.strip()
                if stripped_line.startswith('<think>'):
                    in_think_block = True
                    continue
                elif stripped_line.endswith('</think>'):
                    in_think_block = False
                    continue

                if not in_think_block:
                    # Check if the line starts with a number followed by a period and optional space
                    match = re.match(r'^\s*\d+\.?\s*(.*)$', stripped_line)
                    if match:
                        cleaned_question = match.group(1).strip()
                        if cleaned_question:
                            questions_list.append(cleaned_question)

            # Fallback: If no numbered list found or extraction failed, split by lines and do basic cleaning (less ideal)
            # This fallback is less likely needed with the improved logic but kept as a safeguard.
            if not questions_list:
                print("Warning: Could not find or extract numbered list after filtering think blocks. Attempting line-by-line split as fallback.")
                questions_list = [line.strip() for line in questions_text.split('\n') if line.strip() and len(line.split()) > 3 and not line.strip().startswith('<')] # Added filter for lines starting with < (like <think>)
            # --- End of refined question extraction logic ---

            print(f"Generated questions list: {questions_list}")
            return questions_list

        except Exception as e:
            print(f"Error generating mock interview questions: {e}")
            return [] 