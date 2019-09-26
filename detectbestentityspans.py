import sys,os,json,re
import urllib.request
from elasticsearch import Elasticsearch
from fuzzywuzzy import fuzz
from itertools import groupby

def generate_ngrams(s, n):
    # Convert to lowercases
    #s = s.lower()
    
    # Replace all none alphanumeric characters with spaces
    #s = re.sub(r'[^a-zA-Z0-9\s]', ' ', s)
    
    # Break sentence in the token, remove empty tokens
    if not s:
        tokens = []
    else:
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
    _ents = re.findall( r'wd:(.*?) ', wikisparql)
    _rels = re.findall( r'wdt:(.*?) ',wikisparql)
    entities = ['http://wikidata.dbpedia.org/resource/'+ent for ent in _ents]
#    unit['relations'] = ['http://www.wikidata.org/entity/'+rel for rel in _rels]
    question = item['question']
    ngrammatchdict = {}
    for i in range(1,4):
        ngrams = generate_ngrams(question, i)
        for ngram in ngrams:
            #entities
            res = es.search(index="wikidataentitylabelindex01", body={"query":{"multi_match":{"query":ngram,"fields":["wikidataLabel"]}},"size":200})
            for idx,hit in enumerate(res['hits']['hits']):
                if hit['_source']['uri'] in entities:
                    if hit['_source']['uri'] in ngrammatchdict:
                        if idx < ngrammatchdict[hit['_source']['uri']]['esrank']:
                            ngrammatchdict[hit['_source']['uri']] = {'ngram':ngram,'esrank':idx}
                    else:
                        ngrammatchdict[hit['_source']['uri']] = {'ngram':ngram,'esrank':idx}
            #relations
            if len(ngram) < 3:
                continue
            inputjson = {'chunks': [{'chunk':ngram, 'class':'relation'}] }
            req = urllib.request.Request('http://localhost:8887/textMatch', data=json.dumps(inputjson).encode('utf8'),headers={'content-type': 'application/json'} )
            response = urllib.request.urlopen(req)
            response = json.loads(response.read())
            for idx,relurl in enumerate(response[0]['topkmatches']):
                if '_' in relurl:
                    relid = relurl.split('http://www.wikidata.org/entity/')[1].split('_')[0]
                    qualid = relurl.split('http://www.wikidata.org/entity/')[1].split('_')[1]
                    if relid in _rels and qualid in _rels:
                        if relurl in ngrammatchdict:
                            if idx < ngrammatchdict[relurl]['rank']:
                                ngrammatchdict[relurl] = {'ngram':ngram,'rank':idx}
                        else:
                            ngrammatchdict[relurl] = {'ngram':ngram,'rank':idx}
                else:
                    relid = relurl.split('http://www.wikidata.org/entity/')[1]
                    if relid in _rels:
                        if relurl in ngrammatchdict:
                            if idx < ngrammatchdict[relurl]['rank']:
                                ngrammatchdict[relurl] = {'ngram':ngram,'rank':idx}
                        else:
                            ngrammatchdict[relurl] = {'ngram':ngram,'rank':idx} 
             
    unit['uid'] = item['uid']
    unit['question'] = item['question']
    unit['spanmatch'] = ngrammatchdict
    spanarr.append(unit)
    #if len(unit['spanmatch']) == 0:
    print(iddx,item['uid'],unit,_ents,_rels)

f = open('ngramentityspanslcquad2.0.2.json','w')
f.write(json.dumps(spanarr,indent=4, sort_keys=True))
f.close()
