"""
CIFE Edu-Suite - Exporter Module
=================================
Generates PDF and DOCX files for quiz worksheets and answer keys.
Creates professional, print-ready documents with proper formatting.
"""

import io
import json
from typing import List, Dict, Any, Optional
from datetime import datetime


def create_pdf(
    quiz_data: List[Dict[str, Any]],
    title: str = "Practice Quiz",
    subject: str = "",
    grade: str = "",
    include_answers: bool = False
) -> bytes:
    """
    Create a PDF document from quiz data.

    Generates a student worksheet (questions only) and optionally
    includes a teacher key with answers and explanations.

    Args:
        quiz_data: List of question dictionaries
        title: Title for the worksheet
        subject: Subject name to display
        grade: Grade level to display
        include_answers: Whether to include answer key

    Returns:
        PDF file as bytes
    """
    from fpdf import FPDF

    class QuizPDF(FPDF):
        def __init__(self):
            super().__init__()
            self.set_auto_page_break(auto=True, margin=20)

        def header(self):
            self.set_font('Helvetica', 'B', 16)
            self.cell(0, 10, title, 0, 1, 'C')
            if subject or grade:
                self.set_font('Helvetica', '', 10)
                info = f"{subject} - Grade {grade}" if subject and grade else (subject or f"Grade {grade}")
                self.cell(0, 6, info, 0, 1, 'C')
            self.set_font('Helvetica', 'I', 8)
            self.cell(0, 6, f"Generated: {datetime.now().strftime('%B %d, %Y')}", 0, 1, 'C')
            self.ln(5)

        def footer(self):
            self.set_y(-15)
            self.set_font('Helvetica', 'I', 8)
            self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    pdf = QuizPDF()
    pdf.add_page()

    # Student Worksheet
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 10, 'Student Worksheet', 0, 1, 'L')
    pdf.set_draw_color(79, 70, 229)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)

    # Name and Date fields
    pdf.set_font('Helvetica', '', 11)
    pdf.cell(40, 8, 'Name: _______________________', 0, 0, 'L')
    pdf.cell(0, 8, 'Date: ____________', 0, 1, 'R')
    pdf.ln(8)

    # Questions
    for i, q in enumerate(quiz_data, 1):
        q_type = q.get("question_type", "multiple_choice")
        q_text = q.get("question_text", "")

        # Question type badge
        type_labels = {
            "multiple_choice": "[MC]",
            "true_false": "[T/F]",
            "short_answer": "[SA]"
        }
        badge = type_labels.get(q_type, "")

        # Question header
        pdf.set_font('Helvetica', 'B', 11)
        pdf.multi_cell(0, 7, f"{i}. {badge} {q_text}")

        # Options based on type
        pdf.set_font('Helvetica', '', 10)

        if q_type == "multiple_choice":
            options = q.get("options", [])
            labels = ["A", "B", "C", "D"]
            for j, opt in enumerate(options):
                if j < len(labels):
                    pdf.cell(10, 6, '', 0, 0)  # Indent
                    pdf.cell(0, 6, f"({labels[j]}) {opt}", 0, 1)
            pdf.ln(2)

        elif q_type == "true_false":
            pdf.cell(10, 6, '', 0, 0)
            pdf.cell(0, 6, "(   ) True    (   ) False", 0, 1)
            pdf.ln(2)

        else:  # short_answer
            pdf.cell(10, 6, '', 0, 0)
            pdf.cell(0, 6, "Answer: _________________________________", 0, 1)
            pdf.ln(2)

        pdf.ln(3)

        # Check for page break
        if pdf.get_y() > 250:
            pdf.add_page()

    # Teacher Answer Key (separate page)
    if include_answers:
        pdf.add_page()
        pdf.set_font('Helvetica', 'B', 14)
        pdf.set_text_color(79, 70, 229)
        pdf.cell(0, 10, 'Teacher Answer Key', 0, 1, 'L')
        pdf.set_text_color(0, 0, 0)
        pdf.set_draw_color(79, 70, 229)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(8)

        for i, q in enumerate(quiz_data, 1):
            q_type = q.get("question_type", "multiple_choice")
            q_text = q.get("question_text", "")
            correct = q.get("correct_answer", "")
            explanation = q.get("explanation", "")

            # Question
            pdf.set_font('Helvetica', 'B', 10)
            pdf.multi_cell(0, 6, f"{i}. {q_text}")

            # Correct answer
            pdf.set_font('Helvetica', '', 10)
            pdf.set_text_color(34, 197, 94)  # Green
            pdf.cell(10, 6, '', 0, 0)
            pdf.multi_cell(0, 6, f"Correct Answer: {correct}")
            pdf.set_text_color(0, 0, 0)

            # Explanation
            if explanation:
                pdf.set_font('Helvetica', 'I', 9)
                pdf.set_text_color(100, 100, 100)
                pdf.cell(10, 5, '', 0, 0)
                pdf.multi_cell(0, 5, f"Explanation: {explanation}")
                pdf.set_text_color(0, 0, 0)

            pdf.ln(4)

            if pdf.get_y() > 250:
                pdf.add_page()

    # fpdf2 returns bytearray from output(dest='S'), handle all cases safely
    output = pdf.output(dest='S')
    if isinstance(output, bytearray):
        return bytes(output)
    if isinstance(output, str):
        return output.encode('latin-1')
    return bytes(output)


