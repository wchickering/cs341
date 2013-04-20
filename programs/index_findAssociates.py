#!/usr/bin/python

import sys
import os

# import local modules
import index_query
import Similarity

def main():
    if len(sys.argv) != 3:
        print 'usage: %s <corpus.index> <posting.dict>' % sys.argv[0]
        os._exit(-1)
    index_f = open(sys.argv[1])
    posting_dict_f = open(sys.argv[2])
    posting_dict = index_query.get_posting_dict(posting_dict_f)

    itemids = posting_dict.keys()
    print 'Searching through ' + str(len(itemids)) + ' itemids. . . '
    for i in range(len(itemids)):
        queryIds1 = index_query.get_posting(index_f, posting_dict, itemids[i])
        for j in range(i+1, len(itemids)):
            queryIds2 = index_query.get_posting(index_f, posting_dict, itemids[i])
            if Similarity.jaccard(','.join(queryIds1), ','.join(queryIds2)) > 0:
                print str(i) + ', ' + str(j)

if __name__ == '__main__':
    main()
