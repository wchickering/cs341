#!/usr/bin/python
# To execute, do something like:
# prompt$ python uniqueQueryMapper.py < 000000_0.queries | sort | python uniqueQueryReducer.py > 000000_0.unique_queries

import sys
import json

def main():
    for line in sys.stdin:
        output = {}
        record = json.loads(line)
        firstpageitems = record['firstpageitems']
        output['shownitems'] = record['shownitems']
        output['rawquery'] = record['rawquery']
        output['searchattributes'] = record['searchattributes']
        sep = '\t'
        print sep.join([json.dumps(firstpageitems), json.dumps(output)])

if __name__ == '__main__':
  main()
