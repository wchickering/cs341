#!/usr/bin/python
# To execute, do something like:
# > python visitorQueryMapper.py < 000000_0.filtered | sort -k1,1n -k2,2 -k3,3 -k4,4 -k5,5n | python visitorQueryReducer.py > 000000_0.queries

from itertools import groupby
from operator import itemgetter
import sys
import re
import json

def read_mapper_output(file, separator='\t'):
    for line in file:
        yield line.rstrip().split(separator, 1)

def main():
    sep='\t'
    queryDict = {}
    data = read_mapper_output(sys.stdin, separator=sep)
    # loop through keys (visitorID)
    for visitorid, group in groupby(data, itemgetter(0)):
        query_sessionid = None
        query_rawquery = None
        query_searchattributes = None
        query_record = None
        query_firstpageitems = None
        query_shownitems = None
        query_clickeditems = None
  
        lineNum = 0
        for visitorid, dataString in group:
            try:
                lineNum = lineNum + 1

                # get M/R secondary keys
                dataColumns = dataString.split(sep)
                sessionid = dataColumns[0]
                rawquery = dataColumns[1]
                searchattributes = dataColumns[2]
                timestamp = int(dataColumns[3])

                # get raw data
                line = dataColumns[4]
                record = json.loads(line)

                shownitems = record['shownitems']
                clickeditems = record['clickeditems']
  
                # check if still processing query
                if sessionid == query_sessionid and \
                   rawquery == query_rawquery and \
                   searchattributes == query_searchattributes:
                    for item in shownitems:
                        if item not in query_shownitems:
                            query_shownitems.append(item)
                    for item in clickeditems:
                        if item not in query_clickeditems:
                            query_clickeditems.append(item)
  
                # otherwise, print query record
                else:
                    if lineNum != 1:
                        query_record['shownitems'] = query_shownitems
                        query_record['clickeditems'] = query_clickeditems
                        query_record['firstpageitems'] = query_firstpageitems
                        print json.dumps(query_record)

                    # initialize new query
                    query_record = record
                    query_firstpageitems = shownitems
                    query_shownitems = shownitems
                    query_clickeditems = clickeditems
                    query_sessionid = sessionid
                    query_rawquery = rawquery
                    query_searchattributes = searchattributes
            except:
                print >> sys.stderr, 'Exception thrown for dataString:\n' + dataString
                raise
        # print last one    
        query_record['shownitems'] = query_shownitems
        query_record['clickeditems'] = query_clickeditems
        query_record['firstpageitems'] = query_firstpageitems
        print json.dumps(query_record)

if __name__ == '__main__':
	main()
