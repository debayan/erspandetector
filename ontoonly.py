import sys,os,json

d = json.loads(open('qald-7-train-multilingual.json').read())

ontoonlylcq = []

for item in d['questions']:
    if item['onlydbo'] == True:
        ontoonlylcq.append(item)

print(len(ontoonlylcq))
f = open('qald7ontoonly.json','w')
f.write(json.dumps(ontoonlylcq, indent=4, sort_keys=True))
f.close()
