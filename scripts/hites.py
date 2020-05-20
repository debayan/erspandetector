import sys,os,json,re
from elasticsearch import Elasticsearch

es = Elasticsearch()

ngram = sys.argv[1]

res = es.search(index="wikidataentitylabelindex01", body={"query":{"multi_match":{"query":ngram,"fields":["wikidataLabel"]}},"size":200})
for rec in res['hits']['hits']:
    print(rec['_source'])
