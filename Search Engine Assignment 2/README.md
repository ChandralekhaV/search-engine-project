# Wikipedia-Based Image Search Engine

##  Overview
This project implements a lightweight image search engine focused on animal-related images from Wikipedia. It combines BM25-based keyword search with CLIP-based visual similarity for re-ranking. The goal is to replicate the simplicity of early Google Image Search while enhancing accuracy using modern vision-language models.

---

## Features
-  Custom web crawler for Wikipedia animal categories  
-  Image annotation using title, alt text, file name, and animal name  
-  BM25 keyword-based retrieval  
-  CLIP re-ranking for visual similarity  
-  Jungle-themed, responsive web interface using Flask  

---

## How to Run
1️. **Clone the Repository**
   git clone https://github.com/ChandralekhaV/search-engine-project/tree/main/Search%20Engine%20Assignment%202

   cd search-engine-project/assignment2

2️. **Install Dependencies**
    
    pip install -r requirements.txt
    
    To use CLIP:
      
      pip install git+https://github.com/openai/CLIP.git

3. **Crawl and collect images**  
   ```bash
   python crawler.py
This gathers images and metadata into image_surrogates.json

4. **Index images for BM25 search**
    ```bash
    python indexer.py
Generates BM25 indexes for text-based search

5. **Generate CLIP embeddings**
    ```bash
    python embed_images.py
Creates image_embeddings.json for re-ranking

6. **Launch the web interface**
     ```bash
     python app.py
Then visit http://127.0.0.1:5000 in your browser



Try These Queries - 
        hare, capra, frog, deer, civet, kudu, rabbit, wolf, savanna, mongoose, sheep, leopard 

### Homepage  
![Homepage](screenshots/Webpage.png)

### Search Example  
![Search Result](screenshots/hare.png)
![Search Result](screenshots/capra.png)
![Search Result](screenshots/frog.png)



## Quantitative Results

To assess the system’s effectiveness in a measurable way, a quantitative evaluation (`evaluate.py`) was conducted using a filtered subset of 153 animal-related queries (e.g., *deer*, *rabbit*, *leopard*). Each query was matched against a corresponding set of relevant images in a custom-built ground truth file (`ground_truth_filtered.json`), and three standard evaluation metrics were computed:

- **Mean Average Precision (MAP)** – Reflects the average precision across ranked relevant documents for each query.
- **Precision@5** – Measures the proportion of relevant results in the top 5 images.
- **Precision@10** – Measures relevance among the top 10 images.

| Metric                     | Score   |
|----------------------------|---------|
| Mean Average Precision (MAP) | 0.2642  |
| Precision@5               | 0.0667  |
| Precision@10              | 0.0333  |

> **Table 1**: Evaluation metrics over 153 filtered animal-related queries

While the MAP score indicates promising overall ranking behavior, early precision remains modest. This can be attributed to the limited dataset size, metadata quality, and the challenge of matching short queries to noisy real-world image data.


###  **Developed by:**  
**Chandralekha Venkatesh Perumal**  
[LinkedIn](https://www.linkedin.com/in/chandralekha-v/) | [GitHub](https://github.com/ChandralekhaV) | [Email](mailto:chandralekha.venkateshperumal2@mail.dcu.ie)
