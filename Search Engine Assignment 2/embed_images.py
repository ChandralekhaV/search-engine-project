import os
import json
import torch
import clip
import requests
from PIL import Image
from io import BytesIO
from tqdm import tqdm

# Load CLIP model
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)

# Load image metadata
with open("image_surrogates.json", "r", encoding="utf-8") as f:
    images = json.load(f)

image_embeddings = []

print(f" Processing {len(images)} images with CLIP...")

for img in tqdm(images):
    try:
        url = img["image_url"]
        response = requests.get(url, timeout=10)
        image = Image.open(BytesIO(response.content)).convert("RGB")
        image_input = preprocess(image).unsqueeze(0).to(device)

        with torch.no_grad():
            image_features = model.encode_image(image_input)
            image_features /= image_features.norm(dim=-1, keepdim=True)  # normalize

        # Save vector and metadata
        image_embeddings.append({
            "image_url": url,
            "title": img.get("title", ""),
            "alt_text": img.get("alt_text", ""),
            "source_page": img.get("source_page", ""),
            "animal_name": img.get("animal_name", ""),
            "embedding": image_features[0].cpu().tolist()
        })

    except Exception as e:
        print(f" Skipped image {img['image_url']} due to error: {e}")

# Save all embeddings
with open("image_embeddings.json", "w", encoding="utf-8") as f:
    json.dump(image_embeddings, f, indent=2)

print(f"\n Saved {len(image_embeddings)} image embeddings to image_embeddings.json")
