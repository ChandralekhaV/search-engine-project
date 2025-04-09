import json
from collections import Counter
from urllib.parse import urlparse

#with open("image_surrogates.json", "r", encoding="utf-8") as f:
 #   images = json.load(f)

with open("image_embeddings.json", "r", encoding="utf-8") as f:
    images = json.load(f)

# Count by category (roughly from source_page)
sources = [img["source_page"].split("/wiki/")[-1] for img in images if "source_page" in img]
top_sources = Counter(sources).most_common(10)

print(f" Total images: {len(images)}")
print("\n Top source pages:")
for title, count in top_sources:
    print(f"- {title}: {count} images")

# Optionally group by first part of title
categories = Counter()
for s in sources:
    if "Asia" in s:
        categories["Asia"] += 1
    elif "Africa" in s:
        categories["Africa"] += 1
    elif "Bird" in s or "bird" in s:
        categories["Birds"] += 1
    elif "Reptile" in s:
        categories["Reptiles"] += 1
    else:
        categories["Other"] += 1

print("\n Approximate breakdown by topic:")
for k, v in categories.items():
    print(f"{k}: {v} images")
