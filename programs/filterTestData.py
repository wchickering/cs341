#!/usr/bin/env python

import sys

# import local modules
from Query import Query
from SimilarityCalculator import SimilarityCalculator

class BreakoutException(Exception):
    def __init__(self):
        pass
    def __str__(self):
        return ""

if len(sys.argv) != 3:
    print "Usage: %s <index file> <posting dict>" % sys.argv[0]
    sys.exit()

simCalc = SimilarityCalculator(sys.argv[1], sys.argv[2], verbose=True)

for line in sys.stdin:
    try:
        query = Query(line)
        if query.previously_clicked_items == []:
            continue
        if query.clicked_shown_items == []:
            continue

        for shownItem in query.shown_items:
            if shownItem in query.previously_clicked_items:
                continue
            for prevItem in query.previously_clicked_items:
                if simCalc.similarity(prevItem, shownItem) > 0.0:
                    print line.rstrip()
                    raise BreakoutException
    except BreakoutException:
        pass
                
