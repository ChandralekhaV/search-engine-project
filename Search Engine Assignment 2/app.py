from flask import Flask, render_template, request
import json
import math
import torch
import clip
import numpy as np
from PIL import Image
from collections import defaultdict
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import re

nltk.download('punkt')
nltk.download('stopwords')

app = Flask(__name__)

# Load CLIP model
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)

# Load data
with open("image_surrogates.json", "r", encoding="utf-8") as f:
    documents = json.load(f)

with open("index/inverted_index.json", "r", encoding="utf-8") as f:
    inverted_index = json.load(f)

with open("index/tf_index.json", "r", encoding="utf-8") as f:
    tf_index = json.load(f)

with open("index/bm25_data.json", "r", encoding="utf-8") as f:
    bm25_data = json.load(f)

with open("image_embeddings.json", "r", encoding="utf-8") as f:
    image_embeddings = json.load(f)

# Map image_url to embedding
embedding_dict = {img["image_url"]: np.array(img["embedding"]) for img in image_embeddings}

stop_words = set(stopwords.words('english'))

doc_lengths = bm25_data["doc_lengths"]
avg_doc_length = bm25_data["avg_doc_length"]
N = len(documents)
k1 = 2.9
b = 0.3

def preprocess(text):
    tokens = word_tokenize(text.lower())
    return [t for t in tokens if t.isalnum() and t not in stop_words]

def compute_idf(term):
    df = len(inverted_index.get(term, []))
    return math.log(1 + (N / (df + 1))) if df > 0 else 0.1

def clean_display_title(text):
    blacklist = {
        "a", "an", "the", "close", "view", "photo", "image", "standing", "in", "on", "by",
        "bush", "area", "kruger", "park", "wildlife", "zoo", "africa"
    }
    words = text.lower().strip().split()
    filtered = [word for word in words if word not in blacklist]
    if not filtered:
        return text.title()
    final_words = filtered[:3]
    return " ".join(w.capitalize() for w in final_words)

def cosine_similarity(a, b):
    a = a / np.linalg.norm(a)
    b = b / np.linalg.norm(b)
    return np.dot(a, b)

def bm25_search(query, top_k=20):
    query_terms = preprocess(query)
    scores = defaultdict(float)

    for term in query_terms:
        if term not in inverted_index:
            continue
        idf_score = compute_idf(term)
        for doc_id in inverted_index[term]:
            tf = tf_index.get(doc_id, {}).get(term, 0)
            doc_len = doc_lengths.get(doc_id, 0)
            numerator = tf * (k1 + 1)
            denominator = tf + k1 * (1 - b + b * doc_len / avg_doc_length)
            scores[doc_id] += idf_score * (numerator / (denominator + 1e-6))

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:5]

    # Group and pick best image per source page
    grouped = defaultdict(list)
    for doc_id, score in ranked:
        doc = documents[int(doc_id)]
        key = (doc["title"], doc["source_page"])
        doc["score"] = round(score, 4)
        grouped[key].append(doc)

    results = []
    for group in grouped.values():
        def image_score(d):
            alt = d.get("alt_text", "").lower()
            filename = d.get("image_url", "").split("/")[-1].lower()
            score = 0
            if any(x in alt for x in ["animal", "photo", "rabbit", "turtle", "mouse", "hyena", "elephant", "lion"]):
                score += 2
            score += len(alt) * 0.5
            if any(x in filename for x in ["animal", "jpg", "jpeg", "leopard", "frog", "owl", "elephant"]):
                score += 1
            return score

        best = max(group, key=image_score)

        # Fallback logic for display title
        alt = best.get("alt_text", "").strip()
        animal_name = best.get("animal_name", "").strip()
        title = best.get("title", "").strip()
        query_lower = query.lower()

        if query_lower in alt.lower() and len(alt.split()) >= 2:
            best["display_title"] = alt
        elif query_lower in animal_name.lower():
            best["display_title"] = query.capitalize()
        else:
            best["display_title"] = clean_display_title(animal_name or title)

        best["alt_text"] = alt if alt else animal_name
        results.append(best)

    # --- CLIP reranking ---
    # Encode query using CLIP
    text_input = clip.tokenize([query]).to(device)
    with torch.no_grad():
        text_features = model.encode_text(text_input)[0].cpu().numpy()
        text_features /= np.linalg.norm(text_features)

    for res in results:
        url = res["image_url"]
        if url in embedding_dict:
            image_feat = embedding_dict[url]
            similarity = cosine_similarity(text_features, image_feat)
            res["clip_score"] = float(similarity)
        else:
            res["clip_score"] = 0.0

       # Combine BM25 and CLIP score (weighted) + boost exact animal name match
    for res in results:
        bm25_score = res.get("score", 0.0)
        clip_score = res.get("clip_score", 0.0)
        base_score = 0.5 * bm25_score + 10.0 * clip_score

        animal_name = res.get("animal_name", "").lower()
        if query.lower() in animal_name:
            base_score += 3.0  # ✅ Boost if query matches animal name

        res["final_score"] = base_score

    # Safe sorting using final_score
    results = sorted(results, key=lambda x: x.get("final_score", 0), reverse=True)
    return results[:top_k]


@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    query = ""
    if request.method == "POST":
        query = request.form.get("query")
        results = bm25_search(query)
    return render_template("index.html", results=results, query=query)

if __name__ == "__main__":
    app.run(debug=True)
