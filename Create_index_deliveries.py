#Creation of the index deliveries
from datetime import datetime
from elasticsearch_dsl import Search
from elasticsearch import Elasticsearch
import requests, csv

es = Elasticsearch([{'host': 'localhost', 'port':9200}])

settings = { 'settings': {"number_of_shards" : 3},
'mappings': {
    'properties': {
        'deliveries_datetime': {'type': 'date', "format": 'yyyy-MM-dd HH:mm'},
        'postcodes_column': {'type': 'keyword'}
    }
}
}

es.indices.create(index='deliveries', body=settings)
es.indices.put_settings(index='deliveries',
                    body={'index' : {
                        'max_result_window': 800000
                    }})
print("index created")
