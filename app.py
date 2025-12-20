import streamlit as st
import openai
import base64
import json
import random

# Configure the OpenAI client with API key from Streamlit secrets
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ============================================
# PAGE CONFIG
# ============================================
st.set_page_config(
    page_title="CIFE Quiz Game 🎮",
    page_icon="🐯",
    layout="centered"
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
    h1, h2, h3, h4, p, span, div, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stButton > button {
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

    .stSuccess > div {
        color: #7A9E2E !important;
    }

    /* Style success text elements */
    [data-testid="stNotification"][data-kind="success"] {
        background-color: rgba(155, 197, 61, 0.15) !important;
        border-left: 4px solid #9BC53D !important;
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

    /* Progress bar container */
    .progress-container {
        background-color: #f0f0f0 !important;
        border-radius: 15px !important;
        padding: 5px !important;
        margin: 1rem 0 !important;
    }

    .progress-bar {
        background: linear-gradient(90deg, #2AB7CA 0%, #9BC53D 100%) !important;
        border-radius: 10px !important;
        height: 20px !important;
        transition: width 0.5s ease !important;
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

    /* File uploader styling */
    [data-testid="stFileUploader"] {
        border-radius: 15px !important;
    }

    /* Expander header styling */
    .streamlit-expanderHeader {
        font-family: 'Fredoka', sans-serif !important;
        color: #2AB7CA !important;
    }

    /* Info box styling */
    .stInfo {
        background-color: rgba(42, 183, 202, 0.1) !important;
        border-left-color: #2AB7CA !important;
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

    .badge-fib {
        background-color: #E04F80 !important;
        color: white !important;
    }

    /* Text input for fill in blank */
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
    </style>
""", unsafe_allow_html=True)

# ============================================
# SESSION STATE INITIALIZATION
# ============================================
def init_session_state():
    """Initialize all session state variables for the game."""
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
    if 'uploaded_files_cache' not in st.session_state:
        st.session_state.uploaded_files_cache = None

init_session_state()

# ============================================
# HELPER FUNCTIONS
# ============================================
def reset_game():
    """Reset all game state to start fresh."""
    st.session_state.quiz_data = None
    st.session_state.current_question_index = 0
    st.session_state.score = 0
    st.session_state.game_active = False
    st.session_state.user_answer = None
    st.session_state.answer_submitted = False
    st.session_state.wrong_answers = []
    st.session_state.game_completed = False
    st.session_state.uploaded_files_cache = None

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
    if question_type == "fill_in_the_blank":
        # Case-insensitive comparison for fill in blank
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
        return ("✏️ Fill in the Blank", "badge-fib")

# ============================================
# AI QUIZ GENERATION
# ============================================
def generate_quiz(uploaded_files):
    """Generate quiz using AI from uploaded notebook images."""

    # Prepare the content list with text prompt and all images
    content_list = [
        {
            "type": "text",
            "text": "Please analyze ALL of these notebook pages together as a complete set of notes on a topic. Detect the primary language of the handwritten notes and create a comprehensive practice quiz covering all the material across all pages. Output as pure JSON only."
        }
    ]

    # Add each image to the content list
    for uploaded_file in uploaded_files:
        # Reset file pointer to beginning
        uploaded_file.seek(0)

        # Convert image to Base64
        image_bytes = uploaded_file.getvalue()
        base64_image = base64.b64encode(image_bytes).decode("utf-8")

        # Determine the image MIME type
        file_extension = uploaded_file.name.split(".")[-1].lower()
        if file_extension in ["jpg", "jpeg"]:
            mime_type = "image/jpeg"
        else:
            mime_type = "image/png"

        # Add image to content list
        content_list.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:{mime_type};base64,{base64_image}"
            }
        })

    # System prompt for multi-page analysis with mixed question types
    system_prompt = """You are a helpful teacher's assistant specialized in analyzing student notebooks and creating FUN, INTERACTIVE practice quizzes for students.

You will be provided with MULTIPLE images of a student's handwritten notes that together cover a complete topic or lesson.

IMPORTANT INSTRUCTIONS:

1. MULTI-PAGE ANALYSIS: Analyze ALL provided images as a cohesive set of notes. The pages together represent complete coverage of a topic - synthesize the information across all pages.

2. LANGUAGE DETECTION: Detect the primary language of the handwritten notes (e.g., Spanish, English, French, Portuguese, etc.). Generate the ENTIRE practice quiz in that SAME language. If the notes are in Spanish, ALL quiz content must be in Spanish. If in English, ALL content must be in English.

3. GRADE LEVEL: Use Puerto Rico K-12 notation for grade levels:
   - Kindergarten through 6th grade: "Kinder", "1er Grado", "2do Grado", "3er Grado", "4to Grado", "5to Grado", "6to Grado"
   - Middle/High school: "7mo Grado", "8vo Grado", "9no Grado", "10mo Grado", "11mo Grado", "12mo Grado"

4. CONTENT ANALYSIS:
   - Identify the subject matter (e.g., Mathematics, Science, History, etc.)
   - Identify the specific topic spanning across the notes
   - Determine the appropriate grade level
   - Extract key concepts, definitions, formulas, dates, or facts from ALL pages

5. QUIZ GENERATION: Create a FUN, INTERACTIVE 10-question quiz with a MIX of these 3 question types:
   - "multiple_choice" (4 options) - Use for concept understanding questions
   - "true_false" (2 options: True/False or Verdadero/Falso) - Use for fact verification questions
   - "fill_in_the_blank" (student types the answer) - Use for vocabulary, formulas, or key terms

   Make sure to include at least 3 of each type, distributed randomly throughout the quiz.

6. OUTPUT FORMAT: You MUST output your response as a valid JSON object with NO markdown formatting around it (no ```json blocks). Use this EXACT structure:

{
  "subject": "The detected subject (e.g., Biology, Mathematics, History)",
  "topic": "The specific topic spanning the notes (e.g., Cell Division, Quadratic Equations, World War II)",
  "grade_level": "Detected grade level using Puerto Rico notation (e.g., '10mo Grado')",
  "questions": [
    {
      "type": "multiple_choice",
      "q": "The question text here",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "answer": "The correct option text (must match one of the options exactly)"
    },
    {
      "type": "true_false",
      "q": "Statement to evaluate as true or false",
      "options": ["Verdadero", "Falso"],
      "answer": "Verdadero or Falso (or True/False in English)"
    },
    {
      "type": "fill_in_the_blank",
      "q": "The _____ is the powerhouse of the cell.",
      "options": [],
      "answer": "mitochondria"
    }
  ]
}

REQUIREMENTS:
- Generate exactly 10 questions that span content from ALL uploaded pages
- Include a good MIX of all 3 question types (at least 3 of each type)
- For multiple_choice: exactly 4 options
- For true_false: exactly 2 options (Verdadero/Falso in Spanish, True/False in English)
- For fill_in_the_blank: empty options array, answer should be a single word or short phrase
- The "answer" field must contain the exact text of the correct answer
- ALL text must be in the SAME language as the student's notes
- Use proper UTF-8 characters for special characters (ñ, á, é, í, ó, ú, ü, ¿, ¡, etc.)
- Questions should be FUN and ENGAGING for students
- Vary question difficulty to include both recall and comprehension questions
- RANDOMIZE the order of question types throughout the quiz"""

    # Make the API call with vision capabilities
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": content_list
            }
        ],
        max_tokens=3000
    )

    # Extract the generated content
    raw_content = response.choices[0].message.content

    # Clean up response if it has markdown code blocks
    cleaned_content = raw_content.strip()
    if cleaned_content.startswith("```json"):
        cleaned_content = cleaned_content[7:]
    if cleaned_content.startswith("```"):
        cleaned_content = cleaned_content[3:]
    if cleaned_content.endswith("```"):
        cleaned_content = cleaned_content[:-3]
    cleaned_content = cleaned_content.strip()

    # Parse the JSON response
    quiz_data = json.loads(cleaned_content)

    # Shuffle the questions for variety
    random.shuffle(quiz_data['questions'])

    return quiz_data

# ============================================
# SCREEN 1: SETUP SCREEN
# ============================================
def render_setup_screen():
    """Render the setup screen with file uploader and start button."""

    # Logo
    st.image("logo.png", width=200)

    # Title with emoji
    st.title("🎮 CIFE Quiz Game")
    st.markdown("### 📚 Turn your notes into a fun quiz adventure! 🚀")

    st.write("")
    st.write("Upload photos of your notebook pages and challenge yourself with an interactive quiz! 🐯")

    # Multi-file uploader for images
    uploaded_files = st.file_uploader(
        "📷 Upload notebook images",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
        help="Supported formats: JPG, PNG. Upload multiple pages covering a complete topic."
    )

    # Process the uploaded images
    if uploaded_files:
        # Display upload count
        st.success(f"✅ {len(uploaded_files)} image(s) uploaded successfully!")

        # Display all uploaded images in an expandable section
        with st.expander(f"👀 View Uploaded Images ({len(uploaded_files)} pages)", expanded=False):
            cols = st.columns(min(len(uploaded_files), 3))
            for idx, uploaded_file in enumerate(uploaded_files):
                col_idx = idx % 3
                with cols[col_idx]:
                    st.image(uploaded_file, caption=f"📄 Page {idx + 1}", use_container_width=True)

        st.write("")

        # Start Quiz button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Start Quiz!", type="primary", use_container_width=True):
                with st.spinner("🧠 AI is creating your quiz... Get ready! 🎯"):
                    try:
                        quiz_data = generate_quiz(uploaded_files)
                        st.session_state.quiz_data = quiz_data
                        st.session_state.game_active = True
                        st.session_state.uploaded_files_cache = uploaded_files
                        st.rerun()
                    except json.JSONDecodeError as e:
                        st.error("❌ Oops! Something went wrong with the AI response. Please try again!")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
    else:
        # Show instructions when no files are uploaded
        st.info("👆 Upload one or more notebook page images to get started. For best results, upload all pages covering a complete topic! 📚")

        # Fun facts section
        st.write("")
        st.markdown("---")
        st.markdown("### 🌟 How it works:")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("#### 1️⃣ Upload")
            st.write("📷 Take photos of your notebook pages")
        with col2:
            st.markdown("#### 2️⃣ Play")
            st.write("🎮 Answer fun quiz questions")
        with col3:
            st.markdown("#### 3️⃣ Learn")
            st.write("🏆 See your score and review!")

# ============================================
# SCREEN 2: GAME SCREEN
# ============================================
def render_game_screen():
    """Render the interactive game screen."""

    quiz_data = st.session_state.quiz_data
    current_idx = st.session_state.current_question_index
    question = quiz_data['questions'][current_idx]
    total_questions = len(quiz_data['questions'])

    # Header with progress
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"### 📚 {quiz_data['subject']}: {quiz_data['topic']}")
        st.markdown(f"*{quiz_data['grade_level']}*")
    with col2:
        st.markdown(f"### 🏆 Score: {st.session_state.score}/{current_idx}")

    # Progress bar
    progress = (current_idx) / total_questions
    st.progress(progress)
    st.markdown(f"**Question {current_idx + 1} of {total_questions}**")

    st.write("")

    # Question type badge
    badge_text, badge_class = get_question_type_display(question['type'])
    st.markdown(f'<span class="question-badge {badge_class}">{badge_text}</span>', unsafe_allow_html=True)

    # Question text - big and bold
    st.markdown(f'<div class="question-text">❓ {question["q"]}</div>', unsafe_allow_html=True)

    st.write("")

    # Answer section - depends on question type
    if not st.session_state.answer_submitted:
        # Show answer options based on question type
        if question['type'] == "fill_in_the_blank":
            # Text input for fill in the blank
            st.markdown("#### ✏️ Type your answer:")
            user_input = st.text_input(
                "Your answer",
                key=f"fib_input_{current_idx}",
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

        elif question['type'] == "true_false":
            # Two big buttons for True/False
            st.markdown("#### 🤔 Is this statement true or false?")
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"✅ {question['options'][0]}", key="tf_true", use_container_width=True, type="secondary"):
                    submit_answer(question['options'][0])
                    st.rerun()
            with col2:
                if st.button(f"❌ {question['options'][1]}", key="tf_false", use_container_width=True, type="secondary"):
                    submit_answer(question['options'][1])
                    st.rerun()

        else:  # multiple_choice
            # Four buttons in 2x2 grid
            st.markdown("#### 🎯 Choose the correct answer:")
            col1, col2 = st.columns(2)

            option_emojis = ["🅰️", "🅱️", "©️", "🅳"]

            for idx, option in enumerate(question['options']):
                with col1 if idx % 2 == 0 else col2:
                    if st.button(
                        f"{option_emojis[idx]} {option}",
                        key=f"mc_option_{idx}",
                        use_container_width=True,
                        type="secondary"
                    ):
                        submit_answer(option)
                        st.rerun()

    else:
        # Show feedback after answer is submitted
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
# SCREEN 3: RESULTS SCREEN
# ============================================
def render_results_screen():
    """Render the final results screen."""

    quiz_data = st.session_state.quiz_data
    total_questions = len(quiz_data['questions'])
    score = st.session_state.score
    percentage = (score / total_questions) * 100

    # Celebration for high scores!
    if percentage >= 70:
        st.balloons()

    # Logo
    st.image("logo.png", width=150)

    # Title
    st.title("🏆 Quiz Complete!")

    # Score display
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
    st.markdown(f"**📚 Subject:** {quiz_data['subject']}")
    st.markdown(f"**📝 Topic:** {quiz_data['topic']}")
    st.markdown(f"**🎓 Grade:** {quiz_data['grade_level']}")

    st.write("")
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

    st.write("")
    st.markdown("---")
    st.write("")

    # Play Again button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 Play Again!", type="primary", use_container_width=True):
            reset_game()
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

    if st.session_state.game_completed:
        # Show results screen
        render_results_screen()
    elif st.session_state.game_active:
        # Show game screen
        render_game_screen()
    else:
        # Show setup screen
        render_setup_screen()

# Run the app
if __name__ == "__main__":
    main()
