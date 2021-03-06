#!/usr/bin/python
# To execute, enter something like:
# python createPageViewImport.py 000000_0_filt.json > 000000_0_pageview.csv

import sys
import fileinput
import json

# Locally defined modules
import encodeField

def main():
    lineNum = 0
    queryid = 0
    last_visitorid = None
    last_wmsessionid = None
    last_rawquery = None
    for line in fileinput.input(sys.argv[1]):
        lineNum = lineNum + 1
        record = json.loads(line)
        if last_visitorid != record['visitorid'] or \
           last_wmsessionid != record['wmsessionid'] or \
           last_rawquery != record['rawquery']:
            queryid = queryid + 1
            last_visitorid = record['visitorid']
            last_wmsessionid = record['wmsessionid']
            last_rawquery = record['rawquery']
        itemShowCount = 0
        itemClickCount = 0
        itemClickTopPosition = -1
        for itemid in record['shownitems']:
            itemShowCount = itemShowCount + 1
        for click in record['clicks']:
            itemClickCount = itemClickCount + 1
            if itemClickTopPosition == -1 or itemClickTopPosition > click['Position']:
                itemClickTopPosition = click['Position']
        output = encodeField.encode(lineNum) + ',' + \
                 encodeField.encode(queryid) + ',' + \
                 encodeField.encode(record['visitorid']) + ',' + \
                 encodeField.encode(record['searchtimestamp']) + ',' + \
                 encodeField.encode(record['wmsessionid']) + ',' + \
                 encodeField.encode(record['rawquery']) + ',' + \
                 encodeField.encode(itemShowCount) + ',' + \
                 encodeField.encode(itemClickCount) + ',' + \
                 encodeField.encode(itemClickTopPosition)
        print output

if __name__ == '__main__':
    main()
