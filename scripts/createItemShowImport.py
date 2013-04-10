#!/usr/bin/python
# To execute, enter something like:
# python createItemShowImport.py 000000_0 > 000000_0_itemshow.csv 2> 000000_0_itemshow.err

import sys
import fileinput
import json

# Locally defined modules
import encodeField

# GLOBALS
lineNum = 0
queryid = 0
numErrors = 0

def main():
    global lineNum
    global queryid
    global numErrors
    last_line = None
    last_visitorid = None
    last_wmsessionid = None
    last_rawquery = None
    for line in fileinput.input(sys.argv[1]):
        lineNum = lineNum + 1
        if last_line == line:
            continue
        else:
            last_line = line
        try:
            query = json.loads(line)
            if last_visitorid != record['visitorid'] or \
               last_wmsessionid != record['wmsessionid'] or \
               last_rawquery != record['rawquery']:
                queryid = queryid + 1
                last_visitorid = record['visitorid']
                last_wmsessionid = record['wmsessionid']
                last_rawquery = record['rawquery']
            pagePosition = 0
            for itemid in query['shownitems']:
                output = encodeField.encode(queryid) + ',' + \
                         encodeField.encode(lineNum) + ',' + \
                         encodeField.encode(pagePosition) + ',' + \
                         encodeField.encode(itemid)
                print output
                pagePosition = pagePosition + 1
        except:
            numErrors = numErrors + 1
            sys.stderr.write(line)

if __name__ == '__main__':
    main()
