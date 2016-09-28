import hazm
from nltk import bigrams, trigrams
from elasticsearch import Elasticsearch

from newsbot.settings import ELASTIC_URL

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


def sent_tokenize(text, num_char=-1):
    ret = hazm.sent_tokenize(text)
    if num_char == -1:
        return ret

    cnt = 0
    ret2 = []
    for item in ret:
        if cnt + len(item) > num_char:
            return ret2
        else:
            ret2.append(item)
            cnt += len(item)
    return ret2


def lemmatize(text):
    return lemmatizer.lemmatize(text)


def word_tokenize(text):
    return hazm.word_tokenize(text)


def bi_gram(text):
    bi_words = []
    words = word_tokenize(text)
    bi_tokens = set(bigrams(words))
    for item in bi_tokens:
        bi_words.append(item[0] + ' ' + item[1])
    return bi_words


def tri_gram(text):
    tri_words = []
    words = word_tokenize(text)
    tri_tokens = set(trigrams(words))
    for item in tri_tokens:
        tri_words.append(item[0] + ' ' + item[1] + ' ' + item[2])
    return tri_words


def per_to_eng(st):
    trans = {
        '۱': '1',
        '۲': '2',
        '۳': '3',
        '۴': '4',
        '۵': '5',
        '۶': '6',
        '۷': '7',
        '۸': '8',
        '۹': '9',
        '۰': '0',
    }
    ret = ''
    for i, item in enumerate(st):
        ret += trans[item]
    return ret
