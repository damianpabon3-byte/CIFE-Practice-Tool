"""
CIFE Edu-Suite - Main Application
===================================
A production-ready Streamlit application for generating gamified,
interactive quizzes from student notebook photos.

Workflow:
1. Upload: Teacher uploads notebook image(s)
2. Analyze: GPT-4o Vision transcribes and identifies content
3. Generate: GPT-4o creates pedagogical quiz questions
4. Edit: Human-in-the-loop review with st.data_editor
5. Action: Play interactive game or download PDF/DOCX

Author: CIFE Educational Technology
"""

import streamlit as st
import pandas as pd
import json
from typing import Optional

# Import custom modules
from modules.ui_components import (
    load_custom_css,
    render_header,
    render_wizard_steps,
    render_progress_bar,
    render_score_display,
    render_question_badge,
    render_feedback,
    render_celebration,
    render_empty_state
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


# ============================================
# Page Configuration
# ============================================
st.set_page_config(
    page_title="CIFE Edu-Suite",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================
# Session State Initialization
# ============================================
def init_session_state():
    """Initialize all session state variables."""

    # Game mode: "setup" or "play"
    if "game_mode" not in st.session_state:
        st.session_state.game_mode = "setup"

    # Wizard step: "upload", "analyze", "edit", "action", "play", "results"
    if "wizard_step" not in st.session_state:
        st.session_state.wizard_step = "upload"

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

    # Teacher mode (debug)
    if "teacher_mode" not in st.session_state:
        st.session_state.teacher_mode = False

    # Sound and animation toggles
    if "sound_enabled" not in st.session_state:
        st.session_state.sound_enabled = True

    if "animations_enabled" not in st.session_state:
        st.session_state.animations_enabled = True


def reset_to_setup():
    """Reset all state and return to setup mode."""
    st.session_state.game_mode = "setup"
    st.session_state.wizard_step = "upload"
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
    st.session_state.wizard_step = "play"
    st.session_state.current_question_index = 0
    st.session_state.score = 0
    st.session_state.streak = 0
    st.session_state.max_streak = 0
    st.session_state.wrong_answers = []
    st.session_state.answer_submitted = False


# ============================================
# Sidebar Configuration
# ============================================
def render_sidebar():
    """Render the sidebar with API key input and settings."""

    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <h1 style="color: white; font-family: 'Fredoka', sans-serif; font-size: 1.8rem;">
                📚 CIFE Edu-Suite
            </h1>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        # API Key input
        st.markdown("### 🔑 OpenAI API Key")
        api_key = st.text_input(
            "Enter your API key",
            type="password",
            key="openai_api_key",
            help="Required for image analysis and quiz generation"
        )

        if api_key:
            st.success("✓ API Key set")
        else:
            st.warning("⚠️ API Key required")

        st.divider()

        # Settings
        st.markdown("### ⚙️ Settings")

        st.session_state.sound_enabled = st.toggle(
            "🔊 Sound Effects",
            value=st.session_state.sound_enabled
        )

        st.session_state.animations_enabled = st.toggle(
            "✨ Animations",
            value=st.session_state.animations_enabled
        )

        st.session_state.teacher_mode = st.toggle(
            "👩‍🏫 Teacher Mode",
            value=st.session_state.teacher_mode,
            help="Show debug information and advanced options"
        )

        st.divider()

        # Debug info (Teacher Mode)
        if st.session_state.teacher_mode:
            st.markdown("### 🔧 Debug Info")
            st.json({
                "game_mode": st.session_state.game_mode,
                "wizard_step": st.session_state.wizard_step,
                "score": st.session_state.score,
                "streak": st.session_state.streak,
                "current_question": st.session_state.current_question_index,
                "total_questions": len(st.session_state.quiz_data)
            })

        # Reset button
        st.divider()
        if st.button("🔄 Start Over", use_container_width=True):
            reset_to_setup()
            st.rerun()

        return api_key


# ============================================
# Upload Step
# ============================================
def render_upload_step(api_key: str):
    """Render the image upload step."""

    render_header(
        "Upload Notebook Photos",
        "Take a photo of your student's notebook and upload it here",
        "📷"
    )

    render_wizard_steps(
        ["Upload", "Analyze", "Edit", "Action"],
        current_step=0
    )

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("""
        <div style="
            background: white;
            border-radius: 20px;
            padding: 2rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        ">
            <h3 style="margin-top: 0; font-family: 'Fredoka', sans-serif;">📸 Upload Images</h3>
            <p style="color: #6B7280;">
                Upload photos of handwritten student notebooks. Our AI will analyze
                the content and generate personalized practice questions.
            </p>
        </div>
        """, unsafe_allow_html=True)

        uploaded_files = st.file_uploader(
            "Choose notebook images",
            type=["jpg", "jpeg", "png", "webp"],
            accept_multiple_files=True,
            key="notebook_uploader"
        )

        if uploaded_files:
            st.session_state.uploaded_files = uploaded_files
            st.success(f"✓ {len(uploaded_files)} image(s) uploaded")

            # Show previews
            cols = st.columns(min(len(uploaded_files), 4))
            for i, file in enumerate(uploaded_files[:4]):
                with cols[i]:
                    st.image(file, caption=f"Image {i+1}", use_container_width=True)

    with col2:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #EEF2FF 0%, #E0E7FF 100%);
            border-radius: 20px;
            padding: 1.5rem;
            border: 2px solid #C7D2FE;
        ">
            <h4 style="margin-top: 0; color: #4F46E5;">💡 Tips for best results</h4>
            <ul style="color: #4338CA; padding-left: 1.2rem;">
                <li>Use good lighting</li>
                <li>Keep camera steady</li>
                <li>Include full page</li>
                <li>Avoid shadows</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Next button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(
            "🔍 Analyze Notebook →",
            use_container_width=True,
            disabled=not uploaded_files or not api_key
        ):
            st.session_state.wizard_step = "analyze"
            st.rerun()


# ============================================
# Analyze Step
# ============================================
def render_analyze_step(api_key: str):
    """Render the analysis step with progress."""

    render_header(
        "Analyzing Notebook",
        "Our AI is reading the handwriting and identifying concepts",
        "🔍"
    )

    render_wizard_steps(
        ["Upload", "Analyze", "Edit", "Action"],
        current_step=1
    )

    with st.spinner("Analyzing images..."):
        try:
            progress_placeholder = st.empty()
            progress_placeholder.info("📖 Reading handwriting...")

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

            progress_placeholder.success("✅ Analysis complete!")

            # Show analysis results
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("""
                <div style="background: white; border-radius: 16px; padding: 1.5rem;">
                    <h4 style="margin-top: 0;">📝 Transcribed Text</h4>
                </div>
                """, unsafe_allow_html=True)
                st.text_area(
                    "Transcription",
                    value=analysis.get("transcribed_text", ""),
                    height=200,
                    label_visibility="collapsed"
                )

            with col2:
                st.markdown(f"""
                <div style="background: white; border-radius: 16px; padding: 1.5rem;">
                    <h4 style="margin-top: 0;">📊 Analysis Results</h4>
                    <p><strong>Subject:</strong> {analysis.get("subject", "Unknown")}</p>
                    <p><strong>Grade Level:</strong> {analysis.get("detected_grade_level", "Unknown")}</p>
                    <p><strong>Core Concept:</strong> {analysis.get("core_concept", "Unknown")}</p>
                    <p><strong>Language:</strong> {analysis.get("language", "Unknown")}</p>
                </div>
                """, unsafe_allow_html=True)

                if analysis.get("key_terms"):
                    st.markdown("**Key Terms:**")
                    st.write(", ".join(analysis.get("key_terms", [])))

            st.markdown("<br>", unsafe_allow_html=True)

            # Question configuration
            st.markdown("### 📝 Quiz Configuration")

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
            st.info(f"Total questions: {total}")

            # Navigation buttons
            col1, col2, col3 = st.columns([1, 1, 1])

            with col1:
                if st.button("← Back to Upload"):
                    st.session_state.wizard_step = "upload"
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
                        st.session_state.wizard_step = "edit"
                        st.rerun()

        except Exception as e:
            st.error(f"❌ Analysis failed: {str(e)}")
            if st.button("← Try Again"):
                st.session_state.wizard_step = "upload"
                st.rerun()


# ============================================
# Edit Step (Human-in-the-Loop)
# ============================================
def render_edit_step():
    """Render the question editing step."""

    render_header(
        "Review & Edit Questions",
        "Make any changes before starting the quiz",
        "✏️"
    )

    render_wizard_steps(
        ["Upload", "Analyze", "Edit", "Action"],
        current_step=2
    )

    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);
        border-radius: 16px;
        padding: 1rem 1.5rem;
        border: 2px solid #FBBF24;
        margin-bottom: 1.5rem;
    ">
        <strong>👩‍🏫 Teacher Review:</strong> Edit questions, fix errors, or adjust difficulty below.
        Double-click any cell to edit.
    </div>
    """, unsafe_allow_html=True)

    # Data editor for questions
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

    st.markdown("<br>", unsafe_allow_html=True)

    # Quiz title input
    st.session_state.quiz_title = st.text_input(
        "Quiz Title",
        value=st.session_state.quiz_title,
        placeholder="Enter a title for this quiz"
    )

    # Navigation buttons
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("← Back"):
            st.session_state.wizard_step = "analyze"
            st.rerun()

    with col3:
        if st.button("Continue →", use_container_width=True):
            st.session_state.wizard_step = "action"
            st.rerun()


# ============================================
# Action Step (Play or Download)
# ============================================
def render_action_step():
    """Render the action selection step."""

    render_header(
        "Quiz Ready!",
        "Choose to play the interactive game or download for printing",
        "🎮"
    )

    render_wizard_steps(
        ["Upload", "Analyze", "Edit", "Action"],
        current_step=3
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #D1FAE5 0%, #A7F3D0 100%);
            border-radius: 24px;
            padding: 2rem;
            text-align: center;
            border: 3px solid #34D399;
            height: 300px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        ">
            <div style="font-size: 4rem;">🎮</div>
            <h2 style="color: #059669; font-family: 'Fredoka', sans-serif;">Play Game</h2>
            <p style="color: #047857;">Interactive quiz with scoring, streaks, and celebrations!</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🎮 Start Playing", use_container_width=True, key="play_btn"):
            start_game()
            st.rerun()

    with col2:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #EEF2FF 0%, #E0E7FF 100%);
            border-radius: 24px;
            padding: 2rem;
            text-align: center;
            border: 3px solid #818CF8;
            height: 300px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        ">
            <div style="font-size: 4rem;">📄</div>
            <h2 style="color: #4F46E5; font-family: 'Fredoka', sans-serif;">Download</h2>
            <p style="color: #4338CA;">Get PDF or Word document for printing</p>
        </div>
        """, unsafe_allow_html=True)

        # Download options
        st.markdown("<br>", unsafe_allow_html=True)

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
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← Back to Edit"):
        st.session_state.wizard_step = "edit"
        st.rerun()


