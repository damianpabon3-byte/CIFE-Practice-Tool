"""
CIFE Edu-Suite - Content Generator Module
==========================================
Generates pedagogically-sound quizzes using GPT-4o.
Creates multiple-choice, true/false, and short-answer questions
with intelligent distractors based on common student misconceptions.
"""

import json
import math
import re
from typing import Dict, Any, List, Optional
from openai import OpenAI
import pandas as pd


def generate_quiz(
    text: str,
    grade: str,
    num_questions: int,
    api_key: str,
    subject: str = "General",
    language: str = "English",
    core_concept: str = "",
    question_types: Optional[Dict[str, int]] = None
) -> List[Dict[str, Any]]:
    """
    Generate a pedagogically-sound quiz from the given text using GPT-4o.

    The quiz uses common student misconceptions for distractors,
    adjusts vocabulary based on grade level, and provides explanations.

    Args:
        text: The source text/content to generate questions from
        grade: Grade level (1-12) to adjust difficulty and vocabulary
        num_questions: Total number of questions to generate
        api_key: OpenAI API key
        subject: Subject area (Math, Science, English, etc.)
        language: Target language (English or Spanish)
        core_concept: Main concept being assessed
        question_types: Dict specifying counts per type
            e.g., {"multiple_choice": 5, "true_false": 3, "short_answer": 2}

    Returns:
        List of question dictionaries with the schema:
        [
            {
                "question_text": "...",
                "question_type": "multiple_choice",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correct_answer_index": 0,
                "correct_answer": "Option A",
                "explanation": "Brief explanation...",
                "misconception_tag": "Common mistake addressed"
            }
        ]

    Raises:
        ValueError: If API key is invalid
        Exception: If API call fails
    """
    if not api_key or not api_key.strip():
        raise ValueError("OpenAI API key is required")

    if not text or not text.strip():
        raise ValueError("Source text is required to generate questions")

    client = OpenAI(api_key=api_key)

    # Default question type distribution if not specified
    if question_types is None:
        mc_count = max(1, int(num_questions * 0.5))
        tf_count = max(1, int(num_questions * 0.3))
        sa_count = num_questions - mc_count - tf_count
        question_types = {
            "multiple_choice": mc_count,
            "true_false": tf_count,
            "short_answer": sa_count
        }

    # Grade-level vocabulary guidance
    vocabulary_guidance = _get_vocabulary_guidance(grade)

    # Language-specific instructions
    lang_instruction = ""
    if language.lower() == "spanish":
        lang_instruction = """
IMPORTANT: Generate ALL content in Spanish, including:
- Questions
- Answer options
- Explanations
- True/False as "Verdadero/Falso"

Use appropriate Spanish educational terminology."""

    # Build the system prompt
    system_prompt = f"""You are an expert educational content creator specializing in K-12 curriculum.
Your task is to generate high-quality quiz questions that:
1. Are age-appropriate for Grade {grade} students
2. Test understanding of the core concept: "{core_concept}"
3. Use vocabulary suitable for the grade level
4. Include common student misconceptions as distractors (NOT random wrong answers)
5. Provide clear, educational explanations

{vocabulary_guidance}

SUBJECT AREA: {subject}
{lang_instruction}

PEDAGOGICAL GUIDELINES FOR DISTRACTORS:
- Multiple Choice: Each wrong answer should represent a REAL misconception students commonly have
- For Math: Use computational errors students typically make (wrong operation, place value errors, etc.)
- For Science: Use common misunderstandings about natural phenomena
- For Language Arts: Use grammar mistakes students frequently make
- NEVER use obviously wrong or silly answers

QUESTION DISTRIBUTION:
- Multiple Choice: {question_types.get('multiple_choice', 0)} questions (4 options each, labeled A-D)
- True/False: {question_types.get('true_false', 0)} questions
- Short Answer: {question_types.get('short_answer', 0)} questions (answer should be 1-3 words)

OUTPUT FORMAT - Respond ONLY with a valid JSON array:
[
    {{
        "question_text": "What is the result of 24 ÷ 6?",
        "question_type": "multiple_choice",
        "options": ["4", "6", "18", "30"],
        "correct_answer_index": 0,
        "correct_answer": "4",
        "explanation": "24 ÷ 6 = 4 because 6 × 4 = 24",
        "misconception_tag": "Confusing division with subtraction or addition"
    }},
    {{
        "question_text": "The sum of 15 + 8 equals 22.",
        "question_type": "true_false",
        "options": ["True", "False"],
        "correct_answer_index": 1,
        "correct_answer": "False",
        "explanation": "15 + 8 = 23, not 22. Count carefully!",
        "misconception_tag": "Careless addition errors"
    }},
    {{
        "question_text": "In division, the number being divided is called the _____.",
        "question_type": "short_answer",
        "options": [],
        "correct_answer_index": -1,
        "correct_answer": "dividend",
        "explanation": "In a division problem like 24 ÷ 6, the dividend (24) is the number being divided.",
        "misconception_tag": "Confusing dividend and divisor"
    }}
]

CRITICAL REQUIREMENTS:
1. Generate EXACTLY the number of questions requested for each type
2. Each question must have a unique misconception_tag
3. Explanations should be educational and encouraging
4. Short answer correct_answer should be 1-3 words maximum
5. All content must directly relate to the provided source text"""

    user_prompt = f"""Based on the following student notes/content, generate a quiz:

---SOURCE CONTENT---
{text}
---END CONTENT---

Generate:
- {question_types.get('multiple_choice', 0)} multiple choice questions
- {question_types.get('true_false', 0)} true/false questions
- {question_types.get('short_answer', 0)} short answer questions

Total: {num_questions} questions

Remember: Use real student misconceptions as distractors, not random errors."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=4000,
            temperature=0.7
        )

        content = response.choices[0].message.content.strip()

        # Clean up potential markdown
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        # Parse JSON
        questions = json.loads(content)

        # Validate and normalize each question
        validated_questions = []
        for i, q in enumerate(questions):
            validated_q = _validate_question(q, i)
            if validated_q:
                validated_questions.append(validated_q)

        return validated_questions

    except json.JSONDecodeError as e:
        raise Exception(f"Failed to parse quiz response: {str(e)}")
    except Exception as e:
        raise Exception(f"Quiz generation failed: {str(e)}")


def _get_vocabulary_guidance(grade: str) -> str:
    """Get vocabulary complexity guidance based on grade level."""
    try:
        grade_num = int(grade.replace("K", "0"))
    except ValueError:
        grade_num = 5

    if grade_num <= 2:
        return """VOCABULARY LEVEL: Very Simple
