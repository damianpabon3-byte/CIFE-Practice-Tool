"""
CIFE Quiz Platform - Backend Module
====================================
This module contains all the logic and AI-powered functions:
- OpenAI API integration
- Quiz generation (batched)
- Language detection
- Smart blank creation for short answer questions
- Answer checking logic
"""

import streamlit as st
import openai
import base64
import json
import random
import re
from datetime import datetime

# Configure the OpenAI client with API key from Streamlit secrets
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])


# ============================================
# LANGUAGE DETECTION
# ============================================
def detect_language(text):
    """
    Simple language detection based on common Spanish words.

    Args:
        text: The text to analyze

    Returns:
        'Spanish' if Spanish indicators are found, otherwise 'English'
    """
    spanish_indicators = ['el', 'la', 'los', 'las', 'de', 'en', 'que', 'es', 'un', 'una',
                         'para', 'con', 'por', 'como', 'del', 'al', 'son', 'está', 'este',
                         'esta', 'estos', 'qué', 'cómo', 'cuál', 'cuándo', 'dónde']
    text_lower = text.lower()
    spanish_count = sum(1 for word in spanish_indicators if f' {word} ' in f' {text_lower} ')
    return 'Spanish' if spanish_count >= 2 else 'English'


# ============================================
# SMART BLANK CREATION
# ============================================
def create_smart_blank(question_text, correct_answer):
    """
    Replace generic blank placeholders with a smart blank that matches
    the correct answer length (ignoring spaces).

    Example: If the answer is "fuerza" (6 letters), creates "_ _ _ _ _ _"

    Args:
        question_text: The question text containing a blank placeholder
        correct_answer: The correct answer to determine blank length

    Returns:
        The question text with the smart blank replacing the placeholder
    """
    # Calculate the length of the answer (ignoring spaces)
    answer_length = len(correct_answer.replace(" ", ""))

    # Create the smart blank: underscores separated by spaces for readability
    smart_blank = " ".join(["_"] * answer_length)

    # Regex pattern to find common blank placeholders:
    # - Multiple underscores: ____, ________, etc. (3 or more)
    # - Multiple dots: ...., ........, etc. (3 or more)
    # - Already spaced underscores: _ _ _ _ (3 or more underscores with spaces)
    blank_pattern = r'(?:_{3,}|\.{4,}|(?:_\s+){2,}_)'

    # Check if there's a blank placeholder in the question
    if re.search(blank_pattern, question_text):
        # Replace the first placeholder with the smart blank
        return re.sub(blank_pattern, smart_blank, question_text, count=1)
    else:
        # Edge case: no blank found, append smart blank at the end
        return f"{question_text} {smart_blank}"


# ============================================
# ANSWER CHECKING
# ============================================
def check_answer(user_answer, correct_answer, question_type):
    """
    Check if the answer is correct based on question type.

    Args:
        user_answer: The answer provided by the user
        correct_answer: The correct answer
        question_type: Type of question (short_answer, multiple_choice, true_false)

    Returns:
        True if the answer is correct, False otherwise
    """
    if question_type == "short_answer":
        # Case-insensitive comparison for short answer
        return user_answer.strip().lower() == correct_answer.strip().lower()
    else:
        return user_answer == correct_answer


# ============================================
# QUESTION TYPE DISPLAY INFO
# ============================================
def get_question_type_display(q_type):
    """
    Get the display info for question type badge.

    Args:
        q_type: The question type string

    Returns:
        Tuple of (badge_text, badge_class)
    """
    if q_type == "multiple_choice":
        return ("🎯 Multiple Choice", "badge-mc")
    elif q_type == "true_false":
        return ("✅ True or False", "badge-tf")
    else:
        return ("✏️ Short Answer", "badge-sa")


