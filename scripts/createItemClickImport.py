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
numErrors = 0

def str2bool(s):
    return s.lower() == 'true'

def main():
    global numErrors
    global lineNum
    last_line = None
    for line in fileinput.input(sys.argv[1]):
        lineNum = lineNum + 1
        if last_line == line:
            continue
        else:
            last_line = line
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
