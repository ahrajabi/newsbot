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
        es.index(index=settings.ELASTIC_NEWS, doc_type='new', id=obj.id, body=body, request_timeout=50)
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


def elastic_search_entity(query, size, offset=0):
    body = {
        "query": {
            "multi_match": {
                "query": query,
                "type": "phrase",
                "fields": ["title^2", "body"]
            }
        },
        "fields": ['published_date', '_uid', 'body'],
        "sort": [{"published_date": {"order": "desc"}}],
        "from": offset,
        "size": size
    }
    r = es.search(index=settings.ELASTIC_NEWS, body=body, request_timeout=20)
    return r['hits']['hits']


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

    r = es.search(index=settings.ELASTIC_NEWS, body=body)
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
                "fields": ["title^2", "body"],
                "fuzziness": "AUTO"
            }
        },
        "fields": ['published_date', '_uid', 'body'],
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

    r = es.search(index=settings.ELASTIC_NEWS, body=body, request_timeout=20)
    return [hit['_id'] for hit in r['hits']['hits']]


def news_with_terms(terms_list, size=10, start_time='now-3h', end_time='now', offset=0):
    if not isinstance(start_time, six.string_types):
        start_time = start_time.strftime('%Y-%m-%dT%H:%M:%S')

    if not isinstance(end_time, six.string_types):
        end_time = end_time.strftime('%Y-%m-%dT%H:%M:%S')

    print(start_time)
    body = {
        "query": {
            "filtered": {
                "query": {
                    "bool": {
                        "should": [{"match_phrase": {"_all": item}} for item in terms_list]
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
    print(size, offset, start_time, end_time, terms_list)
    r = es.search(index=settings.ELASTIC_NEWS, body=body, request_timeout=20)
    return r


def list_missed_elastic(li):
    if len(li) == 0:
        return list()
    BODY = {
            "docs" : [{"_id": str(item), "_source": "false"} for item in li]
        }
    ret = es.mget(index='news', doc_type='new', body=BODY)

    missed = []
    for item in ret['docs']:
        missed.append(int(item['_id']))
    return missed


def miss_elastic():
    cnt = 0
    li = []
    all_missed = []
    for item in BaseNews.objects.filter(complete_news=True, save_to_elastic=True):
        cnt += 1
        li.append(item.id)
        if cnt % 5000 == 0:
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
        s = BaseNews.objects.get(id=item)
        s.save_to_elastic = False
        s.save()
        if cnt % 5000 == 0:
            print('Wait', cnt)
    print('Repair', datetime.datetime.now() - start_time)



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