def create_docx(
    quiz_data: List[Dict[str, Any]],
    title: str = "Practice Quiz",
    subject: str = "",
    grade: str = "",
    include_answers: bool = True
) -> bytes:
    """
    Create a Word document from quiz data.

    Creates an editable document with proper formatting.

    Args:
        quiz_data: List of question dictionaries
        title: Title for the worksheet
        subject: Subject name
        grade: Grade level
        include_answers: Whether to include answer key section

    Returns:
        DOCX file as bytes
    """
    from docx import Document
    from docx.shared import Inches, Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.style import WD_STYLE_TYPE

    doc = Document()

    # Set default font
    style = doc.styles['Normal']
    style.font.name = 'Arial'
    style.font.size = Pt(11)

    # Title
    title_para = doc.add_heading(title, level=0)
    title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Subtitle
    if subject or grade:
        info = f"{subject} - Grade {grade}" if subject and grade else (subject or f"Grade {grade}")
        subtitle = doc.add_paragraph(info)
        subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
        subtitle.runs[0].font.size = Pt(12)
        subtitle.runs[0].font.color.rgb = RGBColor(100, 100, 100)

    # Date
    date_para = doc.add_paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y')}")
    date_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    date_para.runs[0].font.italic = True
    date_para.runs[0].font.size = Pt(9)

    doc.add_paragraph()

    # Student section header
    section_title = doc.add_heading('Student Worksheet', level=1)
    section_title.runs[0].font.color.rgb = RGBColor(79, 70, 229)

    # Name/Date line
    name_date = doc.add_paragraph()
    name_date.add_run("Name: _________________________    Date: ____________")

    doc.add_paragraph()

    # Questions
    for i, q in enumerate(quiz_data, 1):
        q_type = q.get("question_type", "multiple_choice")
        q_text = q.get("question_text", "")

        type_labels = {
            "multiple_choice": "[MC]",
            "true_false": "[T/F]",
            "short_answer": "[SA]"
        }
        badge = type_labels.get(q_type, "")

        # Question paragraph
        q_para = doc.add_paragraph()
        q_num = q_para.add_run(f"{i}. {badge} ")
        q_num.bold = True
        q_para.add_run(q_text)

        # Options
        if q_type == "multiple_choice":
            options = q.get("options", [])
            labels = ["A", "B", "C", "D"]
            for j, opt in enumerate(options):
                if j < len(labels):
                    opt_para = doc.add_paragraph()
                    opt_para.paragraph_format.left_indent = Inches(0.5)
                    opt_para.add_run(f"({labels[j]}) {opt}")

        elif q_type == "true_false":
            tf_para = doc.add_paragraph()
            tf_para.paragraph_format.left_indent = Inches(0.5)
            tf_para.add_run("(   ) True    (   ) False")

        else:  # short_answer
            ans_para = doc.add_paragraph()
            ans_para.paragraph_format.left_indent = Inches(0.5)
            ans_para.add_run("Answer: _________________________________")

        doc.add_paragraph()

    # Answer Key Section
    if include_answers:
        doc.add_page_break()

        key_title = doc.add_heading('Teacher Answer Key', level=1)
        key_title.runs[0].font.color.rgb = RGBColor(79, 70, 229)

        doc.add_paragraph()

        for i, q in enumerate(quiz_data, 1):
            q_text = q.get("question_text", "")
            correct = q.get("correct_answer", "")
            explanation = q.get("explanation", "")

            # Question
            q_para = doc.add_paragraph()
            q_num = q_para.add_run(f"{i}. ")
            q_num.bold = True
            q_para.add_run(q_text)

            # Correct answer
            ans_para = doc.add_paragraph()
            ans_para.paragraph_format.left_indent = Inches(0.3)
            ans_label = ans_para.add_run("Correct Answer: ")
            ans_label.bold = True
            ans_value = ans_para.add_run(correct)
            ans_value.font.color.rgb = RGBColor(34, 197, 94)

            # Explanation
            if explanation:
                exp_para = doc.add_paragraph()
                exp_para.paragraph_format.left_indent = Inches(0.3)
                exp_label = exp_para.add_run("Explanation: ")
                exp_label.italic = True
                exp_text = exp_para.add_run(explanation)
                exp_text.font.color.rgb = RGBColor(100, 100, 100)
                exp_text.font.size = Pt(10)

            doc.add_paragraph()

    # Save to bytes
    doc_bytes = io.BytesIO()
    doc.save(doc_bytes)
    doc_bytes.seek(0)
    return doc_bytes.read()


