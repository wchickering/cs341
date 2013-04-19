#!/usr/bin/python

from itertools import groupby
from operator import itemgetter
import sys

# import local modules
import compression

def read_mapper_output(file, separator='\t'):
    for line in file:
        yield line.rstrip().split(separator, 1)

def main(separator='\t'):
    data = read_mapper_output(sys.stdin, separator=separator)
    for current_itemid, group in groupby(data, itemgetter(0)):
        last_rawqueryid = None
        rawqueryids = []
        for current_itemid, rawqueryid in group:
            if rawqueryid != last_rawqueryid:
                rawqueryids.append(rawqueryid)
                last_rawqueryid = rawqueryid
        print '%s%s%s' % (current_itemid, separator, ','.join(rawqueryids))

if __name__ == '__main__':
    main()
