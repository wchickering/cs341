#!/usr/bin/python
# To execute, enter something like:
# python reformatItems.py items.json > items_reformatted.json

import sys
import fileinput
import json

# PARAMS
inputFile = 'data/items.json.raw'
bufSize = 1024

# GLOBALS
numErrors = 0

def main():
    global numErrors
    fd = open(inputFile)
    buf = fd.read(bufSize)
    data = buf
    idx = data.find('{"itemId"')
    if idx == -1:
        sys.stderr.write('Failed to parse first item.')
        return
    data = data[idx:]
    while buf != "":
        idx = data.find(',{"itemId"')
        while idx != -1:
            line = data[:idx]
            print line
            data = data[idx+1:]
            idx = data.find(',{"itemId"')
        buf = fd.read(bufSize)
        data = data + buf
    idx = data.find('}]}')
    if idx == -1:
        sys.stderr.write('Failed to parse last item.')
        return
    data = data[:idx+1]
    print data

if __name__ == '__main__':
    main()
