import streamlit as st
import base64

def load_custom_css():
    """Inject custom CSS for fonts, buttons, and animations."""
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@300;400;500;600;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Fredoka', sans-serif;
        }
        
        /* Button Styling */
        .stButton > button {
            border-radius: 9999px !important;
            height: 60px !important;
            font-weight: 600 !important;
            font-size: 1.1rem !important;
            border: none !important;
            transition: all 0.2s ease !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06) !important;
        }
        
        .stButton > button:hover {
            transform: scale(1.02) !important;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05) !important;
        }

        /* Shake Animation for Wrong Answers */
        @keyframes shake {
            0% { transform: translateX(0); }
            25% { transform: translateX(-5px); }
            50% { transform: translateX(5px); }
            75% { transform: translateX(-5px); }
            100% { transform: translateX(0); }
        }
        
        .shake {
            animation: shake 0.5s;
        }
        
        /* Clean up Streamlit padding */
        .block-container {
            padding-top: 2rem !important;
            padding-bottom: 5rem !important;
        }
        </style>
    """, unsafe_allow_html=True)

def render_header(title, subtitle, icon="📚"):
    """Render a header with a large icon and Fredoka font."""
    st.markdown(f"""
        <div style="text-align: center; margin-bottom: 2rem;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">{icon}</div>
            <h1 style="
                color: #4F46E5; 
                font-family: 'Fredoka', sans-serif; 
                font-size: 3rem; 
                margin: 0;
                font-weight: 700;
            ">{title}</h1>
            <p style="
                color: #6B7280; 
                font-size: 1.2rem; 
                margin-top: 0.5rem;
            ">{subtitle}</p>
        </div>
    """, unsafe_allow_html=True)

def render_wizard_steps(steps, current_step):
    """
    Render a progress wizard with circles and connecting lines.
    Correctly uses st.markdown to render HTML instead of showing code.
    """
    html_steps = []
    
    for i, step in enumerate(steps):
        is_active = i == current_step
        is_completed = i < current_step
        
        # Colors
        bg_color = "#4F46E5" if (is_active or is_completed) else "#E5E7EB"
        text_color = "white" if (is_active or is_completed) else "#6B7280"
        border_color = "#4F46E5" if is_active else "transparent"
        
        # The Step Circle
        circle = f"""
            <div style="
                width: 40px; 
                height: 40px; 
                border-radius: 50%; 
                background-color: {bg_color}; 
                color: {text_color};
                display: flex; 
                align-items: center; 
                justify-content: center; 
                font-weight: bold;
                font-size: 1.2rem;
                border: 3px solid {border_color};
                z-index: 10;
                font-family: 'Fredoka', sans-serif;
            ">
                {i + 1}
            </div>
        """
        
        # The Step Label
        label = f"""
            <div style="
                margin-top: 0.5rem; 
                color: {bg_color if is_active else '#9CA3AF'};
                font-weight: {'bold' if is_active else 'normal'};
                font-size: 0.9rem;
                font-family: 'Fredoka', sans-serif;
            ">
                {step}
            </div>
        """
        
        step_html = f"""
            <div style="display: flex; flex-direction: column; align-items: center; position: relative;">
                {circle}
                {label}
            </div>
        """
        html_steps.append(step_html)

    # Combine steps with a connecting line behind them
    steps_html = "".join(html_steps)
    
    # Render the full container
    st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin: 0 auto 3rem auto; max-width: 600px; position: relative;">
            <div style="
                position: absolute; 
                top: 20px; 
                left: 0; 
                right: 0; 
                height: 3px; 
                background: #E5E7EB; 
                z-index: 0;
            "></div>
            <div style="
                position: absolute; 
                top: 20px; 
                left: 0; 
                width: {current_step / (len(steps) - 1) * 100}%; 
                height: 3px; 
                background: #4F46E5; 
                z-index: 1;
                transition: width 0.5s ease;
            "></div>
            <div style="display: flex; justify-content: space-between; width: 100%; z-index: 2;">
                {steps_html}
            </div>
        </div>
    """, unsafe_allow_html=True)

