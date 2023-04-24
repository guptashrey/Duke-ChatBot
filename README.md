# Duke ChatBot
**Duke AIPI 540 Individual Project**

## Project Overview
Welcome to the Duke University Chatbot!

This cutting-edge AI-powered tool is specifically designed to make the lives of Duke University students easier by providing quick and accurate answers to their questions. Powered by a robust chatbot framework, advanced natural language processing, and machine learning technologies, this chatbot is designed to interact with website visitors, understand the semantics of questions asked, and deliver meaningful and immediate answers. Say goodbye to time-consuming searches and hello to a convenient and efficient way to get information about Duke University!

Duke Chatbot is designed to address the following pain points:

**1. Information overload:** Duke University students may often feel overwhelmed by the vast amount of information available about the university, such as campus locations, resources, events, and policies. This chatbot can serve as a one-stop source of accurate and up-to-date information, helping students easily find what they need without sifting through multiple sources.

**2. Time-consuming searches:** Students may spend significant time searching for answers to common questions, such as academic deadlines, financial aid information, or campus services. This chatbot can provide quick responses, saving students time and effort by delivering immediate answers to their inquiries in a conversational manner.

**3. User-friendly interaction:** Traditional methods of obtaining information, such as browsing websites or sending emails, may not always be user-friendly or intuitive for students. This chatbot can provide a conversational and user-friendly interface, making it easy for students to ask questions in a natural language format and receive prompt and relevant responses.

**4. Accessibility:** The DukeChat Bot can be accessed on the web or via the DukeChat mobile app, making it accessible to students on the go. Students can ask questions and receive answers at any time, from anywhere, without having to wait for a response.

&nbsp;
## Data Sources

Data about Duke University is needed to power the answers to the questions asked by the users. There is no particular dataset or data source that can be used to get all the information about Duke University. Hence, we need to scrape data from multiple websites and webpages to get the required information.

