import os,sys,json
from itertools import groupby

d = json.loads(open('ngramentityspanslcquad2.0.2.json').read())
finalspans = []
for item in d:
    question = item['question']
    if not question:
        continue
    print(question)
    qblock = [0]*len(question)
    qspantokens = []
    for url,span in item['spanmatch'].items():
        print(url,span)
        startpos = question.find(span['ngram'])
        if len(span['ngram']) < 3:
            continue
        print(startpos)
        if '/entity/' in url:
            qblock[startpos:startpos+len(span['ngram'])] = [2] * len(span['ngram'])
        if '/resource/' in url:
            qblock[startpos:startpos+len(span['ngram'])] = [1] * len(span['ngram'])
        for i in range(len(question)):
            if question[i] == ' ':
                qblock[i] = -1
    qspantokens = [x[0] for x in groupby(qblock)]
    print(qspantokens)
    qspantokens = list(filter(lambda a: a != -1, qspantokens))
    print(qspantokens)
    finalspans.append({'question':question, 'spanlabelled':qspantokens})

f = open('ngramentitylabelled2.json','w')
f.write(json.dumps(finalspans, indent=4, sort_keys=True))
f.close()
        
