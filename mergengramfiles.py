import sys,os,json

d1 = json.loads(open('ngramentitylabelled2.json').read())

d2 = json.loads(open('entityonlywordvecsngramsparaphrased3.json').read())

final = []
for i1,i2 in zip(d1,d2):
     unit = {}
     unit['question'] = i1['question']
     unit['erspan'] = i1['spanlabelled']
     unit['wordvectors'] = i2['wordvectors']
     final.append(unit)

f = open('wordvecsngrams4.json','w')
f.write(json.dumps(final, sort_keys=True,indent=4))
f.close()
