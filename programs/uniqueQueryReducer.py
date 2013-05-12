#!/usr/bin/python
# To execute, do something like:
# prompt$ python uniqueQueryMapper.py < 000000_0.queries | sort | python uniqueQueryReducer.py > 000000_0.unique_queries

from itertools import groupby
from operator import itemgetter
import sys
import json

def read_mapper_output(file, separator='\t'):
    for line in file:
        yield line.rstrip().split(separator, 1)

def main(separator='\t'):
    data = read_mapper_output(sys.stdin, separator=separator)
    for key, group in groupby(data, itemgetter(0)):
        net_shownitems = []
        net_rawquery = []
        net_searchattributes = []
        for key, data_json in group:
            record = json.loads(data_json)
            for item in record['shownitems']:
                if item not in net_shownitems:
                    net_shownitems.append(item)
            
            net_rawquery.append(record['rawquery'])
            net_searchattributes.append(record['searchattributes'])
        if len(net_shownitems) > 1:
            output = {}
            output['key'] = key
            output['shownitems'] = net_shownitems
            output['rawqueries'] = net_rawquery
            output['searchattributes'] = net_searchattributes
            print json.dumps(output)

if __name__ == '__main__':
    main()
