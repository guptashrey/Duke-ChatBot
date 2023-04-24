# library imports
import pandas as pd
import argparse
import requests
from tqdm import tqdm

def get_answers(test_questions_file_path):
    """
    Function to get the answers using different QnA Pipelines to the test questions.

    Args:
        test_questions_file_path (str): Path to the .csv file containing the test questions
    
    Returns:
        None
    """
    # read test questions
    test_questions = pd.read_csv(test_questions_file_path)

    # send requests to the QnA Pipelines and get the answers
    for i in tqdm(range(len(test_questions))):
        answer_ndl = requests.get('http://0.0.0.0:8060/chat_v0/'+str(test_questions.iloc[i, 0])).json()
        answer_dl_1 = requests.get('http://0.0.0.0:8060/chat_v1/'+str(test_questions.iloc[i, 0])).json()
        answer_dl_2 = requests.get('http://0.0.0.0:8060/chat_v2/'+str(test_questions.iloc[i, 0])).json()
        answer_ndl = answer_ndl["choices"][0]["text"]
        answer_dl_1 = answer_dl_1["choices"][0]["text"]
        answer_dl_2 = answer_dl_2["choices"][0]["text"]

        test_questions.iloc[i, 1] = answer_ndl
        test_questions.iloc[i, 2] = answer_dl_1
        test_questions.iloc[i, 3] = answer_dl_2

    # save the answers to the test questions
    test_questions.to_csv("../performance_testing/test_answers.csv", index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                    prog='testing',
                    description='This script is used to get the answers using different QnA Pipelines to the test questions.')
    parser.add_argument('test_questions_file_path', type=str, help='Path to the .csv file containing the test questions')
    
    # parse arguments
    args = parser.parse_args()
    test_questions_file_path = args.test_questions_file_path

    # call function to get the answers to the test questions
    get_answers(test_questions_file_path)