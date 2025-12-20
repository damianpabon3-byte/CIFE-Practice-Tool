"""
CIFE Edu-Suite - Gamification Module
=====================================
Handles game mechanics, audio feedback, Lottie animations,
streak tracking, and scoring logic for engaging quiz experiences.
"""

import streamlit as st
from typing import Optional, Tuple
import base64


# Base64 encoded audio for sound effects (short, simple beeps)
# These are placeholder values - in production, you'd use actual sound files

# Correct answer sound (cheerful ding)
CORRECT_SOUND_BASE64 = """
UklGRjIAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQAAAAA=
"""

# Incorrect answer sound (soft buzz)
INCORRECT_SOUND_BASE64 = """
UklGRjIAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQAAAAA=
"""

# Streak milestone sound
STREAK_SOUND_BASE64 = """
UklGRjIAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQAAAAA=
"""


def init_game_state() -> None:
    """
    Initialize all gamification-related session state variables.
    Call this at the start of your app.
    """
    if "score" not in st.session_state:
        st.session_state.score = 0

    if "streak" not in st.session_state:
        st.session_state.streak = 0

    if "max_streak" not in st.session_state:
        st.session_state.max_streak = 0

    if "total_questions" not in st.session_state:
        st.session_state.total_questions = 0

    if "correct_answers" not in st.session_state:
        st.session_state.correct_answers = 0

    if "wrong_answers_list" not in st.session_state:
        st.session_state.wrong_answers_list = []

    if "sound_enabled" not in st.session_state:
        st.session_state.sound_enabled = True

    if "animations_enabled" not in st.session_state:
        st.session_state.animations_enabled = True


def reset_game_state() -> None:
    """Reset all game state variables for a new game."""
    st.session_state.score = 0
    st.session_state.streak = 0
    st.session_state.max_streak = 0
    st.session_state.total_questions = 0
    st.session_state.correct_answers = 0
    st.session_state.wrong_answers_list = []


def play_sound(sound_type: str) -> None:
    """
    Play a sound effect using HTML5 audio with Base64 encoding.

    Args:
        sound_type: "correct", "incorrect", or "streak"
    """
    if not st.session_state.get("sound_enabled", True):
        return

    sounds = {
        "correct": CORRECT_SOUND_BASE64,
        "incorrect": INCORRECT_SOUND_BASE64,
        "streak": STREAK_SOUND_BASE64
    }

    sound_data = sounds.get(sound_type, CORRECT_SOUND_BASE64)

    # Clean up the base64 string
    sound_data = sound_data.strip().replace("\n", "")

    audio_html = f"""
    <audio autoplay style="display:none;">
        <source src="data:audio/wav;base64,{sound_data}" type="audio/wav">
    </audio>
    """

    st.markdown(audio_html, unsafe_allow_html=True)


def show_confetti() -> None:
    """
    Display a Lottie confetti animation for celebrations.
    Uses a CDN-hosted Lottie animation.
    """
    if not st.session_state.get("animations_enabled", True):
        return

    # Lottie animation URLs (public, CDN-hosted)
    confetti_url = "https://assets5.lottiefiles.com/packages/lf20_u4yrau.json"

    try:
        from streamlit_lottie import st_lottie
        import requests

        response = requests.get(confetti_url, timeout=5)
        if response.status_code == 200:
            st_lottie(response.json(), height=200, key="confetti")
    except ImportError:
        # Fallback: CSS confetti animation
        _show_css_confetti()
    except Exception:
        # Fallback on any error
        _show_css_confetti()


def show_celebration_animation(celebration_type: str = "confetti") -> None:
    """
    Show a celebration animation.

    Args:
        celebration_type: "confetti", "fireworks", "stars", or "balloons"
    """
    if not st.session_state.get("animations_enabled", True):
        return

    lottie_urls = {
        "confetti": "https://assets5.lottiefiles.com/packages/lf20_u4yrau.json",
        "fireworks": "https://assets2.lottiefiles.com/packages/lf20_xlmz9xwm.json",
        "stars": "https://assets10.lottiefiles.com/packages/lf20_xyadoh9h.json",
        "balloons": "https://assets3.lottiefiles.com/packages/lf20_ihzehey7.json"
    }

    url = lottie_urls.get(celebration_type, lottie_urls["confetti"])

    try:
        from streamlit_lottie import st_lottie
        import requests

        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            st_lottie(
                response.json(),
                height=250,
                key=f"celebration_{celebration_type}"
            )
    except Exception:
        _show_css_confetti()


