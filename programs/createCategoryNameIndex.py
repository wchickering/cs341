import sys
import json

catDataFn = "data/allCategoryNames.data"
catDataFo = open(catDataFn, 'r')

catIndexFn = sys.argv[1]
catIndexFo = open(catIndexFn, 'w')

catPostingDictFn = sys.argv[2]
catPostingDictFo = open(catPostingDictFn, 'w')

catPostingDict = {}

for line in catDataFo:
    catId, catName = line.split('\t')
    catPostingDict[catId] = catIndexFo.tell()
    print >> catIndexFo, catName,

print >> catPostingDictFo, json.dumps(catPostingDict)

