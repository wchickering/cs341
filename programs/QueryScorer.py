#!/usr/bin/env python

__author__ = """Charles Celerier <cceleri@cs.stanford.edu>,
              Bill Chickering <bchick@cs.stanford.edu>,
              Jamie Irvine <jirvine@cs.stanford.edu>"""

__date__ = """13 April 2013"""

#local modules
import Query

class QueryScorer:

    def __init__(self, ctr_by_position):
        self.ctr_by_position = ctr_by_position

    def clickPositionOrig(self, query):
        score = 0.0
        for i in range(len(query.shown_items)):
            if i > len(self.ctr_by_position):
                break
            if query.shown_items[i] in query.clicked_shown_items:
                score += self.ctr_by_position[i]
        return score

    def clickPositionReordered(self, query):
        score = 0.0
        for i in range(len(query.reordered_shown_items)):
            if i > len(self.ctr_by_position):
                break
            if query.reordered_shown_items[i] in query.clicked_shown_items:
                score += self.ctr_by_position[i]
        return score

    def clickPositionIncrease(self, query):
        score_orig = self.clickPositionOrig(query)
        score_reordered = self.clickPositionReordered(query)
        if score_orig > 0.0:
            return (score_reordered - score_orig)/score_orig
        elif score_reordered > 0.0:
            return float('inf')
        else:
            return 0.0

