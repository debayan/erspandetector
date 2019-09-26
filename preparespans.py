import sys,json,re
from itertools import groupby

d = json.loads(open('lcquad.json').read())

items = []

for item in d:
    q = item['question']
    #print(q)
    q = re.sub("\s*\?", "", q.strip())
    #print(q)
    qspan = [0]*len(q)
    for entity in item['entity mapping']:
        if entity['matchedBy'] != 'miss':
            beg = q.find(entity["label"])
            if beg == -1:
                continue
            end = beg + len(entity["label"])
            #span = pred["seq"]
            #beg,end = span.split(',')
            #beg,end = int(beg),int(end)
            #if beg == -1:
            #    continue
            qspan[beg:end] = [1] * len(entity["label"]) #entity
    for pred in item['predicate mapping']:
        if pred['mappedBy'] != 'miss':
            beg = q.find(pred["label"])
            if beg == -1:
                continue
            end = beg + len(pred["label"])
            #span = pred["seq"]
            #beg,end = span.split(',')
            #beg,end = int(beg),int(end)
            #if beg == -1:
            #    continue
            qspan[beg:end] = [2] * len(pred["label"]) #predicate
    #print(len(q),len(qspan))
    count = 0
    for char in q:
        if char == ' ':
            qspan[count] = -1 #space
        count += 1
    qspantokens = [x[0] for x in groupby(qspan)]
    #print(qspantokens)
    qspantokens = filter(lambda a: a != -1, qspantokens)
    if 1 in qspantokens and 2 in qspantokens:
        #print(q)
        #print(item)
        #print(qspan)
        #print(qspantokens)
        items.append({'question':q, 'erspan':list(qspantokens)})

for item in d:
    q = item['question'].lower()
    #print(q)
    q = re.sub("\s*\?", "", q.strip())
    #print(q)
    qspan = [0]*len(q)
    for entity in item['entity mapping']:
        if entity['matchedBy'] != 'miss':
            beg = q.find(entity["label"].lower())
            if beg == -1:
                continue
            end = beg + len(entity["label"].lower())
            qspan[beg:end] = [1] * len(entity["label"].lower()) #entity
    for pred in item['predicate mapping']:
        if pred['mappedBy'] != 'miss':
            beg = q.find(pred["label"].lower())
            if beg == -1:
                continue
            end = beg + len(pred["label"].lower())
            qspan[beg:end] = [2] * len(pred["label"].lower()) #predicate
    #print(len(q),len(qspan))
    count = 0
    for char in q:
        if char == ' ':
            qspan[count] = -1 #space
        count += 1
    qspantokens = [x[0] for x in groupby(qspan)]
    #print(qspantokens)
    qspantokens = filter(lambda a: a != -1, qspantokens)
    if 1 in qspantokens and 2 in qspantokens:
        #print(q)
        #print(item)
        #print(qspan)
        #print(qspantokens)
        items.append({'question':q, 'erspan':list(qspantokens)})

print(len(items))
f = open('erspans.json','w')
f.write(json.dumps(items,indent=4, sort_keys=True))
f.close()
