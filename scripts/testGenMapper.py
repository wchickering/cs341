#!/usr/bin/python

import sys
import fileinput
import json

def main():
    jsonErrors = 0
    for line in fileinput.input(sys.argv[1]):
        record = json.loads(line)
        visitorid = record['visitorid']
        sessionid = record['wmsessionid']
        rawquery = record['rawquery']
        timestamp = record['searchtimestamp']
        shownitems = str(record['shownitems'])
        clickeditems = str(record['clickeditems'])
        sep = '\t'
        print sep.join([visitorid, sessionid, rawquery, timestamp, shownitems, clickeditems])

if __name__ == '__main__':
  main()
