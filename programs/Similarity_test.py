#!/usr/bin/python

import sys
import os

# import local modules
import index_query
import Similarity

def main():
    if len(sys.argv) != 5:
        print 'usage: %s <corpus.index> <posting.dict> itemid1 itemid2' % sys.argv[0]
        os._exit(-1)
    index_f = open(sys.argv[1])
    posting_dict_f = open(sys.argv[2])
    posting_dict = index_query.get_posting_dict(posting_dict_f)

    queryIds1 = index_query.get_posting(index_f, posting_dict, sys.argv[3])
    queryIds2 = index_query.get_posting(index_f, posting_dict, sys.argv[4])
    sim = Similarity.jaccard(queryIds1, queryIds2, verbose=True)
    print 'sim = ' + str(sim)

if __name__ == '__main__':
    main()
