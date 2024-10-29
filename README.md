# Stable Diffusion 3 Image Generation with FastAPI & Gradio

This project is a FastAPI-based application for generating images using Stable Diffusion 3, secured with JWT authentication. It provides a REST API to request JWT tokens, authenticate users, and handle image generation. A Gradio interface allows users to log in and generate images with custom settings through an interactive web app.

Also Download the SD3-Medium Model from huggingface, I'm using "sd3_medium_incl_clips_t5xxlfp8.safetensors".

## Features

- **JWT Authentication**: Secure user access with a token-based system.
- **Stable Diffusion 3 Integration**: Generate images with custom prompts, inference steps, and other parameters.
- **Gradio Interface**: User-friendly interface for setting generation parameters and viewing results.
- **Base64 Image Encoding**: Generated images are returned in base64 format for easy handling and display.

## Project Structure

- **app.py**: FastAPI application with endpoints for authentication and image generation.
- **gradio_app.py**: Gradio interface that interacts with the FastAPI backend.

## Setup

### Prerequisites

- **Python 3.11.8+**
- **Install Dependencies**: Run `pip install -r requirements.txt`
  - Install FastAPI, Gradio, Hugging Face libraries, and necessary dependencies.

### Authentication Setup

1. Set the `SECRET_KEY` and `HF_TOKEN` in `app.py`:
   - `SECRET_KEY`: A secure key for signing JWT tokens.
   - `HF_TOKEN`: Hugging Face API token for accessing Stable Diffusion 3.

2. The default credentials for login are set to `"admin"` for both username and password in `app.py`. You can modify them as needed.

### Running the Application

1. **Start the FastAPI server**:
   ```bash
   uvicorn app:app --reload
   ```
   FastAPI will run on `http://127.0.0.1:8000`.

2. **Launch Gradio Interface**:
   ```bash
   python gradio_app.py
   ```
   Gradio will start and open a browser window with the interface.

## API Endpoints

1. **Token Generation** - `POST /token`
   - Request body: `username`, `password`
   - Response: Access token for API usage.

2. **Image Generation** - `POST /generate-image`
   - Headers: `Authorization: Bearer <token>`
   - Request body: JSON object with image generation parameters:
     - `prompt` (str): Description of the image.
     - `negative_prompt` (str, optional): Description of elements to avoid.
     - `num_inference_steps` (int): Steps for generation.
     - `guidance_scale` (float): Guidance level for output style.
     - `width` (int), `height` (int): Dimensions of the output image.
     - `num_images_per_prompt` (int): Number of images to generate.

## Usage with Gradio

1. **Login Tab**:
   - Enter username and password to generate a JWT token for secure access.
   
2. **Generate Image Tab**:
   - Configure the prompt, inference steps, guidance scale, dimensions, and number of images.
   - Click "Generate Image" to view generated images in the gallery.

## Contributing

Feel free to open issues, suggest improvements, or submit pull requests.