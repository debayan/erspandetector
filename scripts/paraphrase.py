import sys,os,json,copy,re

d = json.loads(open('wordvectorstraintestngram.json').read())


newitems = []
for item in d:
    newitems.append(item)
    q = item['question']
    if 'Which ' in  q:
        newitem = copy.deepcopy(item)
        newitem['question'] = re.sub(r'^Which ', 'Give ', q)
        newitems.append(newitem)
        newitem = copy.deepcopy(item)
        newitem['question'] = re.sub(r'^Which ', 'Name ', q)
        newitems.append(newitem)
    if 'which ' in  q:
        newitem = copy.deepcopy(item)
        newitem['question'] = re.sub(r'^which ', 'give ', q)
        newitems.append(newitem)
        newitem = copy.deepcopy(item)
        newitem['question'] = re.sub(r'^which ', 'name ', q)
        newitems.append(newitem)

f = open('wordvectorstraintestngramparaphrased.json','w')
f.write(json.dumps(newitems, indent=4, sort_keys=True))
f.close()
