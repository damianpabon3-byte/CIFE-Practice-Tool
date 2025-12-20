"""
CIFE Edu-Suite - Main Application Router
=========================================
A production-ready Streamlit application for generating gamified,
interactive quizzes from student notebook photos.

This file acts as a strict Router and State Manager that delegates
all visual rendering to the specialized UI module (modules/ui_components.py).

Wizard Workflow (4-Step Linear Path):
1. Ingestion: Teacher uploads notebook image(s)
2. Extraction: GPT-4o Vision transcribes and identifies content
3. Editor: Human-in-the-Loop review with st.data_editor
4. Publication/Play: Interactive game or download PDF/DOCX

Author: CIFE Educational Technology
"""

import streamlit as st
import pandas as pd
import json
import os
from typing import Optional

# =============================================================================
# Import UI Components - Strict alignment with modules/ui_components.py
# =============================================================================
from modules.ui_components import (
    load_custom_css,
    render_header,
    render_wizard_steps,
    render_progress_bar,
    render_score_display,
    render_question_badge,
    render_feedback,
    render_celebration,
    render_empty_state,
    render_card,
    render_info_box,
    render_stat_card,
    render_option_card,
    render_card_button
)

from modules.vision_processor import analyze_notebook_image, analyze_multiple_images
from modules.content_generator import (
    generate_quiz,
    generate_quiz_from_analysis,
    quiz_to_dataframe,
    dataframe_to_quiz,
    create_smart_blank
)
from modules.gamification import (
    init_game_state,
    reset_game_state,
    check_answer,
    update_score,
    get_streak_message,
    show_confetti,
    calculate_final_grade,
    get_performance_stats
)
from modules.exporter import (
    create_pdf,
    create_docx,
    create_json_export,
    get_download_filename
)


