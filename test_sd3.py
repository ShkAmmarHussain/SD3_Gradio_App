from diffusers import StableDiffusion3Pipeline
import torch
from huggingface_hub import login

login(token='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')


pipe = StableDiffusion3Pipeline.from_single_file(
"sd3_medium_incl_clips_t5xxlfp8.safetensors",
torch_dtype=torch.float32,
text_encoder_3=None
)

image = pipe(
    "A cat holding a sign that says hello world",
    negative_prompt="",
    num_inference_steps=20,
    guidance_scale=7.0,
).images[0]

# Optionally, to display the image directly in your code
image.show()