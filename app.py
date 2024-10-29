from fastapi import FastAPI, Depends, HTTPException, Header
from pydantic import BaseModel
from typing import Optional
import torch
from diffusers import StableDiffusion3Pipeline
from huggingface_hub import login
from jose import JWTError, jwt
from datetime import datetime, timedelta
from PIL import Image
import io
import base64
from dotenv import load_dotenv
import os

load_dotenv()

# JWT settings
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
HF_TOKEN = os.getenv("HF_TOKEN")
print(HF_TOKEN)

app = FastAPI()

# Authentication dependencies
class TokenData(BaseModel):
    username: str

def authenticate_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return TokenData(username=username)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user(authorization: str = Header(None)):
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = authorization.split(" ")[1]
    return authenticate_token(token)

# Endpoint to generate JWT token
@app.post("/token")
def generate_token(username: str, password: str):
    if username == "admin" and password == "admin":
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        token = jwt.encode({"sub": username, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)
        return {"access_token": token, "token_type": "bearer"}
    else:
        raise HTTPException(status_code=401, detail="Incorrect username or password")

# Request model
class ImageRequest(BaseModel):
    prompt: str
    negative_prompt: Optional[str] = ""
    num_inference_steps: Optional[int] = 20
    guidance_scale: Optional[float] = 7.0
    width: Optional[int] = 1024
    height: Optional[int] = 1024
    num_images_per_prompt: Optional[int] = 1

# Hugging Face login
try:
    login(token=HF_TOKEN)
except Exception as e:
    raise HTTPException(status_code=500, detail=f"Failed to login to Hugging Face: {str(e)}")

# Load the pipeline
try:
    pipe = StableDiffusion3Pipeline.from_single_file(
        "sd3_medium_incl_clips_t5xxlfp8.safetensors",
        torch_dtype=torch.float32,
        text_encoder_3=None
    )
except Exception as e:
    raise HTTPException(status_code=500, detail=f"Failed to load model pipeline: {str(e)}")

# Generate image function
def generate_image(params: ImageRequest):
    try:
        images = pipe(
            prompt=params.prompt,
            negative_prompt=params.negative_prompt,
            num_inference_steps=params.num_inference_steps,
            guidance_scale=params.guidance_scale,
            height=params.height,
            width=params.width,
            num_images_per_prompt=params.num_images_per_prompt
        ).images
        # Add debug print
        # print(f"Generated Images: {images}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")

    if not images:
        raise HTTPException(status_code=500, detail="No images were generated")

    # Convert the images to base64
    base64_images = []
    for image in images:
        try:
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
            base64_images.append(img_str)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to convert image to base64: {str(e)}")

    return base64_images

# FastAPI endpoint with Bearer authentication
@app.post("/generate-image")
def generate_image_endpoint(params: ImageRequest, token_data: TokenData = Depends(get_current_user)):
    try:
        images_base64 = generate_image(params)
        return {"images": images_base64}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
