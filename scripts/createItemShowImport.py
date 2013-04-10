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
    query_shownitems = None
    for line in fileinput.input(sys.argv[1]):
        lineNum = lineNum + 1
        if last_line == line:
            continue
        else:
            last_line = line
        try:
            query = json.loads(line)
            if last_visitorid != query['visitorid'] or \
               last_wmsessionid != query['wmsessionid'] or \
               last_rawquery != query['rawquery']:
                queryid = queryid + 1
                last_visitorid = query['visitorid']
                last_wmsessionid = query['wmsessionid']
                last_rawquery = query['rawquery']
                query_shownitems = query['shownitems']
            pagePosition = 0
            for itemid in query['shownitems']:
                if itemid in query_shownitems:
                    queryPosition = query_shownitems.index(itemid)
                else:
                    queryPosition = len(query_shownitems)
                    query_shownitems.append(itemid)
                output = encodeField.encode(queryid) + ',' + \
                         encodeField.encode(lineNum) + ',' + \
                         encodeField.encode(queryPosition) + ',' + \
                         encodeField.encode(pagePosition) + ',' + \
                         encodeField.encode(itemid)
                print output
                pagePosition = pagePosition + 1
        except:
            numErrors = numErrors + 1
            sys.stderr.write(line)

if __name__ == '__main__':
    main()
