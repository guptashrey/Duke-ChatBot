# library imports
from fastapi import FastAPI, Request
from starlette.responses import JSONResponse

from haystack import Pipeline
from haystack.nodes import FARMReader
from haystack.nodes import DensePassageRetriever

import pandas as pd
import os
import logging
import json
import openai

logging.basicConfig(format="%(levelname)s - %(name)s -  %(message)s", level=logging.WARNING)
logging.getLogger("haystack").setLevel(logging.INFO)

# load the api key from config.json
config = json.load(open("../config.json"))
api_key = config["api_key"]
openai_api_key = config["openai_api_key"]

def initialize():
    '''
    Function to initialize elasticsearch document store objects, retrievers, reader and qna pipelines.

    Args:
        None

    Returns:
        querying_pipeline_reddit (haystack.Pipeline): Qna pipeline for reddit posts.
        querying_pipeline_research_papers (haystack.Pipeline): Qna pipeline for research papers.
        api_key (str): API key for authentication.
    '''

# initialize fastapi app
app = FastAPI()

# # define middleware for authentication
# @app.middleware("http")
# async def authentication(request: Request, call_next):
#     '''
#     Middleware for authentication.

#     Args:
#         request (Request): Request object.
#         call_next (function): Function to call next.

#     Returns:
#         JSONResponse: JSON response object.
#     '''
#     if request.headers.get('api-key') == api_key:
#         response = await call_next(request)

#     else:
#         response = JSONResponse(
#             content={"message": "unauthorized access"}, status_code=401
#         )
#     return response

# define search endpoint
@app.get("/answer/{query}")
async def search(query: str):
    '''
    Search endpoint for searching reddit posts and research papers.

    Args:
        query (str): Query string.

    Returns:
        dict: Dictionary containing search results.
    '''

    openai.api_key = openai_api_key
    info = "Duke University is a private research university in Durham, North Carolina. Founded by Methodists and Quakers in the present-day city of Trinity in 1838, the school moved to Durham in 1892. In 1924, tobacco and electric power industrialist James Buchanan Duke established The Duke Endowment and the institution changed its name to honor his deceased father, Washington Duke."
    
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user",
             "content": f"Can you answer the given question based on the provided information? Question: '{query}' Information: '{info}'"}
        ]
    )

    corrected_text = dict(completion.choices[0].message)["content"].replace("\n", "")
    print(corrected_text)
    return {"id": "1", "choices": [{"text": corrected_text}]}