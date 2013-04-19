#!/usr/bin/python
# To execute, do something like:
# > python testGenMapper.py < 000000_0_filt.json | sort -k1,1n -k2,2 -k3,3 -k4,4n | python testGenReducer.py > testdata.json

import sys
import json
import unicodedata

def normalizeStr(s):
    return unicodedata.normalize('NFKD', s)\
           .encode('ascii','ignore').replace('"','\"').strip()

def main():
    for line in sys.stdin:
        try:
            record = json.loads(line)
            visitorid = record['visitorid']
            sessionid = normalizeStr(record['wmsessionid'])
            rawquery = normalizeStr(record['rawquery'])
            timestamp = record['searchtimestamp']
            shownitems = str(record['shownitems'])
            clickeditems = str(record['clickeditems'])
            sep = '\t'
            print sep.join([visitorid, sessionid, rawquery, timestamp, shownitems, clickeditems])
        except:
            print >> sys.stderr, 'Error on line:\n' + line
            raise

if __name__ == '__main__':
  main()
