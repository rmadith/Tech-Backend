from bs4 import BeautifulSoup
import requests
import pandas as pd
import advertools as adv
import chromadb
import time


techcrunch = None
count = 10

client = chromadb.PersistentClient(path="chroma.db")
collection = client.get_collection("tech")

while True:
    try:
        techcrunchCurrent = adv.sitemap_to_df('https://techcrunch.com/news-sitemap.xml', recursive=True)
        techcrunch = pd.concat([techcrunch, techcrunchCurrent]).drop_duplicates(keep=False)
    except:
        continue
    
    for url in techcrunch['loc']:
        try:
            # Get the content of the url
            response = requests.get(url)
            html = response.content

            # Parse the html content
            soup = BeautifulSoup(html, 'html.parser')

            # Get the title of the page
            title = soup.title.text

            # Get the content of the page
            content = soup.find('div', class_='article-content').text

            context = {
                'title': title,
                'content': content,
                'source': 'techcrunch',
                'url': url,
            }

            collection.add(documents=content, uris = url, metadatas=context)

            count -= 1

            if count < 0:
                time.sleep(60)
                count = 10

        except:
            continue