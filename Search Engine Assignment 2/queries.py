import json

# Load image surrogates
with open("image_surrogates.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Keywords to filter
keywords = ["hare", "capra", "frog", "deer", "civet", "rabbit", "wolf", "savanna", "mongoose", "sheep", "leopard"]

# Extract and clean unique animal names
queries = set()
for item in data:
    name = item.get("animal_name", "").strip().lower()
    if name:
        # Clean common file-related noise
        name = name.replace("jpg", "").replace("jpeg", "").replace("png", "").strip()

        # Include only if it matches one of the keywords
        if any(k in name for k in keywords):
            queries.add(name)

# Sort and save
sorted_queries = sorted(queries)

with open("queries.txt", "w", encoding="utf-8") as f:
    for q in sorted_queries:
        f.write(q + "\n")

print(f"Filtered and saved {len(sorted_queries)} keyword-based queries to 'queries.txt'")
