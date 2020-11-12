import json

f = open('vocab.json', 'r')
print(f)

with open('vocab.json', 'r') as file:
    f = json.load(file)
    print(f)