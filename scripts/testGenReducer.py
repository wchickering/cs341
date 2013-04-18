#!/usr/bin/python

from itertools import groupby
from operator import itemgetter
import sys
import re
import encodeField

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
    query_shown = []
    total_clicked = []
    query_clicked = []

    # sort by query data columns in order they are output by mapper
    group = sorted(group, key=itemgetter(1))
    lineNum = 0

    # loop through values for this key to consolidate and then print out full queries,
    #   (over multiple lines), the items clicked by this user before this query, and
    #   the items clicked in this full query
    # unfortunately only want to print when we know the query is done, so this loop
    #   prints the previous one when the query has changed. This means we need to exclude
    #   the first case and add a print once the loop is finished
    for visitorid, queryDataString in group:
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
        # if this has new query results, add them to query_shown so far
        if not (set(shownitems) <= set(query_shown)): 
          query_shown = query_shown + shownitems
          query_clicked = query_clicked + clickeditems
          continue
        # if repeat view but click this time, add the click
        elif not (set(clickeditems) <= set(query_clicked)):
          query_clicked = query_clicked + clickeditems
          continue

      # otherwise, print last line and restart query
      else:
        if lineNum != 1:
          output = encodeField.encode(query_shown) + ',' + \
            encodeField.encode(total_clicked) + ',' + \
            encodeField.encode(query_clicked)
          print output
          #print query_shown, sep, total_clicked, sep, query_clicked
        # now add clicks to total clicks and clear the chambers
        total_clicked = total_clicked + query_clicked
        query_shown = shownitems
        query_clicked = clickeditems
        last_sessionid = sessionid
        last_rawquery = rawquery
    # print last one    
    output = encodeField.encode(query_shown) + ',' + \
            encodeField.encode(total_clicked) + ',' + \
            encodeField.encode(query_clicked)
    print output
   # print query_shown, sep, total_clicked, sep, query_clicked

if __name__ == '__main__':
	main()
