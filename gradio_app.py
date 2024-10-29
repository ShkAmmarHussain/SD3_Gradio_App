import gradio as gr
import requests
import base64
from io import BytesIO
from PIL import Image

# API URLs
BASE_URL = "http://127.0.0.1:8000"
TOKEN_URL = f"{BASE_URL}/token"
GENERATE_IMAGE_URL = f"{BASE_URL}/generate-image"

# Variable to store the token globally
token_storage = None

# Function to request JWT token
def get_token(username, password):
    try:
        response = requests.post(TOKEN_URL, params={"username": username, "password": password})
        response.raise_for_status()
        token = response.json().get("access_token")
        return token
    except requests.exceptions.RequestException as e:
        return f"Error getting token: {e}"

# Function to request image generation
def generate_image(prompt, negative_prompt, num_inference_steps, guidance_scale, width, height, num_images_per_prompt):
    global token_storage
    if token_storage is None:
        return "Please login first.", None
    try:
        headers = {"Authorization": f"Bearer {token_storage}"}
        payload = {
            "prompt": prompt,
            "negative_prompt": negative_prompt or "",
            "num_inference_steps": num_inference_steps,
            "guidance_scale": guidance_scale,
            "width": width,
            "height": height,
            "num_images_per_prompt": num_images_per_prompt
        }
        response = requests.post(GENERATE_IMAGE_URL, json=payload, headers=headers)
        # response.raise_for_status()
        images_base64 = response.json().get("images", [])
        # images = [f"data:image/png;base64,{img}" for img in images_base64]
        images = []
        for img_str in images_base64:
            img_data = base64.b64decode(img_str)
            img = Image.open(BytesIO(img_data))
            images.append(img)
        return images
    except requests.exceptions.RequestException as e:
        return f"Error generating image", None

# Gradio login interface
def login_interface(username, password):
    global token_storage
    token = get_token(username, password)
    if "Error" in token:
        return token
    token_storage = token
    return "Login successful! Token obtained."

# Gradio app
with gr.Blocks() as demo:
    with gr.Tab("Login"):
        gr.Markdown("## Login to get access token")
        username = gr.Textbox(label="Username")
        password = gr.Textbox(label="Password", type="password")
        login_button = gr.Button("Login")
        login_output = gr.Textbox(label="Output")
        
        login_button.click(login_interface, inputs=[username, password], outputs=login_output)
    
    with gr.Tab("Generate Image"):
        gr.Markdown("## Enter image generation details")
        prompt = gr.Textbox(label="Prompt", placeholder="Describe the image you want")
        negative_prompt = gr.Textbox(label="Negative Prompt", placeholder="Things to avoid in the image")
        num_inference_steps = gr.Slider(minimum=10, maximum=100, step=1, value=20, label="Inference Steps")
        guidance_scale = gr.Slider(minimum=0.1, maximum=30, step=0.1, value=7.0, label="Guidance Scale")
        width = gr.Slider(minimum=256, maximum=1024, step=64, value=1024, label="Width")
        height = gr.Slider(minimum=256, maximum=1024, step=64, value=1024, label="Height")
        num_images_per_prompt = gr.Slider(minimum=1, maximum=5, step=1, value=1, label="Number of Images")

        generate_button = gr.Button("Generate Image")
        image_output = gr.Gallery(label="Generated Images")
        
        generate_button.click(
            generate_image,
            inputs=[prompt, negative_prompt, num_inference_steps, guidance_scale, width, height, num_images_per_prompt],
            outputs=image_output
        )

demo.launch()
