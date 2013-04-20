#!/usr/bin/python

import sys
import os

# import local modules
import index_query

def main():
    if len(sys.argv) != 4:
        print 'usage: %s <corpus.index> <posting.dict> itemid' % sys.argv[0]
        os._exit(-1)
    index_f = open(sys.argv[1])
    posting_dict_f = open(sys.argv.[2])
    posting_dict = index_query.get_posting_dict(posting_dict_f)
    uniqueQueryIds = index_query.get_posting(index_f, posting_dict, sys.argv[3])
    print str(uniqueQueryIds)

if __name__ == '__main__':
    main()
