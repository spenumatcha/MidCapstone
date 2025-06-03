import re

def process_interview_questions(response):
    try:
        questions_text = response.choices[0].message.content.strip()

        # Extract questions using a more flexible regex
        # Look for lines starting with a number, potentially followed by a period and space
        questions_list = []
        # Use re.findall to find all occurrences matching the pattern
        matches = re.findall(r'^\s*\d+\.?\s*(.*)$', questions_text, re.MULTILINE)

        # Clean up extracted matches and filter out empty ones
        for match in matches:
            cleaned_question = match.strip()
            if cleaned_question:
                questions_list.append(cleaned_question)

        # Fallback: If no numbered list found, split by lines and do basic cleaning (less ideal)
        if not questions_list:
            print("Warning: No numbered list format detected. Attempting line-by-line split.")
            questions_list = [line.strip() for line in questions_text.split('\n') if line.strip() and len(line.split()) > 3] # Simple filter for short lines

        return questions_list

    except Exception as e:
        print(f"Error processing interview questions: {e}")
        return [] 