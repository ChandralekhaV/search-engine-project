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

1. **Crawl and collect images**  
   ```bash
   python crawler.py
2. **Index images for BM25 search**
    python indexer.py
3. **Generate CLIP embeddings**
    python embed_images.py
4. **Launch the web interface**
     python app.py


Then visit http://127.0.0.1:5000

Try These Queries - 
        hare, capra, frog, deer, civet, kudu, rabbit, wolf, savanna, mongoose, sheep, leopard 

### Homepage  
![Homepage](screenshots\Webpage.png)

### Search Example  
![Search Result](screenshots/hare.png)
![Search Result](screenshots/capra.png)
![Search Result](screenshots/frog.png)

