import sys
import json
from elasticsearch import Elasticsearch
from fuzzywuzzy import fuzz
import urllib.request
import re
from textblob import TextBlob

d = json.loads(open('erspans.json').read())
postags = ["CC","CD","DT","EX","FW","IN","JJ","JJR","JJS","LS","MD","NN","NNS","NNP","NNPS","PDT","POS","PRP","PRP$","RB","RBR","RBS","RP","SYM","TO","UH","VB","VBD","VBG","VBN","VBP","VBZ","WDT","WP","WP$","WRB"]
items = []
es = Elasticsearch()
for item in d:
    #print(item)
    q = item['question']
    erspan = item['erspan']
    q = re.sub("\s*\?", "", q.strip())
    result = TextBlob(q)
    chunks = result.tags
    fuzzscores = []
    wordvectors = []
    chunkswords = []
    for chunk,word in zip(chunks,q.split(' ')):
        chunkswords.append((chunk,word))
    for idx,chunkwordtuple in enumerate(chunkswords):
        word = chunkwordtuple[1]
        body = {'phrase': word}
        jsondata = json.dumps(body)
        jsondataasbytes = jsondata.encode('utf-8')
        req = urllib.request.Request("http://localhost:8888/ftwv")
        req.add_header('Content-Length', len(jsondataasbytes))
        req.add_header('Content-Type', 'application/json; charset=utf-8')
        response = urllib.request.urlopen(req, jsondataasbytes)
        embedding = json.loads(response.read().decode('utf8'))
        wordvector = embedding
        #n 
        esresult = es.search(index="dbentityindex11", body={"query":{"multi_match":{"query":word,"fields":["wikidataLabel", "dbpediaLabel^1.5"]}},"size":10})
        esresults = esresult['hits']['hits']
        if len(esresults) > 0:
            for esresult in esresults:
                if 'dbpediaLabel' in esresult['_source']:
                    wordvector +=  [fuzz.ratio(word, esresult['_source']['dbpediaLabel'])/100.0, fuzz.partial_ratio(word, esresult['_source']['dbpediaLabel'])/100.0, fuzz.token_sort_ratio(word, esresult['_source']['dbpediaLabel'])/100.0]
                if 'wikidataLabel' in esresult['_source']:
                    wordvector +=  [fuzz.ratio(word, esresult['_source']['wikidataLabel'])/100.0, fuzz.partial_ratio(word, esresult['_source']['wikidataLabel'])/100.0, fuzz.token_sort_ratio(word, esresult['_source']['wikidataLabel'])/100.0]
            wordvector += (10-len(esresults)) * [0.0,0.0,0.0]
        else:
            wordvector +=  10*[0.0,0.0,0.0]
        posonehot = len(postags)*[0.0]
        posonehot[postags.index(chunk[1])] = 1
        wordvector += posonehot
        if len(wordvector) != 366:
            print(len(wordvector))
            print("word vec len wrong")
            sys.exit(1)
        wordvectors.append(wordvector)
    iu = {}
    iu['question'] = item['question']
    iu['wordvectors'] = wordvectors
    iu['erspan'] = erspan
    items.append(iu)

for item in d:
    #print(item)
    q = item['question'].lower()
    erspan = item['erspan']
    q = re.sub("\s*\?", "", q.strip())
    result = TextBlob(q)
    chunks = result.tags
    fuzzscores = []
    wordvectors = []
    chunkswords = []
    for chunk,word in zip(chunks,q.split(' ')):
        chunkswords.append((chunk,word))
    for idx,chunkwordtuple in enumerate(chunkswords):
        word = chunkwordtuple[1]
        body = {'phrase': word}
        jsondata = json.dumps(body)
        jsondataasbytes = jsondata.encode('utf-8')
        req = urllib.request.Request("http://localhost:8888/ftwv")
        req.add_header('Content-Length', len(jsondataasbytes))
        req.add_header('Content-Type', 'application/json; charset=utf-8')
        response = urllib.request.urlopen(req, jsondataasbytes)
        embedding = json.loads(response.read().decode('utf8'))
        wordvector = embedding
        esresult = es.search(index="dbentityindex11", body={"query":{"multi_match":{"query":word,"fields":["wikidataLabel", "dbpediaLabel^1.5"]}},"size":10})
        esresults = esresult['hits']['hits']
        if len(esresults) > 0:
            for esresult in esresults:
                if 'dbpediaLabel' in esresult['_source']:
                    wordvector +=  [fuzz.ratio(word, esresult['_source']['dbpediaLabel'])/100.0, fuzz.partial_ratio(word, esresult['_source']['dbpediaLabel'])/100.0, fuzz.token_sort_ratio(word, esresult['_source']['dbpediaLabel'])/100.0]
                if 'wikidataLabel' in esresult['_source']:
                    wordvector +=  [fuzz.ratio(word, esresult['_source']['wikidataLabel'])/100.0, fuzz.partial_ratio(word, esresult['_source']['wikidataLabel'])/100.0, fuzz.token_sort_ratio(word, esresult['_source']['wikidataLabel'])/100.0]
            wordvector += (10-len(esresults)) * [0.0,0.0,0.0]
        else:
            wordvector +=  10*[0.0,0.0,0.0]
        posonehot = len(postags)*[0.0]
        posonehot[postags.index(chunk[1])] = 1
        wordvector += posonehot
        if len(wordvector) != 366:
            print("word vec len wrong")
            sys.exit(1)
        wordvectors.append(wordvector)
    iu = {}
    iu['question'] = item['question'].lower()
    iu['wordvectors'] = wordvectors
    iu['erspan'] = erspan
    items.append(iu)
 
f = open('wordvectorstraintest.json','w')
f.write(json.dumps(items))
f.close()
