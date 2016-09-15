import datetime
from newsbot.settings import ELASTIC_URL
from elasticsearch import Elasticsearch

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


def elastic_search_entity(query, size, offset=0):
    body = {
        "query": {
            "multi_match": {
                "query": query,
                "type": "phrase",
                "fields": ["title^2", "news_body"]
            }
        },
        "fields": ['published_date', '_uid', 'news_body'],
        "sort": [{"published_date": {"order": "desc"}}],
        "from": offset,
        "size": size
    }
    r = es.search(index='news', body=body, request_timeout=20)
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


def similar_news_to_query(query, size, days, offset=0):
    ''' return most similar docs to query where published in range (today - days, today), sorted by score'''
    # TODO limit results that have score more than thresholde
    today = datetime.datetime.now()
    another_day = today - datetime.timedelta(days=days)
    body = {
        "query": {
            "multi_match": {
                "query": query,
                "fields": ["title^2", "news_body"],
                "fuzziness": "AUTO"
            }
        },
        "fields": ['published_date', '_uid', 'news_body'],
        "size": size,
        "from": offset,

        "filter": {
            "range": {
                "published_date": {
                    "gte": another_day,
                    "lte": today
                }
            }
        }
    }

    r = es.search(index='news', body=body, request_timeout=20)
    for hit in r['hits']['hits']:
        print(hit)
    return [hit['_id'] for hit in r['hits']['hits']]
