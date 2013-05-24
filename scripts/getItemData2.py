#!/usr/bin/python

import sys
import fileinput
import json
import codecs

# PARAMS
inputFile = 'data/items.json.2'

def main():
    global numErrors
    fo = codecs.open(inputFile, mode='r', encoding='utf-8')
    for line in fo:
        line = line.encode('ascii', 'xmlcharrefreplace')

        # quoted fields
        i = 0
        for field in ['"id"', '"title"']:
            idx = line.find(field)
            if (idx != -1):
                end = line.find('","', idx)
                fieldInfo = line[idx+len(field)+2:end]
                if i == 0:
                    sys.stdout.write(fieldInfo)
                else:
                    sys.stdout.write('\t'+fieldInfo)
            else:
                sys.stdout.write('\t')
            i += 1
        sys.stdout.write('\n')

if __name__ == '__main__':
    main()
