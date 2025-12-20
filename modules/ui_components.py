"""
CIFE Edu-Suite - UI Components Module
======================================
Reusable UI components following the child-centric design system.
Includes cards, buttons, progress bars, and styled containers.
"""

import streamlit as st
from typing import Callable, Optional, List, Any
import os


def load_custom_css():
    """
    Load and inject the custom CSS file into the Streamlit app.
    """
    css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "custom.css")

    if os.path.exists(css_path):
        with open(css_path, "r") as f:
            css_content = f.read()
    else:
        # Fallback inline CSS if file doesn't exist
        css_content = _get_fallback_css()

    st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)


def _get_fallback_css() -> str:
    """Return fallback CSS if file is not found."""
    return """
    @import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@300;400;500;600;700&display=swap');
    html, body, button, input { font-family: 'Fredoka', sans-serif !important; }
    .block-container { padding-top: 1rem !important; max-width: 1200px !important; }
    .stButton > button {
        font-family: 'Fredoka', sans-serif !important;
        min-height: 60px !important;
        border-radius: 9999px !important;
        background: linear-gradient(135deg, #4F46E5 0%, #6366F1 100%) !important;
        color: white !important;
        font-weight: 500 !important;
        font-size: 1.1rem !important;
    }
    """


def render_header(title: str, subtitle: str = "", emoji: str = ""):
    """
    Render a styled page header.

    Args:
        title: Main title text
        subtitle: Optional subtitle
        emoji: Optional emoji to display
    """
    header_html = f"""
    <div style="text-align: center; padding: 2rem 0; margin-bottom: 2rem;">
        {f'<div style="font-size: 4rem; margin-bottom: 0.5rem;">{emoji}</div>' if emoji else ''}
        <h1 style="
            font-family: 'Fredoka', sans-serif;
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #4F46E5 0%, #818CF8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin: 0;
        ">{title}</h1>
        {f'<p style="font-size: 1.2rem; color: #6B7280; margin-top: 0.5rem;">{subtitle}</p>' if subtitle else ''}
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)


def render_card(
    content: str,
    title: str = "",
    variant: str = "default",
    custom_class: str = ""
) -> None:
    """
    Render a styled card container.

    Args:
        content: HTML content inside the card
        title: Optional card title
        variant: "default", "success", "error", "warning"
        custom_class: Additional CSS class
    """
    bg_colors = {
        "default": "#FFFFFF",
        "success": "linear-gradient(135deg, #D1FAE5 0%, #A7F3D0 100%)",
        "error": "linear-gradient(135deg, #FEE2E2 0%, #FECACA 100%)",
        "warning": "linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%)"
    }

    border_colors = {
        "default": "transparent",
        "success": "#34D399",
        "error": "#F87171",
        "warning": "#FBBF24"
    }

    card_html = f"""
    <div class="game-card {custom_class}" style="
        background: {bg_colors.get(variant, bg_colors['default'])};
        border: 3px solid {border_colors.get(variant, 'transparent')};
        border-radius: 24px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    ">
        {f'<h3 style="margin-top: 0; font-family: Fredoka, sans-serif; font-weight: 600;">{title}</h3>' if title else ''}
        {content}
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)


def render_card_button(
    text: str,
    key: str,
    callback: Optional[Callable] = None,
    icon: str = "",
    variant: str = "primary",
    disabled: bool = False
) -> bool:
    """
    Render a large, game-style card button.

    Args:
        text: Button text
        key: Unique key for the button
        callback: Function to call on click
        icon: Emoji or icon to display
        variant: "primary", "success", "error", "secondary"
        disabled: Whether button is disabled

    Returns:
        True if button was clicked
    """
    colors = {
        "primary": ("linear-gradient(135deg, #4F46E5 0%, #6366F1 100%)", "#4338CA"),
        "success": ("linear-gradient(135deg, #34D399 0%, #10B981 100%)", "#059669"),
        "error": ("linear-gradient(135deg, #F87171 0%, #EF4444 100%)", "#DC2626"),
        "secondary": ("linear-gradient(135deg, #E5E7EB 0%, #D1D5DB 100%)", "#9CA3AF")
    }

    bg, hover_bg = colors.get(variant, colors["primary"])
    text_color = "#FFFFFF" if variant != "secondary" else "#374151"

    # Create a unique container with custom styling
    button_id = f"card-btn-{key}"

    custom_style = f"""
    <style>
    div[data-testid="stHorizontalBlock"] div[data-testid="column"]:has(button[kind="primary"]) {{
        width: 100%;
    }}
    </style>
    """
    st.markdown(custom_style, unsafe_allow_html=True)

    # Use Streamlit's native button with custom key
    with st.container():
        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            button_text = f"{icon} {text}" if icon else text
            clicked = st.button(
                button_text,
                key=key,
                use_container_width=True,
                disabled=disabled
            )

            if clicked and callback:
                callback()

            return clicked


