import datetime
from django.conf import settings
from elasticsearch import Elasticsearch
import six
from rss.models import News, BaseNews

es = Elasticsearch([settings.ELASTIC_URL])


def save_to_elastic_search(obj):
    try:
        body = {
            'title': obj.base_news.title,
            'summary': obj.summary,
            'body': obj.body,
            'published_date': obj.base_news.published_date

        }
        es.index(index=settings.ELASTIC_NEWS['index'], doc_type=settings.ELASTIC_NEWS['doc_type'], id=obj.id, body=body,
                 request_timeout=50)
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
    for obj in News.objects.filter(base_news__save_to_elastic=False)[0:500]:
        fields_keys = ('body', 'summary', 'title', 'published_date')
        fields_values = (obj.body, obj.summary, obj.base_news.title, obj.base_news.published_date)
        source = dict(zip(fields_keys, fields_values))
        # TODO below line msut execute after bulk save to elastic function
        obj.base_news.save_to_elastic = True
        obj.base_news.save()
        yield obj.id, source


def entity_validation_search(query, size=settings.MIN_HITS_ENTITY_VALIDATION):
    body = {
        "query": {
            "multi_match": {
                "query": query,
                "type": "phrase",
                "fields": ["title", "body", "summary"]
            }
        },
        "fields": ['published_date', '_uid', 'body'],
        "size": size
    }
    r = es.search(index=settings.ELASTIC_NEWS['index'], body=body, request_timeout=20)
    print(r['hits']['hits'])
    return r['hits']['hits']


def elastic_search_entity(query, size, offset=0):
    today = datetime.datetime.now()
    last_weak = today - datetime.timedelta(days=7)
    body = {
        "query": {
            "multi_match": {
                "query": query,
                "type": "phrase",
                "fields": ["title^2", "body"]
            }
        },
        "fields": ['published_date', '_uid', 'body'],
        # "sort": [{"published_date": {"order": "desc"}}],
        "from": offset,
        "size": size,
        "filter": {
            "range": {
                "published_date": {
                    "gte": last_weak,
                    "lte": today
                }
            }
        }

    }
    r = es.search(index=settings.ELASTIC_NEWS['index'], body=body, request_timeout=20)
    for x in r['hits']['hits']: print(x['_score'], x['_id'])
    return r['hits']['hits']


def highlights_news(query):
    number = 10
    body = {
        "query": {
            "filtered": {
                "query": {
                    "more_like_this": {
                        "fields": ["summary", "title"],
                        "like": query,
                        "min_term_freq": 1,
                        "max_query_terms": 12
                    }
                },
                "filter": {
                    "range": {
                        "published_date": {
                            "gte": "now-20h"
                        }
                    }
                }
            }
        },
        'size': number,
        'fields': ['title'],
    }

    r = es.search(index=settings.ELASTIC_NEWS['index'], body=body)
    for item in r['hits']['hits']:
        if item['_score'] > 0.5:
            news = News.objects.get(id=item['_id'])
            if news.importance:
                news.importance += item['_score']
            else:
                news.importance = item['_score']
            news.save()
    return r


def more_like_this(query, number):
    body = {
        "query": {
            "more_like_this": {
                "fields": ["title", "body"],
                "like": query,
                "min_term_freq": 1,
                "max_query_terms": 12
            }
        },
        'size': number,
    }

    r = es.search(index=settings.ELASTIC_NEWS['index'], body=body)
    news_id = [item['_id'] for item in r['hits']['hits']]
    return news_id


def similar_news_to_query(query, size=10, start_time=7, end_time='now', offset=0, sort='_score'):
    ''' return most similar docs to query where published in range (today - days, today), sorted by score'''
    # TODO limit results that have score more than thresholde
    if not isinstance(start_time, six.string_types):
        start_time = start_time.strftime('%Y-%m-%dT%H:%M:%S')

    if not isinstance(end_time, six.string_types):
        end_time = end_time.strftime('%Y-%m-%dT%H:%M:%S')

    body = {
        "sort": [
            {sort: {"order": "desc"}},
        ],
        "query": {
            "multi_match": {
                "query": query,
                "fields": ["title^2", "body"],
                #                "fuzziness": "AUTO"
            }
        },
        "fields": ['published_date', '_uid', 'body'],
        "size": size,
        "from": offset,

        "filter": {
            "range": {
                "published_date": {
                    "gte": start_time,
                    "lte": end_time
                }
            }
        }
    }

    r = es.search(index=settings.ELASTIC_NEWS['index'], body=body, request_timeout=20)
    return r


