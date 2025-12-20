# CIFE Edu-Suite

A production-ready Streamlit application that allows teachers to upload photos of student notebooks and automatically generates gamified, interactive quizzes and downloadable practice sheets.

## Features

- **AI-Powered Analysis**: Uses GPT-4o Vision to transcribe handwritten notes and identify learning concepts
- **Intelligent Quiz Generation**: Creates pedagogically-sound questions with common misconceptions as distractors
- **Gamified Experience**: Streak tracking, score multipliers, and celebration animations
- **Multiple Question Types**: Multiple choice, True/False, and Short Answer
- **Human-in-the-Loop Editing**: Review and edit generated questions before use
- **Export Options**: Download as PDF (student worksheet + teacher key) or Word document
- **Child-Centric Design**: Colorful, accessible UI with Fredoka font and engaging animations

## Project Structure

```
CIFE-Practice-Tool/
├── main.py                      # Main application entry point
├── modules/
│   ├── __init__.py              # Module exports
│   ├── vision_processor.py      # GPT-4o Vision integration
│   ├── content_generator.py     # Quiz generation engine
│   ├── ui_components.py         # Reusable UI components
│   ├── gamification.py          # Scoring, streaks, animations
│   └── exporter.py              # PDF/DOCX generation
├── assets/
│   └── custom.css               # Child-centric design system
├── requirements.txt             # Python dependencies
└── README.md
```

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
streamlit run main.py
```

1. Enter your OpenAI API key in the sidebar
2. Upload photos of student notebooks
3. Review AI analysis and configure quiz settings
4. Edit generated questions as needed
5. Play the interactive quiz or download for printing

## Requirements

- Python 3.8+
- OpenAI API key with GPT-4o access
- See `requirements.txt` for full dependencies

## Design System

The application uses a child-centric design language:
- **Typography**: Fredoka font for playful, readable text
- **Colors**: Indigo primary (#4F46E5), Emerald success (#34D399), Red errors (#F87171)
- **Buttons**: Pill-shaped (border-radius: 9999px) with minimum 60px height
- **Animations**: Shake for incorrect, bounce for correct, confetti for celebrations
