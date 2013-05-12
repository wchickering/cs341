#!/usr/bin/python
# To execute, do something like:
# prompt$ python indexMapperClicks.py < 000000_0.queries | sort -k1,1n -k2,2n | python indexReducer.py 000000_0.clicks.posting.dict > 000000_0.clicks.index

import sys
import json

def main():
    sep = '\t'
    for line in sys.stdin:
        record = json.loads(line)
        visitorid = int(record['visitorid'])
        for itemid in record['clickeditems']:
            print'%d%s%d'%(itemid, sep, visitorid)

if __name__ == '__main__':
  main()
