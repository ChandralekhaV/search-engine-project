import requests
from bs4 import BeautifulSoup
import json
import time
import os
from tqdm import tqdm
import shutil
import re

BASE_URL = "https://en.wikipedia.org"
API_URL = "https://en.wikipedia.org/w/api.php"

CATEGORIES = [
    "Mammals_of_Africa",
    "Mammals_of_Asia",
    "Birds_by_common_name",
    "Amphibians_of_South_America",
    "Mammals_of_Europe",
    "Mammals_of_North_America",
    "Reptiles_of_North_America",
    "Birds_of_South_America",
    "Mammals_of_South_America",
    "Birds_of_Australia"
    "Reptiles_of_Africa",
    "Birds_of_North_America"
]


visited_pages = set()
seen_urls = set()
image_data = []

def get_animal_links_from_category(category, limit=300):
    links = []
    params = {
        "action": "query",
        "list": "categorymembers",
        "cmtitle": f"Category:{category}",
        "cmlimit": "max",
        "format": "json"
    }

    print(f" Getting pages from Category: {category}")
    while len(links) < limit:
        response = requests.get(API_URL, params=params)
        data = response.json()

        for page in data["query"]["categorymembers"]:
            title = page["title"]
            if not title.startswith("Category:") and not title.startswith("File:"):
                links.append(BASE_URL + "/wiki/" + title.replace(" ", "_"))

        if "continue" in data:
            params["cmcontinue"] = data["continue"]["cmcontinue"]
        else:
            break

    return links[:limit]

def clean_animal_name(raw_name):
    # Lowercase and replace underscores
    name = raw_name.lower().replace("_", " ")

    # Remove things like '220px', digits, brackets, symbols, and collapse whitespace
    name = re.sub(r'\b\d{2,4}px\b', '', name)
    name = re.sub(r'[^a-z\s]', ' ', name)
    name = re.sub(r'\s+', ' ', name)

    # Keep only the first 2-3 words (optional)
    name = ' '.join(name.strip().split()[:3])

    return name.title().strip()

def extract_images_from_page(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.find("h1").get_text()
        content = soup.find("div", class_="mw-parser-output")
        if not content:
            return

        images = content.find_all("img")
        for img in images:
            src = img.get("src")
            alt = img.get("alt", "")
            if not src or not src.startswith("//upload.wikimedia.org"):
                continue

            filename = src.split("/")[-1].lower()

            # Filter out non-animal visuals
            if any(x in filename for x in ["map", "range", "distribution", "location", "logo", "icon", "flag"]):
                continue
            if any(x in alt.lower() for x in ["map", "range", "distribution", "location"]):
                continue
            if not filename.endswith((".jpg", ".jpeg", ".png")):
                continue

            image_url = "https:" + src
            if image_url in seen_urls:
                continue
            seen_urls.add(image_url)

            # Use alt if available, otherwise fallback to filename (without extension)
            raw_name = alt.strip() if alt.strip() else filename.split(".")[0]
            animal_name = clean_animal_name(raw_name)

            image_data.append({
                "title": title,
                "image_url": image_url,
                "alt_text": alt,
                "source_page": url,
                "animal_name": animal_name
            })

    except Exception as e:
        print(f"Error processing {url}: {e}")

# --- MAIN ---
for category in CATEGORIES:
    animal_links = get_animal_links_from_category(category, limit=300)
    print(f"Found {len(animal_links)} animal pages in {category}")

    for link in tqdm(animal_links, desc=f"Crawling {category}"):
        if len(image_data) >= 10000:
            break
        if link not in visited_pages:
            extract_images_from_page(link)
            visited_pages.add(link)
            time.sleep(0.5)

# Backup existing file
json_file = "image_surrogates.json"
if os.path.exists(json_file):
    shutil.copy(json_file, json_file + ".bak")

# Load existing data (if any)
existing = []
if os.path.exists(json_file):
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            existing = json.load(f)
    except Exception as e:
        print(f" Couldn't load existing file: {e}")
else:
    print(" No previous file found. Creating new dataset.")

# Merge + deduplicate based on image_url
combined = {img["image_url"]: img for img in existing + image_data}
all_data = list(combined.values())

with open(json_file, "w", encoding="utf-8") as f:
    json.dump(all_data, f, indent=2)

print(f"\n Saved total {len(all_data)} unique images to {json_file}")
