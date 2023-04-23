#library imports
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from transformers import pipeline
import torch

class t5_qa():
    """
    This class is used to generate answers to questions based on the context provided using T5 based model from Conscious AI.
    
    Attributes:
        device: The device to be used for the model.
        tokenizer: The tokenizer to be used for the model.
        model: The model to be used for the pipeline.

    Methods:
        generate_answer: This method is used to generate answers to questions based on the context provided.
    """
    def __init__(self):
        
        # set device
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # load tokenizer and model
        self.tokenizer = AutoTokenizer.from_pretrained("consciousAI/question-answering-generative-t5-v1-base-s-q-c")
        self.model = AutoModelForSeq2SeqLM.from_pretrained("consciousAI/question-answering-generative-t5-v1-base-s-q-c").to(self.device)

    def generate_answer(self, question, context):

        # create input string
        input_text = "question: " + question + "</s> question_context: " + context

        # encode input string using tokenizer
        input_tokenized = self.tokenizer.encode(input_text, return_tensors='pt', truncation=True, padding='max_length', max_length=1024).to(self.device)

        # generate answer
        summary_ids = self.model.generate(input_tokenized, max_length=50, min_length=20, num_beams=5, early_stopping=True)
        
        # decode output string
        output = [self.tokenizer.decode(id, clean_up_tokenization_spaces=True, skip_special_tokens=True) for id in summary_ids]
        
        return str(output[0])