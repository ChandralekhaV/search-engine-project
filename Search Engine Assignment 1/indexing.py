import xml.etree.ElementTree as ET
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import os
from collections import defaultdict
import json
import math

###Inverted Indexing

# Downloading stopwords (only need to run once)
#nltk.download('punkt')
#nltk.download('stopwords')

# Loading Stopwords
stop_words = set(stopwords.words('english'))
dataset_path = r"C:\Users\Chand\OneDrive\Desktop\Mechanics of Search\Search Engine Assignment 1\cranfield-trec-dataset-main\cranfield-trec-dataset-main\cran.all.1400.xml" # Update this if needed

# Checking if file exists
if not os.path.exists(dataset_path):
    print("Error: XML file not found. Check the path.")
    exit()

# Reading the file and wrapping it inside a root element
with open(dataset_path, "r", encoding="utf-8") as file:
    xml_content = file.read()

# Manually adding a root element
fixed_xml = f"<root>\n{xml_content}\n</root>"

# Parsing the modified XML string
try:
    root = ET.fromstring(fixed_xml)
    print("XML Parsed Successfully!")
except ET.ParseError as e:
    print("XML Parsing Error:", e)
    exit()

# Initializing dictionary for storing documents
stemmer = PorterStemmer()
documents = {}

# Extracting document ID and text
for doc in root.findall("doc"):  # Now <doc> elements are inside <root>
    doc_id = doc.find("docno").text.strip() if doc.find("docno") is not None else "Unknown"
    title_element = doc.find("title")
    abstract_element = doc.find("text")
    title = title_element.text.strip() if title_element is not None and title_element.text else ""
    abstract = abstract_element.text.strip() if abstract_element is not None and abstract_element.text else ""
    content = f"{title} {abstract}"
    tokens = word_tokenize(content.lower())
    tokens = [stemmer.stem(word) for word in tokens if word.isalnum() and word not in stop_words]  # Apply stemming
    documents[doc_id] = tokens

# Building Inverted Index
inverted_index = defaultdict(set)
for doc_id, words in documents.items():
    for word in words:
        inverted_index[word].add(doc_id)

print("Sample indexed words:", list(inverted_index.items())[:5])

# Saving inverted index as a JSON file
with open("inverted_index.json", "w", encoding="utf-8") as f:
    json.dump({k: list(v) for k, v in inverted_index.items()}, f, indent=4)

print("Inverted index saved successfully as 'inverted_index.json'")

###VSM

# Computing TF values for each term in each document
tf_index = {}

for term, doc_list in inverted_index.items():
    tf_index[term] = {}
    for doc_id in doc_list:
        tf_index[term][doc_id] = documents[doc_id].count(term) / len(documents[doc_id])

# Saving TF values to a JSON file
with open("tf_index.json", "w", encoding="utf-8") as f:
    json.dump(tf_index, f, indent=4)

print("Term Frequency (TF) values saved as 'tf_index.json'")

###BM25

# Computing document lengths
doc_lengths = {doc_id: len(doc) for doc_id, doc in documents.items()}
avg_doc_length = sum(doc_lengths.values()) / len(doc_lengths)  # Average document length

# Saving document lengths and average length for BM25
bm25_data = {
    "doc_lengths": doc_lengths,
    "avg_doc_length": avg_doc_length
}

with open("bm25_data.json", "w", encoding="utf-8") as f:
    json.dump(bm25_data, f, indent=4)

print("BM25 Data (Document Lengths & Avg Length) saved as 'bm25_data.json'")

###Language Model [Jelinek-Mercer Smoothing]

# Computing term frequency in the whole corpus
corpus_term_freq = {}
total_terms_in_corpus = 0

for term, doc_list in inverted_index.items():
    corpus_term_freq[term] = sum(len(tf_index[term]) for doc in doc_list)
    total_terms_in_corpus += corpus_term_freq[term]

# Computing probability of a term occurring in the entire corpus
prob_w_given_corpus = {term: freq / total_terms_in_corpus for term, freq in corpus_term_freq.items()}

# Saving corpus term probabilities
lm_data = {
    "corpus_term_freq": corpus_term_freq,
    "prob_w_given_corpus": prob_w_given_corpus
}

with open("lm_data.json", "w", encoding="utf-8") as f:
    json.dump(lm_data, f, indent=4)

print("Language Model Data (Corpus Probabilities) saved as 'lm_data.json'")
