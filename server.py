from flask import Flask

app = Flask(__name__)

from pinecone import Pinecone
import google.generativeai as ga
import numpy as np
import requests
from flask import request
import json

pc = Pinecone(api_key="165724f3-337c-4129-aece-106b08e6a221")
ga.configure(api_key="*")
model = ga.GenerativeModel("gemini-pro")

index = pc.Index('openai')

url = "https://api.github.com/search/repositories?q="

headers = {
  'Authorization': 'Token *'
}

def build(query: str, context: str):
    base_prompt = {
        "content": "I am going to give you an article, generate key points"
        " based only on the provided context, and not any other information."
        " Just generate the points, I don't want you to say Sure here is the answer or here are the key points or anything like that"
        " Break your answer up into nicely readable points.",
    }
    user_prompt = {
        "content": f" The question is '{query}'. Here is all the context you have:"
        f'{(" ").join(context)}',
    }
    system = f"{base_prompt['content']} {user_prompt['content']}"

    return system[:100000]

def get_article(id_list: list):
    if(id_list == [[],[]]):
        vector = list(np.zeros(1536))
    else:
        vector = index.fetch(id_list[0])["vectors"][id_list[0][len(id_list[0]) - 1]]["values"]

    query = index.query(
            vector=vector,
            top_k=len(id_list[0]) + 1 + len(id_list[1]),
            include_values=True,
            include_metadata=True
    )

    #print(query["matches"])

    for i in range(len(query["matches"])):
        if(query["matches"][i]["id"] not in id_list[0] and query["matches"][i]["id"] not in id_list[1]):
            key = model.generate_content(build(query["matches"][i]["metadata"]["text"], ""))
            topic = model.generate_content("Generate a one word word topic keyword: \n\n" + query["matches"][i]["metadata"]["text"]).text
            title = model.generate_content("Generate a title for the article: \n\n" + query["matches"][i]["metadata"]["text"]).text
            to_be_returned = {
                "id": query["matches"][i]["id"],
                "text": query["matches"][i]["metadata"]["text"],
                "url": query["matches"][i]["metadata"]["url"],
                "title": query["matches"][i]["metadata"]["title"],
                "generatedTitle": title,
                "keyPoints": key.text,
                "github": requests.request("GET", url+(topic.replace(" ", ",").replace('\n',"").replace('"', "")+"&sort='stars'"), headers=headers).json()
            }
            return to_be_returned
        




@app.route('/', methods=['GET'])
def handle_get_request():
    # Get the request parameters
    param1 = request.args.get('json')
    # Your code to handle the GET request goes here
    param1 = json.loads(param1)
    return get_article([[param1["like"]], [param1["dislike"]]])

if __name__ == '__main__':
    app.run()