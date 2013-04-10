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
numErrors = 0

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
