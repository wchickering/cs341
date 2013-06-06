#!/usr/bin/env python

__author__ = """Charles Celerier <cceleri@cs.stanford.edu>,
              Bill Chickering <bchick@cs.stanford.edu>,
              Jamie Irvine <jirvine@cs.stanford.edu>"""

__date__ = """13 April 2013"""

import sys
import unicodedata
from math import log10, floor

#local modules
import Query
import indexRead as idx

def normalizeStr(s):
    return ' '.join(unicodedata.normalize('NFKD', s)\
                    .encode('ascii','ignore').replace('"','\"').strip().split())

def nSigFigs(x, n):
    return round(x, -int(floor(log10(x))) + (n - 1))

class QueryPrinter:

    # params
    _sigfigs = 3

    def __init__(self,\
                 outFile=sys.stdout,\
                 index_item_title_fname=None, posting_dict_item_title_fname=None,\
                 index_categories_fname=None, posting_dict_categories_fname=None,\
                 reRanker=None):
        self.outFile = outFile
        self.__initializeIndex(index_item_title_fname, posting_dict_item_title_fname, 'item_title')
        self.__initializeIndex(index_categories_fname, posting_dict_categories_fname, 'categories')
        self.reRanker = reRanker

    def __initializeIndex(self, index_fname, posting_dict_fname, name):
        if index_fname:
            setattr(self, 'index_%s_fd' % name, open(index_fname))
            dict_fd = open(posting_dict_fname)
            setattr(self, 'posting_dict_%s' % name, idx.get_posting_dict(dict_fd))
        else:
            setattr(self, 'index_%s_fd' % name, None)

    def printLine(self, line):
        try:
            print >> self.outFile, line
        except UnicodeEncodeError:
            print >> self.outFile, normalizeStr(line)

    def getTitle(self, item):
        if self.index_item_title_fd:
            title = idx.get_posting_raw(self.index_item_title_fd,\
                                        self.posting_dict_item_title, item)
            return title.rstrip()
        else:
            return None

    def printItem(self, item, score=None, cost=None, ctr=None,\
                  clicks_score=None, items_score=None, carts_score=None,\
                  queries_score=None, item_title_score=None):
        line = str(item)
        title = self.getTitle(item)
        if title:
            line += ': ' + title
        if score:
            line += ' (' + str(nSigFigs(score, self._sigfigs))
            if cost:
                line += ' cost:' + str(nSigFigs(cost, self._sigfigs))
            if ctr:
                line += ' ctr:' + str(nSigFigs(ctr, self._sigfigs))
            if clicks_score:
                line += ' C:' + str(nSigFigs(clicks_score, self._sigfigs))
            if items_score:
                line += ' I:' + str(nSigFigs(items_score, self._sigfigs))
            if carts_score:
                line += ' A:' + str(nSigFigs(carts_score, self._sigfigs))
            if queries_score:
                line += ' Q:' + str(nSigFigs(queries_score, self._sigfigs))
            if item_title_score:
                line += ' T:' + str(nSigFigs(item_title_score, self._sigfigs))
            line += ')'
        self.printLine(line)

    def printCategoryName(self, cat_id):
        line = cat_id + ": "
        if self.index_categories_fd:
            categoryName = idx.get_posting_raw(self.index_categories_fd,
                                               self.posting_dict_categories, cat_id)
            line += categoryName.rstrip()
        else:
            line += ""
        self.printLine(line)

    def printQuery(self, query):
        self.printLine('RawQuery: ' + query.rawquery)
        self.printLine('SearchAttributes: ' + str(query.searchattributes))
        if 'cat_id' in query.searchattributes:
            self.printLine('Category Names: (%d)' % len(query.searchattributes['cat_id'].split('_')))
            for cat_id in query.searchattributes['cat_id'].split('_'):
                self.printCategoryName(cat_id)
        self.printLine('Clicked Items:')
        for item in query.clicked_shown_items:
            self.printItem(item)
        self.printLine('Previously Clicked Items:')
        for item in query.previously_clicked_items:
            self.printItem(item)
        self.printLine('Original Items:')
        for item in query.shown_items:
            self.printItem(item)
        if query.reordered_shown_items:
            self.printLine('Reordered Items:')
            for i in range(len(query.reordered_shown_items)):
                item = query.reordered_shown_items[i]
                score = None
                cost = None
                ctr = None
                clicks_score = None
                items_score = None
                carts_score = None
                queries_score = None
                item_title_score = None
                if self.reRanker:
                    origPos = query.shown_items.index(item)
                    score = self.reRanker.getItemScore(query, item, origPos)
                    if self.reRanker.ctr_by_position and\
                       i < len(self.reRanker.ctr_by_position):
                        cost = self.reRanker.ctr_by_position[i]
                    if self.reRanker.ctr_by_position and\
                       origPos < len(self.reRanker.ctr_by_position):
                        ctr = self.reRanker.ctr_by_position[origPos]
                    clicks_score = 0.0
                    items_score = 0.0
                    carts_score = 0.0
                    queries_score = 0.0
                    item_title_score = 0.0
                    for prevItem in query.previously_clicked_items:
                        clicks_score += self.reRanker.simCalc.clicks_sim(prevItem, item)
                        items_score += self.reRanker.simCalc.items_sim(prevItem, item)
                        carts_score += self.reRanker.simCalc.carts_sim(prevItem, item)
                        queries_score += self.reRanker.simCalc.queries_sim(prevItem, item)
                        item_title_score += self.reRanker.simCalc.item_title_sim(prevItem, item)
                self.printItem(item, score, cost, ctr, clicks_score, items_score, carts_score,\
                               queries_score, item_title_score)
        self.printLine('')