def _show_css_confetti() -> None:
    """Fallback CSS-based confetti animation."""
    confetti_html = """
    <style>
    @keyframes confetti-fall {
        0% { transform: translateY(-100vh) rotate(0deg); opacity: 1; }
        100% { transform: translateY(100vh) rotate(720deg); opacity: 0; }
    }

    .confetti-container {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        overflow: hidden;
        z-index: 9999;
    }

    .confetti {
        position: absolute;
        width: 10px;
        height: 10px;
        animation: confetti-fall 3s ease-out forwards;
    }
    </style>

    <div class="confetti-container">
        <div class="confetti" style="left: 10%; background: #4F46E5; animation-delay: 0s;"></div>
        <div class="confetti" style="left: 20%; background: #34D399; animation-delay: 0.2s;"></div>
        <div class="confetti" style="left: 30%; background: #F87171; animation-delay: 0.1s;"></div>
        <div class="confetti" style="left: 40%; background: #FBBF24; animation-delay: 0.3s;"></div>
        <div class="confetti" style="left: 50%; background: #818CF8; animation-delay: 0.15s;"></div>
        <div class="confetti" style="left: 60%; background: #34D399; animation-delay: 0.25s;"></div>
        <div class="confetti" style="left: 70%; background: #4F46E5; animation-delay: 0.05s;"></div>
        <div class="confetti" style="left: 80%; background: #F87171; animation-delay: 0.35s;"></div>
        <div class="confetti" style="left: 90%; background: #FBBF24; animation-delay: 0.4s;"></div>
    </div>
    """
    st.markdown(confetti_html, unsafe_allow_html=True)


def check_answer(
    selected_index: int,
    correct_index: int,
    user_text: str = "",
    correct_text: str = "",
    question_type: str = "multiple_choice"
) -> bool:
    """
    Check if the given answer is correct.

    Args:
        selected_index: Index of selected option (for MC/TF)
        correct_index: Index of correct answer
        user_text: User's text input (for short answer)
        correct_text: Correct answer text (for short answer)
        question_type: Type of question

    Returns:
        True if answer is correct
    """
    if question_type == "short_answer":
        # Case-insensitive comparison, strip whitespace
        user_clean = user_text.strip().lower()
        correct_clean = correct_text.strip().lower()

        # Exact match or close enough (within common variations)
        if user_clean == correct_clean:
            return True

        # Check for common acceptable variations
        # Remove punctuation for comparison
        import re
        user_simple = re.sub(r'[^\w\s]', '', user_clean)
        correct_simple = re.sub(r'[^\w\s]', '', correct_clean)

        return user_simple == correct_simple

    else:
        # Multiple choice or True/False
        return selected_index == correct_index


def update_score(is_correct: bool, question_data: Optional[dict] = None) -> Tuple[int, int]:
    """
    Update the score and streak based on answer correctness.

    Args:
        is_correct: Whether the answer was correct
        question_data: Optional question dict to track wrong answers

    Returns:
        Tuple of (points_earned, new_streak)
    """
    init_game_state()

    if is_correct:
        # Base points
        base_points = 10

        # Streak bonus (10% per streak level, max 50%)
        streak_bonus = min(st.session_state.streak * 0.1, 0.5)
        points_earned = int(base_points * (1 + streak_bonus))

        # Update state
        st.session_state.score += points_earned
        st.session_state.streak += 1
        st.session_state.correct_answers += 1

        # Update max streak
        if st.session_state.streak > st.session_state.max_streak:
            st.session_state.max_streak = st.session_state.streak

        # Play celebration sounds for milestones
        if st.session_state.streak in [3, 5, 10]:
            play_sound("streak")
        else:
            play_sound("correct")

        return points_earned, st.session_state.streak

    else:
        # Wrong answer
        st.session_state.streak = 0

        # Track wrong answer if question data provided
        if question_data:
            st.session_state.wrong_answers_list.append(question_data)

        play_sound("incorrect")

        return 0, 0


