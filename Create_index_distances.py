#Creation of the index distances
from datetime import datetime
from elasticsearch_dsl import Search
from elasticsearch import Elasticsearch
import requests, csv

es = Elasticsearch([{'host': 'localhost', 'port':9200}])

settings = { 'settings': {"number_of_shards" : 3},
'mappings': {
    'properties': {
        'src': {'type': 'keyword'},
        'dest': {'type': 'keyword'},
        'meters': {'type': 'float'},
        'seconds': {'type': 'float'}
    }
}
}

es.indices.create(index='distances', body=settings)
es.indices.put_settings(index='distances',
                    body={'index' : {'max_result_window': 120000}})
print("index created")