# =============================================================================
# Page Configuration
# =============================================================================
st.set_page_config(
    page_title="CIFE Edu-Suite",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =============================================================================
# Wizard Step Constants - 4-Step Linear Path
# =============================================================================
WIZARD_STEPS = ["Ingestion", "Extraction", "Editor", "Play"]
STEP_INGESTION = "ingestion"
STEP_EXTRACTION = "extraction"
STEP_EDITOR = "editor"
STEP_PLAY = "play"
STEP_RESULTS = "results"


# =============================================================================
# Session State Initialization
# =============================================================================
def init_session_state():
    """Initialize all session state variables for state persistence."""

    # Game mode: "setup" or "play"
    if "game_mode" not in st.session_state:
        st.session_state.game_mode = "setup"

    # Wizard step: follows 4-step linear path
    if "wizard_step" not in st.session_state:
        st.session_state.wizard_step = STEP_INGESTION

    # Score tracking
    if "score" not in st.session_state:
        st.session_state.score = 0

    if "streak" not in st.session_state:
        st.session_state.streak = 0

    if "max_streak" not in st.session_state:
        st.session_state.max_streak = 0

    # Quiz data
    if "quiz_data" not in st.session_state:
        st.session_state.quiz_data = []

    if "quiz_df" not in st.session_state:
        st.session_state.quiz_df = None

    # Current question tracking
    if "current_question_index" not in st.session_state:
        st.session_state.current_question_index = 0

    # Analysis results
    if "analysis_result" not in st.session_state:
        st.session_state.analysis_result = None

    # Answer state
    if "answer_submitted" not in st.session_state:
        st.session_state.answer_submitted = False

    if "selected_answer" not in st.session_state:
        st.session_state.selected_answer = None

    if "user_text_answer" not in st.session_state:
        st.session_state.user_text_answer = ""

    # Wrong answers for review
    if "wrong_answers" not in st.session_state:
        st.session_state.wrong_answers = []

    # Quiz metadata
    if "quiz_title" not in st.session_state:
        st.session_state.quiz_title = "Practice Quiz"

    if "quiz_subject" not in st.session_state:
        st.session_state.quiz_subject = ""

    if "quiz_grade" not in st.session_state:
        st.session_state.quiz_grade = ""

    # Uploaded files cache
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = None

    # Generation settings
    if "mc_count" not in st.session_state:
        st.session_state.mc_count = 5

    if "tf_count" not in st.session_state:
        st.session_state.tf_count = 3

    if "sa_count" not in st.session_state:
        st.session_state.sa_count = 2

    # Teacher mode (Human-in-the-Loop)
    if "teacher_mode" not in st.session_state:
        st.session_state.teacher_mode = False

    # Sound and animation toggles
    if "sound_enabled" not in st.session_state:
        st.session_state.sound_enabled = True

    if "animations_enabled" not in st.session_state:
        st.session_state.animations_enabled = True


def get_current_step_index() -> int:
    """Get the current wizard step index for visual progress."""
    step_mapping = {
        STEP_INGESTION: 0,
        STEP_EXTRACTION: 1,
        STEP_EDITOR: 2,
        STEP_PLAY: 3,
        STEP_RESULTS: 3
    }
    return step_mapping.get(st.session_state.wizard_step, 0)


def reset_to_setup():
    """Reset all state and return to setup mode (Ingestion step)."""
    st.session_state.game_mode = "setup"
    st.session_state.wizard_step = STEP_INGESTION
    st.session_state.score = 0
    st.session_state.streak = 0
    st.session_state.max_streak = 0
    st.session_state.current_question_index = 0
    st.session_state.quiz_data = []
    st.session_state.quiz_df = None
    st.session_state.analysis_result = None
    st.session_state.answer_submitted = False
    st.session_state.selected_answer = None
    st.session_state.user_text_answer = ""
    st.session_state.wrong_answers = []
    st.session_state.uploaded_files = None


def start_game():
    """Transition from setup to play mode."""
    st.session_state.game_mode = "play"
    st.session_state.wizard_step = STEP_PLAY
    st.session_state.current_question_index = 0
    st.session_state.score = 0
    st.session_state.streak = 0
    st.session_state.max_streak = 0
    st.session_state.wrong_answers = []
    st.session_state.answer_submitted = False


# =============================================================================
# Sidebar Configuration (Rendered via UI components)
# =============================================================================
def render_sidebar():
    """Render the sidebar with API key input and settings."""

    with st.sidebar:
        # Sidebar header - delegated to UI component pattern
        render_card(
            content='<p style="margin: 0; font-size: 0.9rem; color: #6B7280;">Gamified Quiz Generator</p>',
            title="📚 CIFE Edu-Suite"
        )

        st.divider()

                # API Key (prefer Streamlit secrets / env; allow optional override)
        default_key = ""
        try:
            default_key = st.secrets.get("OPENAI_API_KEY", "")
        except Exception:
            default_key = ""
        default_key = default_key or os.getenv("OPENAI_API_KEY", "")

        with st.expander("🔑 API Key", expanded=not bool(default_key)):
            api_key_override = st.text_input(
                "API Key",
                type="password",
                key="openai_api_key_override",
                help="Optional override. Recommended: set OPENAI_API_KEY in Streamlit Secrets.",
                label_visibility="collapsed",
                placeholder=("Using Streamlit Secrets" if default_key else "Paste OpenAI API key here")
            )

        api_key = (api_key_override or default_key).strip()

        if api_key:
            if api_key_override:
                render_info_box("Using override API key", variant="success", icon="🔐")
            else:
                render_info_box("API key loaded from secrets", variant="success", icon="🔐")
        else:
            render_info_box("API key required to proceed (set OPENAI_API_KEY in Streamlit Secrets)", variant="warning", icon="⚠️")
# Reset button
        st.divider()
        if st.button("🔄 Start Over", use_container_width=True):
            reset_to_setup()
            st.rerun()

        return api_key


# =============================================================================
# Step 1: Ingestion (Upload)
# =============================================================================
def render_ingestion_step(api_key: str):
    """Render the image upload (Ingestion) step."""

    render_header(
        "Upload Notebook Photos",
        "Take a photo of your student's notebook and upload it here",
        "📷"
    )

    render_wizard_steps(WIZARD_STEPS, current_step=0)

    col1, col2 = st.columns([2, 1])

    with col1:
        render_card(
            content="""
            <p style="color: #6B7280; margin: 0;">
                Upload photos of handwritten student notebooks. Our AI will analyze
                the content and generate personalized practice questions.
            </p>
            """,
            title="📸 Upload Images"
        )

        uploaded_files = st.file_uploader(
            "Choose notebook images",
            type=["jpg", "jpeg", "png", "webp"],
            accept_multiple_files=True,
            key="notebook_uploader"
        )

        if uploaded_files:
            st.session_state.uploaded_files = uploaded_files
            render_info_box(
                f"{len(uploaded_files)} image(s) uploaded successfully",
                variant="success",
                icon="✓"
            )

            # Show previews
            cols = st.columns(min(len(uploaded_files), 4))
            for i, file in enumerate(uploaded_files[:4]):
                with cols[i]:
                    st.image(file, caption=f"Image {i+1}", use_container_width=True)

    with col2:
        render_card(
            content="""
            <ul style="color: #4338CA; padding-left: 1.2rem; margin: 0;">
                <li>Use good lighting</li>
                <li>Keep camera steady</li>
                <li>Include full page</li>
                <li>Avoid shadows</li>
            </ul>
            """,
            title="💡 Tips for best results",
            variant="warning"
        )

    # Next button - triggers visual update of progress circles
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(
            "🔍 Analyze Notebook →",
            use_container_width=True,
            disabled=not uploaded_files or not api_key
        ):
            st.session_state.wizard_step = STEP_EXTRACTION
            st.rerun()


# =============================================================================
# Step 2: Extraction (Analyze)
# =============================================================================
def render_extraction_step(api_key: str):
    """Render the analysis (Extraction) step with progress."""

    render_header(
        "Analyzing Notebook",
        "Our AI is reading the handwriting and identifying concepts",
        "🔍"
    )

    render_wizard_steps(WIZARD_STEPS, current_step=1)

    with st.spinner("Analyzing images..."):
        try:
            progress_placeholder = st.empty()
            with progress_placeholder.container():
                render_info_box("Reading handwriting...", variant="info", icon="📖")

            # Analyze images
            if len(st.session_state.uploaded_files) == 1:
                analysis = analyze_notebook_image(
                    st.session_state.uploaded_files[0],
                    api_key
                )
            else:
                analysis = analyze_multiple_images(
                    st.session_state.uploaded_files,
                    api_key
                )

            st.session_state.analysis_result = analysis
            st.session_state.quiz_subject = analysis.get("subject", "General")
            st.session_state.quiz_grade = analysis.get("detected_grade_level", "5")

            progress_placeholder.empty()
            render_info_box("Analysis complete!", variant="success", icon="✅")

            # Show analysis results using render_card
            col1, col2 = st.columns(2)

            with col1:
                render_card(
                    content="",
                    title="📝 Transcribed Text"
                )
                st.text_area(
                    "Transcription",
                    value=analysis.get("transcribed_text", ""),
                    height=200,
                    label_visibility="collapsed"
                )

            with col2:
                analysis_content = f"""
                <p><strong>Subject:</strong> {analysis.get("subject", "Unknown")}</p>
                <p><strong>Grade Level:</strong> {analysis.get("detected_grade_level", "Unknown")}</p>
                <p><strong>Core Concept:</strong> {analysis.get("core_concept", "Unknown")}</p>
                <p><strong>Language:</strong> {analysis.get("language", "Unknown")}</p>
                """
                render_card(
                    content=analysis_content,
                    title="📊 Analysis Results"
                )

                if analysis.get("key_terms"):
                    key_terms = ", ".join(analysis.get("key_terms", []))
                    render_info_box(f"Key Terms: {key_terms}", variant="info", icon="🏷️")

            # Question configuration
            render_card(
                content="<p style='margin:0; color:#6B7280;'>Configure the number of questions to generate</p>",
                title="📝 Quiz Configuration"
            )

            col1, col2, col3 = st.columns(3)

            with col1:
                st.session_state.mc_count = st.number_input(
                    "Multiple Choice Questions",
                    min_value=0,
                    max_value=10,
                    value=st.session_state.mc_count
                )

            with col2:
                st.session_state.tf_count = st.number_input(
                    "True/False Questions",
                    min_value=0,
                    max_value=10,
                    value=st.session_state.tf_count
                )

            with col3:
                st.session_state.sa_count = st.number_input(
                    "Short Answer Questions",
                    min_value=0,
                    max_value=10,
                    value=st.session_state.sa_count
                )

            total = st.session_state.mc_count + st.session_state.tf_count + st.session_state.sa_count
            render_info_box(f"Total questions: {total}", variant="info", icon="📊")

            # Navigation buttons
            col1, col2, col3 = st.columns([1, 1, 1])

            with col1:
                if st.button("← Back to Ingestion"):
                    st.session_state.wizard_step = STEP_INGESTION
                    st.rerun()

            with col3:
                if st.button(
                    "Generate Quiz →",
                    use_container_width=True,
                    disabled=total == 0
                ):
                    # Generate quiz
                    with st.spinner("Generating questions..."):
                        questions = generate_quiz_from_analysis(
                            analysis,
                            api_key,
                            mc_count=st.session_state.mc_count,
                            tf_count=st.session_state.tf_count,
                            sa_count=st.session_state.sa_count
                        )
                        st.session_state.quiz_data = questions
                        st.session_state.quiz_df = quiz_to_dataframe(questions)
                        st.session_state.wizard_step = STEP_EDITOR
                        st.rerun()

        except Exception as e:
            render_info_box(f"Analysis failed: {str(e)}", variant="error", icon="❌")
            if st.button("← Try Again"):
                st.session_state.wizard_step = STEP_INGESTION
                st.rerun()


# =============================================================================
# Step 3: Editor (Human-in-the-Loop)
# =============================================================================
def render_editor_step():
    """
    Render the question editing step with Human-in-the-Loop st.data_editor.
    Teacher Mode: Content verification before Play mode begins.
    """

    render_header(
        "Review & Edit Questions",
        "Human-in-the-Loop: Verify content before the quiz",
        "✏️"
    )

    render_wizard_steps(WIZARD_STEPS, current_step=2)

    render_card(
        content="""
        <p style="margin: 0;">
            <strong>👩‍🏫 Teacher Review:</strong> Edit questions, fix errors, or adjust difficulty below.
            Double-click any cell to edit. This is your Human-in-the-Loop checkpoint.
        </p>
        """,
        variant="warning"
    )

    # Data editor for questions - Human-in-the-Loop verification
    if st.session_state.quiz_df is not None:
        edited_df = st.data_editor(
            st.session_state.quiz_df,
            use_container_width=True,
            num_rows="dynamic",
            column_config={
                "Index": st.column_config.NumberColumn("Q#", disabled=True),
                "Type": st.column_config.SelectboxColumn(
                    "Type",
                    options=["multiple_choice", "true_false", "short_answer"],
                    required=True
                ),
                "Question": st.column_config.TextColumn("Question", width="large"),
                "Option A": st.column_config.TextColumn("A"),
                "Option B": st.column_config.TextColumn("B"),
                "Option C": st.column_config.TextColumn("C"),
                "Option D": st.column_config.TextColumn("D"),
                "Correct Answer": st.column_config.TextColumn("Answer"),
                "Explanation": st.column_config.TextColumn("Explanation", width="medium"),
                "Misconception": st.column_config.TextColumn("Misconception")
            },
            key="quiz_editor"
        )

        # Update quiz data from edited DataFrame
        st.session_state.quiz_df = edited_df
        st.session_state.quiz_data = dataframe_to_quiz(edited_df)

    # Quiz title input
    st.session_state.quiz_title = st.text_input(
        "Quiz Title",
        value=st.session_state.quiz_title,
        placeholder="Enter a title for this quiz"
    )

    # Navigation buttons
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("← Back to Extraction"):
            st.session_state.wizard_step = STEP_EXTRACTION
            st.rerun()

    with col3:
        if st.button("Continue to Play →", use_container_width=True):
            st.session_state.wizard_step = STEP_PLAY
            st.session_state.game_mode = "setup"
            st.rerun()


# =============================================================================
# Step 4: Publication/Play (Action Selection)
# =============================================================================
def render_action_step():
    """Render the action selection step (Publication or Play)."""

    render_header(
        "Quiz Ready!",
        "Choose to play the interactive game or download for printing",
        "🎮"
    )

    render_wizard_steps(WIZARD_STEPS, current_step=3)

    col1, col2 = st.columns(2)

    with col1:
        render_card(
            content="""
            <div style="text-align: center;">
                <div style="font-size: 4rem;">🎮</div>
                <h2 style="color: #059669; font-family: 'Fredoka', sans-serif; margin: 0.5rem 0;">Play Game</h2>
                <p style="color: #047857; margin: 0;">Interactive quiz with scoring, streaks, and celebrations!</p>
            </div>
            """,
            variant="success"
        )

        if st.button("🎮 Start Playing", use_container_width=True, key="play_btn"):
            start_game()
            st.rerun()

    with col2:
        render_card(
            content="""
            <div style="text-align: center;">
                <div style="font-size: 4rem;">📄</div>
                <h2 style="color: #4F46E5; font-family: 'Fredoka', sans-serif; margin: 0.5rem 0;">Download</h2>
                <p style="color: #4338CA; margin: 0;">Get PDF or Word document for printing</p>
            </div>
            """
        )

        # Download options
        dcol1, dcol2 = st.columns(2)

        with dcol1:
            # Student worksheet (no answers)
            pdf_student = create_pdf(
                st.session_state.quiz_data,
                title=st.session_state.quiz_title,
                subject=st.session_state.quiz_subject,
                grade=st.session_state.quiz_grade,
                include_answers=False
            )
            st.download_button(
                "📝 Student PDF",
                data=pdf_student,
                file_name=get_download_filename(st.session_state.quiz_title + "_Student", "pdf"),
                mime="application/pdf",
                use_container_width=True
            )

        with dcol2:
            # Teacher key (with answers)
            pdf_teacher = create_pdf(
                st.session_state.quiz_data,
                title=st.session_state.quiz_title,
                subject=st.session_state.quiz_subject,
                grade=st.session_state.quiz_grade,
                include_answers=True
            )
            st.download_button(
                "📋 Teacher PDF",
                data=pdf_teacher,
                file_name=get_download_filename(st.session_state.quiz_title + "_Teacher", "pdf"),
                mime="application/pdf",
                use_container_width=True
            )

        dcol3, dcol4 = st.columns(2)

        with dcol3:
            # Word document
            docx_file = create_docx(
                st.session_state.quiz_data,
                title=st.session_state.quiz_title,
                subject=st.session_state.quiz_subject,
                grade=st.session_state.quiz_grade
            )
            st.download_button(
                "📄 Word Doc",
                data=docx_file,
                file_name=get_download_filename(st.session_state.quiz_title, "docx"),
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )

        with dcol4:
            # JSON export
            json_data = create_json_export(
                st.session_state.quiz_data,
                metadata={
                    "title": st.session_state.quiz_title,
                    "subject": st.session_state.quiz_subject,
                    "grade": st.session_state.quiz_grade
                }
            )
            st.download_button(
                "💾 JSON Data",
                data=json_data,
                file_name=get_download_filename(st.session_state.quiz_title, "json"),
                mime="application/json",
                use_container_width=True
            )

    # Back button
    if st.button("← Back to Editor"):
        st.session_state.wizard_step = STEP_EDITOR
        st.rerun()


# =============================================================================
# Interactive Play Mode
# =============================================================================
def render_play_mode():
    """Render the interactive quiz game."""

    quiz_data = st.session_state.quiz_data
    current_idx = st.session_state.current_question_index
    total_questions = len(quiz_data)

    if current_idx >= total_questions:
        st.session_state.wizard_step = STEP_RESULTS
        st.rerun()
        return

    current_q = quiz_data[current_idx]

    # Header with score display - delegated to UI component
    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        render_score_display(
            st.session_state.score,
            total_questions * 10,  # Max possible score
            st.session_state.streak,
            show_streak=True
        )

    with col2:
        render_progress_bar(
            current_idx + 1,
            total_questions,
            label=f"Question {current_idx + 1} of {total_questions}"
        )

    with col3:
        # Streak message - rendered via UI component
        if st.session_state.streak > 0:
            streak_msg = get_streak_message(st.session_state.streak)
            render_card(
                content=f'<div style="text-align: center; font-size: 1.1rem;">{streak_msg}</div>',
                variant="warning"
            )

    # Question card
    q_type = current_q.get("question_type", "multiple_choice")
    q_text = current_q.get("question_text", "")

    # Apply smart blank for short answer
    if q_type == "short_answer":
        q_text = create_smart_blank(q_text, current_q.get("correct_answer", ""))

    # Render question badge via UI component
    render_question_badge(q_type)

    # Question text in card
    render_card(
        content=f'<h2 style="font-family: \'Fredoka\', sans-serif; font-size: 1.5rem; color: #1F2937; margin: 0;">{q_text}</h2>'
    )

    # Answer options based on type
    if not st.session_state.answer_submitted:
        if q_type == "multiple_choice":
            render_mc_options(current_q)
        elif q_type == "true_false":
            render_tf_options(current_q)
        else:
            render_sa_input(current_q)
    else:
        # Show feedback via UI component
        is_correct = check_answer(
            st.session_state.selected_answer,
            current_q.get("correct_answer_index", 0),
            st.session_state.user_text_answer,
            current_q.get("correct_answer", ""),
            q_type
        )

        render_feedback(
            is_correct,
            explanation=current_q.get("explanation", ""),
            correct_answer=current_q.get("correct_answer", "")
        )

        if is_correct and st.session_state.animations_enabled:
            if st.session_state.streak >= 3:
                show_confetti()

        # Next button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if current_idx + 1 < total_questions:
                if st.button("Next Question →", use_container_width=True):
                    st.session_state.current_question_index += 1
                    st.session_state.answer_submitted = False
                    st.session_state.selected_answer = None
                    st.session_state.user_text_answer = ""
                    st.rerun()
            else:
                if st.button("🏆 See Results", use_container_width=True):
                    st.session_state.wizard_step = STEP_RESULTS
                    st.rerun()


def render_mc_options(question: dict):
    """Render multiple choice options using UI components."""
    options = question.get("options", [])
    labels = ["A", "B", "C", "D"]

    col1, col2 = st.columns(2)

    for i, opt in enumerate(options):
        with col1 if i % 2 == 0 else col2:
            if st.button(
                f"{labels[i]}. {opt}",
                key=f"mc_opt_{i}",
                use_container_width=True
            ):
                st.session_state.selected_answer = i
                process_answer(question, i)
                st.rerun()


def render_tf_options(question: dict):
    """Render true/false options."""
    col1, col2 = st.columns(2)

    with col1:
        if st.button("✓ True", key="tf_true", use_container_width=True):
            st.session_state.selected_answer = 0
            process_answer(question, 0)
            st.rerun()

    with col2:
        if st.button("✗ False", key="tf_false", use_container_width=True):
            st.session_state.selected_answer = 1
            process_answer(question, 1)
            st.rerun()


def render_sa_input(question: dict):
    """Render short answer input."""
    user_answer = st.text_input(
        "Your answer:",
        key="sa_input",
        placeholder="Type your answer here..."
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Submit Answer", use_container_width=True, disabled=not user_answer):
            st.session_state.user_text_answer = user_answer
            process_answer(question, -1, user_answer)
            st.rerun()


def process_answer(question: dict, selected_idx: int, user_text: str = ""):
    """Process the submitted answer and update score/streak."""
    q_type = question.get("question_type", "multiple_choice")

    is_correct = check_answer(
        selected_idx,
        question.get("correct_answer_index", 0),
        user_text,
        question.get("correct_answer", ""),
        q_type
    )

    # Update score and streak
    if is_correct:
        st.session_state.score += 10 + min(st.session_state.streak, 5)
        st.session_state.streak += 1
        if st.session_state.streak > st.session_state.max_streak:
            st.session_state.max_streak = st.session_state.streak
    else:
        st.session_state.streak = 0
        st.session_state.wrong_answers.append(question)

    st.session_state.answer_submitted = True


# =============================================================================
# Results Screen
# =============================================================================
def render_results_step():
    """Render the final results screen using UI components."""

    total_questions = len(st.session_state.quiz_data)
    score = st.session_state.score

    # Calculate stats
    correct = total_questions - len(st.session_state.wrong_answers)
    percentage = (correct / total_questions * 100) if total_questions > 0 else 0

    grade, message, emoji = calculate_final_grade(correct, total_questions)

    # Celebration animation via UI component
    if st.session_state.animations_enabled and percentage >= 70:
        show_confetti()

    render_celebration(correct, total_questions)

    # Stats cards - using render_stat_card from UI components
    col1, col2, col3 = st.columns(3)

    with col1:
        render_stat_card(
            value=str(score),
            label="Total Points",
            icon="⭐",
            color="#4F46E5"
        )

    with col2:
        render_stat_card(
            value=f"🔥 {st.session_state.max_streak}",
            label="Best Streak",
            color="#FF6B35"
        )

    with col3:
        render_stat_card(
            value=grade,
            label=message,
            icon=emoji,
            color="#34D399"
        )

    # Wrong answers review
    if st.session_state.wrong_answers:
        render_card(
            content="<p style='margin:0;'>Review the questions you missed below</p>",
            title="📚 Review These Questions"
        )

        for i, q in enumerate(st.session_state.wrong_answers):
            with st.expander(f"Question: {q.get('question_text', '')[:50]}..."):
                render_info_box(f"Question: {q.get('question_text', '')}", variant="info")
                render_info_box(f"Correct Answer: {q.get('correct_answer', '')}", variant="success")
                if q.get('explanation'):
                    render_info_box(f"Explanation: {q.get('explanation', '')}", variant="info", icon="💡")

    # Action buttons
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("🔄 Play Again", use_container_width=True):
            start_game()
            st.rerun()

    with col2:
        if st.button("✏️ Edit Quiz", use_container_width=True):
            st.session_state.game_mode = "setup"
            st.session_state.wizard_step = STEP_EDITOR
            st.rerun()

    with col3:
        if st.button("📚 New Quiz", use_container_width=True):
            reset_to_setup()
            st.rerun()


# =============================================================================
# Main Application Router
# =============================================================================
def main():
    """
    Main application entry point.
    Acts as a strict Router and State Manager that delegates
    all visual rendering to the specialized UI module.
    """

    # CRITICAL: Load custom CSS FIRST to ensure Fredoka font and 60px touch targets
    load_custom_css()

    # Initialize session state for persistence
    init_session_state()

    # Render sidebar and get API key
    api_key = render_sidebar()

    # ==========================================================================
    # ROUTING LOGIC - Based on wizard_step state
    # ==========================================================================

    if st.session_state.game_mode == "setup":
        # Setup mode: 4-step wizard workflow
        if st.session_state.wizard_step == STEP_INGESTION:
            render_ingestion_step(api_key)
        elif st.session_state.wizard_step == STEP_EXTRACTION:
            render_extraction_step(api_key)
        elif st.session_state.wizard_step == STEP_EDITOR:
            render_editor_step()
        elif st.session_state.wizard_step == STEP_PLAY:
            render_action_step()
        else:
            # Default fallback to Ingestion
            render_ingestion_step(api_key)

    elif st.session_state.game_mode == "play":
        # Play mode: Interactive quiz or results
        if st.session_state.wizard_step == STEP_PLAY:
            render_play_mode()
        elif st.session_state.wizard_step == STEP_RESULTS:
            render_results_step()
        else:
            render_play_mode()


if __name__ == "__main__":
    main()
