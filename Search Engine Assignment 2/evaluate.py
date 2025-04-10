import json
from app import bm25_search  # directly use your app's bm25+CLIP search
from tqdm import tqdm

def precision_at_k(retrieved, relevant, k):
    retrieved_at_k = retrieved[:k]
    relevant_retrieved = [doc for doc in retrieved_at_k if doc in relevant]
    return len(relevant_retrieved) / k

def average_precision(retrieved, relevant):
    hits = 0
    sum_precisions = 0.0
    for i, doc in enumerate(retrieved):
        if doc in relevant:
            hits += 1
            sum_precisions += hits / (i + 1)
    return sum_precisions / len(relevant) if relevant else 0.0

def evaluate_all(queries, ground_truth, k_values=[5, 10]):
    map_total = 0
    precision_totals = {k: 0 for k in k_values}
    num_queries = 0

    for query in tqdm(queries, desc="Evaluating"):
        if query not in ground_truth:
            continue

        relevant = ground_truth[query]
        results = bm25_search(query, top_k=max(k_values))
        retrieved_urls = [r["image_url"] for r in results]

        num_queries += 1
        map_total += average_precision(retrieved_urls, relevant)
        for k in k_values:
            precision_totals[k] += precision_at_k(retrieved_urls, relevant, k)

    results = {
        "MAP": round(map_total / num_queries, 4)
    }
    for k in k_values:
        results[f"Precision@{k}"] = round(precision_totals[k] / num_queries, 4)
    
    return results

# Load queries
with open("queries.txt", "r", encoding="utf-8") as f:
    queries = [q.strip() for q in f.readlines() if q.strip()]

# Load ground truth
with open("ground_truth_filtered.json", "r", encoding="utf-8") as f:

    ground_truth = json.load(f)

# Run evaluation
metrics = evaluate_all(queries, ground_truth)
print("\nEvaluation Results:")
for metric, score in metrics.items():
    print(f"{metric}: {score}")
