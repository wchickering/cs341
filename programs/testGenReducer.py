#!/usr/bin/python
# To execute, do something like:
# > python testGenMapper.py < 000000_0_filt.json | sort -k1,1n -k2,2 -k3,3 -k4,4n | python testGenReducer.py > testdata.json

from itertools import groupby
from operator import itemgetter
import sys
import re
import json

def read_mapper_output(file, separator='\t'):
    for line in file:
        yield line.rstrip().split(separator, 1)

def string_to_intlist(string):
    intlist = re.findall(r"[\w']+", string)
    for i in range(len(intlist)):
        intlist[i] = int(intlist[i])
    return intlist

def main():
    sep='\t'
    data = read_mapper_output(sys.stdin, separator=sep)
    # loop through keys (visitorID)
    for visitorid, group in groupby(data, itemgetter(0)):
        # for all values, keep track of previous value
        last_sessionid = None
        last_rawquery = None
        last_shownitems = None
        # also keep track of this query (+ clicks) and total clicks for this visitor
        shown_items = []
        previously_clicked_items = []
        clicked_shown_items = []
  
        # sort by query data columns in order they are output by mapper
        # BC: SORTING SHOULD BE TAKEN CARE OF BY MAP REDUCE FRAMEWORK
        #group = sorted(group, key=itemgetter(1))
        lineNum = 0
  
        # loop through values for this key to consolidate and then print out full queries,
        #   (over multiple lines), the items clicked by this user before this query, and
        #   the items clicked in this full query
        # unfortunately only want to print when we know the query is done, so this loop
        #   prints the previous one when the query has changed. This means we need to exclude
        #   the first case and add a print once the loop is finished
        for visitorid, queryDataString in group:
            try:
                lineNum = lineNum + 1
                # unfold data in quesryData
                queryData = queryDataString.split(sep)
                sessionid = queryData[0]
                rawquery = queryData[1]
                timestamp = int(queryData[2])
                shownitems = string_to_intlist(queryData[3])
                clickeditems = string_to_intlist(queryData[4])
  
                # check if this is same query as last 
                if sessionid == last_sessionid and rawquery == last_rawquery:
                    # if this has new query results, add them to shown_items so far
                    #if not (set(shownitems) <= set(shown_items)): 
                    #    shown_items = shown_items + shownitems
                    #    clicked_shown_items = clicked_shown_items + clickeditems
                    #    continue
                    ## if repeat view but click this time, add the click
                    #elif not (set(clickeditems) <= set(clicked_shown_items)):
                    #    clicked_shown_items = clicked_shown_items + clickeditems
                    #    continue
                    for item in shownitems:
                        if item not in shown_items:
                            shown_items.append(item)
                    for item in clickeditems:
                        if item not in clicked_shown_items:
                            clicked_shown_items.append(item)
  
                # otherwise, print last line and restart query
                else:
                    if lineNum != 1:
                        record = {}
                        record['shown_items'] = shown_items
                        record['previously_clicked_items'] = previously_clicked_items
                        record['clicked_shown_items'] = clicked_shown_items
                        record['visitorid'] = visitorid
                        print json.dumps(record)
                    # now add clicks to total clicks and clear the chambers
                    previously_clicked_items = previously_clicked_items + clicked_shown_items
                    shown_items = shownitems
                    clicked_shown_items = clickeditems
                    last_sessionid = sessionid
                    last_rawquery = rawquery
            except:
                print >> sys.stderr, 'Exception thrown for queryDataString:\n' + queryDataString
                raise
        # print last one    
        record = {}
        record['shown_items'] = shown_items
        record['previously_clicked_items'] = previously_clicked_items
        record['clicked_shown_items'] = clicked_shown_items
        record['visitorid'] = visitorid
        print json.dumps(record)

if __name__ == '__main__':
	main()
