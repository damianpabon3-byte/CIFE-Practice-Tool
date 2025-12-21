"""
CIFE Edu-Suite - Main Application Router
=========================================
A production-ready Streamlit application for generating gamified,
interactive quizzes from student notebook photos.

This file acts as a strict Router and State Manager that delegates
all visual rendering to the specialized UI module (modules/ui_components.py).

Wizard Workflow (4-Step Linear Path):
1. Ingestion: Teacher uploads notebook image(s) or loads saved quiz
2. Extraction: GPT-4o Vision transcribes and identifies content (cached)
3. Editor: Human-in-the-Loop review with st.data_editor
4. Publication/Play: Interactive game or download PDF/DOCX

Two-Stage Pipeline for Cost Control:
- Stage A: Notebook photos → analysis_result (cached by upload signature)
- Stage B: analysis_result + quiz_settings → quiz_data (form-gated)

Author: CIFE Educational Technology
"""

import streamlit as st
import pandas as pd
import json
import os
import hashlib
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple

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
    generate_quiz_from_analysis_batched,
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
    get_download_filename,
    import_from_json,
    QUIZ_SCHEMA_VERSION
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

    # Upload signature for caching analysis (avoid re-running extraction)
    if "upload_signature" not in st.session_state:
        st.session_state.upload_signature = None

    # Cached analysis signature to know if we already analyzed these files
    if "analysis_signature" not in st.session_state:
        st.session_state.analysis_signature = None

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

    # Generation state tracking (for two-stage pipeline)
    if "generation_in_progress" not in st.session_state:
        st.session_state.generation_in_progress = False

    if "generation_progress" not in st.session_state:
        st.session_state.generation_progress = 0

    if "last_generation_settings" not in st.session_state:
        st.session_state.last_generation_settings = None

    # Quiz difficulty setting
    if "quiz_difficulty" not in st.session_state:
        st.session_state.quiz_difficulty = "medium"

    # Language preference
    if "quiz_language" not in st.session_state:
        st.session_state.quiz_language = "auto"


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
# Helper: Compute upload signature for caching
# =============================================================================
def _compute_upload_signature(files) -> str:
    """
    Compute a signature from uploaded files to detect changes.
    Uses MD5 hash of file contents for reliable change detection.
    """
    if not files:
        return ""
    sig_parts = []
    for f in files:
        try:
            f.seek(0)
            content = f.read()
            f.seek(0)
            file_hash = hashlib.md5(content).hexdigest()[:12]
            sig_parts.append(f"{f.name}:{len(content)}:{file_hash}")
        except Exception:
            sig_parts.append(f"{f.name}:unknown")
    return "|".join(sorted(sig_parts))


def _validate_quiz_data(quiz_data: List[Dict]) -> Tuple[bool, List[str]]:
    """
    Validate quiz data structure and return validation status with warnings.

    Returns:
        Tuple of (is_valid, list_of_warnings)
    """
    warnings = []
    if not quiz_data:
        return False, ["No questions found"]

    for i, q in enumerate(quiz_data):
        q_num = i + 1
        q_type = q.get("question_type", "")

        # Check required fields
        if not q.get("question_text"):
            warnings.append(f"Q{q_num}: Missing question text")

        if not q.get("correct_answer"):
            warnings.append(f"Q{q_num}: Missing correct answer")

        # Type-specific validation
        if q_type == "multiple_choice":
            options = q.get("options", [])
            if len(options) < 2:
                warnings.append(f"Q{q_num}: MC needs at least 2 options")
            correct = q.get("correct_answer", "")
            if correct and correct not in options:
                warnings.append(f"Q{q_num}: Correct answer not in options")

        elif q_type == "true_false":
            correct = str(q.get("correct_answer", "")).lower()
            if correct not in ["true", "false", "verdadero", "falso"]:
                warnings.append(f"Q{q_num}: T/F answer must be True/False")

    is_valid = len([w for w in warnings if "Missing" in w]) == 0
    return is_valid, warnings


