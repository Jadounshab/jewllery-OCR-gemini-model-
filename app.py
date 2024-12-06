import streamlit as st
import google.generativeai as genai
from PIL import Image
import time
import re

# Set up the API Key
st.title("Jewelry Details Using Image")
api_key = "AIzaSyApVuZcpL0CMmuiRhogQ4fKjHtMlYz18V4"  # Replace with your actual API key

if api_key:
    genai.configure(api_key=api_key)

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
        # Define a regex pattern to capture key-value pairs
        pattern = re.compile(r"(Metal Type|Type of Jewelry|Karat|Weight|Hallmark|Design Style|Setting|Pattern|Color|Gemstone|Type of Gemstone|Shape|Cut|Clarity|Carat):\s*(.*?)(?=\b(?:Metal Type|Type of Jewelry|Karat|Weight|Hallmark|Design Style|Setting|Pattern|Color|Gemstone|Type of Gemstone|Shape|Cut|Clarity|Carat|$))", re.DOTALL)
        
        # Use regex to find all key-value matches and format them line by line
        formatted_lines = []
        for match in pattern.finditer(response):
            key = match.group(1)
            value = match.group(2).strip()
            # Only include values that are not "Not visible" or "Not applicable"
            if value.lower() not in ["not visible", "not applicable", "not specified"]:
                formatted_lines.append(f"{key}: {value}")

        return formatted_lines

    st.write("## Upload an Image to Get Details")

    # Uploading primary file for analysis
    uploaded_file = st.file_uploader("Choose an image (e.g., jewelry)", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, caption="Uploaded Image", use_column_width=True)

        # Upload to Gemini API
        st.write("Uploading the image to Gemini API...")
        sample_file = upload_image(uploaded_file, display_name="Uploaded Image")
        st.write(f"Uploaded file URI: {sample_file.uri}")

        # Wait for the file to be ready
        file = check_file_status(sample_file.name)
        st.write(f"File status: {file.state.name}")

        if file.state.name == "ACTIVE":
            # Prompt to analyze the uploaded image
            prompt = (
                "Analyze the image to determine if it is a jewelry item. "
                "If not, respond with 'Sorry, this is not a jewelry image.' "
                "If it is a jewelry image, provide the details in this structured format, and omit points if not visible:\n\n"
                "Jewelry Analysis\n"
                "Metal Type: (e.g., Yellow Gold)\n"
                "Type of Jewelry: (e.g., Necklace, Earrings, Bracelet, Bangles, etc)\n"
                "Karat: (if visible)\n"
                "Weight: (if visible)\n"
                "Hallmark: (if visible)\n"
                "Design Style: (e.g., Floral and Circular)\n"
                "Setting: (e.g., Bezel setting)\n"
                "Pattern: (e.g., Floral motifs)\n"
                "Color: (e.g., Yellow Gold)\n\n"
                "If the jewelry includes a gemstone, provide details as follows. If no gemstone, state 'No gemstone in this jewelry':\n"
                "Gemstone: (e.g., Pearl)\n"
                "Type of Gemstone: (e.g., Cultured Pearl)\n"
                "Shape: (e.g., Round)\n"
                "Cut: (if applicable)\n"
                "Clarity: (if applicable)\n"
                "Color: (e.g., White)\n"
                "Carat: (if visible)"
            )

            if st.button("Analyze Image"):
                response = analyze_content([sample_file], prompt)
                formatted_lines = format_response(response)
                
                st.write("### Analysis Result")
                for line in formatted_lines:
                    st.write(line)  # Output each line individually