- Use short, common words (1-2 syllables)
- Avoid complex sentence structures
- Use concrete, familiar concepts
- Questions should be 1-2 sentences maximum"""

    elif grade_num <= 4:
        return """VOCABULARY LEVEL: Elementary
- Use simple but varied vocabulary
- Introduce grade-appropriate terms
- Keep sentences clear and direct
- Avoid idioms and figurative language"""

    elif grade_num <= 6:
        return """VOCABULARY LEVEL: Intermediate
- Use grade-level vocabulary
- Include some academic language
- Sentences can be more complex
- Context clues for new terms are helpful"""

    elif grade_num <= 8:
        return """VOCABULARY LEVEL: Middle School
- Use academic vocabulary appropriate for subject
- More complex sentence structures are acceptable
- Include subject-specific terminology
- Critical thinking questions are encouraged"""

    else:
        return """VOCABULARY LEVEL: High School
- Use sophisticated academic vocabulary
- Complex reasoning and analysis questions
- Subject-specific terminology expected
- Higher-order thinking skills assessed"""


def _validate_question(question: Dict, index: int) -> Optional[Dict]:
    """
    Validate and normalize a question dictionary.

    Returns None if the question is invalid.
    Supports: multiple_choice, true_false, short_answer, matching, fill_in_blank
    """
    required_fields = ["question_text", "question_type", "correct_answer"]

    # Check required fields
    for field in required_fields:
        if field not in question or not question[field]:
            return None

    # Normalize question type
    q_type = question["question_type"].lower().replace(" ", "_").replace("-", "_")

    # Map aliases to canonical types
    type_aliases = {
        "mc": "multiple_choice",
        "multiplechoice": "multiple_choice",
        "tf": "true_false",
        "truefalse": "true_false",
        "sa": "short_answer",
        "shortanswer": "short_answer",
        "match": "matching",
        "pairs": "matching",
        "fill": "fill_in_blank",
        "fillin": "fill_in_blank",
        "blank": "fill_in_blank",
        "fib": "fill_in_blank"
    }

    q_type = type_aliases.get(q_type, q_type)

    # Validate question type
    valid_types = ["multiple_choice", "true_false", "short_answer", "matching", "fill_in_blank"]
    if q_type not in valid_types:
        q_type = "multiple_choice"
    question["question_type"] = q_type

    # Type-specific validation
    if q_type == "multiple_choice":
        if "options" not in question or len(question.get("options", [])) < 2:
            return None
        # Pad to 4 options if needed
        while len(question["options"]) < 4:
            question["options"].append("")

    elif q_type == "true_false":
        # Normalize T/F options
        if "options" not in question or len(question.get("options", [])) < 2:
            question["options"] = ["True", "False"]

    elif q_type == "matching":
        # Matching needs pairs array
        if "pairs" not in question or not isinstance(question.get("pairs"), list):
            # Try to convert from other formats
            if "options" in question and isinstance(question["options"], list):
                # Convert options to pairs format
                pairs = []
                for i, opt in enumerate(question["options"][:10]):
                    if isinstance(opt, dict):
                        pairs.append(opt)
                    elif isinstance(opt, str) and ":" in opt:
                        left, right = opt.split(":", 1)
                        pairs.append({"left": left.strip(), "right": right.strip()})
                question["pairs"] = pairs if pairs else []
            else:
                question["pairs"] = []
        question["options"] = []  # Matching doesn't use traditional options

    elif q_type == "fill_in_blank":
        question["options"] = []

    else:  # short_answer
        question["options"] = []

    # Ensure correct_answer_index exists and is valid
    if "correct_answer_index" not in question:
        if q_type == "multiple_choice" and question["correct_answer"] in question.get("options", []):
            question["correct_answer_index"] = question["options"].index(question["correct_answer"])
        elif q_type == "true_false":
            correct_lower = str(question["correct_answer"]).lower()
            question["correct_answer_index"] = 0 if correct_lower in ["true", "verdadero"] else 1
        else:
            question["correct_answer_index"] = -1

    # Ensure explanation exists
    if "explanation" not in question or not question["explanation"]:
        question["explanation"] = "Great job reviewing this concept!"

    # Ensure misconception_tag exists
    if "misconception_tag" not in question or not question["misconception_tag"]:
        question["misconception_tag"] = "General concept check"

    return question


def generate_quiz_from_analysis(
    analysis: Dict[str, Any],
    api_key: str,
    mc_count: int = 5,
    tf_count: int = 3,
    sa_count: int = 2
) -> List[Dict[str, Any]]:
    """
    Generate a quiz from a vision analysis result.

    Convenience function that extracts relevant fields from analysis.

    Args:
        analysis: Result from analyze_notebook_image()
        api_key: OpenAI API key
        mc_count: Number of multiple choice questions
        tf_count: Number of true/false questions
        sa_count: Number of short answer questions

    Returns:
        List of question dictionaries
    """
    text = analysis.get("transcribed_text", "")
    grade = analysis.get("detected_grade_level", "5")
    subject = analysis.get("subject", "General")
    language = analysis.get("language", "English")
    core_concept = analysis.get("core_concept", "")

    total_questions = mc_count + tf_count + sa_count
    question_types = {
        "multiple_choice": mc_count,
        "true_false": tf_count,
        "short_answer": sa_count
    }

    return generate_quiz(
        text=text,
        grade=grade,
        num_questions=total_questions,
        api_key=api_key,
        subject=subject,
        language=language,
        core_concept=core_concept,
        question_types=question_types
    )


def generate_quiz_from_analysis_batched(
    analysis: Dict[str, Any],
    api_key: str,
    mc_count: int = 5,
    tf_count: int = 3,
    sa_count: int = 2,
    batch_size: int = 15,
    progress_callback: Optional[callable] = None
) -> List[Dict[str, Any]]:
    """
    Generate a quiz from a vision analysis result using batched API calls.

    This version is *count-accurate*: it will attempt to "top up" missing
    questions (due to duplicates, invalid outputs, or partial batches) until
    the requested counts are met or a retry limit is reached.

    Args:
        analysis: Result from analyze_notebook_image()
        api_key: OpenAI API key
        mc_count: Number of multiple choice questions
        tf_count: Number of true/false questions
        sa_count: Number of short answer questions
        batch_size: Maximum questions per API call (default 15)
        progress_callback: Optional callback(current, total) for UI progress

    Returns:
        List of question dictionaries (unique by normalized question_text)
    """
    text = analysis.get("transcribed_text", "") or analysis.get("content", "")
    grade = analysis.get("grade_level", "5")
    subject = analysis.get("subject", "General")
    language = analysis.get("language", "English")
    core_concept = analysis.get("core_concept", "") or analysis.get("main_topic", "")

    total_requested = int(mc_count) + int(tf_count) + int(sa_count)
    all_questions: List[Dict[str, Any]] = []
    seen_questions = set()

    def _norm(s: str) -> str:
        s = (s or "").strip().lower()
        s = re.sub(r"\s+", " ", s)
        return s

    def _append_unique(q: Dict[str, Any]) -> bool:
        q_text = _norm(q.get("question_text", ""))
        if not q_text:
            return False
        if q_text in seen_questions:
            return False
        seen_questions.add(q_text)
        all_questions.append(q)
        if progress_callback:
            progress_callback(len(all_questions), total_requested)
        return True

    def _overshoot_buffer(remaining: int) -> int:
        # Small overshoot reduces the chance we end short due to duplicates/invalid items.
        if remaining <= 3:
            return 2
        if remaining <= 10:
            return 3
        return min(5, max(2, math.ceil(remaining * 0.1)))

    def _generate_for_type(type_code: str, target: int):
        if target <= 0:
            return

        expected_type = {
            "mc": "multiple_choice",
            "tf": "true_false",
            "sa": "short_answer",
        }[type_code]

        # Safety: don't loop forever if the model keeps failing.
        max_attempts = max(6, math.ceil(target / max(1, batch_size)) + 4)
        attempts = 0
        stagnant_rounds = 0  # rounds with zero new unique questions

        while attempts < max_attempts:
            current_type_count = sum(1 for q in all_questions if q.get("question_type") == expected_type)
            remaining = target - current_type_count
            if remaining <= 0:
                break

            request_n = min(batch_size, remaining + _overshoot_buffer(remaining))
            question_types = {
                "multiple_choice": request_n if type_code == "mc" else 0,
                "true_false": request_n if type_code == "tf" else 0,
                "short_answer": request_n if type_code == "sa" else 0,
            }

            try:
                batch = generate_quiz(
                    text=text,
                    grade=grade,
                    num_questions=request_n,
                    api_key=api_key,
                    subject=subject,
                    language=language,
                    core_concept=core_concept,
                    question_types=question_types,
                )
            except Exception as e:
                print(f"Batch generation failed for {type_code}: {e}")
                attempts += 1
                continue

            added = 0
            for q in (batch or []):
                # Enforce expected type (models can sometimes mislabel).
                q["question_type"] = expected_type
                if _append_unique(q):
                    added += 1
                # Stop early if we already reached target for this type.
                current_type_count = sum(1 for qq in all_questions if qq.get("question_type") == expected_type)
                if current_type_count >= target:
                    break

            if added == 0:
                stagnant_rounds += 1
            else:
                stagnant_rounds = 0

            # If we're not making progress, bail out after a couple rounds.
            if stagnant_rounds >= 2:
                break

            attempts += 1

    # Generate each type with "top-up" behavior
    _generate_for_type("mc", int(mc_count))
    _generate_for_type("tf", int(tf_count))
    _generate_for_type("sa", int(sa_count))

    # Final safety: if we're still short (rare), attempt one generic top-up pass.
    if len(all_questions) < total_requested:
        remaining = total_requested - len(all_questions)
        request_n = min(batch_size, remaining + _overshoot_buffer(remaining))
        try:
            batch = generate_quiz(
                text=text,
                grade=grade,
                num_questions=request_n,
                api_key=api_key,
                subject=subject,
                language=language,
                core_concept=core_concept,
                question_types={
                    "multiple_choice": request_n,  # default to MC for filler
                    "true_false": 0,
                    "short_answer": 0,
                },
            )
            for q in (batch or []):
                q["question_type"] = "multiple_choice"
                _append_unique(q)
                if len(all_questions) >= total_requested:
                    break
        except Exception as e:
            print(f"Final top-up batch failed: {e}")

    # Trim any overshoot
    return all_questions[:total_requested]


def quiz_to_dataframe(questions: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Convert a list of questions to a Pandas DataFrame for editing.

    Supports: multiple_choice, true_false, short_answer, matching, fill_in_blank

    Args:
        questions: List of question dictionaries

    Returns:
        DataFrame with editable columns
    """
    rows = []
    for i, q in enumerate(questions):
        q_type = q.get("question_type", "multiple_choice")
        options = q.get("options", [])

        row = {
            "Index": i + 1,
            "Type": q_type,
            "Question": q.get("question_text", ""),
            "Option A": options[0] if len(options) > 0 else "",
            "Option B": options[1] if len(options) > 1 else "",
            "Option C": options[2] if len(options) > 2 else "",
            "Option D": options[3] if len(options) > 3 else "",
            "Correct Answer": q.get("correct_answer", ""),
            "Explanation": q.get("explanation", ""),
            "Misconception": q.get("misconception_tag", "")
        }

        # For matching questions, serialize pairs to Option A column
        if q_type == "matching" and "pairs" in q:
            pairs = q.get("pairs", [])
            pairs_str = "; ".join([f"{p.get('left', '')}:{p.get('right', '')}" for p in pairs[:10]])
            row["Option A"] = pairs_str
            row["Option B"] = "(matching pairs)"
            row["Option C"] = ""
            row["Option D"] = ""

        rows.append(row)

    return pd.DataFrame(rows)


