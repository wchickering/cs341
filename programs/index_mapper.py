#!/usr/bin/python
# To execute, do something like:
# prompt$ python index_mapper.py < 000000_0.unique_queries | sort -k1,1n -k2,2n | python index_reducer.py > 000000_0.index

import sys
import json

def main():
    sep = '\t'
    queryid = 0
    for line in sys.stdin:
        queryid += 1
        record = json.loads(line)
        for itemid in record['shownitems']:
            print'%d%s%d'%(itemid, sep, queryid)

if __name__ == '__main__':
  main()