def render_option_card(
    option_text: str,
    option_label: str,
    key: str,
    is_selected: bool = False,
    is_correct: Optional[bool] = None,
    disabled: bool = False
) -> bool:
    """
    Render a selectable option card for multiple choice questions.

    Args:
        option_text: The option text content
        option_label: Label like "A", "B", "C", "D"
        key: Unique key for the button
        is_selected: Whether this option is currently selected
        is_correct: None if not revealed, True/False after answer
        disabled: Whether the option can be clicked

    Returns:
        True if clicked
    """
    # Determine styling based on state
    if is_correct is True:
        bg = "linear-gradient(135deg, #D1FAE5 0%, #A7F3D0 100%)"
        border = "#34D399"
        icon = "✓"
    elif is_correct is False:
        bg = "linear-gradient(135deg, #FEE2E2 0%, #FECACA 100%)"
        border = "#F87171"
        icon = "✗"
    elif is_selected:
        bg = "linear-gradient(135deg, #EEF2FF 0%, #E0E7FF 100%)"
        border = "#4F46E5"
        icon = ""
    else:
        bg = "#FFFFFF"
        border = "#E5E7EB"
        icon = ""

    label_colors = {
        "A": "#4F46E5",
        "B": "#059669",
        "C": "#DC2626",
        "D": "#D97706"
    }

    label_color = label_colors.get(option_label, "#4F46E5")

    card_html = f"""
    <div style="
        background: {bg};
        border: 3px solid {border};
        border-radius: 16px;
        padding: 1rem 1.5rem;
        margin: 0.5rem 0;
        display: flex;
        align-items: center;
        gap: 1rem;
        transition: all 0.2s ease;
        cursor: {'not-allowed' if disabled else 'pointer'};
        opacity: {'0.7' if disabled else '1'};
    ">
        <div style="
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: {label_color};
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 1.2rem;
            flex-shrink: 0;
        ">{option_label}</div>
        <div style="
            font-family: 'Fredoka', sans-serif;
            font-size: 1.1rem;
            flex-grow: 1;
        ">{option_text}</div>
        {f'<div style="font-size: 1.5rem;">{icon}</div>' if icon else ''}
    </div>
    """

    # We can't make the HTML directly clickable, so we use a button
    clicked = st.button(
        f"{option_label}. {option_text}",
        key=key,
        use_container_width=True,
        disabled=disabled
    )

    return clicked


def render_progress_bar(
    current: int,
    total: int,
    show_text: bool = True,
    label: str = ""
) -> None:
    """
    Render a custom chunky progress bar.

    Args:
        current: Current progress value
        total: Maximum value
        show_text: Whether to show progress text
        label: Optional label to display
    """
    percentage = (current / total * 100) if total > 0 else 0

    progress_html = f"""
    <div style="margin: 1.5rem 0;">
        {f'<div style="font-family: Fredoka, sans-serif; font-weight: 500; margin-bottom: 0.5rem; color: #374151;">{label}</div>' if label else ''}
        <div style="
            background: #E5E7EB;
            border-radius: 9999px;
            height: 24px;
            overflow: hidden;
            box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
            position: relative;
        ">
            <div style="
                height: 100%;
                width: {percentage}%;
                border-radius: 9999px;
                background: linear-gradient(90deg, #4F46E5 0%, #818CF8 50%, #34D399 100%);
                transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
            "></div>
        </div>
        {f'<div style="text-align: center; font-family: Fredoka, sans-serif; font-weight: 600; margin-top: 0.5rem; color: #4F46E5;">{current} / {total}</div>' if show_text else ''}
    </div>
    """
    st.markdown(progress_html, unsafe_allow_html=True)


