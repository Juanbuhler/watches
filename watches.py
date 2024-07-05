import os
import google.generativeai as genai
import streamlit as st
from PIL import Image
import requests
from io import BytesIO
from glob import glob
from dotenv import load_dotenv

load_dotenv()
# Demo images
demo_images = {f"Demo Image {i}": im for i, im in enumerate(glob("images/*.jpg"))}

genai.configure(api_key=os.environ.get("G_API_KEY"))


def upload_to_gemini(path, mime_type=None):
    file = genai.upload_file(path, mime_type=mime_type)
    print(f"Uploaded file '{file.display_name}' as: {file.uri}")
    return file


# Create the model
# See https://ai.google.dev/api/python/google/generativeai/GenerativeModel
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "application/json",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    # safety_settings = Adjust safety settings
    # See https://ai.google.dev/gemini-api/docs/safety-settings
)


# Function to load image from URL
def load_image(url):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    return img


# Title of the app
st.title("Gemini Watch Analysis")

# File uploader
uploaded_file = st.sidebar.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

image = None

# Display uploaded image if available
if uploaded_file is not None:
    Image.open(uploaded_file).save("watch.jpg")
    image = "watch.jpg"
else:
    st.sidebar.write("Or select a demo image below:")

    # Display demo images
    image_id = None
    for i, (name, img) in enumerate(demo_images.items()):
        st.sidebar.image(img)
        if st.sidebar.button(f"Select {name}", key=name):
            image_id = name
        st.sidebar.markdown("---")

    # Display image
    if image_id:
        image = demo_images[image_id]


if image:
    st.image(image)

    files = [
      upload_to_gemini(image, mime_type="image/jpeg"),
    ]

    chat_session = model.start_chat(
      history=[
        {
          "role": "user",
          "parts": [
            files[0],
          ],
        },
      ]
    )

    prompt = '''Describe the watch in the photo. Include brand and model plus materials and anything else visible'''

    response = chat_session.send_message(prompt)

    st.json(response.text)