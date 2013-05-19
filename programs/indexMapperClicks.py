#!/usr/bin/python
# To execute, do something like:
# prompt$ python indexMapperClicks.py < 000000_0.queries | sort -k1,1n -k2,2n | python indexReducer.py 000000_0.clicks.posting.dict > 000000_0.clicks.index

import sys
import json

def main():
    sep = '\t'
    numSessionClickIds = 0
    sessionClickDict = {}
    for line in sys.stdin:
        record = json.loads(line)
        # the idea here is to only create entries for sessions
        # in which at least two items are clicked
        key = record['visitorid'] + record['wmsessionid']
        for itemid in set(record['clickeditems']):
            if key in sessionClickDict:
                if sessionClickDict[key][1]:
                    print '%d%s%d'%(sessionClickDict[key][1], sep, sessionClickDict[key][0])
                    sessionClickDict[key][1] = None
                print '%d%s%d'%(itemid, sep, sessionClickDict[key][0])
            else:
                numSessionClickIds += 1
                sessionClickDict[key] = []
                sessionClickDict[key].append(numSessionClickIds)
                sessionClickDict[key].append(itemid)

if __name__ == '__main__':
  main()
