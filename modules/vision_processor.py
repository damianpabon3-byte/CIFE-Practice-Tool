"""
CIFE Edu-Suite - Vision Processor Module
=========================================
Handles GPT-4o Vision API for analyzing student notebook images.
Transcribes handwriting, detects subject, grade level, and core concepts.
"""

import base64
import json
from typing import Dict, Any, Optional, List
from openai import OpenAI


def encode_image_to_base64(image_file) -> str:
    """
    Encode an uploaded image file to base64 string.

    Args:
        image_file: Streamlit UploadedFile object

    Returns:
        Base64 encoded string of the image
    """
    image_file.seek(0)
    return base64.standard_b64encode(image_file.read()).decode("utf-8")


def get_image_mime_type(filename: str) -> str:
    """
    Determine the MIME type based on file extension.

    Args:
        filename: Name of the file

    Returns:
        MIME type string
    """
    extension = filename.lower().split('.')[-1]
    mime_types = {
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'gif': 'image/gif',
        'webp': 'image/webp'
    }
    return mime_types.get(extension, 'image/jpeg')


def analyze_notebook_image(
    image_file,
    api_key: str,
    language_hint: str = "auto"
) -> Dict[str, Any]:
    """
    Analyze a student notebook image using GPT-4o Vision.

    Transcribes the handwritten text, identifies the subject,
    estimates grade level, and extracts core learning concepts.

    Args:
        image_file: Streamlit UploadedFile object containing the notebook image
        api_key: OpenAI API key
        language_hint: "auto", "english", or "spanish" for language detection

    Returns:
        Dictionary containing:
        - transcribed_text: Full text of the notes
        - subject: Detected subject (Math, Science, English, etc.)
        - detected_grade_level: Estimated grade level (1-12)
        - core_concept: Main learning concept identified
        - language: Detected language (English/Spanish)
        - confidence: Confidence score for the analysis
        - key_terms: List of important vocabulary/terms

    Raises:
        ValueError: If API key is invalid or empty
        Exception: If API call fails
    """
    if not api_key or not api_key.strip():
        raise ValueError("OpenAI API key is required")

    client = OpenAI(api_key=api_key)

    # Encode the image
    base64_image = encode_image_to_base64(image_file)
    mime_type = get_image_mime_type(image_file.name)

    # System prompt for pedagogical analysis
    system_prompt = """You are an expert pedagogue and educational content analyst.
Your task is to analyze handwritten student notebook pages with precision and educational insight.

When analyzing the image:
1. TRANSCRIBE all visible handwritten text exactly as written (preserve any errors or unique spellings)
2. IDENTIFY the academic subject (Math, Science, English/Language Arts, Social Studies, Art, Music, etc.)
3. ESTIMATE the grade level (1-12) based on content complexity, vocabulary, and concepts
4. EXTRACT the core learning concept being studied
5. DETECT the language (English or Spanish)
6. IDENTIFY key terms or vocabulary that are central to the content
7. Note any diagrams, formulas, or visual elements present

Respond ONLY with valid JSON in this exact format:
{
    "transcribed_text": "Full transcription of all text...",
    "subject": "Math",
    "detected_grade_level": "5",
    "core_concept": "Long Division with Remainders",
    "language": "English",
    "confidence": 0.85,
    "key_terms": ["dividend", "divisor", "quotient", "remainder"],
    "visual_elements": ["division bracket diagram", "worked examples"],
    "content_summary": "Brief 1-2 sentence summary of what the student is learning"
}

Important guidelines:
- Be accurate but not overly critical of handwriting variations
- Identify the MAIN subject even if multiple topics appear
- Grade level should reflect the complexity of the CONTENT, not handwriting quality
- Include ALL readable text in transcription
- If uncertain about any field, provide best estimate with lower confidence score
- Key terms should be actual vocabulary from the notes, not generic terms"""

    language_instruction = ""
    if language_hint == "spanish":
        language_instruction = "\n\nNote: The content is expected to be in Spanish. Transcribe in the original language."
    elif language_hint == "english":
        language_instruction = "\n\nNote: The content is expected to be in English."

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt + language_instruction
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Please analyze this student notebook page and provide the structured analysis."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{base64_image}",
                                "detail": "high"
                            }
                        }
                    ]
                }
            ],
            max_tokens=2000,
            temperature=0.3
        )

        # Extract and parse the response
        content = response.choices[0].message.content.strip()

        # Clean up potential markdown code blocks
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        # Parse JSON response
        result = json.loads(content)

        # Ensure all required fields exist with defaults
        default_result = {
            "transcribed_text": "",
            "subject": "General",
            "detected_grade_level": "5",
            "core_concept": "Unknown",
            "language": "English",
            "confidence": 0.5,
            "key_terms": [],
            "visual_elements": [],
            "content_summary": ""
        }

        for key, default_value in default_result.items():
            if key not in result:
                result[key] = default_value

        return result

    except json.JSONDecodeError as e:
        # Return a structured error response
        return {
            "transcribed_text": content if 'content' in locals() else "",
            "subject": "Unknown",
            "detected_grade_level": "5",
            "core_concept": "Could not parse response",
            "language": "Unknown",
            "confidence": 0.0,
            "key_terms": [],
            "visual_elements": [],
            "content_summary": "",
            "error": f"JSON parsing failed: {str(e)}"
        }
    except Exception as e:
        raise Exception(f"Vision API error: {str(e)}")