# ============================================
# AI QUIZ GENERATION - BATCHED
# ============================================
def generate_quiz_batch(uploaded_files, mc_count, tf_count, sa_count, batch_num, total_batches):
    """
    Generate a batch of quiz questions (max 10 per batch).

    Args:
        uploaded_files: List of uploaded image files
        mc_count: Number of multiple choice questions for this batch
        tf_count: Number of true/false questions for this batch
        sa_count: Number of short answer questions for this batch
        batch_num: Current batch number
        total_batches: Total number of batches

    Returns:
        Dictionary containing quiz metadata and questions
    """

    # Prepare the content list with text prompt and all images
    content_list = [
        {
            "type": "text",
            "text": f"Please analyze ALL of these notebook pages together as a complete set of notes on a topic. Detect the primary language of the handwritten notes and create practice questions covering the material. This is batch {batch_num} of {total_batches}. Generate varied questions that don't repeat themes from other batches. Output as pure JSON only."
        }
    ]

    # Add each image to the content list
    for uploaded_file in uploaded_files:
        uploaded_file.seek(0)
        image_bytes = uploaded_file.getvalue()
        base64_image = base64.b64encode(image_bytes).decode("utf-8")

        file_extension = uploaded_file.name.split(".")[-1].lower()
        mime_type = "image/jpeg" if file_extension in ["jpg", "jpeg"] else "image/png"

        content_list.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:{mime_type};base64,{base64_image}"
            }
        })

    # Build the question type distribution string
    type_requirements = []
    if mc_count > 0:
        type_requirements.append(f'{mc_count} multiple_choice questions')
    if tf_count > 0:
        type_requirements.append(f'{tf_count} true_false questions')
    if sa_count > 0:
        type_requirements.append(f'{sa_count} short_answer questions')

    type_string = ", ".join(type_requirements)
    total_in_batch = mc_count + tf_count + sa_count

    system_prompt = f"""You are a helpful teacher's assistant specialized in analyzing student notebooks and creating FUN, INTERACTIVE practice quizzes for students.

You will be provided with MULTIPLE images of a student's handwritten notes that together cover a complete topic or lesson.

IMPORTANT INSTRUCTIONS:

1. MULTI-PAGE ANALYSIS: Analyze ALL provided images as a cohesive set of notes. The pages together represent complete coverage of a topic - synthesize the information across all pages.

2. LANGUAGE DETECTION: Detect the primary language of the handwritten notes (e.g., Spanish, English). Generate the ENTIRE practice quiz in that SAME language.

3. GRADE LEVEL: Use Puerto Rico K-12 notation for grade levels:
   - Kindergarten through 6th grade: "Kinder", "1er Grado", "2do Grado", "3er Grado", "4to Grado", "5to Grado", "6to Grado"
   - Middle/High school: "7mo Grado", "8vo Grado", "9no Grado", "10mo Grado", "11mo Grado", "12mo Grado"

4. CONTENT ANALYSIS:
   - Identify the subject matter (e.g., Mathematics, Science, History)
   - Identify the specific topic spanning across the notes
   - Determine the appropriate grade level
   - Extract key concepts from ALL pages

5. QUIZ GENERATION: Create exactly {total_in_batch} questions with this distribution: {type_string}

   Question Types:
   - "multiple_choice" (4 options) - Concept understanding questions
   - "true_false" (2 options: Verdadero/Falso or True/False) - Fact verification
   - "short_answer" (student types answer) - Vocabulary, formulas, key terms

6. OUTPUT FORMAT: Output as valid JSON with NO markdown formatting:

{{
  "subject": "The detected subject",
  "topic": "The specific topic",
  "grade_level": "Using Puerto Rico notation (e.g., '10mo Grado')",
  "language": "Spanish or English",
  "questions": [
    {{
      "type": "multiple_choice",
      "q": "Question text",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "answer": "The correct option text"
    }},
    {{
      "type": "true_false",
      "q": "Statement to evaluate",
      "options": ["Verdadero", "Falso"],
      "answer": "Verdadero or Falso"
    }},
    {{
      "type": "short_answer",
      "q": "The _____ is the powerhouse of the cell.",
      "options": [],
      "answer": "mitochondria"
    }}
  ]
}}

REQUIREMENTS:
- Generate exactly {total_in_batch} questions as specified
- For multiple_choice: exactly 4 options
- For true_false: exactly 2 options
- For short_answer: empty options array, single word or short phrase answer
- ALL text must be in the SAME language as the notes
- Questions should be FUN and ENGAGING
- Vary difficulty levels
- This is batch {batch_num} of {total_batches} - vary the question themes"""

    # Make the API call
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": content_list}
        ],
        max_tokens=4000
    )

    # Extract and parse response
    raw_content = response.choices[0].message.content
    cleaned_content = raw_content.strip()
    if cleaned_content.startswith("```json"):
        cleaned_content = cleaned_content[7:]
    if cleaned_content.startswith("```"):
        cleaned_content = cleaned_content[3:]
    if cleaned_content.endswith("```"):
        cleaned_content = cleaned_content[:-3]
    cleaned_content = cleaned_content.strip()

    return json.loads(cleaned_content)


