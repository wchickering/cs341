#!/usr/bin/python
# To execute, do something like:
# prompt$ python uniqueQueryMapper.py < 000000_0.queries | sort | python uniqueQueryReducer.py > 000000_0.unique_queries

import sys
import json
from stemming.porter2 import stem

def main():
    for line in sys.stdin:
        output = {}
        record = json.loads(line)
        key = ' '.join([stem(t) for t in record['rawquery'].lower().split()])
        key += str(record['searchattributes'])
        output['shownitems'] = record['shownitems']
        output['rawquery'] = record['rawquery']
        searchattributes = record['searchattributes']
        if 'search_constraint' not in searchattributes:
            searchattributes['search_constraint'] = "0"
        output['searchattributes'] = searchattributes
        sep = '\t'
        print sep.join([json.dumps(key), json.dumps(output)])

if __name__ == '__main__':
  main()