def analyze_multiple_images(
    image_files: List,
    api_key: str,
    language_hint: str = "auto"
) -> Dict[str, Any]:
    """
    Analyze multiple notebook images and combine the results.

    Args:
        image_files: List of Streamlit UploadedFile objects
        api_key: OpenAI API key
        language_hint: Language detection hint

    Returns:
        Combined analysis result with merged transcriptions and unified metadata
    """
    if not image_files:
        raise ValueError("At least one image is required")

    all_analyses = []
    all_text = []
    all_key_terms = set()
    subjects = []
    grade_levels = []

    for img_file in image_files:
        try:
            analysis = analyze_notebook_image(img_file, api_key, language_hint)
            all_analyses.append(analysis)
            all_text.append(analysis.get("transcribed_text", ""))
            all_key_terms.update(analysis.get("key_terms", []))
            subjects.append(analysis.get("subject", ""))

            # Parse grade level
            grade_str = analysis.get("detected_grade_level", "5")
            try:
                grade_levels.append(int(grade_str.replace("th", "").replace("st", "").replace("nd", "").replace("rd", "")))
            except ValueError:
                grade_levels.append(5)

        except Exception as e:
            all_analyses.append({"error": str(e)})

    # Combine results
    combined_text = "\n\n---\n\n".join(filter(None, all_text))

    # Determine most common subject
    from collections import Counter
    subject_counts = Counter(s for s in subjects if s and s != "Unknown")
    primary_subject = subject_counts.most_common(1)[0][0] if subject_counts else "General"

    # Average grade level
    avg_grade = round(sum(grade_levels) / len(grade_levels)) if grade_levels else 5

    # Determine language from first successful analysis
    detected_language = "English"
    for analysis in all_analyses:
        if "language" in analysis and analysis["language"] != "Unknown":
            detected_language = analysis["language"]
            break

    # Combine core concepts
    core_concepts = [a.get("core_concept", "") for a in all_analyses if a.get("core_concept")]
    combined_concept = "; ".join(set(filter(None, core_concepts)))

    return {
        "transcribed_text": combined_text,
        "subject": primary_subject,
        "detected_grade_level": str(avg_grade),
        "core_concept": combined_concept or "Multiple concepts",
        "language": detected_language,
        "confidence": sum(a.get("confidence", 0) for a in all_analyses) / len(all_analyses),
        "key_terms": list(all_key_terms),
        "individual_analyses": all_analyses,
        "image_count": len(image_files)
    }


def detect_language(text: str) -> str:
    """
    Simple language detection based on common words.

    Args:
        text: Text to analyze

    Returns:
        "English" or "Spanish"
    """
    spanish_indicators = [
        'que', 'de', 'el', 'la', 'los', 'las', 'es', 'en', 'un', 'una',
        'por', 'con', 'para', 'como', 'pero', 'si', 'su', 'al', 'del',
        'son', 'esta', 'esto', 'ese', 'eso', 'muy', 'bien', 'todo',
        'puede', 'tiene', 'hace', 'cuando', 'donde', 'porque', 'hay'
    ]

    english_indicators = [
        'the', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'could', 'should', 'may', 'might', 'must', 'shall', 'can',
        'need', 'dare', 'ought', 'used', 'to', 'of', 'in', 'for',
        'on', 'with', 'at', 'by', 'from', 'or', 'an', 'not'
    ]

    text_lower = text.lower()
    words = set(text_lower.split())

    spanish_count = sum(1 for word in spanish_indicators if word in words)
    english_count = sum(1 for word in english_indicators if word in words)

    if spanish_count > english_count:
        return "Spanish"
    return "English"
