import sys,os,json,re
from elasticsearch import Elasticsearch
from fuzzywuzzy import fuzz
from itertools import groupby

def generate_ngrams(s, n):
    # Convert to lowercases
    #s = s.lower()
    
    # Replace all none alphanumeric characters with spaces
    #s = re.sub(r'[^a-zA-Z0-9\s]', ' ', s)
    
    # Break sentence in the token, remove empty tokens
    tokens = [token for token in s.split(" ") if token != ""]
    
    # Use the zip function to help us generate n-grams
    # Concatentate the tokens into ngrams and return
    ngrams = zip(*[tokens[i:] for i in range(n)])
    return [" ".join(ngram) for ngram in ngrams]


es = Elasticsearch()

d = json.loads(open('dataset/train.json').read())
spanarr = []
for iddx,item in enumerate(d):
    unit = {}
    wikisparql = item['sparql_wikidata']
    _rels = re.findall( r'wdt:(.*?) ',wikisparql)
    unit['relations'] = ['http://www.wikidata.org/entity/'+rel for rel in _rels]
    question = item['question']
    ngrammatchdict = {}
    for i in range(1,4):
        ngrams = generate_ngrams(question, i)
        for ngram in ngrams:
            res = es.search(index="wikidataentitylabelindex01", body={"query":{"multi_match":{"query":ngram,"fields":["wikidataLabel"]}},"size":200})
            for idx,hit in enumerate(res['hits']['hits']):
                if hit['_source']['uri'] in entities:
                    if hit['_source']['uri'] in ngrammatchdict:
                        if idx < ngrammatchdict[hit['_source']['uri']]['esrank']:
                            ngrammatchdict[hit['_source']['uri']] = {'ngram':ngram,'esrank':idx}
                    else:
                        ngrammatchdict[hit['_source']['uri']] = {'ngram':ngram,'esrank':idx}
    unit['uid'] = item['uid']
    unit['question'] = item['question']
    unit['entityspanmatch'] = ngrammatchdict
    spanarr.append(unit)
    if len(unit['entityspanmatch']) == 0:
        print(item['uid'],unit)

f = open('ngramentityspanslcquad2.0.2.json','w')
f.write(json.dumps(spanarr,indent=4, sort_keys=True))
f.close()
