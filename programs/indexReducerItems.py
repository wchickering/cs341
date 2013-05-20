#!/usr/bin/python
# To execute, do something like:
# prompt$ python indexMapperItems.py < 000000_0.queries | sort -k1,1n -k2,2n | python indexReducerItems.py | sort -k1,1n -k2,2n | python indexReducer.py 000000_0.items.posting.dict > 000000_0.items.index

from itertools import groupby
from operator import itemgetter
import sys
import json

# import local modules
import compression

def read_mapper_output(file, separator='\t'):
    for line in file:
        yield line.rstrip().split(separator, 1)

def main():
    sep = '\t'
    data = read_mapper_output(sys.stdin, separator=sep)
    for currVisitorSessionId, group in groupby(data, itemgetter(0)):
        last_itemId = None
        itemIds = []
        for currVisitorSessionId_str, itemId_str in group:
            currVisitorSessionId = int(currVisitorSessionId_str)
            itemId = int(itemId_str)
            if itemId != last_itemId:
                itemIds.append(itemId)
                last_itemId = itemId
        for itemId_A in itemIds:
            for itemId_B in itemIds:
                print '%d%s%d'%(itemId_A, sep, itemId_B)

if __name__ == '__main__':
    main()
