# Information Retrieval System

## Overview
This repository contains the implementation of an **Information Retrieval (IR) System** that utilizes three ranking models:
- **Vector Space Model (VSM)** (TF-IDF with Cosine Similarity)
- **BM25** (Best Matching 25)
- **Language Model (LM)** (Jelinek-Mercer Smoothing)

The system indexes and retrieves documents from the **Cranfield dataset**, a standard benchmark for IR research. The ranking effectiveness is evaluated using **trec_eval**, with performance metrics such as **Mean Average Precision (MAP), Precision at 5 (P@5), and Normalized Discounted Cumulative Gain (NDCG).**

---

## Features
- **Efficient indexing pipeline** with tokenization, stopword removal, and case normalization.
- **Implementation of three retrieval models (VSM, BM25, LM).**
- **Query-based document ranking with similarity scores.**
- **Evaluation using trec_eval to measure retrieval effectiveness.**
- **Optimized for reproducibility with structured scripts and output files.**

---

##  Directory Structure
```
📁 search-engine-project/
│── 📁 data/                # Contains the Cranfield dataset
│   ├── cran.all.1400.xml   # Cranfield dataset (documents)
│   ├── cran.qry.xml   # queries used for retrieval evaluation
    ├── cranqrel.trec.txt   # Ground truth relevance file (Moved to tec_eval for evaluation)
│
│── 📁 tec_eval/            # Evaluation directory
│   ├── vsm_results.txt     # Ranked results for VSM (Moved here after ranking)
│   ├── bm25_results.txt    # Ranked results for BM25 (Moved here after ranking)
│   ├── lm_results.txt      # Ranked results for LM (Moved here after ranking)
│   ├── cranqrel.trec.txt   # Ground truth relevance file (Used for evaluation)
│   ├── vsm_eval.txt        # Evaluation metrics for VSM (Generated after evaluation)
│   ├── bm25_eval.txt       # Evaluation metrics for BM25 (Generated after evaluation)
│   ├── lm_eval.txt         # Evaluation metrics for LM (Generated after evaluation)
│
│── indexing.py             # Script for indexing documents
│── generate_results.py     # Script for document retrieval and ranking
│── inverted_index.json     # Stores the inverted index
│── tf_index.json           # Contains the term frequency (TF) values for each term in each document
│── bm25_data.json          # Contains document lengths and the average document length
│── lm_data.json            # Stores corpus-wide term probabilities
│── requirements.txt        # Dependencies for the project
│── README.md               # Documentation
```

---

##  **Ranking Process and Score Computation**
For a given user query, documents are ranked using three models:
- **VSM**: Computes Cosine Similarity between query and document vectors.
- **BM25**: Uses probabilistic ranking based on term frequency and document length.
- **LM**: Estimates query likelihood using Jelinek-Mercer smoothing.

Each ranked output follows **TREC format**:
```
query_id  iter  document_id  rank  similarity  run_id
```
Example outputs:
```
 1 0 875 1 0.8646 BM25_run
 1 0 621 1 0.0871 VSM_run
 1 0 1102 1-2146.1797 LM_run
```

---

## ⚙️ **Installation & Setup**
### **1️. Install Dependencies**
Ensure you have Python installed, then install required libraries.

### **2️. Run the Indexing Process**
```bash
python indexing.py
```
This generates `inverted_index.json` for fast retrieval.

### **3️. Retrieve Documents Using Ranking Models**
```bash
python generate_results.py
```
This generates ranked results for **VSM, BM25, and LM**, which are then moved to `tec_eval/` for evaluation.

### **4️. Evaluate the Ranking Models**
Move to the `tec_eval/` directory and run:
```bash
cd tec_eval
./trec_eval cranqrel.trec.txt vsm_results.txt > vsm_eval.txt
./trec_eval cranqrel.trec.txt bm25_results.txt > bm25_eval.txt
./trec_eval cranqrel.trec.txt lm_results.txt > lm_eval.txt
```
This computes metrics such as **MAP and P@5** storing evaluation results in respective files.

To get **NDCG** and store in respective files, run:
```bash
cd trec_eval
./trec_eval -m ndcg_cut.5 -m ndcg_cut.10 -m ndcg_cut.20 cranqrel.trec.txt vsm_results.txt > ndcg_vsm.txt
./trec_eval -m ndcg_cut.5 -m ndcg_cut.10 -m ndcg_cut.20 cranqrel.trec.txt bm25_results.txt > ndcg_bm25.txt
./trec_eval -m ndcg_cut.5 -m ndcg_cut.10 -m ndcg_cut.20 cranqrel.trec.txt lm_results.txt > ndcg_lm.txt

cat vsm_eval.txt ndcg_vsm.txt > temp_vsm_eval.txt && mv temp_vsm_eval.txt vsm_eval.txt
cat bm25_eval.txt ndcg_bm25.txt > temp_bm25_eval.txt && mv temp_bm25_eval.txt bm25_eval.txt
cat lm_eval.txt ndcg_lm.txt > temp_lm_eval.txt && mv temp_lm_eval.txt lm_eval.txt
```

---

##  **Evaluation Results**
The effectiveness of each ranking model is measured using `trec_eval`. Summary of results:

| **Metric**   | **VSM**  | **BM25**  | **LM**  |
|-------------|---------|---------|---------|
| **MAP**     | 0.1169  | 0.1907  | 0.1272  |
| **P@5**     | 0.1058  | 0.1893  | 0.1138  |
| **NDCG@10** | 0.1390  | 0.2448  | 0.1486  |

🔹 **BM25 consistently outperforms VSM and LM, ranking relevant documents higher.**  
🔹 **Jelinek-Mercer LM has better recall but lower ranking precision.**  
🔹 **VSM is competitive but suffers from document length bias.**

---

##  **Key Takeaways**
- **BM25 is the most effective** ranking model for relevance-based retrieval.
- **VSM is useful for similarity-based search** but lacks length normalization.
- **LM improves recall** but requires better smoothing for precision.
- **Further tuning** of hyperparameters (e.g., BM25's `k1`, `b`, and LM's `λ`) can improve retrieval.

---

##  **Resources**
- **Cranfield Dataset**: [GitHub](https://github.com/oussbenk/cranfield-trec-dataset)
- **TREC_EVAL Tool**: [Download v9.0.7](https://github.com/usnistgov/trec_eval/archive/refs/tags/v9.0.7.tar.gz)
- **Project Repository**: [GitHub](https://github.com/ChandralekhaV/search-engine-project)

---


---

##  **License**
This project is licensed under the **MIT License**. Feel free to modify and use it for research or educational purposes.

---

###  **Developed by:**  
**Chandralekha Venkatesh Perumal**  
[LinkedIn](www.linkedin.com/in/chandralekha-v) | [GitHub](https://github.com/ChandralekhaV) | [Email](mailto:chandralekha.venkateshperumal2@mail.dcu.ie)

