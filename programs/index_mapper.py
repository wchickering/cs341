#!/usr/bin/python
# To execute, do something like:
# prompt$ python index_mapper.py < 000000_0_filt.json | sort -k1,1n -k2,2n | python index_reducer.py > 000000_0.index

import sys
import fileinput
import json

def main(separator='\t'):
    lineNum = 0
    uniqueQuery_dict = {}
    uniqueQueryId = 0
    query_key = None
    last_visitorid = None
    last_wmsessionid = None
    last_rawquery = None
    for line in sys.stdin:
        lineNum += 1
        record = json.loads(line)
        if last_visitorid != record['visitorid'] or \
           last_wmsessionid != record['wmsessionid'] or \
           last_rawquery != record['rawquery']:
            query_key = ','.join([str(i) for i in record['shownitems']])
            last_visitorid = record['visitorid']
            last_wmsessionid = record['wmsessionid']
            last_rawquery = record['rawquery']
        shownitems = record['shownitems']
        if query_key not in uniqueQuery_dict:
            uniqueQuery_dict[query_key] = uniqueQueryId
            uniqueQueryId += 1
        for itemid in shownitems:
            print '%d%s%d'%(itemid, separator, uniqueQuery_dict[query_key])

if __name__ == '__main__':
  main()
