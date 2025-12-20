"""
CIFE Edu-Suite - Modules Package
=================================
Central module exports for the CIFE educational application.
"""

from .vision_processor import (
    analyze_notebook_image,
    analyze_multiple_images,
    encode_image_to_base64,
    detect_language
)

from .content_generator import (
    generate_quiz,
    generate_quiz_from_analysis,
    quiz_to_dataframe,
    dataframe_to_quiz,
    create_smart_blank
)

from .ui_components import (
    load_custom_css,
    render_header,
    render_card,
    render_card_button,
    render_option_card,
    render_progress_bar,
    render_score_display,
    render_question_badge,
    render_wizard_steps,
    render_feedback,
    render_celebration,
    render_empty_state
)

from .gamification import (
    init_game_state,
    reset_game_state,
    play_sound,
    show_confetti,
    show_celebration_animation,
    check_answer,
    update_score,
    get_streak_message,
    get_score_multiplier,
    calculate_final_grade,
    get_performance_stats,
    render_streak_indicator,
    render_score_popup
)

from .exporter import (
    create_pdf,
    create_docx,
    create_json_export,
    import_from_json,
    create_answer_sheet_pdf,
    get_download_filename
)

__all__ = [
    # Vision processor
    'analyze_notebook_image',
    'analyze_multiple_images',
    'encode_image_to_base64',
    'detect_language',

    # Content generator
    'generate_quiz',
    'generate_quiz_from_analysis',
    'quiz_to_dataframe',
    'dataframe_to_quiz',
    'create_smart_blank',

    # UI components
    'load_custom_css',
    'render_header',
    'render_card',
    'render_card_button',
    'render_option_card',
    'render_progress_bar',
    'render_score_display',
    'render_question_badge',
    'render_wizard_steps',
    'render_feedback',
    'render_celebration',
    'render_empty_state',

    # Gamification
    'init_game_state',
    'reset_game_state',
    'play_sound',
    'show_confetti',
    'show_celebration_animation',
    'check_answer',
    'update_score',
    'get_streak_message',
    'get_score_multiplier',
    'calculate_final_grade',
    'get_performance_stats',
    'render_streak_indicator',
    'render_score_popup',

    # Exporter
    'create_pdf',
    'create_docx',
    'create_json_export',
    'import_from_json',
    'create_answer_sheet_pdf',
    'get_download_filename'
]
