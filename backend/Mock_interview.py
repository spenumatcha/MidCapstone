import re

def process_interview_questions(response):
    """
    Process (extract) a list of interview questions from an AI-generated response.
    (This function is nearly identical to generate_mock_interview_questions.)
    """
    try:
        questions_text = response.choices[0].message.content.strip()
        questions_list = []
        # Use re.findall to extract lines starting with a number (e.g. "1." or "1 ")
        matches = re.findall(r'^\s*\d+\.?\s*(.*)$', questions_text, re.MULTILINE)
        for match in matches:
            cleaned_question = match.strip()
            if cleaned_question:
                questions_list.append(cleaned_question)
        if not questions_list:
            print("Warning: No numbered list format detected. Attempting line-by-line split.")
            questions_list = [line.strip() for line in questions_text.split('\n') if line.strip() and len(line.split()) > 3]
        return questions_list
    except Exception as e:
        print(f"Error processing interview questions: {e}")
        return []


def generate_mock_interview_questions(response):
    """
    Generate (extract) a list of mock interview questions from an AI-generated response.
    (This function is nearly identical to process_interview_questions.)
    """
    try:
        questions_text = response.choices[0].message.content.strip()
        questions_list = []
        # Use re.findall to extract lines starting with a number (e.g. "1." or "1 ")
        matches = re.findall(r'^\s*\d+\.?\s*(.*)$', questions_text, re.MULTILINE)
        for match in matches:
            cleaned_question = match.strip()
            if cleaned_question:
                questions_list.append(cleaned_question)
        if not questions_list:
            print("Warning: No numbered list format detected. Attempting line-by-line split.")
            questions_list = [line.strip() for line in questions_text.split('\n') if line.strip() and len(line.split()) > 3]
        return questions_list
    except Exception as e:
        print(f"Error generating mock interview questions: {e}")
        return [] 