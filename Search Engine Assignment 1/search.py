import json
import math

# Loading necessary data
with open("inverted_index.json", "r", encoding="utf-8") as f:
    inverted_index = json.load(f)

with open("tf_index.json", "r", encoding="utf-8") as f:
    tf_index = json.load(f)

with open("bm25_data.json", "r", encoding="utf-8") as f:
    bm25_data = json.load(f)

with open("lm_data.json", "r", encoding="utf-8") as f:
    lm_data = json.load(f)

# Extracting document length data
doc_lengths = bm25_data["doc_lengths"]
avg_doc_length = bm25_data["avg_doc_length"]

# Extracting Language Model data
corpus_term_freq = lm_data["corpus_term_freq"]
prob_w_given_corpus = lm_data["prob_w_given_corpus"]

# VSM and BM25 parameters
k1 = 2.9  # BM25 Term frequency scaling
b = 0.3  # BM25 Length normalization
lambda_smooth = 0.7  # LM smoothing factor
#mu = 2000  # Dirichlet smoothing parameter


# Total number of documents
N = len(doc_lengths)

# Computing IDF for both models
def compute_idf(term):
    df = len(inverted_index.get(term, []))
    return math.log((N - df + 0.5) / (df + 0.5) + 1)

# Computing TF-IDF vector for a document (VSM)
def compute_document_vector(doc_id):
    vector = {}
    for term in tf_index:
        if doc_id in tf_index[term]:
            tf = tf_index[term][doc_id]
            idf = compute_idf(term)
            vector[term] = tf * idf  # TF-IDF weight
    return vector

# Compute Cosine Similarity for VSM
def cosine_similarity(query_vector, doc_vector):
    dot_product = sum(query_vector.get(term, 0) * doc_vector.get(term, 0) for term in query_vector)
    query_norm = math.sqrt(sum(weight ** 2 for weight in query_vector.values()))
    doc_norm = math.sqrt(sum(weight ** 2 for weight in doc_vector.values()))
    
    if query_norm == 0 or doc_norm == 0:
        return 0  # Prevent division by zero
    
    return dot_product / (query_norm * doc_norm)

# Compute BM25 score for a document
def bm25_score(query_terms, doc_id):
    score = 0
    doc_length = doc_lengths.get(doc_id, 0)

    for term in query_terms:
        if doc_id in tf_index.get(term, {}):
            tf = tf_index[term][doc_id]
            idf = compute_idf(term)
            numerator = tf * (k1 + 1)
            denominator = tf + k1 * (1 - b + b * (doc_length / avg_doc_length))
            score += idf * (numerator / denominator)
    
    return score

# Compute LM score for a document
def lm_score(query_terms, doc_id):
    score = 0
    doc_length = doc_lengths.get(doc_id, 0)

    for term in query_terms:
        # P(w|D): Probability of term in document
        p_w_given_d = tf_index.get(term, {}).get(doc_id, 0) / doc_length if doc_length else 0
        
        # P(w|C): Probability of term in entire corpus
        p_w_given_c = prob_w_given_corpus.get(term, 1e-6)  # Avoid zero probability

        # Compute LM score using Jelinek-Mercer Smoothing
        score += math.log(lambda_smooth * p_w_given_d + (1 - lambda_smooth) * p_w_given_c)

    return score 


# Search functions
def search_vsm(query):
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

def search_bm25(query):
    query_terms = query.lower().split()
    scores = {doc_id: bm25_score(query_terms, doc_id) for doc_id in doc_lengths}
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)

def search_lm(query):
    query_terms = query.lower().split()
    scores = {doc_id: lm_score(query_terms, doc_id) for doc_id in doc_lengths}
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)

# Main loop with all ranking models
while True:
    print("\n Choose a Ranking Model:")
    print("1. Vector Space Model (VSM - Cosine Similarity)")
    print("2. BM25")
    print("3. Language Model (Jelinek-Mercer)")
    print("4. Exit")

    choice = input("Enter your choice (1, 2, 3, or 4): ").strip()

    if choice not in ["1", "2", "3", "4"]:
        print(" Invalid choice. Please enter 1, 2, 3, or 4.\n")
        continue

    if choice == "4":
        print("\n Exiting program. Goodbye!\n")
        break

    query = input("\n Enter search query: ")

    if choice == "1":
        search_results = search_vsm(query)
        print("\n Ranked Documents (VSM Cosine Similarity Scores):")
    elif choice == "2":
        search_results = search_bm25(query)
        print("\n Ranked Documents (BM25 Scores):")
    elif choice == "3":
        search_results = search_lm(query)
        print("\n Ranked Documents (Language Model Scores):")

    for doc_id, score in search_results[:10]:  # Show top 10 results
        print(f" Document {doc_id} - Score: {score:.4f}")

    # Ask if user wants to continue
    print("\n Would you like to search again?")
    print("1. Try another ranking model")
    print("2. Exit")

    next_action = input("Enter your choice (1 or 2): ").strip()

    if next_action not in ["1", "2"]:
        print(" Invalid choice. Please enter 1 or 2.\n")
        continue
    
    if next_action != "1":
        print("\n Exiting program. Goodbye!\n")
        break
