
import streamlit as st
import google.generativeai as genai
from PIL import Image
import time
import re
from googletrans import Translator

# Set up the API Key
st.title("Jewelry Details Using Multiple Images")
api_key = "AIzaSyCL58cPfQpngW5kwDIrvqV6e4VaHkcDBBk"  # Replace with your actual API key

if api_key:
    genai.configure(api_key=api_key)

    translator = Translator()

    # File upload function for Gemini API
    def upload_image(image_file, display_name):
        mime_type = "image/jpeg" if image_file.name.endswith(("jpg", "jpeg")) else "image/png"
        image = genai.upload_file(image_file, mime_type=mime_type, display_name=display_name)
        return image

    # Check upload status
    def check_file_status(file_name):
        file = genai.get_file(file_name)
        while file.state.name == "PROCESSING":
            st.write("Processing the uploaded image...")
            time.sleep(5)
            file = genai.get_file(file_name)
        return file

    # Function to analyze content with the model
    def analyze_content(images, prompt):
        model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest")
        response = model.generate_content(images + [prompt])
        return response.text

    # Function to format response using regular expressions
    def format_response(response):
        pattern = re.compile(r"(Metal Type|Type of Jewelry|Karat|Weight|Hallmark|Design Style|Setting|Pattern|Color|Gemstone|Type of Gemstone|Shape|Cut|Clarity|Carat|Metal Finish|Center Stone|Side Stone|Clasp|Strands|Length|Back Type|Meta Title|Meta Keywords):\s*(.*?)(?=\b(?:Metal Type|Type of Jewelry|Karat|Weight|Hallmark|Design Style|Setting|Pattern|Color|Gemstone|Type of Gemstone|Shape|Cut|Clarity|Carat|Metal Finish|Center Stone|Side Stone|Clasp|Strands|Length|Back Type|Meta Title|Meta Keywords|$))", re.DOTALL)

        details = {}
        for match in pattern.finditer(response):
            key = match.group(1).strip()
            value = match.group(2).strip()
            if value.lower() not in ["not visible", "not applicable", "not specified"]:
                details[key] = value
        return details

    st.write("## Upload up to 5 Images of the Same Jewelry")

    uploaded_files = st.file_uploader("Choose up to 5 images (e.g., jewelry)", type=["jpg", "jpeg", "png"], accept_multiple_files=True, key="multi_file")
    if uploaded_files:
        if len(uploaded_files) > 5:
            st.error("You can upload a maximum of 5 images.")
        else:
            # Display uploaded images
            for uploaded_file in uploaded_files:
                img = Image.open(uploaded_file)
                st.image(img, caption=uploaded_file.name, use_column_width=True)

            st.write("Uploading the images to Gemini API...")
            sample_files = []
            for uploaded_file in uploaded_files:
                sample_file = upload_image(uploaded_file, display_name=uploaded_file.name)
                sample_files.append(sample_file)
                st.write(f"Uploaded file URI: {sample_file.uri}")

            files_ready = []
            for sample_file in sample_files:
                file = check_file_status(sample_file.name)
                st.write(f"File status: {file.state.name}")
                if file.state.name == "ACTIVE":
                    files_ready.append(file)

            if len(files_ready) == len(uploaded_files):
                prompt = (
                    "Analyze the images to determine if they represent a jewelry item. "
                    "If not, respond with 'Sorry, this is not a jewelry item.' "
                    "If it is a jewelry item, provide the details in this structured format, and omit points if not visible:\n\n"
                    "Jewelry Analysis\n"
                    "Metal Type: (e.g., Yellow Gold)\n"
                    "Metal Finish: (e.g., Matte, Glossy, Textured)\n"
                    "Type of Jewelry: (e.g., Necklace, Earrings, Bracelet, Bangles, etc)\n"
                    "Center Stone: (e.g., Diamond, Emerald, etc.)\n"
                    "Side Stone: (e.g., Ruby, Sapphire, etc.)\n"
                    "Karat: (if visible)\n"
                    "Weight: (if visible)\n"
                    "Hallmark: (if visible)\n"
                    "Design Style: (e.g., Floral and Circular)\n"
                    "Setting: (e.g., Bezel setting)\n"
                    "Pattern: (e.g., Floral motifs)\n"
                    "Color: (e.g., Yellow Gold)\n"
                    "Length: (for necklaces)\n"
                    "Clasp: (for necklaces)\n"
                    "Strands: (for necklaces, if visible)\n"
                    "Back Type: (for earrings, e.g., Push Back, Screw Back)\n"
                    "Meta Title: Generate an SEO-friendly title for the jewelry item.\n"
                    "Meta Keywords: Generate relevant keywords for the jewelry item.\n"
                )

                if st.button("Analyze Images"):
                    combined_response = ""
                    for file in files_ready:
                        combined_response += analyze_content([file], prompt) + "\n"

                    formatted_details = format_response(combined_response)

                    tabs = st.tabs(["English", "Japanese"])

                    # English Tab
                    with tabs[0]:
                        st.write("#### English Results")
                        for key, value in formatted_details.items():
                            st.write(f"{key}: {value}")

                    # Japanese Tab
                    with tabs[1]:
                        st.write("#### Japanese Translation")
                        translated_details = {key: translator.translate(value, src="en", dest="ja").text for key, value in formatted_details.items()}
                        for key, value in translated_details.items():
                            st.write(f"{key}: {value}")

