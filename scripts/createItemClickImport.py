#!/usr/bin/python
# To execute, enter something like:
# python createItemClickImport.py 000000_0 > 000000_0_itemclick.csv 2> 000000_0_itemclick.err

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

def str2bool(s):
    return s.lower() == 'true'

def main():
    global numErrors
    global lineNum
    for line in fileinput.input(inputFile):
        lineNum = lineNum + 1
        try:
            query = json.loads(line)
            for click in query['clicks']:
                output = encodeField.encode(lineNum) + ',' + \
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
