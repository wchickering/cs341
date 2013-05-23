#!/usr/bin/python

import sys
import fileinput
import json
import codecs

# PARAMS
inputFile = 'items2.uniq.json'

def main():
    global numErrors
    fo = codecs.open(inputFile, mode='r', encoding='utf-8')
    print '\t'.join(['itemId','parentItemId','name','categoryPath'])
    for line in fo:
        line = line.encode('ascii', 'xmlcharrefreplace')

        # quoted fields
        for field in ['"id"', '"parentItemId"', '"title"']:
            idx = line.find(field)
            if (idx != -1):
                end = line.find('","', idx)
                fieldInfo = line[idx+len(field)+2:end]
                print fieldInfo+'\t',
            else:
                print '\t',
        print

if __name__ == '__main__':
    main()
