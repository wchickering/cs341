#!/usr/bin/python
# To execute, enter something like:
# python createItemClickImport.py 000000_0 > 000000_0_itemclick.csv 2> 000000_0_itemclick.err

import sys
import fileinput
import json

# Locally defined modules
import encodeField

# GLOBALS
lineNum = 0
queryid = 0
numErrors = 0

def str2bool(s):
    return s.lower() == 'true'

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
            for click in query['clicks']:
                output = encodeField.encode(queryid) + ',' + \
                         encodeField.encode(lineNum) + ',' + \
                         encodeField.encode(click['ItemId']) + ',' + \
                         encodeField.encode(str2bool(click['Ordered'])) + ',' + \
                         encodeField.encode(str2bool(click['InCart'])) + ',' + \
                         encodeField.encode(click['Position'])
                print output
        except:
            numErrors = numErrors + 1
            sys.stderr.write(line)

if __name__ == '__main__':
    main()
