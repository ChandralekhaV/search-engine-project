import json
import math

# Load the inverted index and TF values
with open("inverted_index.json", "r", encoding="utf-8") as f:
    inverted_index = json.load(f)

with open("tf_index.json", "r", encoding="utf-8") as f:
    tf_index = json.load(f)

# Total number of documents
N = len(tf_index)

# Compute IDF for a term
def compute_idf(term):
    df = len(inverted_index.get(term, []))  # Number of docs containing term
    return math.log((N + 1) / (df + 1))  # Smoothing to prevent division by zero

# Compute TF-IDF vector for a document
def compute_document_vector(doc_id):
    vector = {}
    for term in tf_index:
        if doc_id in tf_index[term]:
            tf = tf_index[term][doc_id]
            idf = compute_idf(term)
            vector[term] = tf * idf  # TF-IDF weight
    return vector

# Compute Cosine Similarity
def cosine_similarity(query_vector, doc_vector):
    dot_product = sum(query_vector.get(term, 0) * doc_vector.get(term, 0) for term in query_vector)
    query_norm = math.sqrt(sum(weight ** 2 for weight in query_vector.values()))
    doc_norm = math.sqrt(sum(weight ** 2 for weight in doc_vector.values()))
    
    if query_norm == 0 or doc_norm == 0:
        return 0  # Prevent division by zero
    
    return dot_product / (query_norm * doc_norm)

# Search function using VSM (Cosine Similarity)
def search(query):
    query_terms = query.lower().split()
    
    # Compute TF-IDF vector for query
    query_vector = {}
    for term in query_terms:
        idf = compute_idf(term)
        query_vector[term] = idf  # Assuming binary TF (1 if term appears in query)
    
    # Compute similarity with each document
    scores = {}
    for doc_id in tf_index[next(iter(tf_index))]:  # Iterate over documents
        doc_vector = compute_document_vector(doc_id)
        scores[doc_id] = cosine_similarity(query_vector, doc_vector)
    
    # Rank documents by similarity
    ranked_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    return ranked_results if ranked_results else "No matching documents found."

# Take user input and search using VSM
query = input(" Enter search query: ")
search_results = search(query)

print("\n Ranked Documents (VSM Cosine Similarity Scores):")
for doc_id, score in search_results[:10]:  # Show top 10 results
    print(f"Document {doc_id} - Score: {score:.4f}")
