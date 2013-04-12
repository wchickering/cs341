#!/usr/bin/python

import sys
import fileinput
import json
import unicodedata

def normalizeQuery(rawquery):
    return ';'.join(sorted(unicodedata.normalize('NFKD', rawquery)\
                           .encode('ascii','ignore').lower().split()))

def main(separator='\t'):
    rawqueryid_dict = {}
    lineNum = 0
    jsonErrors = 0
    unicodeErrors = 0
    rawqueryid = 0
    last_line = None
    for line in sys.stdin:
        lineNum += 1
        if last_line == line:
            continue
        else:
            last_line = line
        try:
            record = json.loads(line)
            rawquery = record['rawquery']
            shownitems = record['shownitems']
        except:
            jsonErrors += 1
            continue
        try:
            normQuery = normalizeQuery(rawquery)
        except:
            unicodeErrors += 1
            continue
        if normQuery not in rawqueryid_dict:
            rawqueryid_dict[normQuery] = rawqueryid
            rawqueryid += 1
        for itemid in shownitems:
            print '%d%s%d'%(itemid, separator, rawqueryid_dict[normQuery])

if __name__ == '__main__':
  main()
