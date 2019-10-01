import json

pwr = 'pwr.json'
with open(pwr) as fin:
    data = json.load(fin)
    with open('pwr.csv' ,'w') as fout:
        for test in data:
            fout.write(str(test.get('name')))
            fout.write(',')
            fout.write(str(test.get('max_current')))
            fout.write('\n')
