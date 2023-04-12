# library imports
from fastapi import FastAPI, Request
from starlette.responses import JSONResponse

from haystack import Pipeline
from haystack.nodes import FARMReader
from haystack.nodes import DensePassageRetriever
from haystack.document_stores import ElasticsearchDocumentStore

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

    host = os.environ.get("ELASTICSEARCH_HOST", "localhost")
    document_store = ElasticsearchDocumentStore(
        host=host,
        username="",
        password="",
        index="document",
        similarity="dot_product",
        embedding_dim=768,
    )

    retriever = DensePassageRetriever(
        document_store=document_store,
        query_embedding_model="facebook/dpr-question_encoder-single-nq-base",
        passage_embedding_model="facebook/dpr-ctx_encoder-single-nq-base"
    )

    reader = FARMReader(model_name_or_path="deepset/roberta-base-squad2", use_gpu=True)

    # initialize qna pipeline for reddit posts
    querying_pipeline = Pipeline()
    querying_pipeline.add_node(component=retriever, name="Retriever", inputs=["Query"])
    querying_pipeline.add_node(component=reader, name="Reader", inputs=["Retriever"])

    return querying_pipeline

# initialize fastapi app
app = FastAPI()
querying_pipeline = initialize()

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

    prediction = querying_pipeline.run(query=query, top_k_retriever=10, top_k_reader=5)
    answers = pd.DataFrame([i.to_dict() for i in prediction["answers"]])
    answers['document_ids'] = answers['document_ids'].apply(lambda x: x[0])
    documents = pd.DataFrame([i.to_dict() for i in prediction["documents"]])
    merge = pd.merge(documents, answers, left_on="id", right_on="document_ids", how="inner")

    openai.api_key = openai_api_key
    info = merge["content"].head(1).values[0]
    
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