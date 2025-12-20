"""
CIFE Quiz Platform - Main Application Controller
==================================================
This is the main entry point that coordinates the UI and Backend modules.
Handles:
- Page configuration
- Session state initialization
- Game state management
- Routing between screens
"""

import streamlit as st

# Import modular components
import ui
import backend

# ============================================
# PAGE CONFIG
# ============================================
st.set_page_config(
    page_title="CIFE Quiz Platform",
    page_icon="🐯",
    layout="wide"
)

# Apply CIFE brand styling
ui.apply_cife_styling()


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
# EARLY GAME CHECK - CRITICAL FOR STATE MANAGEMENT
# ============================================
# This check MUST happen at the top, BEFORE any other UI is rendered.
# If a game is active, we skip straight to the game engine and prevent
# the lobby from loading (which would cause state reset issues).

def check_and_run_game():
    """
    Check if game should be running and render it immediately.
    Returns True if game was rendered, False if we should continue to lobby.
    """
    # First priority: Check if game is completed (show results)
    if st.session_state.get('game_completed', False):
        return 'results'

    # Second priority: Check if game is actively running
    if st.session_state.get('game_active', False) and st.session_state.get('quiz_data') is not None:
        return 'game'

    return None


# ============================================
# HELPER FUNCTIONS (State Management)
# ============================================
def reset_to_home():
    """Reset all state and go to home."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    init_session_state()


def reset_game_state():
    """Reset game state variables only (does NOT touch game_active flag)."""
    st.session_state.current_question_index = 0
    st.session_state.score = 0
    st.session_state.user_answer = None
    st.session_state.answer_submitted = False
    st.session_state.wrong_answers = []
    st.session_state.game_completed = False
    # Clear any scored/tracked attributes
    for key in list(st.session_state.keys()):
        if key.startswith('scored_') or key.startswith('tracked_'):
            del st.session_state[key]


def start_game(quiz_data):
    """Properly start a game with the given quiz data."""
    st.session_state.quiz_data = quiz_data
    st.session_state.game_active = True
    st.session_state.current_question_index = 0
    st.session_state.score = 0
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


# ============================================
# MAIN APP ROUTER
# ============================================
def main():
    """Main app router - determines which screen to show."""

    # CRITICAL: Check game state FIRST before any lobby UI loads
    # This prevents the state reset loop when transitioning to game mode
    game_state = check_and_run_game()

    if game_state == 'results':
        ui.render_results_screen(reset_to_home, reset_game_state)
        return

    if game_state == 'game':
        ui.render_game_screen(reset_to_home, submit_answer, next_question)
        return

    # No active game - render the lobby/menu screens
    if st.session_state.app_mode == 'home':
        ui.render_home_screen()
    elif st.session_state.app_mode == 'create':
        ui.render_create_mode(reset_to_home, start_game)
    elif st.session_state.app_mode == 'play':
        ui.render_play_mode(reset_to_home, start_game)


# Run the app
if __name__ == "__main__":
    main()
