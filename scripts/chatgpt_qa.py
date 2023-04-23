#library imports
import openai

class chatgpt_qa():
    """
    This class is used to generate answers to questions based on the context provided using Chat GPT.

    Attributes:
        openai_api_key: The openai_api_key to be used for the model.

    Methods:
        generate_answer: This method is used to generate answers to questions based on the context provided.
    """

    def __init__(self, openai_api_key):
        openai.api_key = openai_api_key

    def generate_answer(self, question, context):
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user",
                "content": f"Can you answer the given question based on the provided context? Question: '{question}' Context: '{context}'"}
            ]
        )
        return dict(completion.choices[0].message)["content"].replace("\n", "")