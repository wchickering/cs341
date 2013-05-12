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
        query_shownitems = None
        query_clickeditems = None
        query_clicks = None
  
        lineNum = 0
        for visitorid, dataString in group:
            lineNum = lineNum + 1

            try:
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
                clicks = record['clicks']
            except:
                print >> sys.stderr, 'Exception thrown for dataString:\n' + dataString
                print >> sys.stderr, 'Skipping this one. . . '
                continue

            # check if still processing query
            if sessionid == query_sessionid and \
               rawquery == query_rawquery and \
               searchattributes == query_searchattributes:
                for item in shownitems:
                    if item not in query_shownitems:
                        query_shownitems.append(item)
                for click in clicks:
                    if click['ItemId'] not in query_clickeditems:
                        query_clickeditems.append(int(click['ItemId']))
                        query_clicks.append(click)
  
            # otherwise, print query record
            else:
                if lineNum != 1 and query_shownitems:
                    query_record['shownitems'] = query_shownitems
                    query_record['clickeditems'] = query_clickeditems
                    query_record['clicks'] = query_clicks
                    print json.dumps(query_record)

                # initialize new query
                query_record = record
                query_shownitems = shownitems
                query_clickeditems = clickeditems
                query_clicks = clicks
                query_sessionid = sessionid
                query_rawquery = rawquery
                query_searchattributes = searchattributes
        # print last one    
        if query_shownitems:
            query_record['shownitems'] = query_shownitems
            query_record['clickeditems'] = query_clickeditems
            query_record['clicks'] = query_clicks
            print json.dumps(query_record)

if __name__ == '__main__':
	main()
