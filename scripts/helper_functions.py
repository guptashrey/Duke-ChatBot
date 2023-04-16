# library imports
from haystack.document_stores import ElasticsearchDocumentStore

def get_elasticsearch_document_store(host, username="", password="", index="document"):
    
    '''
    Returns an ElasticsearchDocumentStore object.

    Args:
        host (str): Hostname of the Elasticsearch instance.
        username (str): Username of the Elasticsearch instance.
        password (str): Password of the Elasticsearch instance.
        index (str): Name of the Elasticsearch document index.

    Returns:
        ElasticsearchDocumentStore: ElasticsearchDocumentStore object.
    '''

    # create ElasticsearchDocumentStore
    document_store = ElasticsearchDocumentStore(
        host=host,
        username=username,
        password=password,
        index=index,
        similarity="dot_product",
        embedding_dim=768,
    )
    
    return document_store