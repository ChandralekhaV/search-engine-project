import xml.etree.ElementTree as ET
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import os
from collections import defaultdict
import json
import math

# Download stopwords (only need to run once)
nltk.download('punkt')
nltk.download('stopwords')

# Load Stopwords
stop_words = set(stopwords.words('english'))

# Correct file path (Use raw string to avoid escape sequence issues)
dataset_path = r"C:\Users\Chand\OneDrive\Desktop\Mechanics of Search\Search Engine Assignment 1\cranfield-trec-dataset-main\cranfield-trec-dataset-main\cran.all.1400.xml" # Update this if needed

# Check if file exists
if not os.path.exists(dataset_path):
    print("Error: XML file not found. Check the path.")
    exit()

# Read the file and wrap it inside a root element
with open(dataset_path, "r", encoding="utf-8") as file:
    xml_content = file.read()

# Manually add a root element
fixed_xml = f"<root>\n{xml_content}\n</root>"

# Parse the modified XML string
try:
    root = ET.fromstring(fixed_xml)
    print("XML Parsed Successfully!")
except ET.ParseError as e:
    print("XML Parsing Error:", e)
    exit()

# Initialize dictionary for storing documents
documents = {}

# Extract document ID and text
for doc in root.findall("doc"):  # Now <doc> elements are inside <root>
    doc_id = doc.find("docno").text.strip() if doc.find("docno") is not None else "Unknown"

    # Handle missing or empty title and text elements
    title_element = doc.find("title")
    abstract_element = doc.find("text")

    # Ensure the element exists and has text
    title = title_element.text.strip() if title_element is not None and title_element.text else ""
    abstract = abstract_element.text.strip() if abstract_element is not None and abstract_element.text else ""

    # Combine title and abstract
    content = f"{title} {abstract}"

    # Clean text: Remove punctuation, lowercase, and tokenize
    tokens = word_tokenize(content.lower())
    tokens = [word for word in tokens if word.isalnum() and word not in stop_words]

    # Store cleaned document
    documents[doc_id] = tokens

# Build Inverted Index
inverted_index = defaultdict(set)
for doc_id, words in documents.items():
    for word in words:
        inverted_index[word].add(doc_id)

# Print a sample of indexed words
print("Sample indexed words:", list(inverted_index.items())[:5])




# Save inverted index as a JSON file
with open("inverted_index.json", "w", encoding="utf-8") as f:
    json.dump({k: list(v) for k, v in inverted_index.items()}, f, indent=4)

print("Inverted index saved successfully as 'inverted_index.json'")


# Load the index
#with open("inverted_index.json", "r", encoding="utf-8") as f:
 #   index_data = json.load(f)

# Print a sample
#print(list(index_data.items())[:5])



# Compute TF values for each term in each document
tf_index = {}

for term, doc_list in inverted_index.items():
    tf_index[term] = {}
    for doc_id in doc_list:
        tf_index[term][doc_id] = documents[doc_id].count(term) / len(documents[doc_id])

# Save TF values to a JSON file
with open("tf_index.json", "w", encoding="utf-8") as f:
    json.dump(tf_index, f, indent=4)

print("Term Frequency (TF) values saved as 'tf_index.json'")