# ============================================
# Play Step (Interactive Game)
# ============================================
def render_play_step():
    """Render the interactive quiz game."""

    quiz_data = st.session_state.quiz_data
    current_idx = st.session_state.current_question_index
    total_questions = len(quiz_data)

    if current_idx >= total_questions:
        st.session_state.wizard_step = "results"
        st.rerun()
        return

    current_q = quiz_data[current_idx]

    # Header with score
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
        # Streak message
        if st.session_state.streak > 0:
            st.markdown(f"""
            <div style="
                text-align: center;
                padding: 1rem;
                background: linear-gradient(135deg, #FF6B35 0%, #FF9F1C 100%);
                border-radius: 16px;
                color: white;
                font-family: 'Fredoka', sans-serif;
            ">
                {get_streak_message(st.session_state.streak)}
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Question card
    q_type = current_q.get("question_type", "multiple_choice")
    q_text = current_q.get("question_text", "")

    # Apply smart blank for short answer
    if q_type == "short_answer":
        q_text = create_smart_blank(q_text, current_q.get("correct_answer", ""))

    st.markdown(f"""
    <div style="
        background: white;
        border-radius: 24px;
        padding: 2rem;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    ">
        <div style="margin-bottom: 1rem;">
    """, unsafe_allow_html=True)

    render_question_badge(q_type)

    st.markdown(f"""
        </div>
        <h2 style="
            font-family: 'Fredoka', sans-serif;
            font-size: 1.5rem;
            color: #1F2937;
            margin: 0;
        ">{q_text}</h2>
    </div>
    """, unsafe_allow_html=True)

    # Answer options based on type
    if not st.session_state.answer_submitted:
        if q_type == "multiple_choice":
            render_mc_options(current_q)
        elif q_type == "true_false":
            render_tf_options(current_q)
        else:
            render_sa_input(current_q)
    else:
        # Show feedback
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
                    st.session_state.wizard_step = "results"
                    st.rerun()


def render_mc_options(question: dict):
    """Render multiple choice options."""
    options = question.get("options", [])
    labels = ["A", "B", "C", "D"]
    colors = ["#4F46E5", "#059669", "#DC2626", "#D97706"]

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
    """Process the submitted answer."""
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


# ============================================
# Results Step
# ============================================
def render_results_step():
    """Render the final results screen."""

    total_questions = len(st.session_state.quiz_data)
    score = st.session_state.score
    max_score = total_questions * 15  # Approximate max with streaks

    # Calculate stats
    correct = total_questions - len(st.session_state.wrong_answers)
    percentage = (correct / total_questions * 100) if total_questions > 0 else 0

    grade, message, emoji = calculate_final_grade(correct, total_questions)

    # Celebration animation
    if st.session_state.animations_enabled and percentage >= 70:
        show_confetti()

    render_celebration(correct, total_questions)

    # Stats cards
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div style="
            background: white;
            border-radius: 20px;
            padding: 1.5rem;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        ">
            <div style="font-size: 2.5rem; font-weight: 700; color: #4F46E5;">{score}</div>
            <div style="color: #6B7280;">Total Points</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style="
            background: white;
            border-radius: 20px;
            padding: 1.5rem;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        ">
            <div style="font-size: 2.5rem; font-weight: 700; color: #FF6B35;">🔥 {st.session_state.max_streak}</div>
            <div style="color: #6B7280;">Best Streak</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div style="
            background: white;
            border-radius: 20px;
            padding: 1.5rem;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        ">
            <div style="font-size: 2.5rem; font-weight: 700; color: #34D399;">{grade}</div>
            <div style="color: #6B7280;">{message}</div>
        </div>
        """, unsafe_allow_html=True)

    # Wrong answers review
    if st.session_state.wrong_answers:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 📚 Review These Questions")

        for i, q in enumerate(st.session_state.wrong_answers):
            with st.expander(f"Question: {q.get('question_text', '')[:50]}..."):
                st.markdown(f"**Question:** {q.get('question_text', '')}")
                st.markdown(f"**Correct Answer:** {q.get('correct_answer', '')}")
                st.markdown(f"**Explanation:** {q.get('explanation', '')}")

    # Action buttons
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("🔄 Play Again", use_container_width=True):
            start_game()
            st.rerun()

    with col2:
        if st.button("✏️ Edit Quiz", use_container_width=True):
            st.session_state.game_mode = "setup"
            st.session_state.wizard_step = "edit"
            st.rerun()

    with col3:
        if st.button("📚 New Quiz", use_container_width=True):
            reset_to_setup()
            st.rerun()


# ============================================
# Main Application
# ============================================
def main():
    """Main application entry point."""

    # Initialize session state
    init_session_state()

    # Load custom CSS
    load_custom_css()

    # Render sidebar and get API key
    api_key = render_sidebar()

    # Route based on current step
    if st.session_state.game_mode == "setup":
        if st.session_state.wizard_step == "upload":
            render_upload_step(api_key)
        elif st.session_state.wizard_step == "analyze":
            render_analyze_step(api_key)
        elif st.session_state.wizard_step == "edit":
            render_edit_step()
        elif st.session_state.wizard_step == "action":
            render_action_step()
        else:
            render_upload_step(api_key)

    elif st.session_state.game_mode == "play":
        if st.session_state.wizard_step == "play":
            render_play_step()
        elif st.session_state.wizard_step == "results":
            render_results_step()
        else:
            render_play_step()


if __name__ == "__main__":
    main()
