#!/usr/bin/env python

from Query import Query
import index_query as idx
import sys
import Similarity as sim

class BreakoutException(Exception):
    def __init__(self):
        pass
    def __str__(self):
        return ""

if len(sys.argv) != 3:
    print "Usage: %s <index file> <posting dict>" % sys.argv[0]
    sys.exit()

indexFd = open(sys.argv[1], "r")
posting_dict_f = open(sys.argv[2], "r")
posting_dict = idx.get_posting_dict(posting_dict_f)

for line in sys.stdin:
    try:
        query = Query(line)
        if query.previously_clicked_items == []:
            continue
        if query.clicked_shown_items == []:
            continue


        prevQueryLists = []
        for previouslyClickedItem in query.previously_clicked_items:
            prevQueryLists.append(idx.get_posting(indexFd, posting_dict,\
                    str(previouslyClickedItem)))

        for shownItem in query.shown_items:
            if shownItem in query.previously_clicked_items:
                continue
            shownItemQueryIds = idx.get_posting(indexFd, posting_dict,\
                    str(shownItem))
            for i in range(len(query.previously_clicked_items)):
                if query.previously_clicked_items[i] != shownItem\
                        and sim.jaccard(prevQueryLists[i],\
                                        shownItemQueryIds) > 0:
                    print line,
                    raise BreakoutException
    
    except BreakoutException:
        pass
                