# =============================================================================
# Step 1: Ingestion (Upload)
# =============================================================================
def render_ingestion_step(api_key: str):
    """Render the image upload (Ingestion) step."""

    render_header(
        "Upload Notebook Photos",
        "Take a photo of your student's notebook or load a saved quiz",
        "📷"
    )

    render_wizard_steps(WIZARD_STEPS, current_step=0)

    # Two tabs: Upload Images vs Load Saved Quiz
    tab1, tab2 = st.tabs(["📸 Upload Images", "💾 Load Saved Quiz"])

    with tab1:
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
                # Compute and store upload signature
                st.session_state.upload_signature = _compute_upload_signature(uploaded_files)
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

    with tab2:
        render_card(
            content="""
            <p style="color: #6B7280; margin: 0;">
                Load a previously saved quiz (.json file) to edit or play again.
                This restores all quiz data including any saved game progress.
            </p>
            """,
            title="💾 Load Saved Quiz"
        )

        json_file = st.file_uploader(
            "Choose a saved quiz file",
            type=["json"],
            key="json_uploader"
        )

        if json_file:
            try:
                json_content = json_file.read().decode("utf-8")
                questions, metadata, analysis, quiz_settings, game_state = import_from_json(json_content)

                if not questions:
                    st.error("No questions found in the JSON file. Please check the file format.")
                else:
                    # Validate the quiz data
                    is_valid, warnings = _validate_quiz_data(questions)

                    render_info_box(
                        f"Found {len(questions)} questions in the saved quiz",
                        variant="success",
                        icon="✓"
                    )

                    # Show schema version info
                    schema_ver = metadata.get("schema_version", "1.0")
                    if schema_ver != QUIZ_SCHEMA_VERSION:
                        render_info_box(
                            f"Quiz format version {schema_ver} (current: {QUIZ_SCHEMA_VERSION})",
                            variant="info",
                            icon="ℹ️"
                        )

                    # Show metadata preview
                    if metadata:
                        col_meta1, col_meta2, col_meta3 = st.columns(3)
                        with col_meta1:
                            st.markdown(f"**Title:** {metadata.get('title', 'Untitled')}")
                        with col_meta2:
                            st.markdown(f"**Subject:** {metadata.get('subject', 'N/A')}")
                        with col_meta3:
                            st.markdown(f"**Grade:** {metadata.get('grade', 'N/A')}")

                    # Show validation warnings
                    if warnings:
                        with st.expander(f"⚠️ {len(warnings)} validation warning(s)"):
                            for w in warnings[:10]:
                                st.warning(w)
                            if len(warnings) > 10:
                                st.info(f"...and {len(warnings) - 10} more")

                    # Show game state if available
                    if game_state and game_state.get("current_index", 0) > 0:
                        render_info_box(
                            f"Saved progress found: Question {game_state.get('current_index', 0) + 1}, Score: {game_state.get('score', 0)}",
                            variant="info",
                            icon="📊"
                        )

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("✏️ Edit Quiz", use_container_width=True, key="json_edit"):
                            # Restore quiz data and metadata
                            st.session_state.quiz_data = questions
                            st.session_state.quiz_df = quiz_to_dataframe(questions)
                            st.session_state.quiz_title = metadata.get("title", "Imported Quiz")
                            st.session_state.quiz_subject = metadata.get("subject", "")
                            st.session_state.quiz_grade = metadata.get("grade", "")
                            # Restore analysis if available
                            if analysis:
                                st.session_state.analysis_result = analysis
                            st.session_state.wizard_step = STEP_EDITOR
                            st.rerun()

                    with col2:
                        if st.button("🎮 Play Now", use_container_width=True, key="json_play"):
                            # Restore and go to play
                            st.session_state.quiz_data = questions
                            st.session_state.quiz_df = quiz_to_dataframe(questions)
                            st.session_state.quiz_title = metadata.get("title", "Imported Quiz")
                            st.session_state.quiz_subject = metadata.get("subject", "")
                            st.session_state.quiz_grade = metadata.get("grade", "")
                            if analysis:
                                st.session_state.analysis_result = analysis
                            st.session_state.wizard_step = STEP_PLAY
                            st.session_state.game_mode = "setup"
                            st.rerun()

                    with col3:
                        # Resume option if game state exists
                        has_progress = game_state and game_state.get("current_index", 0) > 0
                        if st.button(
                            "▶️ Resume" if has_progress else "🎮 Start Fresh",
                            use_container_width=True,
                            key="json_resume",
                            disabled=not has_progress
                        ):
                            # Restore everything including game state
                            st.session_state.quiz_data = questions
                            st.session_state.quiz_df = quiz_to_dataframe(questions)
                            st.session_state.quiz_title = metadata.get("title", "Imported Quiz")
                            st.session_state.quiz_subject = metadata.get("subject", "")
                            st.session_state.quiz_grade = metadata.get("grade", "")
                            if analysis:
                                st.session_state.analysis_result = analysis
                            # Restore game state
                            if game_state:
                                st.session_state.current_question_index = game_state.get("current_index", 0)
                                st.session_state.score = game_state.get("score", 0)
                                st.session_state.streak = game_state.get("streak", 0)
                                st.session_state.max_streak = game_state.get("max_streak", 0)
                                st.session_state.wrong_answers = game_state.get("wrong_answers", [])
                            st.session_state.wizard_step = STEP_PLAY
                            st.session_state.game_mode = "play"
                            st.rerun()

            except json.JSONDecodeError as e:
                st.error(f"Invalid JSON format: {str(e)}")
                render_info_box("The file doesn't appear to be valid JSON. Please check the file.", variant="error")
            except Exception as e:
                st.error(f"Failed to load quiz: {str(e)}")
                render_info_box("Try re-exporting the quiz or contact support.", variant="warning")


