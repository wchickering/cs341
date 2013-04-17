#!/usr/bin/python
# To execute, enter something like:
# python testGen.py 000000_0 > 000000_0_test

import sys
import fileinput
import json

def main(separator='\t'):
	jsonErrors = 0
	for line in sys.stdin:
		try:
			record = json.loads(line)
			visitorid = record['visitorid']
			sessionid = record['wnseesionid']
			rawquery = record['rawquery']
			shownitems = record['shownitems']
			clickeditems = record['clicks']
		except:
			jsonErrors = jsonErrors + 1
			continue
		print '%d%s%d'%(visitorid, separator, sessionid, separator, rawquery, separator, shownitems, separator, clickeditems)

if __name__ == '__main__':
	main()
