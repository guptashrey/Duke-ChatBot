# Duke-ChatBot

## Project Overview
Welcome to the Duke University Chatbot!

This cutting-edge AI-powered tool is specifically designed to make the lives of Duke University students easier by providing quick and accurate answers to their questions. Powered by a robust chatbot framework, advanced natural language processing, and machine learning technologies, this chatbot is designed to interact with website visitors, understand the semantics of questions asked, and deliver meaningful and immediate answers. Say goodbye to time-consuming searches and hello to a convenient and efficient way to get information about Duke University!

Duke Chatbot is designed to address the following pain points:

Information overload: Duke University students may often feel overwhelmed by the vast amount of information available about the university, such as campus locations, resources, events, and policies. Your chatbot can serve as a one-stop source of accurate and up-to-date information, helping students easily find what they need without sifting through multiple sources.

Time-consuming searches: Students may spend significant time searching for answers to common questions, such as academic deadlines, financial aid information, or campus services. Your chatbot can provide quick responses, saving students time and effort by delivering immediate answers to their inquiries in a conversational manner.

User-friendly interaction: Traditional methods of obtaining information, such as browsing websites or sending emails, may not always be user-friendly or intuitive for students. Your chatbot can provide a conversational and user-friendly interface, making it easy for students to ask questions in a natural language format and receive prompt and relevant responses.

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


## Running the ChatBot

## Project Structure