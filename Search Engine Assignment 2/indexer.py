import json
import os
import re
import nltk
from collections import defaultdict
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

nltk.download('punkt')
nltk.download('stopwords')

# Load data
with open("image_surrogates.json", "r", encoding="utf-8") as f:
    data = json.load(f)

stop_words = set(stopwords.words("english"))
inverted_index = defaultdict(set)
tf_index = defaultdict(lambda: defaultdict(int))

def preprocess(text):
    tokens = word_tokenize(text.lower())
    return [t for t in tokens if t.isalnum() and t not in stop_words]

def clean_animal_name(animal_name):
    animal_name = animal_name.lower()
    animal_name = re.sub(r'[^a-z0-9\s]', ' ', animal_name)  # remove non-alphanum
    animal_name = re.sub(r'\b\d{2,4}px\b', '', animal_name)  # remove size prefixes like 220px
    animal_name = re.sub(r'\s+', ' ', animal_name)  # collapse whitespace
    return animal_name.strip()

# Build index
for idx, item in enumerate(data):
    doc_id = str(idx)

    title = item.get("title", "")
    alt = item.get("alt_text", "")
    filename = item.get("image_url", "").split("/")[-1].replace("_", " ").lower()
    animal_name = clean_animal_name(item.get("animal_name", ""))

    full_text = f"{title} {alt} {filename} {animal_name}"
    terms = preprocess(full_text)

    for term in terms:
        inverted_index[term].add(doc_id)
        tf_index[doc_id][term] += 1

# Convert sets to lists
inverted_index = {term: list(postings) for term, postings in inverted_index.items()}

# Save to 'index' folder
os.makedirs("index", exist_ok=True)

with open("index/inverted_index.json", "w", encoding="utf-8") as f:
    json.dump(inverted_index, f, indent=2)

with open("index/tf_index.json", "w", encoding="utf-8") as f:
    json.dump(tf_index, f, indent=2)

# BM25 doc lengths
doc_lengths = {doc_id: sum(freqs.values()) for doc_id, freqs in tf_index.items()}
avg_doc_length = sum(doc_lengths.values()) / len(doc_lengths)

bm25_data = {
    "doc_lengths": doc_lengths,
    "avg_doc_length": avg_doc_length
}

with open("index/bm25_data.json", "w", encoding="utf-8") as f:
    json.dump(bm25_data, f, indent=2)

print(f" Indexed {len(data)} images.")
print(f" Saved index files in 'index/' folder.")
