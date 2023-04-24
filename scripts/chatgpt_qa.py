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
                "content": f"""
                Answer the question using the given context. If you are not sure about the answer, answer with "I don't have enough context to answer this question.".

                Context: {context}

                Question: {question}
                """
                }
            ]
        )
        return dict(completion.choices[0].message)["content"].replace("\n", "")