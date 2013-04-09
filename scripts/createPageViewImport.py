#!/usr/bin/python
# To execute, enter something like:
# python createPageViewImport.py 000000_0 > 000000_0_pageview.csv 2> 000000_0_pageview.err

import sys
import fileinput
import json

# Locally defined modules
import encodeField

# PARAMS
inputFile = '000000_0'

# GLOBALS
lineNum = 0
numErrors = 0

def main():
    global lineNum
    global numErrors
    for line in fileinput.input(inputFile):
        lineNum = lineNum + 1
        try:
            record = json.loads(line)
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
                     encodeField.encode(record['visitorid']) + ',' + \
                     encodeField.encode(record['wmsessionid']) + ',' + \
                     encodeField.encode(record['rawquery']) + ',' + \
                     encodeField.encode(itemShowCount) + ',' + \
                     encodeField.encode(itemClickCount) + ',' + \
                     encodeField.encode(itemClickTopPosition)
            print output
        except:
            numErrors = numErrors + 1
            sys.stderr.write(line)

if __name__ == '__main__':
    main()