def create_json_export(
    quiz_data: List[Dict[str, Any]],
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """
    Create a JSON export of the quiz for sharing/importing.

    Args:
        quiz_data: List of question dictionaries
        metadata: Optional metadata (title, subject, grade, etc.)

    Returns:
        JSON string
    """
    export_data = {
        "version": "1.0",
        "created_at": datetime.now().isoformat(),
        "metadata": metadata or {},
        "questions": quiz_data
    }

    return json.dumps(export_data, indent=2, ensure_ascii=False)


def import_from_json(json_string: str) -> List[Dict[str, Any]]:
    """
    Import quiz data from a JSON string.

    Args:
        json_string: JSON string containing quiz data

    Returns:
        List of question dictionaries
    """
    try:
        data = json.loads(json_string)

        # Handle both formats (with or without metadata wrapper)
        if "questions" in data:
            return data["questions"]
        elif isinstance(data, list):
            return data
        else:
            raise ValueError("Invalid quiz format")

    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {str(e)}")


def create_answer_sheet_pdf(
    quiz_data: List[Dict[str, Any]],
    title: str = "Answer Sheet"
) -> bytes:
    """
    Create a simple bubble-style answer sheet for scanning.

    Args:
        quiz_data: List of question dictionaries
        title: Title for the answer sheet

    Returns:
        PDF file as bytes
    """
    from fpdf import FPDF

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=20)

    # Title
    pdf.set_font('Helvetica', 'B', 16)
    pdf.cell(0, 10, title, 0, 1, 'C')
    pdf.ln(5)

    # Name field
    pdf.set_font('Helvetica', '', 11)
    pdf.cell(0, 8, 'Name: _______________________________    Date: ____________', 0, 1, 'L')
    pdf.ln(10)

    # Instructions
    pdf.set_font('Helvetica', 'I', 9)
    pdf.multi_cell(0, 5, 'Instructions: Fill in the circle next to your answer choice. For short answer questions, write your response on the line provided.')
    pdf.ln(8)

    pdf.set_font('Helvetica', '', 10)

    for i, q in enumerate(quiz_data, 1):
        q_type = q.get("question_type", "multiple_choice")

        if q_type == "multiple_choice":
            pdf.cell(20, 8, f"{i}.", 0, 0, 'R')
            pdf.cell(0, 8, '(A)     (B)     (C)     (D)', 0, 1, 'L')

        elif q_type == "true_false":
            pdf.cell(20, 8, f"{i}.", 0, 0, 'R')
            pdf.cell(0, 8, '(T)     (F)', 0, 1, 'L')

        else:  # short_answer
            pdf.cell(20, 8, f"{i}.", 0, 0, 'R')
            pdf.cell(0, 8, '________________________________', 0, 1, 'L')

        if pdf.get_y() > 270:
            pdf.add_page()

    # fpdf2 returns bytearray from output(dest='S'), handle all cases safely
    output = pdf.output(dest='S')
    if isinstance(output, bytearray):
        return bytes(output)
    if isinstance(output, str):
        return output.encode('latin-1')
    return bytes(output)


def get_download_filename(title: str, extension: str) -> str:
    """
    Generate a safe filename for downloads.

    Args:
        title: Base title for the file
        extension: File extension (pdf, docx, json)

    Returns:
        Safe filename string
    """
    import re

    # Remove unsafe characters
    safe_title = re.sub(r'[^\w\s-]', '', title)
    safe_title = re.sub(r'[-\s]+', '_', safe_title)

    timestamp = datetime.now().strftime('%Y%m%d')

    return f"{safe_title}_{timestamp}.{extension}"