# =============================================================================
# Step 2: Extraction (Analyze) - STAGE A of Two-Stage Pipeline
# =============================================================================
def render_extraction_step(api_key: str):
    """
    Render the analysis (Extraction) step with progress.

    STAGE A: Notebook photos → analysis_result
    - Only runs when uploads changed OR user clicks "Re-analyze"
    - Results are cached by upload_signature
    """

    render_header(
        "Analyzing Notebook",
        "Our AI is reading the handwriting and identifying concepts",
        "🔍"
    )

    render_wizard_steps(WIZARD_STEPS, current_step=1)

    # Check if we need to run analysis or can use cached result
    current_sig = st.session_state.upload_signature
    cached_sig = st.session_state.analysis_signature
    need_analysis = (current_sig != cached_sig) or (st.session_state.analysis_result is None)

    # Add Re-analyze button for manual refresh
    col_cache1, col_cache2 = st.columns([3, 1])
    with col_cache2:
        if st.session_state.analysis_result is not None:
            if st.button("🔄 Re-analyze", key="reanalyze_btn", use_container_width=True):
                st.session_state.analysis_signature = None
                st.session_state.analysis_result = None
                st.rerun()

    if need_analysis:
        with st.spinner("Analyzing images..."):
            try:
                progress_placeholder = st.empty()
                with progress_placeholder.container():
                    render_info_box("Reading handwriting...", variant="info", icon="📖")

                # Validate API key before calling OpenAI
                if not api_key or len(api_key.strip()) < 10:
                    raise ValueError("Invalid API key. Please provide a valid OpenAI API key.")

                # Check for uploaded files
                if not st.session_state.uploaded_files:
                    raise ValueError("No images uploaded. Please go back and upload notebook images.")

                # Analyze images with defensive error handling
                try:
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
                except Exception as api_error:
                    error_msg = str(api_error).lower()
                    if "rate limit" in error_msg or "429" in error_msg:
                        raise Exception("Rate limit exceeded. Please wait a moment and try again.")
                    elif "invalid" in error_msg and "key" in error_msg:
                        raise Exception("Invalid API key. Please check your OpenAI API key.")
                    elif "timeout" in error_msg:
                        raise Exception("Request timed out. Please try again.")
                    elif "connection" in error_msg:
                        raise Exception("Connection error. Please check your internet connection.")
                    else:
                        raise Exception(f"OpenAI API error: {str(api_error)[:100]}")

                st.session_state.analysis_result = analysis
                st.session_state.analysis_signature = current_sig
                st.session_state.quiz_subject = analysis.get("subject", "General")
                st.session_state.quiz_grade = analysis.get("detected_grade_level", "5")
                st.session_state.quiz_language = analysis.get("language", "English")

                progress_placeholder.empty()
                render_info_box("Analysis complete! Configure your quiz below.", variant="success", icon="✅")

            except Exception as e:
                render_info_box(f"Analysis failed: {str(e)}", variant="error", icon="❌")
                col_retry1, col_retry2 = st.columns(2)
                with col_retry1:
                    if st.button("← Back to Upload", use_container_width=True):
                        st.session_state.wizard_step = STEP_INGESTION
                        st.rerun()
                with col_retry2:
                    if st.button("🔄 Retry Analysis", use_container_width=True):
                        st.rerun()
                return
    else:
        render_info_box("Using cached analysis (same images detected). Click 'Re-analyze' to refresh.", variant="info", icon="📋")

    # Get analysis from session state
    analysis = st.session_state.analysis_result
    if not analysis:
        render_info_box("No analysis available. Please go back and upload images.", variant="error", icon="❌")
        if st.button("← Back to Upload"):
            st.session_state.wizard_step = STEP_INGESTION
            st.rerun()
        return

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

    # ==========================================================================
    # STAGE B: Quiz Configuration Form (form-gated to prevent rerun triggers)
    # ==========================================================================
    render_card(
        content="<p style='margin:0; color:#6B7280;'>Configure the number of questions to generate. Use the form below to prevent accidental re-generation.</p>",
        title="📝 Quiz Configuration (up to 80 per type)"
    )

    with st.form("quiz_config_form", clear_on_submit=False):
        # Question type counts
        col1, col2, col3 = st.columns(3)

        with col1:
            mc_count = st.number_input(
                "Multiple Choice",
                min_value=0,
                max_value=80,
                value=st.session_state.mc_count,
                help="4-option questions with one correct answer"
            )

        with col2:
            tf_count = st.number_input(
                "True/False",
                min_value=0,
                max_value=80,
                value=st.session_state.tf_count,
                help="Simple true or false statements"
            )

        with col3:
            sa_count = st.number_input(
                "Short Answer",
                min_value=0,
                max_value=80,
                value=st.session_state.sa_count,
                help="1-3 word fill-in-the-blank answers"
            )

        total = mc_count + tf_count + sa_count

        # Additional options
        col_opt1, col_opt2 = st.columns(2)
        with col_opt1:
            difficulty = st.selectbox(
                "Difficulty Level",
                options=["easy", "medium", "hard"],
                index=["easy", "medium", "hard"].index(st.session_state.quiz_difficulty),
                help="Adjusts question complexity"
            )
        with col_opt2:
            detected_lang = analysis.get("language", "English") if analysis else "English"
            language = st.selectbox(
                "Language",
                options=["auto", "English", "Spanish"],
                index=0,
                help=f"Detected: {detected_lang}"
            )

        # Show total and batch info
        if total > 0:
            batch_count = (total - 1) // 15 + 1
            if total > 15:
                st.info(f"📊 Total: {total} questions ({batch_count} batches of ~15 each)")
            else:
                st.info(f"📊 Total: {total} questions")
        else:
            st.warning("⚠️ Select at least one question type")

        # Form buttons
        st.markdown("---")
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
        with col_btn1:
            back_btn = st.form_submit_button("← Back to Upload", use_container_width=True)
        with col_btn2:
            # Placeholder for spacing
            pass
        with col_btn3:
            generate_btn = st.form_submit_button(
                "🚀 Generate Quiz",
                type="primary",
                use_container_width=True,
                disabled=(total == 0)
            )

    # Handle form submissions outside the form
    if back_btn:
        st.session_state.wizard_step = STEP_INGESTION
        st.rerun()

    if generate_btn and total > 0:
        # Store the form values in session state
        st.session_state.mc_count = mc_count
        st.session_state.tf_count = tf_count
        st.session_state.sa_count = sa_count
        st.session_state.quiz_difficulty = difficulty
        st.session_state.quiz_language = language if language != "auto" else analysis.get("language", "English")

        # Store generation settings for reference
        st.session_state.last_generation_settings = {
            "mc_count": mc_count,
            "tf_count": tf_count,
            "sa_count": sa_count,
            "difficulty": difficulty,
            "language": st.session_state.quiz_language,
            "timestamp": datetime.now().isoformat()
        }

        # Generate quiz with batched generation for large counts
        progress_container = st.empty()
        status_container = st.empty()

        def update_progress(current: int, total: int):
            """Callback to update progress bar during batched generation."""
            progress = current / total if total > 0 else 0
            progress_container.progress(progress, text=f"Generating questions: {current}/{total}")

        try:
            status_container.info(f"🔄 Generating {total} questions...")

            questions = generate_quiz_from_analysis_batched(
                analysis,
                api_key,
                mc_count=mc_count,
                tf_count=tf_count,
                sa_count=sa_count,
                batch_size=15,
                progress_callback=update_progress
            )

            progress_container.empty()

            if not questions:
                raise ValueError("No questions were generated. Please try again.")

            # Validate generated questions
            is_valid, warnings = _validate_quiz_data(questions)
            if warnings:
                status_container.warning(f"Generated {len(questions)} questions with {len(warnings)} validation notes")
            else:
                status_container.success(f"✅ Successfully generated {len(questions)} questions!")

            st.session_state.quiz_data = questions
            st.session_state.quiz_df = quiz_to_dataframe(questions)
            st.session_state.wizard_step = STEP_EDITOR
            st.rerun()

        except Exception as gen_error:
            progress_container.empty()
            error_msg = str(gen_error).lower()
            if "rate limit" in error_msg or "429" in error_msg:
                status_container.error("⚠️ Rate limit exceeded. Please wait a moment and try again.")
                render_info_box("OpenAI rate limits reset after a short wait. Try again in 30-60 seconds.", variant="warning")
            elif "invalid" in error_msg and "key" in error_msg:
                status_container.error("⚠️ Invalid API key. Please check your OpenAI API key in the sidebar.")
            elif "timeout" in error_msg:
                status_container.error("⚠️ Request timed out. Try generating fewer questions at once.")
            else:
                status_container.error(f"⚠️ Quiz generation failed: {str(gen_error)[:150]}")
            # Show retry button
            if st.button("🔄 Retry Generation", use_container_width=True):
                st.rerun()