As there are multiple departments, schools and programs at Duke University, we need to scrape data from multiple subdomains of the main website [duke.edu](https://www.duke.edu/). The following are the subdomains from where the data is being scraped:

* [Master of Engineering in AI](https://ai.meng.duke.edu/)
* [Biomedical Engineering](https://bme.duke.edu/)
* [Civil & Environmental Engineering](https://cee.duke.edu/)
* [Master of Engineering in Cybersecurity](https://cybersecurity.meng.duke.edu)
* [Electrical & Computer Engineering](https://www.ece.duke.edu/)
* [Master of Engineering Management](https://memp.pratt.duke.edu/)
* [Mechanical Engineering & Materials Science](https://mems.duke.edu/)
* [Master of Engineering](https://meng.pratt.duke.edu/)
* [Pratt School of Engineering](https:/pratt.duke.edu/)

&nbsp;
## Data Processing

### **Creating a list of URLs to scrape**

Before scraping the data from the above listed subdomains, a list of URLs of the webpages and subdirectories needs to be created.

To create this list for each subdomain, a recursive function is used to traverse through the subdirectories and subpages of the subdomain and add the URLs to a dictionary. The dictionary is then converted to a list and saved as a JSON file.

The python script can be found in the `scripts` folder and can be run as follows:

**1. Create a new conda environment and activate it:** 
```
conda create --name nlp python=3.8
conda activate nlp
```
**2. Install python package requirements:** 
```
pip install -r requirements.txt 
```
**3. Change directory to the scripts folder:** 
```
cd scripts
```
**4. Run the URL list creation script:** 
```
python get_subpages.py <subdomain_url> <json_file_name>
```

For example, to create the list of URLs for the subdomain [https://ai.meng.duke.edu](https://ai.meng.duke.edu/), the following command can be run:

```bash
python python get_subpages.py "https://ai.meng.duke.edu" "../data/ai_meng_duke_edu.json"
```

### **Scraping text data from the webpages**

Once the list of URLs is created, the text data from all the webpages of a subdomain need to be scraped. As each webpage has a different structure, parsing the HTML of each webpage and extracting the required text data is a tedious and time-consuming task.

Hence, the [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) library is used to parse the HTML of the webpages and extract the text data. The text data is then cleaned using [html2text](https://pypi.org/project/html2text/) package and stored in a .txt file.

The python script to scrape text can be found in the `scripts` folder. Assuming you are in the same conda environment as the previous step, the python script can be run as follows:

**1. Change directory to the scripts folder:** 
```
cd scripts
```
**2. Run the web scraping script:** 
```
python scrape.py <json_file_name> <data_directory>
```

For example, to scrape the text data from the subdomain [https://ai.meng.duke.edu](https://ai.meng.duke.edu/), the following command can be run:

```bash
python scrape.py "../data/ai_meng_duke_edu.json" "../data"
```

### **Setting up Elasticsearch Document Store**

Elasticsearch is a distributed, open source search and analytics engine for all types of data, including textual, numerical, geospatial, structured, and unstructured. It allows us to store, search, and analyze big volumes of data quickly and in near real time. It is generally used as the underlying engine/technology that powers applications that have complex search features and requirements.

In this project, Elasticsearch is being used as the document store to store the text scraped from multiple websites and webpages.

It can be setup on your local machine using docker. The following steps can be followed to setup Elasticsearch on your local machine:

**1. Install Docker:** 
```bash
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io
```
**2. Pull the Elasticsearch docker image:** 
```bash
docker pull docker.elastic.co/elasticsearch/elasticsearch:7.17.6
```
**3. Create a volume to store the Elasticsearch data:** 
```bash
docker volume create es_v1
```

**4. Run the Elasticsearch docker image:** 
```bash
docker run -d -p 9200:9200 -e 'discovery.type=single-node' --name es_v1 --mount type=volume,src=es_v1,target=/usr/share/elasticsearch/ elasticsearch:7.17.6
```

**5. Check if Elasticsearch is running:** 
```bash
curl -X GET "localhost:9200/"
```

### **Processing & indexing the cleaned text in Elasticsearch**

Once the text data is scraped from the webpages, it needs to be processed and indexed in Elasticsearch. The following steps are performed to process and index the text data:
- Read the text data from all the .txt files
- Remove whitespaces, angle brackets, html tags and urls
- Webpages of a particular subdomain contain specific headers and footers. These headers and footers are removed from the text data
- Remove any non-unicode characters from the text data
- Chunk the text data into smaller chunks of 250 words each (with a 10 word overlap and respecting sentence boundaries)
- Index the chunks in Elasticsearch
- Create embeddings for each document in the Elasticsearch docstore using Dense Passage Retrieval (DPR) model (`facebook/dpr-ctx_encoder-single-nq-base`)

The python script to process and index the text data can be found in the `scripts` folder. Assuming you are in the same conda environment as the previous step, the python script can be run as follows:

**1. Change directory to the scripts folder:** 
```
cd scripts
```
**2. Run the text processing and indexing script:** 
```
python index_in_es.py "../data"
```

&nbsp;
## Non-Deep Learning Based Duke ChatBot Pipeline

The Duke ChatBot pipeline is a question answering system that allows users to ask questions about the Duke University and get answers to their questions. The pipeline consists of the following components:
- **Document Store:** Elasticsearch document store to store the text scraped from multiple websites and webpages
- **Retriever:** BM25 retriever to retrieve the relevant documents from the document store
- **Answer Generator:** A T5 based model to rephrase the formation of the top document returned by the BM25 Retriever based on the question asked

&nbsp;
## Deep Learning Based Duke ChatBot Pipeline

The Duke ChatBot pipeline is a question answering system that allows users to ask questions about the Duke University and get answers to their questions. The pipeline consists of the following components:
- **Document Store:** Elasticsearch document store to store the text scraped from multiple websites and webpages
- **Retriever:** Dense Passage Retrieval (DPR) model (`facebook/dpr-ctx_encoder-single-nq-base`) to retrieve the relevant documents from the document store
- **Reader:** Reader model (`deepset/roberta-base-squad2`) to extract the answer from the retrieved documents
- **Answer Generator:** A T5 or ChatGPT module to rephrase the formation of the answer returned by the Reader based on the question asked

&nbsp;
## Running the Duke ChatBot Pipeline Server

The Duke ChatBot pipeline server is a FastAPI server that allows us to query the ElasticSearch document store based on the user's question and returns the answer through a REST API.

The pipeline server performs the following steps:
1. Get the question from the user
2. Embed the question using Dense Passage Retrieval (DPR) model (`facebook/dpr-question_encoder-single-nq-base`)
3. Retrieve the top 10 relevant documents from the ElasticSearch document store using the question embedding
4. Run the retrieved documents through the Reader model (`deepset/roberta-base-squad2`) to get the answer
5. Pass the answer through the Answer Generator module (either `consciousAI/question-answering-generative-t5-v1-base-s-q-c` or `ChatGPT`) to rephrase the answer
6. Return the answer to the user as a JSON response

Assuming you are in the same conda environment as the previous step, the server can be run as follows:

**1. Change directory:** 
```
cd scripts
```
**2. Start the server:** 
```
uvicorn chatbot:app --reload --host 0.0.0.0 --port 8060
```

&nbsp;
## Performance Evaluation and Metrics

Due to the unsupervised nature of the data, there is no ground truth to evaluate the performance of the Duke ChatBot pipeline. However, the performance of the pipeline can be evaluated by asking questions to the pipeline and checking if the answer returned by the pipeline is relevant to the question asked.

### **Manual Qualitative Evaluation**
A list of 50 questions were asked to the Duke ChatBot pipeline and the answers returned by the pipeline were evaluated manually. Each answer was evaluated on a scale of 0 to 3 as follows:
- 0: The answer is not relevant to the question asked
- 1: No answer is returned by the pipeline
- 2: The answer is partially relevant to the question asked
- 3: The answer is relevant to the question asked

Based on the evaluation of different pipelines, the following table shows the performance of the Duke ChatBot pipeline:

| Pipeline | Incorrect Answer | No Answer | Partially Relevant Answer | Fully Relevant Answer |
| --- | :---: | :---: | :---: | :---: |
| Non-Deep Learning Approach | 76% | 0% | 24% | 0% |
| Deep Learning Approach with T5 Correction | 32% | 0% | 50% | 18% |
| Deep Learning Approach with ChatGPT Correction | **0%** | **32%** | **4%** | **64%** |

The detailed question-answer evaluation can be found in the `performance_testing` folder and the analysis can be found in the `test_answers_analysis.xlsx` file.

### **User Survey**
A user survey was conducted to evaluate the performance of the Duke ChatBot pipeline. The survey consisted of the following 2 questions:

1. How many queries did you try asking Duke ChatBot?
- 1 to 2
- 2 to 4
- more than 4

2. Please evaluate your experience using Duke ChatBot on the following criteria (on a scale of 0 to 3 stars):
- Ease of use
- Accuracy of the provided information
- User interface

The survey was filled by 17 users and the results are as follows:

| Number of queries | Percentage of Users |
| --- | :---: |
| 1 to 2 |  23% |
| 2 to 4 | 24% |
| more than 4 | 53% |

| Criteria | Average Rating |
| --- | :---: |
| Ease of use | 3.0 |
| Accuracy of the provided information | 2.1 |
| User interface | 2.8 |

The survey data can be found in the `performance_testing` folder as `Duke ChatBot_April 23, 2023_18.48.xlsx`.

&nbsp;
## Risks and Limitations

The Duke ChatBot has the following risks and limitations:
- The ChatBot is only able to answer questions about Pratt School of Engineering and its departments, programs, and courses. The pipeline is not able to answer questions about other schools and departments at Duke University.
- The ChatBot is only able to answer questions based on the information scraped from the website as on April 5, 2023. The pipeline is not able to answer questions about the latest updates on the website.
- The ChatBot can provide wrong answers to time sensitive questions if the data on the website was not updated as on April 5, 2023.

&nbsp;
## Project Structure
The project structure is as follows:
```
├── data                                        <- directory for project data (text data scraped from websites)
├── notebooks                                   <- directory to store any exploration notebooks used
├── performance_testing                         <- directory to store performance testing data
    ├── Duke ChatBot_April 23, 2023_18.48.xlsx  <- user survey data
    ├── test_answers_analysis.xlsx              <- analysis of the answers returned by the pipeline
    ├── test_answers.csv                        <- answers returned by the pipeline
    ├── test_questions.csv                      <- questions asked to the pipeline
├── scripts                                     <- directory for pipeline scripts or utility scripts
    ├── chatbot.py                              <- chatbot pipeline server script
    ├── chatgpt_qa.py                           <- chatgpt answer generator script
    ├── get_subpages.py                         <- script to get subpage urls of a website
    ├── helper_functions.py                     <- helper functions used in the pipeline
    ├── index_in_es.py                          <- script to index data in ElasticSearch
    ├── scrape.py                               <- script to scrape data from a website
    ├── t5_qa.py                                <- t5 answer generator script
    ├── testing.py                              <- script to generate answers for manual qualitative evaluation
├── .gitignore                                  <- git ignore file
├── config.json                                 <- config file to store api keys
├── LICENSE                                     <- license file
├── README.md                                   <- description of project and how to set up and run it
├── requirements.txt                            <- requirements file to document dependencies
```

&nbsp;
## References

- [Farm-Haystack](https://haystack.deepset.ai)
- [Dense Passage Retrieval](https://github.com/facebookresearch/DPR)
- [BM25 Retrieval](https://www.elastic.co/blog/practical-bm25-part-2-the-bm25-algorithm-and-its-variables)
- [HuggingFace Transformers](https://huggingface.co/transformers/)
- [Generative QA Using T5](https://huggingface.co/consciousAI/question-answering-generative-t5-v1-base-s-q-c)
- [ChatGPT API](https://platform.openai.com/docs/guides/chat)