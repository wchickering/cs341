#!/usr/bin/python
# To execute, enter something like:
# python createItemClickImport.py 000000_0_filt.json > 000000_0_itemclick.csv

import sys
import fileinput
import json

# Locally defined modules
import encodeField

def str2bool(s):
    return s.lower() == 'true'

def main():
    lineNum = 0
    queryid = 0
    last_visitorid = None
    last_wmsessionid = None
    last_rawquery = None
    query_shownitems = None
    for line in fileinput.input(sys.argv[1]):
        lineNum = lineNum + 1
        query = json.loads(line)
        if last_visitorid != query['visitorid'] or \
           last_wmsessionid != query['wmsessionid'] or \
           last_rawquery != query['rawquery']:
            queryid = queryid + 1
            last_visitorid = query['visitorid']
            last_wmsessionid = query['wmsessionid']
            last_rawquery = query['rawquery']
            query_shownitems = query['shownitems']
        for itemid in query['shownitems']:
            if itemid not in query_shownitems:
                query_shownitems.append(itemid)
        for click in query['clicks']:
            if click['Position'] == "-1":
                queryPosition = -1
            else:
                queryPosition = query_shownitems.index(int(click['ItemId']))
            output = encodeField.encode(queryid) + ',' + \
                     encodeField.encode(lineNum) + ',' + \
                     encodeField.encode(click['ItemId']) + ',' + \
                     encodeField.encode(str2bool(click['Ordered'])) + ',' + \
                     encodeField.encode(str2bool(click['InCart'])) + ',' + \
                     encodeField.encode(queryPosition) + ',' + \
                     encodeField.encode(click['Position'])
            print output

if __name__ == '__main__':
    main()