def get_streak_message(streak: int) -> str:
    """
    Get an encouraging message based on current streak.

    Args:
        streak: Current streak count

    Returns:
        Motivational message string
    """
    messages = {
        0: "Let's go! 💪",
        1: "Good start! 🌟",
        2: "You're on a roll! ⭐",
        3: "Hat trick! 🎩",
        4: "Fantastic! 🔥",
        5: "On fire! 🔥🔥",
        6: "Unstoppable! 🚀",
        7: "Incredible! 💫",
        8: "Legendary! 👑",
        9: "Master level! 🎯",
        10: "PERFECT! 🏆"
    }

    if streak >= 10:
        return f"AMAZING! {streak} in a row! 🏆🔥"

    return messages.get(streak, f"Keep going! {streak} streak! 🌟")


def get_score_multiplier(streak: int) -> float:
    """
    Get the score multiplier based on current streak.

    Args:
        streak: Current streak count

    Returns:
        Multiplier value (1.0 to 1.5)
    """
    return min(1.0 + (streak * 0.1), 1.5)


def calculate_final_grade(score: int, total_possible: int) -> Tuple[str, str, str]:
    """
    Calculate final grade based on score percentage.

    Args:
        score: Final score
        total_possible: Maximum possible score

    Returns:
        Tuple of (grade_letter, grade_description, emoji)
    """
    if total_possible == 0:
        return "N/A", "No questions answered", "❓"

    percentage = (score / total_possible) * 100

    if percentage >= 95:
        return "A+", "Outstanding!", "🏆"
    elif percentage >= 90:
        return "A", "Excellent!", "🌟"
    elif percentage >= 85:
        return "A-", "Great work!", "⭐"
    elif percentage >= 80:
        return "B+", "Very good!", "👏"
    elif percentage >= 75:
        return "B", "Good job!", "👍"
    elif percentage >= 70:
        return "B-", "Nice effort!", "💪"
    elif percentage >= 65:
        return "C+", "Getting there!", "📈"
    elif percentage >= 60:
        return "C", "Keep practicing!", "📚"
    elif percentage >= 55:
        return "C-", "Almost there!", "🎯"
    elif percentage >= 50:
        return "D", "Need more practice", "💡"
    else:
        return "F", "Let's try again!", "🔄"


def get_performance_stats() -> dict:
    """
    Get comprehensive performance statistics.

    Returns:
        Dictionary with all performance metrics
    """
    init_game_state()

    total = st.session_state.total_questions
    correct = st.session_state.correct_answers
    wrong = total - correct

    accuracy = (correct / total * 100) if total > 0 else 0

    return {
        "total_questions": total,
        "correct_answers": correct,
        "wrong_answers": wrong,
        "accuracy_percentage": accuracy,
        "final_score": st.session_state.score,
        "max_streak": st.session_state.max_streak,
        "wrong_answers_list": st.session_state.wrong_answers_list
    }


def render_streak_indicator(streak: int) -> None:
    """
    Render a visual streak indicator.

    Args:
        streak: Current streak count
    """
    if streak == 0:
        return

    fire_count = min(streak, 5)
    fires = "🔥" * fire_count

    glow_class = "streak-fire" if streak >= 3 else ""

    streak_html = f"""
    <div class="{glow_class}" style="
        text-align: center;
        padding: 0.5rem 1rem;
        background: linear-gradient(135deg, #FF6B35 0%, #FF9F1C 100%);
        color: white;
        border-radius: 9999px;
        font-size: 1.2rem;
        font-weight: 600;
        font-family: 'Fredoka', sans-serif;
        display: inline-block;
        box-shadow: 0 4px 15px rgba(255, 107, 53, 0.4);
        animation: pulse 2s ease-in-out infinite;
    ">
        {fires} {streak} Streak!
    </div>
    """
    st.markdown(streak_html, unsafe_allow_html=True)


def render_score_popup(points: int, is_correct: bool) -> None:
    """
    Render a popup showing points earned.

    Args:
        points: Points earned (or 0 for wrong answer)
        is_correct: Whether the answer was correct
    """
    if is_correct:
        popup_html = f"""
        <div class="pop" style="
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 3rem;
            font-weight: 700;
            color: #34D399;
            z-index: 9999;
            text-shadow: 0 2px 10px rgba(52, 211, 153, 0.5);
            animation: scoreUp 1s ease forwards;
        ">
            +{points}
        </div>
        """
    else:
        popup_html = """
        <div class="shake" style="
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 3rem;
            font-weight: 700;
            color: #F87171;
            z-index: 9999;
            text-shadow: 0 2px 10px rgba(248, 113, 113, 0.5);
        ">
            ✗
        </div>
        """

    st.markdown(popup_html, unsafe_allow_html=True)
