import sys,os,json,re
from itertools import groupby

d = json.loads(open('lcquad2.0.json').read())

allspans = []

for item in d:
    q = item['NNQT_question']
    _entsrels = re.findall( r'{(.*?)}', q)
    entsrels = [entrel.replace('_', ' ') for entrel in _entsrels]
    try:
        vq = item['question']
        vq = re.sub("\s*\?", "", vq.strip())
        pq = item['paraphrased_question']
        pq = re.sub("\s*\?", "", pq.strip())
    except Exception,e:
        print e
        continue
    print(q,vq,pq)
    vqspan = [0]*len(vq)
    pqspan = [0]*len(pq)
    foundcount = 0
    if len(vq) > 0:
        for _entrel,entrel in zip(_entsrels,entsrels):
            if len(entrel) == 0:
                continue
            if entrel[0].isupper() or '_' in entrel:
                #vq entity
                pos = vq.lower().find(entrel.lower())
                if pos != -1:
                    foundcount += 1
                    end = pos + len(entrel)
                    vqspan[pos:end] = [1] * len(entrel)
            else:
                #vq relation
                pos = vq.lower().find(entrel.lower())
                if pos != -1:
                    foundcount += 1
                    end = pos + len(entrel)
                    vqspan[pos:end] = [2] * len(entrel)
        if foundcount == len(entsrels):
            count = 0
            for char in vq:
                if char == ' ':
                    vqspan[count] = -1 #space
                count += 1
            vqspantokens = [x[0] for x in groupby(vqspan)]
            vqspantokens = filter(lambda a: a != -1, vqspantokens)
            if 1 in vqspantokens and 2 in vqspantokens:
                allspans.append({'text': vq, 'span': list(vqspantokens)})
    if len(pq) > 0:
        foundcount = 0
        for _entrel,entrel in zip(_entsrels,entsrels):
            if len(entrel) == 0:
                continue
            if entrel[0].isupper() or '_' in entrel:
                #pq entity
                pos = pq.lower().find(entrel.lower())
                if pos != -1:
                    foundcount += 1
                    end = pos + len(entrel)
                    pqspan[pos:end] = [1] * len(entrel)
            else:
                #pq relation
                pos = pq.lower().find(entrel.lower())
                if pos != -1:
                    foundcount += 1
                    end = pos + len(entrel)
                    pqspan[pos:end] = [2] * len(entrel)
        if foundcount == len(entsrels):
            count = 0
            for char in pq:
                if char == ' ':
                    pqspan[count] = -1 #space
                count += 1
            pqspantokens = [x[0] for x in groupby(pqspan)]
            pqspantokens = filter(lambda a: a != -1, pqspantokens)
            if 1 in pqspantokens and 2 in pqspantokens:
                allspans.append({'text': pq, 'span': list(pqspantokens)})

print(len(allspans))
f = open('lcqspans.json','w')
f.write(json.dumps(allspans, indent=4, sort_keys=True))
f.close()
