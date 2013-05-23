import sys
import json

itemDataFn = "data/allItems.data"
itemDataFo = open(itemDataFn, 'r')

itemIndexFn = sys.argv[1]
itemIndexFo = open(itemIndexFn, 'w')

itemPostingDictFn = sys.argv[2]
itemPostingDictFo = open(itemPostingDictFn, 'w')

itemPostingDict = {}

for line in itemDataFo:
    itemId, itemName = line.split('\t')
    itemPostingDict[itemId] = itemIndexFo.tell()
    print >> itemIndexFo, itemName,

print >> itemPostingDictFo, json.dumps(itemPostingDict)