def render_progress_bar(current, total, label=""):
    """Render a chunky, kid-friendly progress bar."""
    percentage = (current / total) * 100
    st.markdown(f"""
        <div style="margin-bottom: 1rem;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem; color: #6B7280; font-size: 0.9rem; font-weight: bold;">
                <span>{label}</span>
                <span>{int(percentage)}%</span>
            </div>
            <div style="width: 100%; height: 16px; background-color: #E5E7EB; border-radius: 9999px; overflow: hidden;">
                <div style="
                    width: {percentage}%; 
                    height: 100%; 
                    background: linear-gradient(90deg, #4F46E5 0%, #818CF8 100%); 
                    border-radius: 9999px;
                    transition: width 0.5s ease;
                "></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def render_score_display(score, max_score, streak, show_streak=True):
    """Render the score and streak counters."""
    streak_html = ""
    if show_streak and streak > 1:
        streak_html = f"""
            <div style="
                background: #FEF3C7; 
                color: #D97706; 
                padding: 0.5rem 1rem; 
                border-radius: 9999px; 
                font-weight: bold; 
                display: flex; 
                align-items: center; 
                gap: 0.5rem;
            ">
                🔥 {streak} Streak!
            </div>
        """
        
    st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 1rem;">
            <div style="
                background: #EEF2FF; 
                color: #4F46E5; 
                padding: 0.5rem 1.5rem; 
                border-radius: 9999px; 
                font-weight: bold; 
                font-size: 1.2rem;
            ">
                ⭐ {score} pts
            </div>
            {streak_html}
        </div>
    """, unsafe_allow_html=True)

def render_question_badge(q_type):
    """Render a badge indicating the question type."""
    badges = {
        "multiple_choice": ("Multiple Choice", "#DBEAFE", "#1E40AF"),
        "true_false": ("True / False", "#D1FAE5", "#065F46"),
        "short_answer": ("Short Answer", "#FCE7F3", "#9D174D")
    }
    
    label, bg, text = badges.get(q_type, ("Question", "#F3F4F6", "#374151"))
    
    st.markdown(f"""
        <span style="
            background-color: {bg}; 
            color: {text}; 
            padding: 0.25rem 0.75rem; 
            border-radius: 9999px; 
            font-size: 0.8rem; 
            font-weight: bold; 
            text-transform: uppercase; 
            letter-spacing: 0.05em;
        ">
            {label}
        </span>
    """, unsafe_allow_html=True)

def render_feedback(is_correct, explanation, correct_answer):
    """Render the feedback card after an answer."""
    color = "#10B981" if is_correct else "#EF4444"
    bg_color = "#D1FAE5" if is_correct else "#FEE2E2"
    icon = "🎉 Correct!" if is_correct else "❌ Incorrect"
    
    st.markdown(f"""
        <div style="
            background-color: {bg_color}; 
            border: 2px solid {color}; 
            border-radius: 16px; 
            padding: 1.5rem; 
            margin-top: 1.5rem;
            animation: fadeIn 0.5s ease;
        ">
            <h3 style="color: {color}; margin-top: 0; display: flex; align-items: center; gap: 0.5rem;">
                {icon}
            </h3>
            <p style="color: #1F2937; font-size: 1.1rem; margin-bottom: 0.5rem;">
                {explanation}
            </p>
            {f'<div style="margin-top: 1rem; font-weight: bold; color: #1F2937;">Correct Answer: <span style="color: {color}">{correct_answer}</span></div>' if not is_correct else ''}
        </div>
    """, unsafe_allow_html=True)

def render_celebration(score, total):
    """Render a celebration message based on score."""
    percentage = (score / total) * 100 if total > 0 else 0
    
    if percentage >= 90:
        msg = "🌟 Outstanding! You're a Superstar!"
        color = "#4F46E5"
    elif percentage >= 70:
        msg = "👍 Great Job! Keep it up!"
        color = "#059669"
    else:
        msg = "💪 Good Effort! Practice makes perfect."
        color = "#D97706"
        
    st.markdown(f"""
        <div style="text-align: center; margin: 2rem 0;">
            <h2 style="color: {color}; font-size: 2rem; margin-bottom: 0.5rem;">{msg}</h2>
            <p style="color: #6B7280; font-size: 1.2rem;">You got {score} out of {total} correct!</p>
        </div>
    """, unsafe_allow_html=True)

def render_empty_state():
    """Render placeholder for empty states."""
    st.markdown("""
        <div style="text-align: center; padding: 3rem; color: #9CA3AF; border: 2px dashed #E5E7EB; border-radius: 16px;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">📭</div>
            <p>No content available yet.</p>
        </div>
    """, unsafe_allow_html=True)
