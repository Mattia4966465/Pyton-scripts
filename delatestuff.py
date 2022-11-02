from elasticsearch import Elasticsearch
import json
import csv

es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

#es.indices.delete(index='taxi', ignore=[400, 404])
#es.indices.delete(index='postcodes', ignore=[400, 404])
#es.indices.delete(index='deliveries', ignore=[400, 404])
#es.indices.delete(index='distances', ignore=[400, 404])
#es.indices.delete(index='prova_1', ignore=[400, 404])

print('index delated')
