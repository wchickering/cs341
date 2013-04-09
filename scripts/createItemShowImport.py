#!/usr/bin/python
# To execute, enter something like:
# python createItemShowImport.py 000000_0 > 000000_0_itemshow.csv 2> 000000_0_itemshow.err

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
    global numErrors
    global lineNum
    for line in fileinput.input(inputFile):
        lineNum = lineNum + 1
        try:
            query = json.loads(line)
            position = 0
            for itemid in query['shownitems']:
                output = encodeField.encode(lineNum) + ',' + \
                         encodeField.encode(position) + ',' + \
                         encodeField.encode(itemid)
                print output
                position = position + 1
        except:
            numErrors = numErrors + 1
            sys.stderr.write(line)

if __name__ == '__main__':
    main()
