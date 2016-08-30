import datetime
from newsbot.settings import ELASTIC_URL
from elasticsearch import Elasticsearch, helpers

from rss.models import News

es = Elasticsearch([ELASTIC_URL])


def save_to_elastic_search(obj):
    try:
        body = {
            'news_body': obj.body,
            'summary': obj.summary,
            'title': obj.base_news.title,
            'published_date': obj.base_news.published_date

        }
        es.index(index='news', doc_type='new', id=obj.id, body=body, request_timeout=50)
        return True
    except Exception:
        return False


def postgres_news_to_elastic():
    start_time = datetime.datetime.now()
    for obj in News.objects.filter(base_news__save_to_elastic=False):
        print('HI')
        if save_to_elastic_search(obj):
            obj.base_news.save_to_elastic = True
            obj.base_news.save()

    print(datetime.datetime.now() - start_time)


def source_generator():
    for obj in News.objects.filter(base_news__save_to_elastic=False):
        fields_keys = ('news_body', 'summary', 'title', 'published_date')
        fields_values = (obj.body, obj.summary, obj.base_news.title, obj.base_news.published_date)
        source = dict(zip(fields_keys, fields_values))
        # TODO below line msut execute after bulk save to elastic function
        obj.base_news.save_to_elastic = True
        obj.base_news.save()
        yield obj.id, source


def bulk_save_to_elastic():
    start_time = datetime.datetime.now()
    k = ({'_index': 'news2', '_type': 'new', '_id': idx, "_source": source}
         for idx, source in source_generator())
    helpers.bulk(es, k)
    print(datetime.datetime.now() - start_time)


def elastic_search_entity(query):
    body = {
        "query": {
            "multi_match": {
                "query": query,
                "type": "phrase",
                "fields": ["news_title^2", "news_body"]
            }
        },
        "fields": ['published_date', '_uid', 'news_body'],
        "sort": [{"published_date": {"order": "desc"}}]
    }
    r = es.search(index='news', body=body)
    for hit in r['hits']['hits']:
        print(hit)
    return r['hits']['hits']

def more_like_this(query, number):
    body = {
        "query": {
            "more_like_this": {
                "fields": ["title", "news_body"],
                "like": query,
                "min_term_freq": 1,
            "max_query_terms": 12
            }
        },
        'size': number,
    }
    r = es.search(index='news', body=body)
    news_id = [item['_id'] for item in r['hits']['hits']]
    return news_id

