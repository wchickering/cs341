#!/usr/bin/python
# To execute, do something like:
# prompt$ python index_mapper.py < 000000_0.unique_queries | sort -k1,1n -k2,2n | python index_reducer.py > 000000_0.index

from itertools import groupby
from operator import itemgetter
import sys
import json

# import local modules
import compression

def read_mapper_output(file, separator='\t'):
    for line in file:
        yield line.rstrip().split(separator, 1)

def main():
    if len(sys.argv) != 2:
        print 'usage: %s <posting.dict> < <input_file>' % sys.argv[0]
        sys.exit()
    sep = '\t'
    posting_dict_fname = sys.argv[1]
    posting_dict = {}
    data = read_mapper_output(sys.stdin, separator=sep)
    for current_itemid, group in groupby(data, itemgetter(0)):
        last_uniqueQueryId = None
        uniqueQueryIds = []
        for current_itemid_str, uniqueQueryId_str in group:
            current_itemid = int(current_itemid_str)
            uniqueQueryId = int(uniqueQueryId_str)
            if uniqueQueryId != last_uniqueQueryId:
                uniqueQueryIds.append(uniqueQueryId)
                last_uniqueQueryId = uniqueQueryId
        # THE FOLLOWING IS FOR WRITING A COMPRESSED INDEX
        uniqueQueryIds_dgap = compression.dgap_encode(uniqueQueryIds)
        uniqueQueryIds_vb = compression.vb_encode(uniqueQueryIds_dgap)
        posting_dict[current_itemid] = (sys.stdout.tell(), len(uniqueQueryIds_vb))
        sys.stdout.write(b''.join(uniqueQueryIds_vb))
        ################################################
        # THE FOLLOWING IS FOR WRITING AN UNCOMPRESSED INDEX
        #posting_dict[current_itemid] = sys.stdout.tell()
        #print ','.join([str(i) for i in uniqueQueryIds])
        ################################################
    posting_dict_f = open(posting_dict_fname, 'w')
    print >> posting_dict_f, json.dumps(posting_dict)

if __name__ == '__main__':
    main()
