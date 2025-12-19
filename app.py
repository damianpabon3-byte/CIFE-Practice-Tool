import streamlit as st
import openai
from docx import Document
import base64
import io
import json

# Configure the OpenAI client with API key from Streamlit secrets
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# App title and description
st.title("Teacher's Assistant")
st.write("Upload a photo of a student's notebook page to generate a practice quiz.")

# File uploader for images
uploaded_file = st.file_uploader(
    "Upload a notebook image",
    type=["jpg", "jpeg", "png"],
    help="Supported formats: JPG, PNG"
)

# Process the uploaded image
if uploaded_file is not None:
    # Display the uploaded image
    st.image(uploaded_file, caption="Uploaded Notebook Page", use_container_width=True)

    # Convert image to Base64
    image_bytes = uploaded_file.getvalue()
    base64_image = base64.b64encode(image_bytes).decode("utf-8")

    # Determine the image MIME type
    file_extension = uploaded_file.name.split(".")[-1].lower()
    if file_extension in ["jpg", "jpeg"]:
        mime_type = "image/jpeg"
    else:
        mime_type = "image/png"

    # Generate Practice Sheet button
    if st.button("Generate Practice Sheet"):
        with st.spinner("Analyzing image and generating practice worksheet..."):
            # System prompt for the AI - requesting JSON output with language detection
            system_prompt = """You are a helpful teacher's assistant. You will be provided with an image of a student's handwritten notes.

IMPORTANT INSTRUCTIONS:
1. LANGUAGE DETECTION: Analyze the language of the handwritten notes (e.g., Spanish, English, French, etc.). Generate the practice worksheet in that SAME language. If the notes are in Spanish, the quiz must be in Spanish. If in English, the quiz must be in English.

2. Analyze the content, identify the grade level and subject.

3. Generate a 10-question multiple choice practice quiz to help the student review these concepts.

4. You MUST output your response as a valid JSON object with NO markdown formatting around it (no ```json blocks). Use this EXACT structure:

{
  "subject": "Subject Name",
  "grade_level": "Grade Level",
  "questions": [
    {
      "q": "The question text here",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "answer": "The correct option text"
    }
  ]
}

REQUIREMENTS:
- Generate exactly 10 questions
- Each question must have exactly 4 options
- The "answer" must match one of the options exactly
- All text must be in the SAME language as the student's notes
- Use proper UTF-8 characters for special characters (ñ, á, é, í, ó, ú, ü, etc.)"""

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
                        "content": [
                            {
                                "type": "text",
                                "text": "Please analyze this notebook page. Detect the language of the notes and create a practice quiz in that same language. Output as pure JSON only."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=2000
            )

            # Extract the generated content
            raw_content = response.choices[0].message.content

            try:
                # Parse the JSON response
                quiz_data = json.loads(raw_content)

                # Display the generated content in Streamlit
                st.subheader("Generated Practice Quiz")
                st.write(f"**Subject:** {quiz_data['subject']}")
                st.write(f"**Grade Level:** {quiz_data['grade_level']}")
                st.write("---")

                for i, question in enumerate(quiz_data['questions'], 1):
                    st.write(f"**{i}. {question['q']}**")
                    for option in question['options']:
                        st.write(f"   • {option}")
                    st.write("")

                # Create professionally formatted Word document
                doc = Document()

                # Add bold title using subject and grade_level
                title = doc.add_heading(level=0)
                title_run = title.add_run(f"{quiz_data['subject']} - {quiz_data['grade_level']}")
                title_run.bold = True

                # Add subtitle
                subtitle = doc.add_paragraph()
                subtitle_run = subtitle.add_run("Practice Quiz")
                subtitle_run.bold = True

                doc.add_paragraph()  # Add spacing

                # Iterate through questions
                for i, question in enumerate(quiz_data['questions'], 1):
                    # Add question text as bold paragraph
                    question_para = doc.add_paragraph()
                    question_run = question_para.add_run(f"{i}. {question['q']}")
                    question_run.bold = True

                    # Add options as bullet points
                    for option in question['options']:
                        doc.add_paragraph(option, style='List Bullet')

                    # Add spacing between questions
                    doc.add_paragraph()

                # Add page break before answer key
                doc.add_page_break()

                # Add Answer Key section with bold heading
                answer_heading = doc.add_heading(level=1)
                answer_heading_run = answer_heading.add_run("Answer Key")
                answer_heading_run.bold = True

                for i, question in enumerate(quiz_data['questions'], 1):
                    answer_para = doc.add_paragraph()
                    answer_para.add_run(f"{i}. ").bold = True
                    answer_para.add_run(question['answer'])

                # Save document to in-memory buffer with UTF-8 encoding
                buffer = io.BytesIO()
                doc.save(buffer)
                buffer.seek(0)

                # Download button for the Word document
                st.download_button(
                    label="Download Practice Quiz",
                    data=buffer,
                    file_name="practice_quiz.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

            except json.JSONDecodeError as e:
                st.error("Failed to parse the AI response as JSON. Please try again.")
                st.text("Raw response:")
                st.code(raw_content)
