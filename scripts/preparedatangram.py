import sys
import json
from elasticsearch import Elasticsearch
from fuzzywuzzy import fuzz
import urllib.request
import re
from textblob import TextBlob

postags = ["CC","CD","DT","EX","FW","IN","JJ","JJR","JJS","LS","MD","NN","NNS","NNP","NNPS","PDT","POS","PRP","PRP$","RB","RBR","RBS","RP","SYM","TO","UH","VB","VBD","VBG","VBN","VBP","VBZ","WDT","WP","WP$","WRB"]
es = Elasticsearch()

def givewordvectors(question):
    q = question
    #q = re.sub("\s*\?", "", q.strip())
    result = TextBlob(q)
    chunks = result.tags
    fuzzscores = []
    wordvectors = []
    chunkswords = []
    for chunk,word in zip(chunks,q.split(' ')):
        chunkswords.append((chunk,word))
    for idx,chunkwordtuple in enumerate(chunkswords):
        word = chunkwordtuple[1]
        body = {'chunk': word}
        jsondata = json.dumps(body)
        jsondataasbytes = jsondata.encode('utf-8')
        req = urllib.request.Request("http://localhost:8887/ftwv")
        req.add_header('Content-Length', len(jsondataasbytes))
        req.add_header('Content-Type', 'application/json; charset=utf-8')
        response = urllib.request.urlopen(req, jsondataasbytes)
        embedding = json.loads(response.read().decode('utf8'))
        wordvector = embedding
        #n-1,n
        if idx > 0:
            word = chunkswords[idx-1][1] + ' ' + chunkswords[idx][1]
            esresult = es.search(index="wikidataentitylabelindex01", body={"query":{"multi_match":{"query":word,"fields":["wikidataLabel"]}},"size":10})
            esresults = esresult['hits']['hits']
            if len(esresults) > 0:
                for esresult in esresults:
                    wordvector +=  [fuzz.ratio(word, esresult['_source']['wikidataLabel'])/100.0, fuzz.partial_ratio(word, esresult['_source']['wikidataLabel'])/100.0, fuzz.token_sort_ratio(word, esresult['_source']['wikidataLabel'])/100.0]
                wordvector += (10-len(esresults)) * [0.0,0.0,0.0]
            else:
                wordvector +=  10*[0.0,0.0,0.0]
        else:
            wordvector +=  10*[0.0,0.0,0.0]
        #n
        word = chunkwordtuple[1] 
        esresult = es.search(index="wikidataentitylabelindex01", body={"query":{"multi_match":{"query":word,"fields":["wikidataLabel"]}},"size":10})
        esresults = esresult['hits']['hits']
        if len(esresults) > 0:
            for esresult in esresults:
                wordvector +=  [fuzz.ratio(word, esresult['_source']['wikidataLabel'])/100.0, fuzz.partial_ratio(word, esresult['_source']['wikidataLabel'])/100.0, fuzz.token_sort_ratio(word, esresult['_source']['wikidataLabel'])/100.0]
            wordvector += (10-len(esresults)) * [0.0,0.0,0.0]
        else:
            wordvector +=  10*[0.0,0.0,0.0]
        #n,n+1
        if idx < len(chunkswords)-1:
            word = chunkswords[idx][1] + ' ' + chunkswords[idx+1][1]
            esresult = es.search(index="wikidataentitylabelindex01", body={"query":{"multi_match":{"query":word,"fields":["wikidataLabel"]}},"size":10})
            esresults = esresult['hits']['hits']
            if len(esresults) > 0:
                for esresult in esresults:
                    wordvector +=  [fuzz.ratio(word, esresult['_source']['wikidataLabel'])/100.0, fuzz.partial_ratio(word, esresult['_source']['wikidataLabel'])/100.0, fuzz.token_sort_ratio(word, esresult['_source']['wikidataLabel'])/100.0]
                wordvector += (10-len(esresults)) * [0.0,0.0,0.0]
            else:
                wordvector +=  10*[0.0,0.0,0.0]
        else:
            wordvector +=  10*[0.0,0.0,0.0]
        #n-1,n,n+1
        if idx > 0 and idx < len(chunkswords)-1:
            word = chunkswords[idx-1][1] + ' ' + chunkswords[idx][1] + ' ' + chunkswords[idx+1][1]
            esresult = es.search(index="wikidataentitylabelindex01", body={"query":{"multi_match":{"query":word,"fields":["wikidataLabel"]}},"size":10})
            esresults = esresult['hits']['hits']
            if len(esresults) > 0:
                for esresult in esresults:
                    wordvector +=  [fuzz.ratio(word, esresult['_source']['wikidataLabel'])/100.0, fuzz.partial_ratio(word, esresult['_source']['wikidataLabel'])/100.0, fuzz.token_sort_ratio(word, esresult['_source']['wikidataLabel'])/100.0]
                wordvector += (10-len(esresults)) * [0.0,0.0,0.0]
            else:
                wordvector +=  10*[0.0,0.0,0.0]
        else:
            wordvector +=  10*[0.0,0.0,0.0]
        posonehot = len(postags)*[0.0]
        posonehot[postags.index(chunk[1])] = 1
        wordvector += posonehot
        if len(wordvector) != 456:
            print(len(wordvector))
            print("word vec len wrong")
            sys.exit(1)
        wordvectors.append(wordvector)
    return wordvectors


d = json.loads(open('ngramentitylabelled2.json').read())
items = []
for item in d:
    wordvectors = givewordvectors(item['question'])
    iu = {}
    iu['question'] = item['question']
    iu['wordvectors'] = wordvectors
    iu['erspan'] = item['spanlabelled']
    items.append(iu)
f = open('entityonlywordvecsngramsparaphrased3.json','w')
f.write(json.dumps(items,sort_keys=True,indent=4, separators=(',', ': ')))
f.close()

#d = json.loads(open('lcqspans.json').read())
#items = []
#for item in d:
#    wordvectors = givewordvectors(item['text'])
#    iu = {}
#    iu['question'] = item['text']
#    iu['wordvectors'] = wordvectors
#    iu['erspan'] = item['span']
#    items.append(iu)
#print('phase 1 done')
#d = json.loads(open('wordvectorstraintestngram.json').read())
#for item in d:
#    wordvectors = givewordvectors(item['question'])
#    iu = {}
#    iu['question'] = item['question']
#    iu['wordvectors'] = wordvectors
#    iu['erspan'] = item['erspan']
#    items.append(iu)
#
#f = open('wordvecsngramsparaphrased1.json','w')
#f.write(json.dumps(items,sort_keys=True,indent=4, separators=(',', ': ')))
#f.close()
