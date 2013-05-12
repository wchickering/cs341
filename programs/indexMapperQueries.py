#!/usr/bin/python
# To execute, do something like:
# prompt$ python indexMapperQueries.py < 000000_0.unique_queries | sort -k1,1n -k2,2n | python indexReducer.py 000000_0.queries.posting.dict > 000000_0.queries.index

import sys
import json
import math

# params
MAX_ITEMS_PER_QUERY = 32

def main():
    sep = '\t'
    queryid = 0
    for line in sys.stdin:
        queryid += 1
        record = json.loads(line)
        shownitems = record['shownitems']
        cnt = 0
        for itemid in record['shownitems']:
            cnt += 1
            print'%d%s%d'%(itemid, sep, queryid)
            if cnt >= MAX_ITEMS_PER_QUERY:
                break

if __name__ == '__main__':
  main()
