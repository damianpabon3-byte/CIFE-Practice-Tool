import streamlit as st
import openai
import base64
import json
import random
from datetime import datetime

# Configure the OpenAI client with API key from Streamlit secrets
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ============================================
# PAGE CONFIG
# ============================================
st.set_page_config(
    page_title="CIFE Quiz Platform 🎮",
    page_icon="🐯",
    layout="wide"
)

# ============================================
# CIFE BRAND THEME - Custom CSS Styling
# ============================================
st.markdown("""
    <style>
    /* Import Fredoka font from Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@400;500;600;700&display=swap');

    /* Top border accent in Brand Pink */
    .stApp {
        border-top: 5px solid #E04F80;
    }

    /* Apply Fredoka font to all headers and body */
    h1, h2, h3, h4, p, span, div, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stButton > button, .stTabs [data-baseweb="tab"] {
        font-family: 'Fredoka', sans-serif !important;
    }

    /* Main Title (h1) in Brand Pink */
    h1, .stMarkdown h1 {
        color: #E04F80 !important;
    }

    /* Subheaders (h2, h3) in Brand Pink */
    h2, h3, .stMarkdown h2, .stMarkdown h3 {
        color: #E04F80 !important;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #FFF8DC;
        padding: 10px;
        border-radius: 15px;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: white;
        border-radius: 10px;
        padding: 10px 20px;
        font-weight: 600;
        border: 2px solid #2AB7CA;
    }

    .stTabs [aria-selected="true"] {
        background-color: #2AB7CA !important;
        color: white !important;
    }

    /* Primary Button styling - Teal with rounded corners */
    .stButton > button[kind="primary"],
    .stButton > button[data-testid="baseButton-primary"] {
        background-color: #2AB7CA !important;
        border-color: #2AB7CA !important;
        border-radius: 20px !important;
        font-family: 'Fredoka', sans-serif !important;
        font-weight: 500 !important;
        padding: 0.5rem 2rem !important;
        transition: all 0.3s ease !important;
    }

    .stButton > button[kind="primary"]:hover,
    .stButton > button[data-testid="baseButton-primary"]:hover {
        background-color: #229AA8 !important;
        border-color: #229AA8 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(42, 183, 202, 0.4) !important;
    }

    /* Secondary buttons - for quiz options */
    .stButton > button[kind="secondary"],
    .stButton > button[data-testid="baseButton-secondary"] {
        background-color: #FFF8DC !important;
        border: 3px solid #2AB7CA !important;
        border-radius: 15px !important;
        font-family: 'Fredoka', sans-serif !important;
        font-weight: 500 !important;
        font-size: 1.1rem !important;
        padding: 1rem 1.5rem !important;
        min-height: 60px !important;
        transition: all 0.3s ease !important;
        color: #333 !important;
    }

    .stButton > button[kind="secondary"]:hover,
    .stButton > button[data-testid="baseButton-secondary"]:hover {
        background-color: #2AB7CA !important;
        color: white !important;
        transform: scale(1.02) !important;
        box-shadow: 0 6px 20px rgba(42, 183, 202, 0.4) !important;
    }

    /* Success messages in Lime Green */
    .stSuccess, .stAlert[data-baseweb="notification"][kind="positive"] {
        background-color: rgba(155, 197, 61, 0.15) !important;
        border-left-color: #9BC53D !important;
    }

    /* Big question text styling */
    .question-text {
        font-family: 'Fredoka', sans-serif !important;
        font-size: 1.8rem !important;
        font-weight: 600 !important;
        color: #E04F80 !important;
        text-align: center !important;
        padding: 1.5rem !important;
        background: linear-gradient(135deg, #FFF8DC 0%, #FFFACD 100%) !important;
        border-radius: 20px !important;
        margin: 1rem 0 !important;
        box-shadow: 0 4px 15px rgba(224, 79, 128, 0.2) !important;
        border: 3px solid #E04F80 !important;
    }

    /* Score display styling */
    .score-display {
        font-family: 'Fredoka', sans-serif !important;
        font-size: 3rem !important;
        font-weight: 700 !important;
        color: #2AB7CA !important;
        text-align: center !important;
        padding: 2rem !important;
        background: linear-gradient(135deg, #E8F8F5 0%, #D1F2EB 100%) !important;
        border-radius: 25px !important;
        margin: 1rem 0 !important;
        box-shadow: 0 6px 20px rgba(42, 183, 202, 0.3) !important;
        border: 4px solid #2AB7CA !important;
    }

    /* Correct answer highlight */
    .correct-answer {
        background-color: rgba(155, 197, 61, 0.3) !important;
        border: 3px solid #9BC53D !important;
        border-radius: 15px !important;
        padding: 1rem !important;
        margin: 0.5rem 0 !important;
    }

    /* Wrong answer highlight */
    .wrong-answer {
        background-color: rgba(224, 79, 128, 0.15) !important;
        border: 3px solid #E04F80 !important;
        border-radius: 15px !important;
        padding: 1rem !important;
        margin: 0.5rem 0 !important;
    }

    /* Review item styling */
    .review-item {
        background-color: #FFF8E7 !important;
        border-left: 4px solid #FFB347 !important;
        border-radius: 10px !important;
        padding: 1rem !important;
        margin: 0.5rem 0 !important;
        font-family: 'Fredoka', sans-serif !important;
    }

    /* Question type badge */
    .question-badge {
        display: inline-block !important;
        padding: 0.3rem 1rem !important;
        border-radius: 20px !important;
        font-family: 'Fredoka', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        margin-bottom: 0.5rem !important;
    }

    .badge-mc {
        background-color: #2AB7CA !important;
        color: white !important;
    }

    .badge-tf {
        background-color: #9BC53D !important;
        color: white !important;
    }

    .badge-sa {
        background-color: #E04F80 !important;
        color: white !important;
    }

    /* Text input styling */
    .stTextInput > div > div > input {
        font-family: 'Fredoka', sans-serif !important;
        font-size: 1.2rem !important;
        border: 3px solid #2AB7CA !important;
        border-radius: 15px !important;
        padding: 0.8rem 1rem !important;
        text-align: center !important;
    }

    .stTextInput > div > div > input:focus {
        border-color: #E04F80 !important;
        box-shadow: 0 0 10px rgba(224, 79, 128, 0.3) !important;
    }

    /* Number input styling */
    .stNumberInput > div > div > input {
        font-family: 'Fredoka', sans-serif !important;
        border: 2px solid #2AB7CA !important;
        border-radius: 10px !important;
    }

    /* Data editor styling */
    .stDataFrame {
        border-radius: 15px !important;
        overflow: hidden !important;
    }

    /* File uploader styling */
    [data-testid="stFileUploader"] {
        border-radius: 15px !important;
        border: 2px dashed #2AB7CA !important;
        padding: 1rem !important;
    }

    /* Download button */
    .stDownloadButton > button {
        background-color: #9BC53D !important;
        border-color: #9BC53D !important;
        border-radius: 15px !important;
        font-family: 'Fredoka', sans-serif !important;
        font-weight: 600 !important;
    }

    .stDownloadButton > button:hover {
        background-color: #7A9E2E !important;
        border-color: #7A9E2E !important;
    }

    /* CMS Card styling */
    .cms-card {
        background: linear-gradient(135deg, #FFF8DC 0%, #FFFACD 100%);
        border-radius: 20px;
        padding: 1.5rem;
        border: 2px solid #2AB7CA;
        margin-bottom: 1rem;
    }

    /* Game option button - Large colorful */
    .game-option-btn {
        background: linear-gradient(135deg, #2AB7CA 0%, #229AA8 100%);
        color: white;
        border: none;
        border-radius: 20px;
        padding: 1.5rem;
        font-size: 1.3rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        width: 100%;
        margin: 0.5rem 0;
    }

    .game-option-btn:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(42, 183, 202, 0.5);
    }

    /* True button */
    .true-btn {
        background: linear-gradient(135deg, #9BC53D 0%, #7A9E2E 100%) !important;
    }

    /* False button */
    .false-btn {
        background: linear-gradient(135deg, #E04F80 0%, #C43E6A 100%) !important;
    }

    /* Progress info styling */
    .progress-info {
        background-color: #E8F8F5;
        border-radius: 15px;
        padding: 1rem;
        text-align: center;
        margin: 1rem 0;
    }

    /* Mode selector card */
    .mode-card {
        background: white;
        border-radius: 25px;
        padding: 2rem;
        text-align: center;
        border: 3px solid #2AB7CA;
        transition: all 0.3s ease;
        cursor: pointer;
        min-height: 200px;
    }

    .mode-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(42, 183, 202, 0.3);
        border-color: #E04F80;
    }

    .mode-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================
# SESSION STATE INITIALIZATION
# ============================================
def init_session_state():
    """Initialize all session state variables."""
    # App mode
    if 'app_mode' not in st.session_state:
        st.session_state.app_mode = 'home'  # home, create, play

    # CMS Creation state
    if 'cms_step' not in st.session_state:
        st.session_state.cms_step = 'config'  # config, generating, editing, ready
    if 'uploaded_files_cache' not in st.session_state:
        st.session_state.uploaded_files_cache = None
    if 'quiz_config' not in st.session_state:
        st.session_state.quiz_config = None
    if 'generated_questions' not in st.session_state:
        st.session_state.generated_questions = []
    if 'generation_progress' not in st.session_state:
        st.session_state.generation_progress = 0
    if 'finalized_quiz' not in st.session_state:
        st.session_state.finalized_quiz = None

    # Game state
    if 'quiz_data' not in st.session_state:
        st.session_state.quiz_data = None
    if 'current_question_index' not in st.session_state:
        st.session_state.current_question_index = 0
    if 'score' not in st.session_state:
        st.session_state.score = 0
    if 'game_active' not in st.session_state:
        st.session_state.game_active = False
    if 'user_answer' not in st.session_state:
        st.session_state.user_answer = None
    if 'answer_submitted' not in st.session_state:
        st.session_state.answer_submitted = False
    if 'wrong_answers' not in st.session_state:
        st.session_state.wrong_answers = []
    if 'game_completed' not in st.session_state:
        st.session_state.game_completed = False

init_session_state()

# ============================================
# HELPER FUNCTIONS
# ============================================
def reset_to_home():
    """Reset all state and go to home."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    init_session_state()

def reset_game():
    """Reset game state only."""
    st.session_state.current_question_index = 0
    st.session_state.score = 0
    st.session_state.game_active = False
    st.session_state.user_answer = None
    st.session_state.answer_submitted = False
    st.session_state.wrong_answers = []
    st.session_state.game_completed = False
    # Clear any scored/tracked attributes
    for key in list(st.session_state.keys()):
        if key.startswith('scored_') or key.startswith('tracked_'):
            del st.session_state[key]

def submit_answer(answer):
    """Handle answer submission."""
    st.session_state.user_answer = answer
    st.session_state.answer_submitted = True

def next_question():
    """Move to the next question or end the game."""
    st.session_state.current_question_index += 1
    st.session_state.user_answer = None
    st.session_state.answer_submitted = False

    if st.session_state.current_question_index >= len(st.session_state.quiz_data['questions']):
        st.session_state.game_active = False
        st.session_state.game_completed = True

def check_answer(user_answer, correct_answer, question_type):
    """Check if the answer is correct based on question type."""
    if question_type == "short_answer":
        # Case-insensitive comparison for short answer
        return user_answer.strip().lower() == correct_answer.strip().lower()
    else:
        return user_answer == correct_answer

def get_question_type_display(q_type):
    """Get the display info for question type badge."""
    if q_type == "multiple_choice":
        return ("🎯 Multiple Choice", "badge-mc")
    elif q_type == "true_false":
        return ("✅ True or False", "badge-tf")
    else:
        return ("✏️ Short Answer", "badge-sa")

def detect_language(text):
    """Simple language detection based on common Spanish words."""
    spanish_indicators = ['el', 'la', 'los', 'las', 'de', 'en', 'que', 'es', 'un', 'una',
                         'para', 'con', 'por', 'como', 'del', 'al', 'son', 'está', 'este',
                         'esta', 'estos', 'qué', 'cómo', 'cuál', 'cuándo', 'dónde']
    text_lower = text.lower()
    spanish_count = sum(1 for word in spanish_indicators if f' {word} ' in f' {text_lower} ')
    return 'Spanish' if spanish_count >= 2 else 'English'

# ============================================
# AI QUIZ GENERATION - BATCHED
# ============================================
def generate_quiz_batch(uploaded_files, mc_count, tf_count, sa_count, batch_num, total_batches):
    """Generate a batch of quiz questions (max 10 per batch)."""

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
    """Generate a full quiz with batched API calls."""
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

# ============================================
# HOME SCREEN
# ============================================
def render_home_screen():
    """Render the home screen with mode selection."""

    # Center the logo
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("logo.png", width=250)

    st.markdown("<h1 style='text-align: center;'>🎮 CIFE Quiz Platform</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.3rem; color: #666;'>Create, Share, and Play Interactive Quizzes!</p>", unsafe_allow_html=True)

    st.write("")
    st.write("")

    # Two mode cards
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
            <div class="mode-card">
                <div class="mode-icon">📝</div>
                <h2 style="color: #E04F80;">Create New Quiz</h2>
                <p>Teachers: Upload notebook images and generate AI-powered quizzes with custom question types.</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("📝 Create Quiz", key="btn_create", type="primary", use_container_width=True):
            st.session_state.app_mode = 'create'
            st.session_state.cms_step = 'config'
            st.rerun()

    with col2:
        st.markdown("""
            <div class="mode-card">
                <div class="mode-icon">🎮</div>
                <h2 style="color: #E04F80;">Play Existing Quiz</h2>
                <p>Students: Load a quiz file shared by your teacher and start playing immediately!</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("🎮 Play Quiz", key="btn_play", type="primary", use_container_width=True):
            st.session_state.app_mode = 'play'
            st.rerun()

    st.write("")
    st.markdown("---")
    st.markdown("""
        <div style="text-align: center; color: #888; padding: 1rem;">
            <p>🐯 Powered by CIFE • Turn your notes into fun learning experiences! 🚀</p>
        </div>
    """, unsafe_allow_html=True)

# ============================================
# TEACHER CMS - CREATE MODE
# ============================================
def render_create_mode():
    """Render the Teacher CMS for creating quizzes."""

    # Header with back button
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("⬅️ Back", key="back_to_home"):
            reset_to_home()
            st.rerun()
    with col2:
        st.markdown("## 📝 Teacher Quiz Creator")

    st.markdown("---")

    # CMS Step Router
    if st.session_state.cms_step == 'config':
        render_cms_config()
    elif st.session_state.cms_step == 'generating':
        render_cms_generating()
    elif st.session_state.cms_step == 'editing':
        render_cms_editing()
    elif st.session_state.cms_step == 'ready':
        render_cms_ready()

def render_cms_config():
    """Step 1: Configuration - Upload images and set question counts."""

    st.markdown("### Step 1: Upload Notebook Images")

    uploaded_files = st.file_uploader(
        "📷 Upload notebook page images",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
        help="Upload all notebook pages covering the topic you want to quiz on."
    )

    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} image(s) uploaded!")

        with st.expander(f"👀 View Uploaded Images", expanded=False):
            cols = st.columns(min(len(uploaded_files), 4))
            for idx, f in enumerate(uploaded_files):
                with cols[idx % 4]:
                    st.image(f, caption=f"Page {idx + 1}", use_container_width=True)

        st.session_state.uploaded_files_cache = uploaded_files

        st.markdown("---")
        st.markdown("### Step 2: Configure Question Types")
        st.markdown("*Specify how many of each question type you want (max 60+ total questions)*")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("#### 🎯 Multiple Choice")
            mc_count = st.number_input(
                "Number of MC questions",
                min_value=0, max_value=30, value=5,
                key="mc_count",
                help="Questions with 4 options to choose from"
            )

        with col2:
            st.markdown("#### ✅ True/False")
            tf_count = st.number_input(
                "Number of T/F questions",
                min_value=0, max_value=30, value=3,
                key="tf_count",
                help="Statements to evaluate as true or false"
            )

        with col3:
            st.markdown("#### ✏️ Short Answer")
            sa_count = st.number_input(
                "Number of SA questions",
                min_value=0, max_value=30, value=2,
                key="sa_count",
                help="Fill-in-the-blank or short response questions"
            )

        total = mc_count + tf_count + sa_count

        st.markdown(f"""
            <div class="progress-info">
                <h3>📊 Total Questions: {total}</h3>
                <p>🎯 MC: {mc_count} | ✅ T/F: {tf_count} | ✏️ SA: {sa_count}</p>
                {'<p style="color: #9BC53D;">✓ Questions will be generated in batches of 10 to ensure quality!</p>' if total > 10 else ''}
            </div>
        """, unsafe_allow_html=True)

        st.write("")

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if total > 0:
                if st.button("🚀 Generate Quiz", type="primary", use_container_width=True):
                    st.session_state.quiz_config = {
                        'mc_count': mc_count,
                        'tf_count': tf_count,
                        'sa_count': sa_count,
                        'total': total
                    }
                    st.session_state.cms_step = 'generating'
                    st.rerun()
            else:
                st.warning("⚠️ Please specify at least 1 question!")
    else:
        st.info("👆 Upload notebook images to get started!")

def render_cms_generating():
    """Step 2: Generating quiz with progress bar."""

    st.markdown("### 🧠 Generating Your Quiz...")

    config = st.session_state.quiz_config
    total = config['total']
    num_batches = (total + 9) // 10  # Ceiling division for batches of 10

    st.markdown(f"""
        <div class="progress-info">
            <h4>📊 Generating {total} questions in {num_batches} batch(es)</h4>
            <p>🎯 MC: {config['mc_count']} | ✅ T/F: {config['tf_count']} | ✏️ SA: {config['sa_count']}</p>
        </div>
    """, unsafe_allow_html=True)

    progress_placeholder = st.progress(0, "Starting generation...")

    try:
        quiz_data = generate_full_quiz(
            st.session_state.uploaded_files_cache,
            config['mc_count'],
            config['tf_count'],
            config['sa_count'],
            progress_placeholder
        )

        st.session_state.generated_questions = quiz_data['questions']
        st.session_state.finalized_quiz = quiz_data
        st.session_state.cms_step = 'editing'
        progress_placeholder.progress(1.0, "✅ Generation complete!")
        st.rerun()

    except Exception as e:
        st.error(f"❌ Error during generation: {str(e)}")
        if st.button("🔄 Try Again"):
            st.session_state.cms_step = 'config'
            st.rerun()

def render_cms_editing():
    """Step 3: Edit and review generated questions."""

    st.markdown("### ✏️ Review & Edit Questions")
    st.markdown("*Review the AI-generated questions and make any corrections before finalizing.*")

    quiz = st.session_state.finalized_quiz

    # Show quiz metadata
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"**📚 Subject:** {quiz['subject']}")
    with col2:
        st.markdown(f"**📝 Topic:** {quiz['topic']}")
    with col3:
        st.markdown(f"**🎓 Grade:** {quiz['grade_level']}")
    with col4:
        st.markdown(f"**🌐 Language:** {quiz.get('language', 'Auto-detected')}")

    st.markdown("---")

    # Convert questions to editable DataFrame format
    questions = st.session_state.generated_questions

    # Create editable data
    edit_data = []
    for i, q in enumerate(questions):
        edit_data.append({
            '#': i + 1,
            'Type': q['type'],
            'Question': q['q'],
            'Options': ' | '.join(q.get('options', [])) if q.get('options') else '',
            'Answer': q['answer']
        })

    # Use data editor
    st.markdown("#### 📋 Question Editor")
    st.markdown("*Click on any cell to edit. Changes are saved automatically.*")

    edited_df = st.data_editor(
        edit_data,
        column_config={
            '#': st.column_config.NumberColumn('#', disabled=True, width='small'),
            'Type': st.column_config.SelectboxColumn(
                'Type',
                options=['multiple_choice', 'true_false', 'short_answer'],
                width='medium'
            ),
            'Question': st.column_config.TextColumn('Question', width='large'),
            'Options': st.column_config.TextColumn('Options (separated by |)', width='large'),
            'Answer': st.column_config.TextColumn('Answer', width='medium'),
        },
        num_rows='dynamic',
        use_container_width=True,
        key='question_editor'
    )

    st.markdown("---")

    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("⬅️ Back to Config"):
            st.session_state.cms_step = 'config'
            st.rerun()

    with col2:
        if st.button("🔄 Regenerate All"):
            st.session_state.cms_step = 'generating'
            st.rerun()

    with col3:
        if st.button("✅ Finalize Quiz", type="primary"):
            # Convert edited data back to questions format
            final_questions = []
            for row in edited_df:
                options = [opt.strip() for opt in row['Options'].split('|')] if row['Options'] else []
                final_questions.append({
                    'type': row['Type'],
                    'q': row['Question'],
                    'options': options,
                    'answer': row['Answer']
                })

            st.session_state.finalized_quiz['questions'] = final_questions
            st.session_state.finalized_quiz['total_questions'] = len(final_questions)
            st.session_state.cms_step = 'ready'
            st.rerun()

def render_cms_ready():
    """Step 4: Quiz is ready - download or play."""

    st.markdown("### 🎉 Quiz Ready!")

    quiz = st.session_state.finalized_quiz

    st.markdown(f"""
        <div class="score-display" style="font-size: 1.5rem;">
            <h2 style="color: #E04F80;">📚 {quiz['subject']}: {quiz['topic']}</h2>
            <p>🎓 {quiz['grade_level']} • 🌐 {quiz.get('language', 'Auto')}</p>
            <p style="font-size: 2rem; margin-top: 1rem;">📝 {quiz['total_questions']} Questions</p>
        </div>
    """, unsafe_allow_html=True)

    st.write("")

    # Create downloadable JSON
    quiz_json = json.dumps(quiz, ensure_ascii=False, indent=2)
    filename = f"CIFE_Quiz_{quiz['subject'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("#### 💾 Share with Students")
        st.download_button(
            label="💾 Download Game File (.json)",
            data=quiz_json,
            file_name=filename,
            mime="application/json",
            use_container_width=True
        )

        st.write("")

        st.markdown("#### 🎮 Or Play Now")
        if st.button("🎮 Start Playing!", type="primary", use_container_width=True):
            st.session_state.quiz_data = quiz
            st.session_state.app_mode = 'game'
            st.session_state.game_active = True
            reset_game()
            st.rerun()

    st.write("")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📝 Create Another Quiz"):
            st.session_state.cms_step = 'config'
            st.session_state.finalized_quiz = None
            st.session_state.generated_questions = []
            st.session_state.uploaded_files_cache = None
            st.rerun()

# ============================================
# STUDENT PLAY MODE
# ============================================
def render_play_mode():
    """Render the student play mode - load quiz file."""

    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("⬅️ Back", key="back_from_play"):
            reset_to_home()
            st.rerun()
    with col2:
        st.markdown("## 🎮 Play Quiz")

    st.markdown("---")

    st.markdown("### 📂 Load Your Quiz")
    st.markdown("*Upload the quiz file (.json) shared by your teacher*")

    uploaded_quiz = st.file_uploader(
        "📂 Upload Quiz File",
        type=["json"],
        help="Upload the .json quiz file shared by your teacher"
    )

    if uploaded_quiz:
        try:
            quiz_data = json.loads(uploaded_quiz.read().decode('utf-8'))

            # Validate quiz structure
            if 'questions' not in quiz_data or len(quiz_data['questions']) == 0:
                st.error("❌ Invalid quiz file - no questions found!")
                return

            st.success(f"✅ Quiz loaded successfully!")

            st.markdown(f"""
                <div class="score-display" style="font-size: 1.2rem;">
                    <h3 style="color: #E04F80;">📚 {quiz_data.get('subject', 'Quiz')}: {quiz_data.get('topic', 'Practice')}</h3>
                    <p>🎓 {quiz_data.get('grade_level', 'General')} • 📝 {len(quiz_data['questions'])} Questions</p>
                </div>
            """, unsafe_allow_html=True)

            st.write("")

            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🚀 Start Game!", type="primary", use_container_width=True):
                    st.session_state.quiz_data = quiz_data
                    st.session_state.app_mode = 'game'
                    st.session_state.game_active = True
                    reset_game()
                    st.rerun()

        except json.JSONDecodeError:
            st.error("❌ Invalid file format. Please upload a valid quiz .json file.")
        except Exception as e:
            st.error(f"❌ Error loading quiz: {str(e)}")
    else:
        st.info("👆 Upload a quiz file to get started!")

        st.write("")
        st.markdown("---")
        st.markdown("### 🎯 How to Get a Quiz File")
        st.markdown("""
        1. Ask your teacher for the quiz file (.json)
        2. Download it to your device
        3. Upload it here to start playing!
        """)

# ============================================
# GAME SCREEN - WORDWALL STYLE
# ============================================
def render_game_screen():
    """Render the interactive WordWall-style game."""

    quiz_data = st.session_state.quiz_data
    current_idx = st.session_state.current_question_index
    question = quiz_data['questions'][current_idx]
    total_questions = len(quiz_data['questions'])

    # Header with progress
    col1, col2, col3 = st.columns([2, 3, 2])
    with col1:
        if st.button("🏠 Exit"):
            reset_to_home()
            st.rerun()
    with col2:
        st.markdown(f"### 📚 {quiz_data.get('subject', 'Quiz')}: {quiz_data.get('topic', 'Practice')}")
    with col3:
        st.markdown(f"### 🏆 Score: {st.session_state.score}/{current_idx}")

    # Progress bar
    progress = (current_idx) / total_questions
    st.progress(progress)
    st.markdown(f"<p style='text-align: center;'><strong>Question {current_idx + 1} of {total_questions}</strong></p>", unsafe_allow_html=True)

    st.write("")

    # Question type badge
    badge_text, badge_class = get_question_type_display(question['type'])
    st.markdown(f'<div style="text-align: center;"><span class="question-badge {badge_class}">{badge_text}</span></div>', unsafe_allow_html=True)

    # Question text - big and bold
    st.markdown(f'<div class="question-text">❓ {question["q"]}</div>', unsafe_allow_html=True)

    st.write("")

    # Answer section - depends on question type
    if not st.session_state.answer_submitted:
        render_answer_options(question, current_idx)
    else:
        render_answer_feedback(question, current_idx, total_questions)

def render_answer_options(question, current_idx):
    """Render answer options based on question type."""

    if question['type'] == 'short_answer':
        # Short answer input
        st.markdown("#### ✏️ Type your answer:")

        user_input = st.text_input(
            "Your answer",
            key=f"sa_input_{current_idx}",
            label_visibility="collapsed",
            placeholder="Type your answer here..."
        )

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("📤 Submit Answer", type="primary", use_container_width=True):
                if user_input.strip():
                    submit_answer(user_input.strip())
                    st.rerun()
                else:
                    st.warning("⚠️ Please type an answer first!")

    elif question['type'] == 'true_false':
        # Big True/False buttons
        st.markdown("#### 🤔 Is this statement true or false?")

        col1, col2 = st.columns(2)

        # Determine button labels based on language
        true_label = question['options'][0] if question.get('options') else "True"
        false_label = question['options'][1] if question.get('options') and len(question['options']) > 1 else "False"

        with col1:
            st.markdown(f"""
                <style>
                    div[data-testid="column"]:first-child .stButton > button {{
                        background: linear-gradient(135deg, #9BC53D 0%, #7A9E2E 100%) !important;
                        color: white !important;
                        font-size: 1.5rem !important;
                        padding: 2rem !important;
                        border: none !important;
                    }}
                </style>
            """, unsafe_allow_html=True)
            if st.button(f"✅ {true_label}", key="tf_true", use_container_width=True):
                submit_answer(true_label)
                st.rerun()

        with col2:
            st.markdown(f"""
                <style>
                    div[data-testid="column"]:last-child .stButton > button {{
                        background: linear-gradient(135deg, #E04F80 0%, #C43E6A 100%) !important;
                        color: white !important;
                        font-size: 1.5rem !important;
                        padding: 2rem !important;
                        border: none !important;
                    }}
                </style>
            """, unsafe_allow_html=True)
            if st.button(f"❌ {false_label}", key="tf_false", use_container_width=True):
                submit_answer(false_label)
                st.rerun()

    else:  # multiple_choice
        # Four colorful option buttons
        st.markdown("#### 🎯 Choose the correct answer:")

        option_colors = ["#2AB7CA", "#9BC53D", "#E04F80", "#FFB347"]
        option_emojis = ["🅰️", "🅱️", "©️", "🅳"]

        # Create 2x2 grid
        col1, col2 = st.columns(2)

        for idx, option in enumerate(question.get('options', [])):
            target_col = col1 if idx % 2 == 0 else col2
            with target_col:
                if st.button(
                    f"{option_emojis[idx]} {option}",
                    key=f"mc_option_{idx}",
                    use_container_width=True,
                    type="secondary"
                ):
                    submit_answer(option)
                    st.rerun()

def render_answer_feedback(question, current_idx, total_questions):
    """Render feedback after answer submission."""

    user_answer = st.session_state.user_answer
    correct_answer = question['answer']
    is_correct = check_answer(user_answer, correct_answer, question['type'])

    if is_correct:
        # Correct answer celebration!
        st.balloons()
        st.markdown(f"""
            <div class="correct-answer">
                <h2 style="color: #9BC53D; text-align: center;">🎉 CORRECT! 🎉</h2>
                <p style="text-align: center; font-size: 1.2rem;">Amazing job! You got it right! 🌟</p>
            </div>
        """, unsafe_allow_html=True)

        # Update score
        if not hasattr(st.session_state, f'scored_{current_idx}'):
            st.session_state.score += 1
            setattr(st.session_state, f'scored_{current_idx}', True)
    else:
        # Wrong answer feedback
        st.markdown(f"""
            <div class="wrong-answer">
                <h2 style="color: #E04F80; text-align: center;">❌ Not quite!</h2>
                <p style="text-align: center; font-size: 1.1rem;">Your answer: <strong>{user_answer}</strong></p>
                <p style="text-align: center; font-size: 1.2rem; color: #9BC53D;">✅ Correct answer: <strong>{correct_answer}</strong></p>
            </div>
        """, unsafe_allow_html=True)

        # Track wrong answers for review
        if not hasattr(st.session_state, f'tracked_{current_idx}'):
            st.session_state.wrong_answers.append({
                'question': question['q'],
                'user_answer': user_answer,
                'correct_answer': correct_answer,
                'type': question['type']
            })
            setattr(st.session_state, f'tracked_{current_idx}', True)

    st.write("")

    # Next button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if current_idx < total_questions - 1:
            if st.button("➡️ Next Question", type="primary", use_container_width=True):
                next_question()
                st.rerun()
        else:
            if st.button("🏁 See Results!", type="primary", use_container_width=True):
                next_question()
                st.rerun()

# ============================================
# RESULTS SCREEN
# ============================================
def render_results_screen():
    """Render the final results screen with celebration."""

    quiz_data = st.session_state.quiz_data
    total_questions = len(quiz_data['questions'])
    score = st.session_state.score
    percentage = (score / total_questions) * 100

    # Celebration for high scores!
    if percentage >= 70:
        st.balloons()
    if percentage >= 90:
        st.snow()

    # Logo
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("logo.png", width=150)

    # Title
    st.markdown("<h1 style='text-align: center;'>🏆 Quiz Complete!</h1>", unsafe_allow_html=True)

    # Score display with dynamic message
    if percentage >= 90:
        emoji = "🌟🏆🌟"
        message = "OUTSTANDING! You're a superstar!"
        color = "#9BC53D"
    elif percentage >= 70:
        emoji = "🎉👏🎉"
        message = "Great job! You passed with flying colors!"
        color = "#2AB7CA"
    elif percentage >= 50:
        emoji = "💪📚💪"
        message = "Good effort! Keep practicing!"
        color = "#FFB347"
    else:
        emoji = "📖🤓📖"
        message = "Time to review! You've got this!"
        color = "#E04F80"

    st.markdown(f"""
        <div class="score-display">
            <div style="font-size: 2rem;">{emoji}</div>
            <div style="font-size: 4rem; font-weight: 700;">{score}/{total_questions}</div>
            <div style="font-size: 1.5rem; color: {color};">{percentage:.0f}%</div>
            <div style="font-size: 1.2rem; margin-top: 1rem;">{message}</div>
        </div>
    """, unsafe_allow_html=True)

    st.write("")

    # Subject and topic info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"**📚 Subject:** {quiz_data.get('subject', 'Quiz')}")
    with col2:
        st.markdown(f"**📝 Topic:** {quiz_data.get('topic', 'Practice')}")
    with col3:
        st.markdown(f"**🎓 Grade:** {quiz_data.get('grade_level', 'General')}")

    st.markdown("---")

    # Review section for wrong answers
    if st.session_state.wrong_answers:
        st.markdown("### 📋 Review Needed")
        st.markdown("*These questions need a bit more practice:*")

        for idx, wrong in enumerate(st.session_state.wrong_answers, 1):
            type_emoji = "🎯" if wrong['type'] == "multiple_choice" else ("✅" if wrong['type'] == "true_false" else "✏️")
            st.markdown(f"""
                <div class="review-item">
                    <p><strong>{type_emoji} Question {idx}:</strong> {wrong['question']}</p>
                    <p style="color: #E04F80;">❌ Your answer: {wrong['user_answer']}</p>
                    <p style="color: #9BC53D;">✅ Correct: {wrong['correct_answer']}</p>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("### 🌟 Perfect Score!")
        st.markdown("*You got every question right! Amazing work!* 🎊")

    st.markdown("---")
    st.write("")

    # Action buttons
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("🔄 Play Again", use_container_width=True):
            reset_game()
            st.session_state.game_active = True
            st.rerun()

    with col2:
        if st.button("🎮 Different Quiz", type="primary", use_container_width=True):
            reset_to_home()
            st.session_state.app_mode = 'play'
            st.rerun()

    with col3:
        if st.button("🏠 Home", use_container_width=True):
            reset_to_home()
            st.rerun()

    # Fun encouragement
    st.write("")
    st.markdown("""
        <div style="text-align: center; padding: 1rem; color: #666;">
            <p>🐯 Keep learning, keep growing! 🚀</p>
            <p style="font-size: 0.9rem;">Powered by CIFE</p>
        </div>
    """, unsafe_allow_html=True)

# ============================================
# MAIN APP ROUTER
# ============================================
def main():
    """Main app router - determines which screen to show."""

    # Check if game is completed first
    if st.session_state.game_completed:
        render_results_screen()
        return

    # Check if actively playing
    if st.session_state.game_active and st.session_state.quiz_data:
        render_game_screen()
        return

    # Route based on app mode
    if st.session_state.app_mode == 'home':
        render_home_screen()
    elif st.session_state.app_mode == 'create':
        render_create_mode()
    elif st.session_state.app_mode == 'play':
        render_play_mode()
    elif st.session_state.app_mode == 'game':
        # If game mode but not active, something went wrong - reset
        reset_to_home()
        st.rerun()

# Run the app
if __name__ == "__main__":
    main()