# =============================================================================
# Step 3: Editor (Human-in-the-Loop)
# =============================================================================
def render_editor_step():
    """
    Render the question editing step with Human-in-the-Loop st.data_editor.
    Teacher Mode: Content verification before Play mode begins.
    Supports: multiple_choice, true_false, short_answer, matching, fill_in_blank
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

    # Show validation warnings if any
    if st.session_state.quiz_data:
        is_valid, warnings = _validate_quiz_data(st.session_state.quiz_data)
        if warnings:
            with st.expander(f"⚠️ {len(warnings)} validation issue(s) - Click to review"):
                for w in warnings[:15]:
                    st.warning(w)
                if len(warnings) > 15:
                    st.info(f"...and {len(warnings) - 15} more")

    # Data editor for questions - Human-in-the-Loop verification
    if st.session_state.quiz_df is not None:
        edited_df = st.data_editor(
            st.session_state.quiz_df,
            use_container_width=True,
            num_rows="dynamic",
            column_config={
                "Index": st.column_config.NumberColumn("Q#", disabled=True, width="small"),
                "Type": st.column_config.SelectboxColumn(
                    "Type",
                    options=["multiple_choice", "true_false", "short_answer", "matching", "fill_in_blank"],
                    required=True,
                    width="small"
                ),
                "Question": st.column_config.TextColumn("Question", width="large"),
                "Option A": st.column_config.TextColumn("A", help="For matching: use 'left:right; left2:right2' format"),
                "Option B": st.column_config.TextColumn("B"),
                "Option C": st.column_config.TextColumn("C"),
                "Option D": st.column_config.TextColumn("D"),
                "Correct Answer": st.column_config.TextColumn("Answer", width="medium"),
                "Explanation": st.column_config.TextColumn("Explanation", width="medium"),
                "Misconception": st.column_config.TextColumn("Misconception", width="small")
            },
            key="quiz_editor"
        )

        # Update quiz data from edited DataFrame
        st.session_state.quiz_df = edited_df
        st.session_state.quiz_data = dataframe_to_quiz(edited_df)

    # Quiz metadata section
    col_meta1, col_meta2 = st.columns(2)
    with col_meta1:
        st.session_state.quiz_title = st.text_input(
            "Quiz Title",
            value=st.session_state.quiz_title,
            placeholder="Enter a title for this quiz"
        )
    with col_meta2:
        st.text_input(
            "Subject",
            value=st.session_state.quiz_subject,
            placeholder="Auto-detected from analysis",
            disabled=True
        )

    # Navigation buttons
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("← Back to Extraction", use_container_width=True):
            st.session_state.wizard_step = STEP_EXTRACTION
            st.rerun()

    with col2:
        # Quick stats
        total_q = len(st.session_state.quiz_data) if st.session_state.quiz_data else 0
        st.info(f"📊 {total_q} questions ready")

    with col3:
        if st.button("Continue to Play →", use_container_width=True, type="primary"):
            st.session_state.wizard_step = STEP_PLAY
            st.session_state.game_mode = "setup"
            st.rerun()


# =============================================================================
# Step 4: Publication/Play (Action Selection)
# =============================================================================
@st.cache_data(show_spinner=False)
def _cached_create_pdf(quiz_data_json: str, title: str, subject: str, grade: str, include_answers: bool) -> bytes:
    """Cached PDF generation to avoid regenerating on every render."""
    import json
    quiz_data = json.loads(quiz_data_json)
    return create_pdf(quiz_data, title=title, subject=subject, grade=grade, include_answers=include_answers)


@st.cache_data(show_spinner=False)
def _cached_create_docx(quiz_data_json: str, title: str, subject: str, grade: str) -> bytes:
    """Cached DOCX generation to avoid regenerating on every render."""
    import json
    quiz_data = json.loads(quiz_data_json)
    return create_docx(quiz_data, title=title, subject=subject, grade=grade)


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

        # Serialize quiz data for caching (makes it hashable)
        quiz_data_json = json.dumps(st.session_state.quiz_data, ensure_ascii=False)

        # Download options - using cached generation
        dcol1, dcol2 = st.columns(2)

        with dcol1:
            # Student worksheet (no answers) - lazily cached
            try:
                pdf_student = _cached_create_pdf(
                    quiz_data_json,
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
            except Exception as e:
                render_info_box(f"PDF error: {str(e)[:50]}", variant="error", icon="⚠️")

        with dcol2:
            # Teacher key (with answers) - lazily cached
            try:
                pdf_teacher = _cached_create_pdf(
                    quiz_data_json,
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
            except Exception as e:
                render_info_box(f"PDF error: {str(e)[:50]}", variant="error", icon="⚠️")

        dcol3, dcol4 = st.columns(2)

        with dcol3:
            # Word document - lazily cached
            try:
                docx_file = _cached_create_docx(
                    quiz_data_json,
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
            except Exception as e:
                render_info_box(f"DOCX error: {str(e)[:50]}", variant="error", icon="⚠️")

        with dcol4:
            # JSON export with full state (lightweight, no caching needed)
            json_data = create_json_export(
                st.session_state.quiz_data,
                metadata={
                    "title": st.session_state.quiz_title,
                    "subject": st.session_state.quiz_subject,
                    "grade": st.session_state.quiz_grade,
                    "language": st.session_state.get("quiz_language", "English"),
                },
                analysis_result=st.session_state.analysis_result,
                quiz_settings=st.session_state.get("last_generation_settings"),
                game_state=None  # No game state on initial export
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
