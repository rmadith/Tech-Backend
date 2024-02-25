from bs4 import BeautifulSoup
import requests
import pandas as pd
import advertools as adv

import json

import google.generativeai as ga
import chromadb.utils.embedding_functions as embedding_functions
import chromadb
import os

client = chromadb.PersistentClient(path="ChromaDB/chroma.db")
google_ef  = embedding_functions.GoogleGenerativeAiEmbeddingFunction(api_key="AIzaSyCP8PWutyKj8N_sM-v1XyPB54_YswnzxYc")
collection = client.get_collection("Tech", embedding_function=google_ef)





cnet = adv.sitemap_to_df('https://www.cnet.com/sitemaps/article/index.xml', recursive=True)

cnet.head()

for i in range(len(cnet)):
    url = cnet.loc[i, 'loc']
    response = requests.get(url)
    html = response.content
    soup = BeautifulSoup(html, 'html.parser')
    title = soup.title.text
    content = soup.find('script', type = 'application/ld+json')
    if content is None:
        continue
    data = json.loads(content.string)
    article_body = data.get("@graph", "Text not found")
    article_body = article_body[2].get("mainEntity", "Text not found")
    text = []
    for i in article_body:
        text.append(i['acceptedAnswer']['text'])
    text =  ' '.join(text)
    if content is None or text is None or len(text) < 900:
        continue
    collection.add(
        ids=url,
        documents=text[:900],
        metadatas={
            "title": title,
            "url": url,
            "source": "CNET",
        }
    )