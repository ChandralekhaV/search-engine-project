import xml.etree.ElementTree as ET
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

# Optimized Parameter Tuning
k1 = 2.9  
b = 0.3   
lambda_smooth = 0.7  
N = len(doc_lengths)  

# Computing IDF for VSM and BM25
def compute_idf(term):
    df = len(inverted_index.get(term, []))
    return math.log(1 + (N / (df + 1))) if df > 0 else 0.1  # Standard IDF with smoothing

# Computing sublinear TF
def compute_tf(term, doc_id):
    tf = tf_index.get(term, {}).get(doc_id, 0)
    return (1 + math.log(tf + 2)) if tf > 0 else 0  # Avoid log(0)

# Computing TF-IDF vector for a document (VSM)
def compute_document_vector(doc_id):
    vector = {}
    for term in tf_index:
        if doc_id in tf_index[term]:
            tf = compute_tf(term, doc_id)
            idf = compute_idf(term)
            vector[term] = tf * idf
    return vector

# Computing Cosine Similarity for VSM
def cosine_similarity(query_vector, doc_vector):
    dot_product = sum(query_vector.get(term, 0) * doc_vector.get(term, 0) for term in query_vector)
    query_norm = math.sqrt(sum(weight ** 2 for weight in query_vector.values())) + 1e-9
    doc_norm = math.sqrt(sum(weight ** 2 for weight in doc_vector.values())) + 1e-9
    return dot_product / (query_norm * doc_norm)

# Computing BM25 score
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

# Computing LM score
def lm_score(query_terms, doc_id):
    score = 0
    doc_length = doc_lengths.get(doc_id, 0)
    for term in query_terms:
        p_w_given_d = tf_index.get(term, {}).get(doc_id, 0) / doc_length if doc_length else 0
        p_w_given_c = prob_w_given_corpus.get(term, 1e-6)
        score += math.log(lambda_smooth * p_w_given_d + (1 - lambda_smooth) * p_w_given_c + 1e-6)
    return score

# Improved Query Expansion
def expand_query(query_terms):
    expanded_terms = set(query_terms)
    for term in query_terms:
        if term in inverted_index:
            index_entry = inverted_index[term]
            if isinstance(index_entry, dict):
                related_terms = list(index_entry.keys())[:20]  # Expanding to 20 terms
            elif isinstance(index_entry, list):
                related_terms = index_entry[:20]  # Taking first 20 terms if it's a list
            else:
                related_terms = []
            expanded_terms.update(related_terms)
    return list(expanded_terms)

# Filtering Stopwords
stopwords = {"the", "is", "and", "a", "of", "to", "in", "on", "with", "that", "for", "as", "by", "at"}

# Parsing Queries from XML
def parse_queries(query_file):
    try:
        tree = ET.parse(query_file)
        root = tree.getroot()
        queries = {}
        query_id_counter = 1
        for query in root.findall("top"):
            query_text = query.find("title").text.strip()
            query_terms = [term for term in query_text.lower().split() if term not in stopwords]
            queries[str(query_id_counter)] = " ".join(query_terms)
            query_id_counter += 1
        print(f"Successfully loaded {len(queries)} queries!")
        return queries
    except FileNotFoundError:
        print(f"Error: {query_file} not found!")
        exit()
    except ET.ParseError as e:
        print(f"XML Parsing Error: {e}")
        exit()

# Generating Results
def generate_results(query_file, output_vsm, output_bm25, output_lm):
    queries = parse_queries(query_file)
    vsm_results, bm25_results, lm_results = [], [], []
    
    for query_id, query_text in queries.items():
        print(f"Processing Query {query_id}...")
        query_terms = expand_query(query_text.split())
        top_docs = list(doc_lengths.keys())[:25000]  # Processing 25,000 docs per query
        
        vsm_scores = {doc_id: cosine_similarity({term: compute_idf(term) for term in query_terms}, compute_document_vector(doc_id)) for doc_id in top_docs}
        bm25_scores = {doc_id: bm25_score(query_terms, doc_id) for doc_id in top_docs}
        lm_scores = {doc_id: lm_score(query_terms, doc_id) for doc_id in top_docs}
        
        for rank, (doc_id, score) in enumerate(sorted(vsm_scores.items(), key=lambda x: x[1], reverse=True)[:25000], start=1):
            vsm_results.append(f"{query_id} 0 {doc_id} {rank} {score:.4f} VSM_run")
        for rank, (doc_id, score) in enumerate(sorted(bm25_scores.items(), key=lambda x: x[1], reverse=True)[:25000], start=1):
            bm25_results.append(f"{query_id} 0 {doc_id} {rank} {score:.4f} BM25_run")
        for rank, (doc_id, score) in enumerate(sorted(lm_scores.items(), key=lambda x: x[1], reverse=True)[:25000], start=1):
            lm_results.append(f"{query_id} 0 {doc_id} {rank} {score:.4f} LM_run")
    
    with open(output_vsm, "w") as f:
        f.write("\n".join(vsm_results))
    with open(output_bm25, "w") as f:
        f.write("\n".join(bm25_results))
    with open(output_lm, "w") as f:
        f.write("\n".join(lm_results))

    print("Search results generated in TREC_EVAL format!")

query_file_path = r"C:\Users\Chand\OneDrive\Desktop\Mechanics of Search\Search Engine Assignment 1\cranfield-trec-dataset-main\cranfield-trec-dataset-main\cran.qry.xml"
generate_results(query_file_path, "vsm_results.txt", "bm25_results.txt", "lm_results.txt")

