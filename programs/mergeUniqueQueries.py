#!/usr/bin/python
# To execute, do something like:
# prompt$ python mergeUniqueQueries.py 000000_0.unique_queries 000001_0.unique_queries > 000000_0.000001_0.unique_queries

import sys
import json

def main():

    if len(sys.argv) != 3:
        print >> sys.stderr,\
             'usage: %s <file1.unique_queries> <file2.unique_queries>' % (sys.argv[0])
        sys.exit()
    fd1 = open(sys.argv[1])
    line1 = fd1.readline()
    record1 = json.loads(line1)
    fd2 = open(sys.argv[2])
    line2 = fd2.readline()
    record2 = json.loads(line2)

    cnt_merged = 0
    cnt_from1 = 0
    cnt_from2 = 0
    while True:
        if record1['key'] == record2['key']:
            cnt_merged += 1
            rawqueries = record1['rawqueries'] + record2['rawqueries']
            searchattributes = record1['searchattributes'] + record2['searchattributes']
            shownitems = record1['shownitems']
            for item in record2['shownitems']:
                if item not in shownitems:
                    shownitems.append(item)
            merged_record = {}
            merged_record['key'] = record1['key']
            merged_record['shownitems'] = shownitems
            merged_record['rawqueries'] = rawqueries
            merged_record['searchattributes'] = searchattributes
            print json.dumps(merged_record)
            line1 = fd1.readline()
            if not line1:
                break
            record1 = json.loads(line1)
            line2 = fd2.readline()
            if not line2:
                break
            record2 = json.loads(line2)
        elif record1['key'] < record2['key']:
            cnt_from1 += 1
            print line1.rstrip()
            line1 = fd1.readline()
            if not line1:
                break
            record1 = json.loads(line1)
        else:
            cnt_from2 += 1
            print line2.rstrip()
            line2 = fd2.readline()
            if not line2:
                break
            record2 = json.loads(line2)
    if line1:
        cnt_from1 += 1
        print line1.rstrip()
    for line1 in fd1:
        cnt_from1 += 1
        print line1.rstrip()
    if line2:
        cnt_from2 += 1
        print line2.rstrip()
    for line2 in fd2:
        cnt_from2 += 1
        print line2.rstrip()
    print >> sys.stderr, 'Merged = ' + str(cnt_merged) + ', 1 only = ' + \
                         str(cnt_from1) + ', 2 only = ' + str(cnt_from2)

if __name__ == '__main__':
  main()
