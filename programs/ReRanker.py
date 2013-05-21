#!/usr/bin/env python
"""reorders the shown itmes for a query based on a user's previously clicked
items

"""

__author__ = """Charles Celerier <cceleri@cs.stanford.edu>,
              Bill Chickering <bchick@cs.stanford.edu>,
              Jamie Irvine <jirvine@cs.stanford.edu>"""

__date__ = """16 April 2013"""

import sys
import heapq
from collections import OrderedDict

# import local modules
from SimilarityCalculator import SimilarityCalculator
from Query import Query

class ReRanker:

    def __init__(self, simCalc, k=1, verbose=False):
        self.simCalc = simCalc
        self.k = k
        self.verbose = verbose
        self.stats = OrderedDict()
        self.initStats()

    def initStats(self):
        self.stats['num_queries'] = 0
        self.stats['num_reranks'] = 0
        self.stats['num_shown_items'] = 0
        self.stats['num_nonzero_scores'] = 0
        self.stats['num_unmodified_queries'] = 0

    def printStats(self, outFile=sys.stdout):
        for key, value in self.stats.items():
            print >> outFile, key + ' = ' + str(value)

    def makeRecord(self, query, top_scores_heap, reordered_shown_items):
        record = {}
        record['visitorid'] = query.visitorid
        record['wmsessionid'] = query.wmsessionid
        record['rawquery'] = query.rawquery
        record['searchattributes'] = query.searchattributes
        record['shown_items'] = query.shown_items
        record['clicked_shown_items'] = query.clicked_shown_items
        record['reordered_shown_items'] = reordered_shown_items
        record['num_promoted_items'] = len(top_scores_heap)
        return record

    # Determine the top k scores 
    def getTopScoresHeap(self, query):
        self.stats['num_queries'] += 1
        top_scores_heap = []
        for i in range(len(query.shown_items)):
            shownItem = query.shown_items[i]
            self.stats['num_shown_items'] += 1
            score = 0
            for j in range(len(query.previously_clicked_items)):
                # ignore previously clicked items themselves
                if query.previously_clicked_items[j] == shownItem:
                    score = 0
                    break
                score += self.simCalc.similarity(query.previously_clicked_items[j], \
                                                 query.shown_items[i])
            if score > 0:
                self.stats['num_nonzero_scores'] += 1
                heapq.heappush(top_scores_heap, (score, i))
                if len(top_scores_heap) > self.k:
                    heapq.heappop(top_scores_heap)

        if len(top_scores_heap) == 0:
            self.stats['num_unmodified_queries'] += 1
        self.stats['num_reranks'] += len(top_scores_heap)
        return top_scores_heap

    def reRankItems(self, query, top_scores_heap):
        if len(top_scores_heap) == 0:
            return query.shown_items
        top_scores = sorted(top_scores_heap, key=lambda tup: tup[0], reverse=True)
        top_score_idxs = sorted(top_scores_heap, key=lambda tup: tup[1])
        i = j = k = 0
        reranked_items = []
        while i < len(query.shown_items):
            if i < len(top_scores):
                index = top_scores[i][1]
                try:
                    item = query.shown_items[index]
                except IndexError:
                    print >> sys.stderr, 'index = ' + str(index)
                    print >> sys.stderr, 'len(query.shown_items) = ' + str(len(query.shown_items))
                    print >> sys.stderr, 'top_scores = ' + str(top_scores)
                    print >> sys.stderr, 'query.shown_items = ' + str(query.shown_items)
                    raise
                reranked_items.append(item)
                i += 1
            elif k < len(top_score_idxs):
                if j < top_score_idxs[k][1]:
                    reranked_items.append(query.shown_items[j])
                    i += 1
                    j += 1
                else:
                    j += 1
                    k += 1
            else:
                reranked_items.append(query.shown_items[j])
                i += 1
                j += 1
        return reranked_items
