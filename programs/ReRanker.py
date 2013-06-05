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
import math
import random
from collections import OrderedDict

# import local modules
from SimilarityCalculator import SimilarityCalculator
from Query import Query

class ReRanker:

    def __init__(self, simCalc, k=1, insert_position=0,\
                 coeff_ctr=0.0, ctr_by_position=None,\
                 coeff_rank=0.0, exp_rank=1.0,\
                 verbose=False):
        self.simCalc = simCalc
        self.k = k
        self.insert_position = insert_position
        self.coeff_ctr = coeff_ctr
        self.ctr_by_position = ctr_by_position
        self.coeff_rank = coeff_rank
        self.exp_rank = exp_rank
        self.verbose = verbose
        self.stats = OrderedDict()
        self.initStats()

    def setParams(self, k=None, insert_position=None,\
                  coeff_ctr=None, ctr_by_position=None,\
                  coeff_rank=None, exp_rank=None):
        if k:
            self.k = k
        if insert_position:
            self.insert_position = insert_position
        if coeff_ctr:
            self.coeff_ctr = coeff_ctr
        if ctr_by_position:
            self.ctr_by_position = ctr_by_position
        if coeff_rank:
            self.coeff_rank = coeff_rank
        if exp_rank:
            self.exp_rank = exp_rank

    def initStats(self):
        self.stats['num_queries'] = 0
        self.stats['num_reranks'] = 0
        self.stats['num_shown_items'] = 0
        self.stats['num_nonzero_scores'] = 0
        self.stats['num_unmodified_queries'] = 0

    def printStats(self, outFile=sys.stdout):
        for key, value in self.stats.items():
            print >> outFile, key + ' = ' + str(value)

    def makeRecord(self, query, num_reranks, reordered_shown_items):
        record = {}
        record['visitorid'] = query.visitorid
        record['wmsessionid'] = query.wmsessionid
        record['rawquery'] = query.rawquery
        record['searchattributes'] = query.searchattributes
        record['shown_items'] = query.shown_items
        record['clicked_shown_items'] = query.clicked_shown_items
        record['carted_shown_items'] = query.carted_shown_items
        record['purchased_shown_items'] = query.purchased_shown_items
        record['reordered_shown_items'] = reordered_shown_items
        record['num_promoted_items'] = num_reranks
        return record

    # Used for testing and data analysis
    def getRandomTopScoresHeap(self, query):
        top_scores_heap = []
        for i in range(self.insert_position, len(query.shown_items)):
            self.stats['num_nonzero_scores'] += 1
            heapq.heappush(top_scores_heap, (random.random(), i))
            if len(top_scores_heap) > self.k:
                heapq.heappop(top_scores_heap)
        return top_scores_heap

    def getItemScore(self, query, item, pos):
        score = 0
        for j in range(len(query.previously_clicked_items)):
            score += self.simCalc.similarity(query.previously_clicked_items[j], item)
        if self.ctr_by_position and pos < len(self.ctr_by_position):
            score += self.coeff_ctr*self.ctr_by_position[pos]
        score += self.coeff_rank*math.exp(-pos)**self.exp_rank
        return score

    # Determine the top k scores 
    def getTopScoresHeap(self, query):
        top_scores_heap = []
        for i in range(self.insert_position, len(query.shown_items)):
            score = self.getItemScore(query, query.shown_items[i], i)
            if score > 0:
                self.stats['num_nonzero_scores'] += 1
                heapq.heappush(top_scores_heap, (score, i))
                if len(top_scores_heap) > self.k:
                    heapq.heappop(top_scores_heap)
        return top_scores_heap

    def reRankItems(self, query, top_scores_heap):
        num_reranks = 0
        self.stats['num_queries'] += 1
        self.stats['num_shown_items'] += len(query.shown_items)
        if len(top_scores_heap) == 0:
            self.stats['num_unmodified_queries'] += 1
            return (num_reranks, query.shown_items)
        top_scores = sorted(top_scores_heap, key=lambda tup: tup[0], reverse=True)
        top_score_idxs = sorted(top_scores_heap, key=lambda tup: tup[1])
        n = 0 # number of top_score items appended to reranked_items
        i = 0 # number of items appended to reranked_items
        j = 0 # index of next item within query.shown_items
        k = 0 # number of top_score_idx's encountered within query.shown_items
        reranked_items = []
        while i < len(query.shown_items):
            if i < self.insert_position:
                reranked_items.append(query.shown_items[j])
                i += 1
                j += 1
            elif n < len(top_scores):
                index = top_scores[n][1]
                reranked_items.append(query.shown_items[index])
                num_reranks += 1
                self.stats['num_reranks'] += 1
                i += 1
                n += 1
            elif k < len(top_score_idxs):
                if j < top_score_idxs[k][1]:
                    reranked_items.append(query.shown_items[j])
                    i += 1
                    j += 1
                else:
                    if j == top_score_idxs[k][1]:
                        j += 1
                    k += 1
            else:
                reranked_items.append(query.shown_items[j])
                i += 1
                j += 1
        return (num_reranks, reranked_items)