def generate_full_quiz(uploaded_files, mc_total, tf_total, sa_total, progress_placeholder):
    """
    Generate a full quiz with batched API calls.

    Args:
        uploaded_files: List of uploaded image files
        mc_total: Total number of multiple choice questions
        tf_total: Total number of true/false questions
        sa_total: Total number of short answer questions
        progress_placeholder: Streamlit placeholder for progress updates

    Returns:
        Complete quiz dictionary with metadata and all questions
    """
    total_questions = mc_total + tf_total + sa_total
    batch_size = 10
    num_batches = (total_questions + batch_size - 1) // batch_size

    all_questions = []
    quiz_metadata = None

    # Distribute question types across batches
    mc_remaining = mc_total
    tf_remaining = tf_total
    sa_remaining = sa_total

    for batch_num in range(1, num_batches + 1):
        # Calculate questions for this batch
        batch_total = min(batch_size, total_questions - len(all_questions))

        # Distribute types proportionally in this batch
        mc_in_batch = min(mc_remaining, max(1, int(batch_total * mc_total / total_questions)) if mc_remaining > 0 else 0)
        tf_in_batch = min(tf_remaining, max(1, int(batch_total * tf_total / total_questions)) if tf_remaining > 0 else 0)
        sa_in_batch = batch_total - mc_in_batch - tf_in_batch

        # Adjust if sa goes negative
        if sa_in_batch < 0:
            sa_in_batch = 0
            if tf_in_batch > 0:
                tf_in_batch = batch_total - mc_in_batch
            else:
                mc_in_batch = batch_total

        # Make sure we don't exceed remaining
        mc_in_batch = min(mc_in_batch, mc_remaining)
        tf_in_batch = min(tf_in_batch, tf_remaining)
        sa_in_batch = min(sa_in_batch, sa_remaining)

        # If batch total is less, fill with remaining types
        actual_batch = mc_in_batch + tf_in_batch + sa_in_batch
        if actual_batch < batch_total:
            diff = batch_total - actual_batch
            if mc_remaining - mc_in_batch > 0:
                add = min(diff, mc_remaining - mc_in_batch)
                mc_in_batch += add
                diff -= add
            if diff > 0 and tf_remaining - tf_in_batch > 0:
                add = min(diff, tf_remaining - tf_in_batch)
                tf_in_batch += add
                diff -= add
            if diff > 0 and sa_remaining - sa_in_batch > 0:
                add = min(diff, sa_remaining - sa_in_batch)
                sa_in_batch += add

        # Update progress
        progress = batch_num / num_batches
        progress_placeholder.progress(progress, f"Generating batch {batch_num} of {num_batches}... ({len(all_questions) + mc_in_batch + tf_in_batch + sa_in_batch}/{total_questions} questions)")

        # Generate this batch
        batch_result = generate_quiz_batch(
            uploaded_files, mc_in_batch, tf_in_batch, sa_in_batch,
            batch_num, num_batches
        )

        # Store metadata from first batch
        if quiz_metadata is None:
            quiz_metadata = {
                'subject': batch_result.get('subject', 'General'),
                'topic': batch_result.get('topic', 'Mixed Topics'),
                'grade_level': batch_result.get('grade_level', 'General'),
                'language': batch_result.get('language', 'English')
            }

        # Add questions from this batch
        all_questions.extend(batch_result.get('questions', []))

        # Update remaining counts
        for q in batch_result.get('questions', []):
            if q['type'] == 'multiple_choice':
                mc_remaining -= 1
            elif q['type'] == 'true_false':
                tf_remaining -= 1
            else:
                sa_remaining -= 1

    # Shuffle questions for variety
    random.shuffle(all_questions)

    # Build final quiz data
    final_quiz = {
        **quiz_metadata,
        'questions': all_questions,
        'created_at': datetime.now().isoformat(),
        'total_questions': len(all_questions)
    }

    return final_quiz
