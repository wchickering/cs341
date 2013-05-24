#!/usr/bin/python

import sys
import fileinput
import json
import codecs

# PARAMS
inputFile = 'data/items.json.1'

def main():
    global numErrors
    fo = codecs.open(inputFile, mode='r', encoding='utf-8')
    line = fo.readline()
    while (line):
        line = line.encode('ascii', 'xmlcharrefreplace')

        # non-quoted fields
        field = '"itemId"'
        idx = line.find(field)
        if (idx != -1):
            end = line.find(',"', idx)
            fieldInfo = line[idx+len(field)+1:end]
            sys.stdout.write(fieldInfo)
        else:
            sys.stderr.write(line)
            line = fo.readline()
            continue

        # quoted fields
        field  = '"name"'
        idx = line.find(field)
        if (idx != -1):
            end = line.find('","', idx)
            fieldInfo = line[idx+len(field)+2:end]
            sys.stdout.write('\t' + fieldInfo)
        else:
            sys.stdout.write('\t')
        sys.stdout.write('\n')

        line = fo.readline()

if __name__ == '__main__':
    main()
