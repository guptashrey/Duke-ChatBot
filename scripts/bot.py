# library imports
from fastapi import FastAPI, Request
from starlette.responses import JSONResponse

from haystack import Pipeline
from haystack.nodes import FARMReader
from haystack.nodes import DensePassageRetriever

from helper_functions import get_elasticsearch_document_store

import pandas as pd
import os
import logging
import json
import openai
import uuid

logging.getLogger("haystack").setLevel(logging.ERROR)
chat_log = logging.getLogger('chat')
chat_log.setLevel(logging.INFO)
handler = logging.FileHandler('chat.log')
handler.setLevel(logging.INFO)
chat_log.addHandler(handler)

def initialize():
    '''
    Function to initialize elasticsearch document store, retrievers, reader and qna pipeline objects.

    Args:
        None

    Returns:
        querying_pipeline (haystack.Pipeline): Qna pipeline object.
        api_key (str): API key for authentication.
        openai_api_key (str): OpenAI API key for authentication.
    '''

    host = os.environ.get("ELASTICSEARCH_HOST", "localhost")
    document_store = get_elasticsearch_document_store(host, "document")

    retriever = DensePassageRetriever(
        document_store=document_store,
        query_embedding_model="facebook/dpr-question_encoder-single-nq-base",
        passage_embedding_model="facebook/dpr-ctx_encoder-single-nq-base"
    )

    reader = FARMReader(model_name_or_path="deepset/roberta-base-squad2", use_gpu=True)

    # initialize qna pipeline
    querying_pipeline = Pipeline()
    querying_pipeline.add_node(component=retriever, name="Retriever", inputs=["Query"])
    querying_pipeline.add_node(component=reader, name="Reader", inputs=["Retriever"])

    # load the api key from config.json
    config = json.load(open("../config.json"))
    api_key = config["api_key"]
    openai_api_key = config["openai_api_key"]

    return querying_pipeline, api_key, openai_api_key

# initialize fastapi app
app = FastAPI()
querying_pipeline, api_key, openai.api_key = initialize()

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

# define chatbot endpoint
@app.get("/chat/{query}")
async def chat(query: str):
    '''
    Chat endpoint for Pratt School of Engineering.

    Args:
        query (str): Query string.

    Returns:
        dict: Dictionary containing the answer
    '''

    prediction = querying_pipeline.run(query=query, params={
        "Retriever": {"top_k": 10},
        "Reader": {"top_k": 5}
        })
    
    answers = pd.DataFrame([i.to_dict() for i in prediction["answers"]])
    answers['document_ids'] = answers['document_ids'].apply(lambda x: x[0])
    documents = pd.DataFrame([i.to_dict() for i in prediction["documents"]])
    merge = pd.merge(documents, answers, left_on="id", right_on="document_ids", how="inner")
    info = merge["content"].head(1).values[0]
    
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user",
             "content": f"Can you answer the given question based on the provided information? Question: '{query}' Information: '{info}'"}
        ]
    )

    corrected_text = dict(completion.choices[0].message)["content"].replace("\n", "")
    chat_log.info(f"Question: {query} Answer: {corrected_text}")
    return {"id": str(uuid.uuid4()), "choices": [{"text": corrected_text}]}

@app.get("/temp/{query}")
async def temp(query: str):
    '''
    Chat endpoint for Pratt School of Engineering.

    Args:
        query (str): Query string.

    Returns:
        dict: Dictionary containing the answer
    '''

    prediction = querying_pipeline.run(query=query, params={
        "Retriever": {"top_k": 10},
        "Reader": {"top_k": 5}
        })
    
    answers = pd.DataFrame([i.to_dict() for i in prediction["answers"]])
    answers['document_ids'] = answers['document_ids'].apply(lambda x: x[0])
    documents = pd.DataFrame([i.to_dict() for i in prediction["documents"]])
    merge = pd.merge(documents, answers, left_on="id", right_on="document_ids", how="inner")
    info = merge["content"].head(1).values[0]

    corrected_text = info
    chat_log.info(f"Question: {query} Answer: {corrected_text}")
    return {"id": str(uuid.uuid4()), "choices": [{"text": corrected_text}]}