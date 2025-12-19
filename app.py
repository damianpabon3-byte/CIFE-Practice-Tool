import streamlit as st
import openai
from docx import Document
import base64
import io

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
            # System prompt for the AI
            system_prompt = (
                "You are a helpful teacher's assistant. You will be provided with an "
                "image of a student's notes. Analyze the content, identify the grade "
                "level and subject, and generate a 10-question practice worksheet "
                "(mixed multiple choice and short answer) to help the student review "
                "these concepts. Output ONLY the text content for the worksheet, no "
                "conversational filler."
            )

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
                                "text": "Please analyze this notebook page and create a practice worksheet."
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
            worksheet_content = response.choices[0].message.content

            # Display the generated content
            st.subheader("Generated Practice Worksheet")
            st.write(worksheet_content)

            # Create Word document
            doc = Document()
            doc.add_heading("Practice Worksheet", level=1)
            doc.add_paragraph(worksheet_content)

            # Save document to in-memory buffer
            buffer = io.BytesIO()
            doc.save(buffer)
            buffer.seek(0)

            # Download button for the Word document
            st.download_button(
                label="Download Practice Worksheet",
                data=buffer,
                file_name="practice_worksheet.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
