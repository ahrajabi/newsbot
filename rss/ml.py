from newsbot.settings import ELASTIC_URL
from elasticsearch import Elasticsearch
import hazm

norm = hazm.Normalizer()
lemmatizer = hazm.Lemmatizer()

es = Elasticsearch([ELASTIC_URL])

def elastic_search_entity(query):
    body = {
        "search_request": {
            "fields": ["news_title", "news_body"],
            "query": {"match": {"_all": query}},
            "size": 100
        },

        "query_hint": query,
        "field_mapping": {
            "title": ["fields.news_title"],
            "content": ["fields.news_body"]
        }
    }
    r = es.search(index='news', body=body)
    print(r)
    return r['hits']['hits']


def normalize(text):
    return norm.normalize(text)


def sent_tokenize(text):
    return hazm.sent_tokenize(text)


def lemmatize(text):
    return lemmatizer.lemmatize(text)

