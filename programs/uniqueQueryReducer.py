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
    for firstpageitems_json, group in groupby(data, itemgetter(0)):
        net_shownitems = []
        net_rawquery = []
        net_searchattributes = []
        for firstpageitems_json, data_json in group:
            firstpageitems = json.loads(firstpageitems_json)
            record = json.loads(data_json)
            for item in record['shownitems']:
                if item not in net_shownitems:
                    net_shownitems.append(item)
            
            net_rawquery.append(record['rawquery'])
            net_searchattributes.append(record['searchattributes'])
        output = {}
        output['firstpageitems'] = firstpageitems
        output['shownitems'] = net_shownitems
        output['rawqueries'] = net_rawquery
        output['searchattributes'] = net_searchattributes
        print json.dumps(output)

if __name__ == '__main__':
    main()
