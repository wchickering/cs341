#!/usr/bin/python
# To execute, do something like:
# > python visitorQueryMapper.py < 000000_0.filtered | sort -k1,1n -k2,2 -k3,3 -k4,4 -k5,5n | python visitorQueryReducer.py > 000000_0.queries

import sys
import json
import unicodedata

def normalizeStr(s):
    return ' '.join(unicodedata.normalize('NFKD', s)\
                    .encode('ascii','ignore').replace('"','\"').strip().split())

def main():
    for line in sys.stdin:
        try:
            record = json.loads(line)
            visitorid = record['visitorid']
            sessionid = normalizeStr(record['wmsessionid'])
            rawquery = normalizeStr(record['rawquery'])
            # create a string from searchattributes with all whitespace removed
            searchattributes = ''.join(str(record['searchattributes']).split())
            timestamp = record['searchtimestamp']
            sep = '\t'
            print sep.join([visitorid, sessionid, rawquery, searchattributes,\
                            timestamp, json.dumps(record)])
        except:
            print >> sys.stderr, 'Error on line:\n' + line
            raise

if __name__ == '__main__':
  main()
