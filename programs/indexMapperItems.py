#!/usr/bin/python
# To execute, do something like:
# prompt$ python indexMapperItems.py < 000000_0.queries | sort -k1,1n -k2,2n | python indexReducerItems.py | sort -k1,1n -k2,2n | python indexReducer.py 000000_0.items.posting.dict > 000000_0.items.index

import sys
import json

def main():
    sep = '\t'
    visitorSessionId = 0
    visitorSessions = {}
    for line in sys.stdin:
        record = json.loads(line)
        # the idea here is to only create entries for sessions
        # in which at least two items are clicked
        key = record['visitorid'] + record['wmsessionid']
        for itemid in set(record['clickeditems']):
            if key in visitorSessions:
                if visitorSessions[key][1]:
                    print '%d%s%d'%(visitorSessions[key][0], sep, visitorSessions[key][1])
                    visitorSessions[key][1] = None
                print '%d%s%d'%(visitorSessions[key][0], sep, itemid)
            else:
                visitorSessionId += 1
                visitorSessions[key] = []
                visitorSessions[key].append(visitorSessionId)
                visitorSessions[key].append(itemid)

if __name__ == '__main__':
  main()
