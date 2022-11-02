#Creation of the index postcodes 
from datetime import datetime
from elasticsearch_dsl import Search
from elasticsearch import Elasticsearch
import requests, csv

es = Elasticsearch([{'host': 'localhost', 'port':9200}])

settings = {'settings': {"number_of_shards" : 3},
'mappings': {
    'properties': {
        'postcode_column': {'type': 'text'},
        'Latitude': {'type': 'float'},
        'Longitude': {'type': 'float'}
    }
}
}

es.indices.create(index='postcodes', body=settings)
print("index created")
