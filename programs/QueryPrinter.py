#!/usr/bin/env python

__author__ = """Charles Celerier <cceleri@cs.stanford.edu>,
              Bill Chickering <bchick@cs.stanford.edu>,
              Jamie Irvine <jirvine@cs.stanford.edu>"""

__date__ = """13 April 2013"""

import sys
import unicodedata

#local modules
import Query
import indexRead as idx

def normalizeStr(s):
    return ' '.join(unicodedata.normalize('NFKD', s)\
                    .encode('ascii','ignore').replace('"','\"').strip().split())

class QueryPrinter:

    def __init__(self,\
                 outFile=sys.stdout,\
                 index_item_title_fname=None, posting_dict_item_title_fname=None,\
                 reRanker=None):
        self.outFile = outFile
        if index_item_title_fname:
            self.index_item_title_fd = open(index_item_title_fname)
            dict_item_title_fd = open(posting_dict_item_title_fname)
            self.posting_dict_item_title = idx.get_posting_dict(dict_item_title_fd)
        else:
            self.index_item_title_fd = None
        self.reRanker = reRanker

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

    def printItem(self, item, score=None):
        line = str(item)
        title = self.getTitle(item)
        if title:
            line += ': ' + title
        if score:
            line += ' (' + str(score) + ')'
        self.printLine(line)

    def printQuery(self, query):
        self.printLine('RawQuery: ' + query.rawquery)
        self.printLine('SearchAttributes: ' + str(query.searchattributes))
        self.printLine('Clicked Items:')
        for item in query.clicked_shown_items:
            self.printItem(item)
        self.printLine('Previously Clicked Items:')
        for item in query.previously_clicked_items:
            self.printItem(item)
        self.printLine('Original Items:')
        for item in query.shown_items:
            self.printItem(item)
        if query.reordered_items:
            self.printLine('Reordered Items:')
            for item in query.reordered_items:
                score = None
                if self.reRanker:
                    score = self.reRanker.getItemScore(query, item,\
                                                       query.shown_items.index(item))
                self.printItem(item, score)
        self.printLine('')

