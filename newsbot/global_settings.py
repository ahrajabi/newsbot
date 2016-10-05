SAMPLE_NEWS_COUNT = 3
MIN_HITS_ENTITY_VALIDATION = 3
NEWS_PER_PAGE = 5
DAYS_FOR_SEARCH_NEWS = 40
MAIN_BUTTONS = [
    ('لیست خبرها', 'newslist_command'),
    ('اخبار زنده', 'live_command'),
    ('توقف اخبار زنده', 'stoplive_command'),
    ('اخبار ویژه', 'special_command'),
    ('راهنمایی', 'help_command'),
]

ELASTIC_NEWS = {
    'index': "newnew",
    'doc_type': "new",
    'settings': {
        "number_of_replicas": 0,
    }
}

NEWS_MAPPING = {
    ELASTIC_NEWS['doc_type']: {
        "properties": {
            "title": {
                "type": "string",
                "analyzer": "persian_shingle"
            },
            "summary": {
                "type": "string",
                "analyzer": "persian_shingle"
            },
            "body": {
                "type": "string",
                "analyzer": "persian_shingle"
            }

        }
    }
}

NEWS_SETTING = {
    "index": {
        "analysis": {
            "char_filter": {
                "zero_width_spaces": {
                    "type": "mapping",
                    "mappings": ["\\u200C=> "]
                }
            },
            "filter": {
                "persian_stop": {
                    "type": "stop",
                    "stopwords": "_persian_"
                },
                "shingle-filter": {
                    "type": "shingle",
                    "min_shingle_size": 2,
                    "max_shingle_size": 4
                }
            },
            "analyzer": {
                "persian_shingle": {
                    "tokenizer": "standard",
                    "char_filter": ["zero_width_spaces"],
                    "filter": [
                        "lowercase",
                        #                        "arabic_normalization",
                        #                        "persian_normalization",
                        "persian_stop",
                        "shingle-filter"
                    ]
                }
            }
        }
    }
}
