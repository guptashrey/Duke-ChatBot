from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

class generative_qa():
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.tokenizer = AutoTokenizer.from_pretrained("consciousAI/question-answering-generative-t5-v1-base-s-q-c")
        self.model = AutoModelForSeq2SeqLM.from_pretrained("consciousAI/question-answering-generative-t5-v1-base-s-q-c").to(self.device)

    def generate_answer(self, question, context):
        input_text = "question: " + question + "</s> question_context: " + context
        input_tokenized = self.tokenizer.encode(input_text, return_tensors='pt', truncation=True, padding='max_length', max_length=1024).to(self.device)

        summary_ids = self.model.generate(input_tokenized, max_length=50, min_length=20, num_beams=5, early_stopping=True)
        output = [self.tokenizer.decode(id, clean_up_tokenization_spaces=True, skip_special_tokens=True) for id in summary_ids]
        return str(output[0])