def dataframe_to_quiz(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Convert an edited DataFrame back to quiz format.

    Supports: multiple_choice, true_false, short_answer, matching, fill_in_blank

    Args:
        df: Edited DataFrame from st.data_editor

    Returns:
        List of question dictionaries
    """
    questions = []

    for _, row in df.iterrows():
        q_type = str(row.get("Type", "multiple_choice")).lower().replace(" ", "_")
        correct_answer = str(row.get("Correct Answer", ""))

        # Normalize question type
        type_map = {
            "mc": "multiple_choice",
            "tf": "true_false",
            "sa": "short_answer",
            "match": "matching",
            "fib": "fill_in_blank"
        }
        q_type = type_map.get(q_type, q_type)

        # Build options based on question type
        if q_type == "multiple_choice":
            options = [
                str(row.get("Option A", "")),
                str(row.get("Option B", "")),
                str(row.get("Option C", "")),
                str(row.get("Option D", ""))
            ]
            # Filter out empty options
            options = [o for o in options if o.strip()]
            # Pad back to 4 if needed
            while len(options) < 4:
                options.append("")

        elif q_type == "true_false":
            options = ["True", "False"]

        elif q_type == "matching":
            options = []
            # Parse pairs from Option A
            pairs_str = str(row.get("Option A", ""))
            pairs = []
            if pairs_str and pairs_str != "(matching pairs)":
                for pair in pairs_str.split(";"):
                    if ":" in pair:
                        left, right = pair.split(":", 1)
                        pairs.append({"left": left.strip(), "right": right.strip()})

        else:  # short_answer, fill_in_blank
            options = []

        # Determine correct_answer_index
        if q_type == "multiple_choice" and correct_answer in options:
            correct_index = options.index(correct_answer)
        elif q_type == "true_false":
            correct_index = 0 if correct_answer.lower() in ["true", "verdadero"] else 1
        else:
            correct_index = -1

        question = {
            "question_text": str(row.get("Question", "")),
            "question_type": q_type,
            "options": options,
            "correct_answer_index": correct_index,
            "correct_answer": correct_answer,
            "explanation": str(row.get("Explanation", "")),
            "misconception_tag": str(row.get("Misconception", ""))
        }

        # Add pairs for matching questions
        if q_type == "matching":
            question["pairs"] = pairs

        questions.append(question)

    return questions


def create_smart_blank(question_text: str, answer: str) -> str:
    """
    Create a visual blank that hints at the answer length.

    Args:
        question_text: The question containing a blank placeholder
        answer: The correct answer to determine blank length

    Returns:
        Question text with formatted blank
    """
    blank_length = len(answer)
    visual_blank = " _ " * min(blank_length, 10)

    # Replace common blank placeholders
    for placeholder in ["_____", "____", "___", "__", "_", "[blank]", "[BLANK]"]:
        if placeholder in question_text:
            return question_text.replace(placeholder, visual_blank.strip())

    # If no placeholder found, append the blank
    if not any(p in question_text for p in ["_", "[blank]"]):
        return question_text + f" {visual_blank.strip()}"

    return question_text
