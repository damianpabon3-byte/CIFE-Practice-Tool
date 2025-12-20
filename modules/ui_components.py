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
        
        .stButton > button {
            border-radius: 9999px !important;
            height: 60px !important;
            font-weight: 600 !important;
            font-size: 1.1rem !important;
            transition: all 0.2s ease !important;
        }
        
        .stButton > button:hover {
            transform: scale(1.02) !important;
        }

        @keyframes shake {
            0% { transform: translateX(0); }
            25% { transform: translateX(-5px); }
            50% { transform: translateX(5px); }
            75% { transform: translateX(-5px); }
            100% { transform: translateX(0); }
        }
        </style>
    """, unsafe_allow_html=True)

def render_header(title, subtitle, icon="📚"):
    """Render a header with a large icon."""
    st.markdown(f"""
        <div style="text-align: center; margin-bottom: 2rem;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">{icon}</div>
            <h1 style="color: #4F46E5; font-family: 'Fredoka', sans-serif; font-size: 2.5rem; margin: 0;">{title}</h1>
            <p style="color: #6B7280; font-size: 1.1rem;">{subtitle}</p>
        </div>
    """, unsafe_allow_html=True)

def render_wizard_steps(steps, current_step):
    [span_0](start_span)[span_1](start_span)"""Render visual progress circles.[span_0](end_span)[span_1](end_span)"""
    cols = st.columns(len(steps))
    for i, step in enumerate(steps):
        with cols[i]:
            color = "#4F46E5" if i <= current_step else "#E5E7EB"
            st.markdown(f"""
                <div style="text-align: center;">
                    <div style="background-color: {color}; color: white; border-radius: 50%; width: 40px; height: 40px; line-height: 40px; margin: 0 auto; font-weight: bold;">
                        {i + 1}
                    </div>
                    <div style="font-size: 0.8rem; color: {color}; margin-top: 5px;">{step}</div>
                </div>
            """, unsafe_allow_html=True)

def render_progress_bar(current, total, label=""):
    [span_2](start_span)[span_3](start_span)"""Render a kid-friendly progress bar.[span_2](end_span)[span_3](end_span)"""
    percentage = (current / total) * 100
    st.progress(current / total, text=label)

def render_score_display(score, max_score, streak, show_streak=True):
    [span_4](start_span)[span_5](start_span)"""Render score and streak counters.[span_4](end_span)[span_5](end_span)"""
    st.markdown(f"### ⭐ Score: {score}")
    if show_streak and streak > 1:
        st.markdown(f"🔥 **{streak} Streak!**")

def render_question_badge(q_type):
    [span_6](start_span)"""Render a badge for question type.[span_6](end_span)"""
    st.info(f"Type: {q_type.replace('_', ' ').title()}")

def render_feedback(is_correct, explanation, correct_answer):
    [span_7](start_span)[span_8](start_span)"""Render result feedback.[span_7](end_span)[span_8](end_span)"""
    if is_correct:
        st.success(f"🎉 Correct! {explanation}")
    else:
        st.error(f"❌ Incorrect. The answer was: {correct_answer}. {explanation}")

def render_celebration(score, total):
    [span_9](start_span)[span_10](start_span)"""Final celebration message.[span_9](end_span)[span_10](end_span)"""
    st.balloons()
    st.markdown(f"## 🏆 Finished! You got {score} points!")

def render_empty_state():
    """Placeholder for empty views."""
    st.warning("No data found. Please upload a notebook photo first.")

# --- THE MISSING FUNCTION THAT WAS CAUSING YOUR ERROR ---
def render_card(title, content, icon="💡"):
    [span_11](start_span)[span_12](start_span)"""Displays a styled card container.[span_11](end_span)[span_12](end_span)"""
    st.markdown(f"""
        <div style="background: white; border-radius: 20px; padding: 1.5rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border: 1px solid #E5E7EB; margin-bottom: 1rem;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">{icon}</div>
            <h4 style="margin: 0; color: #4F46E5;">{title}</h4>
            <p style="color: #4B5563; margin-top: 0.5rem;">{content}</p>
        </div>
    """, unsafe_allow_html=True)
