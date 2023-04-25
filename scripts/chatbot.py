# library imports
from fastapi import FastAPI, Request
from starlette.responses import JSONResponse

from haystack import Pipeline
from haystack.nodes import FARMReader
from haystack.nodes import DensePassageRetriever
from haystack.nodes import BM25Retriever

from helper_functions import get_elasticsearch_document_store
from t5_qa import t5_qa
from chatgpt_qa import chatgpt_qa

import pandas as pd
import os
import logging
import json
import uuid

# set logging level for haystack
logging.getLogger("haystack").setLevel(logging.ERROR)

# define logger for chatbot
chat_log = logging.getLogger('chat')
chat_log.setLevel(logging.INFO)
handler = logging.FileHandler('../chat.log')
handler.setLevel(logging.INFO)
chat_log.addHandler(handler)

def app_initialize():
    '''
    Function to initialize chatgpt_qa, t5_qa and api key objects.

    Args:
        None
    
    Returns:
        chatgpt_qa_obj (chatgpt_qa): Chatgpt_qa object.
        generative_qa_obj (generative_qa): t5_qa object.
        api_key (str): API key for authentication.
    '''

    # load the api key from config.json
    config = json.load(open("../config.json"))
    api_key = config["api_key"]

    t5_qa_obj = t5_qa()
    chatgpt_qa_obj = chatgpt_qa(config["openai_api_key"])

    return chatgpt_qa_obj, t5_qa_obj, api_key

def qna_pipeline_initialize():
    '''
    Function to initialize elasticsearch document store, retrievers, reader and qna pipeline objects.

    Args:
        None

    Returns:
        ndl_querying_pipeline (haystack.Pipeline): Non Deep Learning based QnA pipeline object.
        dl_querying_pipeline (haystack.Pipeline): Deep Learning based QnA pipeline object.
    '''

    # get elasticsearch host from environment variables
    host = os.environ.get("ELASTICSEARCH_HOST", "localhost")
    
    # initialize elasticsearch document store
    document_store = get_elasticsearch_document_store(host, "document")

    # initialize BM25 retriever
    bm25_retriever = BM25Retriever(document_store=document_store)

    # initialize non deep learning based qna pipeline
    ndl_querying_pipeline = Pipeline()
    ndl_querying_pipeline.add_node(component=bm25_retriever, name="Retriever", inputs=["Query"])

    # initialize DPR retriever
    dpr_retriever = DensePassageRetriever(
        document_store=document_store,
        query_embedding_model="facebook/dpr-question_encoder-single-nq-base",
        passage_embedding_model="facebook/dpr-ctx_encoder-single-nq-base"
    )

    # initialize FARM reader
    reader = FARMReader(model_name_or_path="deepset/roberta-base-squad2", use_gpu=True)

    # initialize deep learning based qna pipeline
    dl_querying_pipeline = Pipeline()
    dl_querying_pipeline.add_node(component=dpr_retriever, name="Retriever", inputs=["Query"])
    dl_querying_pipeline.add_node(component=reader, name="Reader", inputs=["Retriever"])

    return ndl_querying_pipeline, dl_querying_pipeline

# initialize fastapi app
app = FastAPI()

ndl_querying_pipeline, dl_querying_pipeline = qna_pipeline_initialize()
chatgpt_qa_obj, t5_qa_obj, api_key = app_initialize()

# define middleware for authentication
@app.middleware("http")
async def authentication(request: Request, call_next):
    '''
    Middleware for authentication.

    Args:
        request (Request): Request object.
        call_next (function): Function to call next.

    Returns:
        JSONResponse: JSON response object.
    '''

    if request.headers.get('api-key') == api_key:
        response = await call_next(request)

    else:
        response = JSONResponse(
            content={"message": "unauthorized access"}, status_code=401
        )
    return response

@app.get("/chat_v0/{question}")
async def chat_v0(question: str):
    '''
    Chat endpoint based non-deep learning approach.

    Args:
        question (str): question string.

    Returns:
        dict: Dictionary containing the answer
    '''

    # get predictions from qna pipeline
    prediction = ndl_querying_pipeline.run(query=question, params={
        "Retriever": {"top_k": 10}
        })
    answers = pd.DataFrame([i.to_dict() for i in prediction["documents"]])
    answers.sort_values(by="score", ascending=False, inplace=True)
    context = answers["content"].head(1).values[0]

    # use generative_qa to correct the answer based on question and context
    corrected_answer = t5_qa_obj.generate_answer(question, context)

    # log the question and answer
    chat_log.info(f"Question: {question} Answer: {corrected_answer}")
    
    return {"id": str(uuid.uuid4()), "choices": [{"text": corrected_answer}]}

@app.get("/chat_v1/{question}")
async def chat_v1(question: str):
    '''
    Chat endpoint based on T5 answer correction model.

    Args:
        question (str): question string.

    Returns:
        dict: Dictionary containing the answer
    '''

    # get predictions from qna pipeline
    prediction = dl_querying_pipeline.run(query=question, params={
        "Retriever": {"top_k": 10},
        "Reader": {"top_k": 5}
        })
    
    # get the highest confidence answer and it's corresponding document
    answers = pd.DataFrame([i.to_dict() for i in prediction["answers"]])
    answers['document_ids'] = answers['document_ids'].apply(lambda x: x[0])
    documents = pd.DataFrame([i.to_dict() for i in prediction["documents"]])
    merge = pd.merge(documents, answers, left_on="id", right_on="document_ids", how="inner")

    # get the text from the document
    context = merge["content"].head(1).values[0]

    # use generative_qa to correct the answer based on question and context
    corrected_answer = t5_qa_obj.generate_answer(question, context)

    # log the question and answer
    chat_log.info(f"Question: {question} Answer: {corrected_answer}")
    
    return {"id": str(uuid.uuid4()), "choices": [{"text": corrected_answer}]}

@app.get("/chat_v2/{question}")
async def chat_v2(question: str):
    '''
    Chat endpoint based on ChatGPT answer correction.

    Args:
        question (str): question string.

    Returns:
        dict: Dictionary containing the answer
    '''

    prediction = dl_querying_pipeline.run(query=question, params={
        "Retriever": {"top_k": 10},
        "Reader": {"top_k": 5}
        })
    
   # get the highest confidence answer and it's corresponding document
    answers = pd.DataFrame([i.to_dict() for i in prediction["answers"]])
    answers['document_ids'] = answers['document_ids'].apply(lambda x: x[0])
    documents = pd.DataFrame([i.to_dict() for i in prediction["documents"]])
    merge = pd.merge(documents, answers, left_on="id", right_on="document_ids", how="inner")

    # get the text from the document
    context = merge["content"].head(1).values[0]

    # use chatgpt_qa to correct the answer based on question and context
    corrected_answer = chatgpt_qa_obj.generate_answer(question, context)

    # log the question and answer
    chat_log.info(f"Question: {question} Answer: {corrected_answer}")

    return {"id": str(uuid.uuid4()), "choices": [{"text": corrected_answer}]}