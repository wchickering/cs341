#!/usr/bin/python

import sys
import fileinput
import json

def main():
  jsonErrors = 0
  for line in fileinput.input(sys.argv[1]):
    try:
      record = json.loads(line)
      visitorid = record['visitorid']
      sessionid = record['wmsessionid']
      rawquery = record['rawquery']
      timestamp = record['searchtimestamp']
      shownitems = record['shownitems']
      clickeditems = record['clickeditems']
      sep = '\t'
      print visitorid , sep, sessionid, sep, rawquery, sep, timestamp, sep, shownitems, sep, clickeditems
    except:
      jsonErrors = jsonErrors + 1
      continue

if __name__ == '__main__':
  main()