def news_with_terms(entity_list, size=10, start_time='now-3h', end_time='now', offset=0, sort='_score'):
    if not isinstance(start_time, six.string_types):
        start_time = start_time.strftime('%Y-%m-%dT%H:%M:%S')

    if not isinstance(end_time, six.string_types):
        end_time = end_time.strftime('%Y-%m-%dT%H:%M:%S')

    print(start_time)

    mquery = []
    for entity_item in entity_list:
        should = []

        if len(entity_item.get_positive()) > 0:
            should = [{"match_phrase": {"_all": item}} for item in entity_item.get_positive()],

        must = []
        if len(entity_item.get_synonym()) > 0:
            must = [{"match_phrase": {"_all": item}} for item in entity_item.get_synonym()],
            must = {
                "bool": {
                    "should": must,
                    "minimum_should_match": 1
                }
            }

        must_not = []
        if len(entity_item.get_negative()) > 0:
            must_not = [{"match_phrase": {"_all": item}} for item in entity_item.get_negative()],

        mquery.append({
            "bool": {
                "should": should,
                "must": must,
                "must_not": must_not,
            }
        })

    body = {
        "sort": [
            {sort: {"order": "desc"}},
        ],
        "query": {
            "filtered": {
                "query": {
                    "bool": {
                        "should": mquery,
                        "minimum_should_match": 1
                    }
                },
                "filter": {
                    "range": {
                        "published_date": {
                            "gte": start_time,
                            "lte": end_time
                        }
                    }
                }
            }
        },
        "size": size,
        "from": offset
    }

    r = es.search(index=settings.ELASTIC_NEWS['index'], body=body, request_timeout=20)
    return r


def list_missed_elastic(li):
    if len(li) == 0:
        return list()
    body = {
        "docs": [{"_id": str(item), "_source": "false"} for item in li]
    }
    ret = es.mget(index=settings.ELASTIC_NEWS['index'], doc_type=settings.ELASTIC_NEWS['doc_type'], body=body)

    missed = []
    for item in ret['docs']:
        if not item['found']:
            missed.append(int(item['_id']))
    return missed


def miss_elastic():
    cnt = 0
    li = []
    all_missed = []
    for item in News.objects.filter(base_news__complete_news=True):
        cnt += 1
        li.append(item.id)
        if cnt % 500 == 0:
            print("YES", cnt)
            all_missed.extend(list_missed_elastic(li))
            li = []
    all_missed.extend(list_missed_elastic(li))
    return all_missed


def repair_missed_elastic():
    start_time = datetime.datetime.now()

    missed_list = miss_elastic()
    cnt = 0
    for item in missed_list:
        cnt += 1
        s = News.objects.get(id=item)
        s.base_news.save_to_elastic = False
        s.base_news.save()
        if cnt % 5000 == 0:
            print('Wait', cnt)
    print('Repair', datetime.datetime.now() - start_time)


def news_elastic_setup():
    index = settings.ELASTIC_NEWS['index']

    body = {
        "settings": settings.NEWS_SETTING,
        "mappings": settings.NEWS_MAPPING
    }

    if not es.indices.exists(index):
        es.indices.create(index, body=body)
        return True

    es.indices.close(index)
    es.indices.put_mapping(index=index, doc_type=settings.ELASTIC_NEWS['doc_type'], body=settings.NEWS_MAPPING)
    es.indices.put_settings(index=index, body=settings.NEWS_SETTING['index'])
    es.indices.open(index)
    es.indices.put_settings(index=index, body={'index': settings.ELASTIC_NEWS['settings']})







    #
    # {
    # 	"query":{
    #     	"filtered" :{
    # 	    	"query":{
    #     	    	"match_all" :{}
    #         	},
    # 	    	"filter": {
    #     	    	"range" :{
    #         	    	"published_date" :{
    #             	    	"gt": "now-100h"
    #                 	}
    # 	            }
    #     	    }
    #     	}
    #     },
    # 	"aggs": {
    #     	"trend_tags" :{
    #         	"date_histogram": {
    #             	"field": "published_date",
    #                 "interval": "1h",
    #                 "format": "yyyy-MM-dd hh-mm",
    #                 "min_doc_count":0
    #             },
    #             "aggs":{
    #         		"items_items": {
    #             		"significant_terms":{
    #                 		"field":"title"
    #                 	}
    # 				}
    #             }
    #         }
    #     }
    # }
