import json

# Load existing ground truth
with open("ground_truth.json", "r", encoding="utf-8") as f:
    full_gt = json.load(f)

# Define keywords to look for in any key (lowercase match)
keywords = ["hare", "capra", "frog", "deer", "civet", "rabbit", "wolf", "savanna", "mongoose", "sheep", "leopard"]

# Collect keys that contain those keywords
filtered_gt = {
    key: val for key, val in full_gt.items()
    if any(k in key.lower() for k in keywords)
}

# Save it
with open("ground_truth_filtered.json", "w", encoding="utf-8") as f:
    json.dump(filtered_gt, f, indent=2)

print(f"Saved filtered ground truth for {len(filtered_gt)} queries.")