def render_score_display(
    score: int,
    total: int,
    streak: int = 0,
    show_streak: bool = True
) -> None:
    """
    Render the score and streak display.

    Args:
        score: Current score
        total: Total possible score
        streak: Current answer streak
        show_streak: Whether to show streak counter
    """
    streak_html = ""
    if show_streak and streak > 0:
        fire_count = min(streak, 5)
        fires = "🔥" * fire_count
        streak_class = "streak-fire" if streak >= 3 else ""
        streak_html = f"""
        <div class="{streak_class}" style="
            font-size: 1.5rem;
            font-weight: 600;
            color: #FF6B35;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
            margin-top: 0.5rem;
        ">
            {fires} Streak: {streak}!
        </div>
        """

    score_html = f"""
    <div style="text-align: center; padding: 1rem;">
        <div style="
            font-size: 3rem;
            font-weight: 700;
            background: linear-gradient(135deg, #4F46E5 0%, #818CF8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        ">
            {score} / {total}
        </div>
        <div style="
            font-size: 1.2rem;
            color: #6B7280;
            font-family: 'Fredoka', sans-serif;
        ">
            Points
        </div>
        {streak_html}
    </div>
    """
    st.markdown(score_html, unsafe_allow_html=True)


def render_question_badge(question_type: str) -> None:
    """
    Render a badge showing the question type.

    Args:
        question_type: "multiple_choice", "true_false", or "short_answer"
    """
    badges = {
        "multiple_choice": ("MC", "linear-gradient(135deg, #2AB7CA 0%, #38BDF8 100%)"),
        "true_false": ("T/F", "linear-gradient(135deg, #9BC53D 0%, #84CC16 100%)"),
        "short_answer": ("SA", "linear-gradient(135deg, #E04F80 0%, #F472B6 100%)")
    }

    label, bg = badges.get(question_type, ("?", "#6B7280"))

    badge_html = f"""
    <span style="
        display: inline-block;
        padding: 0.35rem 1rem;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        background: {bg};
        color: white;
        font-family: 'Fredoka', sans-serif;
    ">{label}</span>
    """
    st.markdown(badge_html, unsafe_allow_html=True)


def render_wizard_steps(
    steps: List[str],
    current_step: int
) -> None:
    """
    Render a wizard progress indicator.

    Args:
        steps: List of step names
        current_step: Current step index (0-based)
    """
    steps_html = '<div style="display: flex; justify-content: center; gap: 2rem; margin: 2rem 0; flex-wrap: wrap;">'

    for i, step_name in enumerate(steps):
        if i < current_step:
            # Completed
            circle_style = "background: #34D399; color: white;"
            label_style = "color: #059669;"
            icon = "✓"
        elif i == current_step:
            # Active
            circle_style = "background: #4F46E5; color: white; box-shadow: 0 0 0 4px rgba(79, 70, 229, 0.2);"
            label_style = "color: #4F46E5; font-weight: 600;"
            icon = str(i + 1)
        else:
            # Pending
            circle_style = "background: #E5E7EB; color: #6B7280;"
            label_style = "color: #9CA3AF;"
            icon = str(i + 1)

        steps_html += f"""
        <div style="display: flex; flex-direction: column; align-items: center; gap: 0.5rem;">
            <div style="
                width: 50px;
                height: 50px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.2rem;
                font-weight: 700;
                font-family: 'Fredoka', sans-serif;
                transition: all 0.3s ease;
                {circle_style}
            ">{icon}</div>
            <div style="
                font-size: 0.9rem;
                font-family: 'Fredoka', sans-serif;
                text-align: center;
                {label_style}
            ">{step_name}</div>
        </div>
        """

        # Add connector line (except after last step)
        if i < len(steps) - 1:
            line_color = "#34D399" if i < current_step else "#E5E7EB"
            steps_html += f"""
            <div style="
                width: 60px;
                height: 3px;
                background: {line_color};
                margin-top: 25px;
                border-radius: 2px;
            "></div>
            """

    steps_html += '</div>'
    st.markdown(steps_html, unsafe_allow_html=True)


