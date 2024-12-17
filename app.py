import streamlit as st
import requests
# import base64
from dotenv import load_dotenv
import os

load_dotenv()

# Stability AI API key
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")

# Inpainting endpoint (using stable-diffusion-inpainting)
API_URL = "https://api.stability.ai/v2beta/stable-image/edit/search-and-replace"

headers = {
    "Authorization": f"Bearer {STABILITY_API_KEY}",
    "Content-Type": "application/json"
}

st.title("Search and Replace")


st.write("**Instructions:** Upload an image and provide: ")
st.markdown("""
- A **prompt** describing what you want to appear in place of the identified object.
- A **search_prompt** describing the object currently in the image to be replaced.
""")

prompt = st.text_input("Enter your prompt (the desired object/scenario):", "golden retriever in a field")
search_prompt = st.text_input("Enter your search prompt (object to replace):", "dog")

# Optional parameters
output_format = st.selectbox("Output Format", ["png", "jpeg", "webp"], index=2)

uploaded_image = st.file_uploader("Upload an image (JPEG/PNG)", type=["png", "jpg", "jpeg"])

if st.button("Perform Search and Replace"):
    if not uploaded_image:
        st.error("Please upload an image.")
    else:
        headers = {
            "authorization": f"Bearer {STABILITY_API_KEY}",
            "accept": "image/*"
        }

        files = {
            "image": (uploaded_image.name, uploaded_image.read(), uploaded_image.type)
        }

        data = {
            "prompt": prompt,
            "search_prompt": search_prompt,
            "output_format": output_format
        }

        # Reset the file read pointer by re-opening if needed
        # since .read() might exhaust the buffer
        # However, we already read the file above, so we have it in memory.
        # If we need original image bytes for display:
        uploaded_image.seek(0)
        original_image_bytes = uploaded_image.read()

        with st.spinner("Processing..."):
            response = requests.post(API_URL, headers=headers, files={"image": (uploaded_image.name, original_image_bytes, uploaded_image.type)}, data=data)

        if response.status_code == 200:
            image_bytes = response.content

            # Create two columns
            col1, col2 = st.columns(2)
            
            with col1:
                st.image(original_image_bytes, caption="Original Image", use_column_width=True)
            with col2:
                st.image(image_bytes, caption="Transformed Image", use_column_width=True)
            
            # Download button for the transformed image
            st.download_button("Download Transformed Image", data=image_bytes, file_name=f"modified_image.{output_format}")
        else:
            try:
                error_msg = response.json()
            except:
                error_msg = response.text
            st.error(f"Error {response.status_code}: {error_msg}")