def render_feedback(
    is_correct: bool,
    explanation: str = "",
    correct_answer: str = ""
) -> None:
    """
    Render answer feedback with animation.

    Args:
        is_correct: Whether the answer was correct
        explanation: Explanation text to show
        correct_answer: The correct answer (shown if wrong)
    """
    if is_correct:
        feedback_html = f"""
        <div class="feedback-correct bounce-in" style="
            background: linear-gradient(135deg, #D1FAE5 0%, #A7F3D0 100%);
            border: 3px solid #34D399;
            border-radius: 20px;
            padding: 1.5rem;
            text-align: center;
            margin: 1rem 0;
        ">
            <div style="font-size: 3rem; margin-bottom: 0.5rem;">🎉</div>
            <div style="
                font-size: 1.5rem;
                font-weight: 600;
                color: #059669;
                font-family: 'Fredoka', sans-serif;
            ">Correct!</div>
            {f'<div style="background: white; border-radius: 16px; padding: 1rem; margin-top: 1rem; border-left: 4px solid #4F46E5; text-align: left;"><strong>💡 Did you know?</strong> {explanation}</div>' if explanation else ''}
        </div>
        """
    else:
        feedback_html = f"""
        <div class="feedback-incorrect shake" style="
            background: linear-gradient(135deg, #FEE2E2 0%, #FECACA 100%);
            border: 3px solid #F87171;
            border-radius: 20px;
            padding: 1.5rem;
            text-align: center;
            margin: 1rem 0;
        ">
            <div style="font-size: 3rem; margin-bottom: 0.5rem;">😮</div>
            <div style="
                font-size: 1.5rem;
                font-weight: 600;
                color: #DC2626;
                font-family: 'Fredoka', sans-serif;
            ">Not quite!</div>
            {f'<div style="margin-top: 0.5rem; color: #374151;"><strong>Correct answer:</strong> {correct_answer}</div>' if correct_answer else ''}
            {f'<div style="background: white; border-radius: 16px; padding: 1rem; margin-top: 1rem; border-left: 4px solid #4F46E5; text-align: left;"><strong>📚 Learn:</strong> {explanation}</div>' if explanation else ''}
        </div>
        """

    st.markdown(feedback_html, unsafe_allow_html=True)


def render_celebration(score: int, total: int) -> None:
    """
    Render a celebration screen for quiz completion.

    Args:
        score: Final score
        total: Total possible score
    """
    percentage = (score / total * 100) if total > 0 else 0

    if percentage >= 90:
        emoji = "🏆"
        message = "Outstanding!"
        color = "#FFD700"
    elif percentage >= 70:
        emoji = "🌟"
        message = "Great job!"
        color = "#34D399"
    elif percentage >= 50:
        emoji = "👍"
        message = "Good effort!"
        color = "#4F46E5"
    else:
        emoji = "💪"
        message = "Keep practicing!"
        color = "#6B7280"

    celebration_html = f"""
    <div class="celebration-container bounce-in" style="text-align: center; padding: 3rem 1rem;">
        <div style="font-size: 6rem; margin-bottom: 1rem;">{emoji}</div>
        <h1 style="
            font-family: 'Fredoka', sans-serif;
            font-size: 2.5rem;
            color: {color};
            margin-bottom: 1rem;
        ">{message}</h1>
        <div style="
            font-size: 4rem;
            font-weight: 700;
            background: linear-gradient(135deg, #4F46E5 0%, #818CF8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        ">{score}/{total}</div>
        <div style="
            font-size: 1.5rem;
            color: #6B7280;
            margin-top: 0.5rem;
        ">{percentage:.0f}% correct</div>
    </div>
    """
    st.markdown(celebration_html, unsafe_allow_html=True)


def render_empty_state(
    message: str,
    icon: str = "📭",
    action_text: str = ""
) -> None:
    """
    Render an empty state placeholder.

    Args:
        message: Message to display
        icon: Emoji icon
        action_text: Optional action hint
    """
    empty_html = f"""
    <div style="
        text-align: center;
        padding: 4rem 2rem;
        background: white;
        border-radius: 24px;
        border: 3px dashed #E5E7EB;
        margin: 2rem 0;
    ">
        <div style="font-size: 4rem; margin-bottom: 1rem; opacity: 0.7;">{icon}</div>
        <div style="
            font-size: 1.2rem;
            color: #6B7280;
            font-family: 'Fredoka', sans-serif;
        ">{message}</div>
        {f'<div style="font-size: 1rem; color: #9CA3AF; margin-top: 0.5rem;">{action_text}</div>' if action_text else ''}
    </div>
    """
    st.markdown(empty_html, unsafe_allow_html=True)
