#!/usr/bin/env python

__author__ = """Charles Celerier <cceleri@cs.stanford.edu>,
              Bill Chickering <bchick@cs.stanford.edu>,
              Jamie Irvine <jirvine@cs.stanford.edu>"""

__date__ = """13 April 2013"""

import sys
import math
from collections import OrderedDict

# local modules
import indexRead as idx

class SimilarityCalculator:

    # params
    _score_dump_separator = '\t'
    _items_posting_cache_size = 100
    _queries_posting_cache_size = 100
    _clicks_posting_cache_size = 100
    _carts_posting_cache_size = 100
    _item_title_posting_cache_size = 100

    def __init__(self,\
                 coeff_items=0.0, coeff_queries=0.0, coeff_clicks=0.0,\
                 coeff_carts=0.0, coeff_item_title=0.0,\
                 exp_items=1.0, exp_queries=1.0, exp_clicks=1.0,\
                 exp_carts=1.0, exp_item_title=1.0,\
                 index_items_fname=None, posting_dict_items_fname=None,\
                 index_queries_fname=None, posting_dict_queries_fname=None,\
                 index_clicks_fname=None, posting_dict_clicks_fname=None,\
                 index_carts_fname=None, posting_dict_carts_fname=None,\
                 index_item_title_fname=None, posting_dict_item_title_fname=None,\
                 items_score_dict_fname=None, items_score_dump_fname=None,\
                 queries_score_dict_fname=None, queries_score_dump_fname=None,\
                 clicks_score_dict_fname=None, clicks_score_dump_fname=None,\
                 carts_score_dict_fname=None, carts_score_dump_fname=None,\
                 item_title_score_dict_fname=None, item_title_score_dump_fname=None,\
                 verbose=False):

        # misc options
        self.verbose = verbose

        # coefficients and exponents
        self.coeff_items = coeff_items
        self.coeff_queries = coeff_queries
        self.coeff_clicks = coeff_clicks
        self.coeff_carts = coeff_carts
        self.coeff_item_title = coeff_item_title
        self.exp_items = exp_items
        self.exp_queries = exp_queries
        self.exp_clicks = exp_clicks
        self.exp_carts = exp_carts
        self.exp_item_title = exp_item_title

        # posting indexes
        if index_items_fname:
            self.index_items_fd = open(index_items_fname)
            dict_items_fd = open(posting_dict_items_fname)
            self.posting_dict_items = idx.get_posting_dict(dict_items_fd)
            if self.verbose:
                print >> sys.stderr, 'Items posting dictionary contains ' + \
                           str(len(self.posting_dict_items)) + ' items.'
        else:
            self.index_items_fd = None
        self.items_posting_cache = {}
        self.items_posting_cache_queue = []
        if index_queries_fname:
            self.index_queries_fd = open(index_queries_fname)
            dict_queries_fd = open(posting_dict_queries_fname)
            self.posting_dict_queries = idx.get_posting_dict(dict_queries_fd)
            if self.verbose:
                print >> sys.stderr, 'Queries posting dictionary contains ' + \
                           str(len(self.posting_dict_queries)) + ' items.'
        else:
            self.index_queries_fd = None
        self.queries_posting_cache = {}
        self.queries_posting_cache_queue = []
        if index_clicks_fname:
            self.index_clicks_fd = open(index_clicks_fname)
            dict_clicks_fd = open(posting_dict_clicks_fname)
            self.posting_dict_clicks = idx.get_posting_dict(dict_clicks_fd)
            if self.verbose:
                print >> sys.stderr, 'Clicks posting dictionary contains ' + \
                           str(len(self.posting_dict_clicks)) + ' items.'
        else:
            self.index_clicks_fd = None
        self.clicks_posting_cache = {}
        self.clicks_posting_cache_queue = []
        if index_carts_fname:
            self.index_carts_fd = open(index_carts_fname)
            dict_carts_fd = open(posting_dict_carts_fname)
            self.posting_dict_carts = idx.get_posting_dict(dict_carts_fd)
            if self.verbose:
                print >> sys.stderr, 'Carts posting dictionary contains ' + \
                           str(len(self.posting_dict_carts)) + ' items.'
        else:
            self.index_carts_fd = None
        self.carts_posting_cache = {}
        self.carts_posting_cache_queue = []
        if index_item_title_fname:
            self.index_item_title_fd = open(index_item_title_fname)
            dict_item_title_fd = open(posting_dict_item_title_fname)
            self.posting_dict_item_title = idx.get_posting_dict(dict_item_title_fd)
            if self.verbose:
                print >> sys.stderr, 'item_title posting dictionary contains ' + \
                           str(len(self.posting_dict_item_title)) + ' items.'
        else:
            self.index_item_title_fd = None
        self.item_title_posting_cache = {}
        self.item_title_posting_cache_queue = []

        # items score dictionary
        self.items_score_dump_fname = items_score_dump_fname
        self.items_score_dict = {}
        self.items_score_dict_from_file = False
        if items_score_dict_fname:
            if self.verbose:
                print >> sys.stderr, 'Uploading items scores from ' + \
                                      items_score_dict_fname + ' . . .'
            self.items_score_dict_from_file = True
            try:
                items_score_dict_f = open(items_score_dict_fname)
                for line in items_score_dict_f:
                    fields = line.rstrip().split(self._score_dump_separator)
                    self.items_score_dict[(int(fields[0]), int(fields[1]))] = float(fields[2])
                if self.verbose:
                    print >> sys.stderr, 'Uploaded ' + str(len(self.items_score_dict)) + \
                                         ' items scores.'
            except:
                print >> sys.stderr, 'ERROR: Failed to upload items scores.'
                raise

        # queries score dictionary
        self.queries_score_dump_fname = queries_score_dump_fname
        self.queries_score_dict = {}
        self.queries_score_dict_from_file = False
        if queries_score_dict_fname:
            if self.verbose:
                print >> sys.stderr, 'Uploading queries scores from ' + \
                                      queries_score_dict_fname + ' . . .'
            self.queries_score_dict_from_file = True
            try:
                queries_score_dict_f = open(queries_score_dict_fname)
                for line in queries_score_dict_f:
                    fields = line.rstrip().split(self._score_dump_separator)
                    self.queries_score_dict[(int(fields[0]), int(fields[1]))] = float(fields[2])
                if self.verbose:
                    print >> sys.stderr, 'Uploaded ' + str(len(self.queries_score_dict)) + \
                                         ' queries scores.'
            except:
                print >> sys.stderr, 'ERROR: Failed to upload queries scores.'
                raise

        # clicks score dictionary
        self.clicks_score_dump_fname = clicks_score_dump_fname
        self.clicks_score_dict = {}
        self.clicks_score_dict_from_file = False
        if clicks_score_dict_fname:
            if self.verbose:
                print >> sys.stderr, 'Uploading clicks scores from ' + \
                                      clicks_score_dict_fname + ' . . .'
            self.clicks_score_dict_from_file = True
            try:
                clicks_score_dict_f = open(clicks_score_dict_fname)
                for line in clicks_score_dict_f:
                    fields = line.rstrip().split(self._score_dump_separator)
                    self.clicks_score_dict[(int(fields[0]), int(fields[1]))] = float(fields[2])
                if self.verbose:
                    print >> sys.stderr, 'Uploaded ' + str(len(self.clicks_score_dict)) + \
                                         ' clicks scores.'
            except:
                print >> sys.stderr, 'ERROR: Failed to upload clicks scores.'
                raise

        # carts score dictionary
        self.carts_score_dump_fname = carts_score_dump_fname
        self.carts_score_dict = {}
        self.carts_score_dict_from_file = False
        if carts_score_dict_fname:
            if self.verbose:
                print >> sys.stderr, 'Uploading carts scores from ' + \
                                      carts_score_dict_fname + ' . . .'
            self.carts_score_dict_from_file = True
            try:
                carts_score_dict_f = open(carts_score_dict_fname)
                for line in carts_score_dict_f:
                    fields = line.rstrip().split(self._score_dump_separator)
                    self.carts_score_dict[(int(fields[0]), int(fields[1]))] = float(fields[2])
                if self.verbose:
                    print >> sys.stderr, 'Uploaded ' + str(len(self.carts_score_dict)) + \
                                         ' carts scores.'
            except:
                print >> sys.stderr, 'ERROR: Failed to upload carts scores.'
                raise

        # item_title score dictionary
        self.item_title_score_dump_fname = item_title_score_dump_fname
        self.item_title_score_dict = {}
        self.item_title_score_dict_from_file = False
        if item_title_score_dict_fname:
            if self.verbose:
                print >> sys.stderr, 'Uploading item_title scores from ' + \
                                      item_title_score_dict_fname + ' . . .'
            self.item_title_score_dict_from_file = True
            try:
                item_title_score_dict_f = open(item_title_score_dict_fname)
                for line in item_title_score_dict_f:
                    fields = line.rstrip().split(self._score_dump_separator)
                    self.item_title_score_dict[(int(fields[0]), int(fields[1]))] = float(fields[2])
                if self.verbose:
                    print >> sys.stderr, 'Uploaded ' + str(len(self.item_title_score_dict)) + \
                                         ' item_title scores.'
            except:
                print >> sys.stderr, 'ERROR: Failed to upload item_title scores.'
                raise

        # stats
        self.stats = OrderedDict()
        self.initStats()

    def setParams(self, coeff_items=None, coeff_queries=None,\
                        coeff_clicks=None, coeff_carts=None,\
                        coeff_item_title=None,\
                        exp_items=None, exp_queries=None,\
                        exp_clicks=None, exp_carts=None,\
                        exp_item_title=None):
        if coeff_items:
            self.coeff_items = coeff_items
        if coeff_queries:
            self.coeff_queries = coeff_queries
        if coeff_clicks:
            self.coeff_clicks = coeff_clicks
        if coeff_carts:
            self.coeff_carts = coeff_carts
        if coeff_item_title:
            self.coeff_item_title = coeff_item_title
        if exp_items:
            self.exp_items = exp_items
        if exp_queries:
            self.exp_queries = exp_queries
        if exp_clicks:
            self.exp_clicks = exp_clicks
        if exp_carts:
            self.exp_carts = exp_carts
        if exp_item_title:
            self.exp_item_title = exp_item_title

    def initStats(self):
        self.stats['items_posting_cache_hits'] = 0
        self.stats['items_posting_cache_misses'] = 0
        self.stats['items_score_cache_hits'] = 0
        self.stats['items_score_cache_misses'] = 0
        self.stats['queries_posting_cache_hits'] = 0
        self.stats['queries_posting_cache_misses'] = 0
        self.stats['queries_score_cache_hits'] = 0
        self.stats['queries_score_cache_misses'] = 0
        self.stats['clicks_posting_cache_hits'] = 0
        self.stats['clicks_posting_cache_misses'] = 0
        self.stats['clicks_score_cache_hits'] = 0
        self.stats['clicks_score_cache_misses'] = 0
        self.stats['carts_posting_cache_hits'] = 0
        self.stats['carts_posting_cache_misses'] = 0
        self.stats['carts_score_cache_hits'] = 0
        self.stats['carts_score_cache_misses'] = 0
        self.stats['item_title_posting_cache_hits'] = 0
        self.stats['item_title_posting_cache_misses'] = 0
        self.stats['item_title_score_cache_hits'] = 0
        self.stats['item_title_score_cache_misses'] = 0

    def printStats(self, outFile):
        for key, value in self.stats.items():
            print >> outFile, key + ' = ' + str(value)
    
    def __del__(self):
        if self.verbose:
            if (self.index_items_fd and not self.items_score_dict_from_file) or\
               (self.index_queries_fd and not self.queries_score_dict_from_file) or\
               (self.index_clicks_fd and not self.clicks_score_dict_from_file) or\
               (self.index_carts_fd and not self.carts_score_dict_from_file) or\
               (self.index_item_title_fd and not self.item_title_score_dict_from_file):
                print >> sys.stderr, 'SimilarityCalculator cache stats:'
            if self.index_items_fd and not self.items_score_dict_from_file:
                print >> sys.stderr,\
                    '\titems posting cache hits: ' +\
                     str(self.stats['items_posting_cache_hits']) +\
                    '\titems posting cache misses: ' +\
                     str(self.stats['items_posting_cache_misses'])
                if self.items_score_dump_fname:
                    print >> sys.stderr, \
                        '\titems score cache hits: ' +\
                        str(self.stats['items_score_cache_hits']) +\
                        '\titems score cache misses: ' +\
                        str(self.stats['items_score_cache_misses'])
            if self.index_queries_fd and not self.queries_score_dict_from_file:
                print >> sys.stderr,\
                    '\tqueries posting cache hits: ' +\
                     str(self.stats['queries_posting_cache_hits']) +\
                    '\tqueries posting cache misses: ' +\
                     str(self.stats['queries_posting_cache_misses'])
                if self.queries_score_dump_fname:
                    print >> sys.stderr, \
                        '\tqueries score cache hits: ' +\
                        str(self.stats['queries_score_cache_hits']) +\
                        '\tqueries score cache misses: ' +\
                        str(self.stats['queries_score_cache_misses'])
            if self.index_clicks_fd and not self.clicks_score_dict_from_file:
                print >> sys.stderr, \
                    '\tclicks posting cache hits: ' +\
                    str(self.stats['clicks_posting_cache_hits']) +\
                    '\tclicks posting cache misses: ' +\
                    str(self.stats['clicks_posting_cache_misses'])
                if self.clicks_score_dump_fname:
                    print >> sys.stderr, \
                        '\tclicks score cache hits: ' +\
                        str(self.stats['clicks_score_cache_hits']) +\
                        '\tclicks score cache misses: ' +\
                        str(self.stats['clicks_score_cache_misses'])
            if self.index_carts_fd and not self.carts_score_dict_from_file:
                print >> sys.stderr, \
                    '\tcarts posting cache hits: ' +\
                    str(self.stats['carts_posting_cache_hits']) +\
                    '\tcarts posting cache misses: ' +\
                    str(self.stats['carts_posting_cache_misses'])
                if self.carts_score_dump_fname:
                    print >> sys.stderr, \
                        '\tcarts score cache hits: ' +\
                        str(self.stats['carts_score_cache_hits']) +\
                        '\tcarts score cache misses: ' +\
                        str(self.stats['carts_score_cache_misses'])
            if self.index_item_title_fd and not self.item_title_score_dict_from_file:
                print >> sys.stderr, \
                    '\titem_title posting cache hits: ' +\
                    str(self.stats['item_title_posting_cache_hits']) +\
                    '\titem_title posting cache misses: ' +\
                    str(self.stats['item_title_posting_cache_misses'])
                if self.item_title_score_dump_fname:
                    print >> sys.stderr, \
                        '\titem_title score cache hits: ' +\
                        str(self.stats['item_title_score_cache_hits']) +\
                        '\titem_title score cache misses: ' +\
                        str(self.stats['item_title_score_cache_misses'])
            
        if self.index_items_fd and self.items_score_dump_fname:
            if self.verbose:
                print >> sys.stderr, 'Dumping items similarity scores to \'%s\'. . .' % \
                                     self.items_score_dump_fname
            items_score_dict_f = open(self.items_score_dump_fname, 'w')
            for (itemid1, itemid2) in self.items_score_dict:
                print >> items_score_dict_f, self._score_dump_separator.join(\
                         [str(itemid1), str(itemid2),\
                          str(self.items_score_dict[(itemid1, itemid2)])])
        if self.index_queries_fd and self.queries_score_dump_fname:
            if self.verbose:
                print >> sys.stderr, 'Dumping queries similarity scores to \'%s\'. . .' % \
                                     self.queries_score_dump_fname
            queries_score_dict_f = open(self.queries_score_dump_fname, 'w')
            for (itemid1, itemid2) in self.queries_score_dict:
                print >> queries_score_dict_f, self._score_dump_separator.join(\
                         [str(itemid1), str(itemid2),\
                          str(self.queries_score_dict[(itemid1, itemid2)])])
        if self.index_clicks_fd and self.clicks_score_dump_fname:
            if self.verbose:
                print >> sys.stderr, 'Dumping clicks similarity scores to \'%s\'. . .' % \
                                     self.clicks_score_dump_fname
            clicks_score_dict_f = open(self.clicks_score_dump_fname, 'w')
            for (itemid1, itemid2) in self.clicks_score_dict:
                print >> clicks_score_dict_f, self._score_dump_separator.join(\
                         [str(itemid1), str(itemid2),\
                          str(self.clicks_score_dict[(itemid1, itemid2)])])
        if self.index_carts_fd and self.carts_score_dump_fname:
            if self.verbose:
                print >> sys.stderr, 'Dumping carts similarity scores to \'%s\'. . .' % \
                                     self.carts_score_dump_fname
            carts_score_dict_f = open(self.carts_score_dump_fname, 'w')
            for (itemid1, itemid2) in self.carts_score_dict:
                print >> carts_score_dict_f, self._score_dump_separator.join(\
                         [str(itemid1), str(itemid2),\
                          str(self.carts_score_dict[(itemid1, itemid2)])])
        if self.index_item_title_fd and self.item_title_score_dump_fname:
            if self.verbose:
                print >> sys.stderr, 'Dumping item_title similarity scores to \'%s\'. . .' % \
                                     self.item_title_score_dump_fname
            item_title_score_dict_f = open(self.item_title_score_dump_fname, 'w')
            for (itemid1, itemid2) in self.item_title_score_dict:
                print >> item_title_score_dict_f, self._score_dump_separator.join(\
                         [str(itemid1), str(itemid2),\
                          str(self.item_title_score_dict[(itemid1, itemid2)])])

    def get_items_posting(self, itemid):
        if itemid in self.items_posting_cache:
            self.stats['items_posting_cache_hits'] += 1
            self.items_posting_cache_queue.remove(itemid)
        else:
            self.stats['items_posting_cache_misses'] += 1
            posting = idx.get_posting(self.index_items_fd,\
                                      self.posting_dict_items, itemid)
            self.items_posting_cache[itemid] = posting
            if len(self.items_posting_cache) > self._items_posting_cache_size:
                del self.items_posting_cache[self.items_posting_cache_queue.pop()]
        self.items_posting_cache_queue.insert(0, itemid)
        return self.items_posting_cache[itemid]

    def get_queries_posting(self, itemid):
        if itemid in self.queries_posting_cache:
            self.stats['queries_posting_cache_hits'] += 1
            self.queries_posting_cache_queue.remove(itemid)
        else:
            self.stats['queries_posting_cache_misses'] += 1
            posting = idx.get_posting(self.index_queries_fd,\
                                      self.posting_dict_queries, itemid)
            self.queries_posting_cache[itemid] = posting
            if len(self.queries_posting_cache) > self._queries_posting_cache_size:
                del self.queries_posting_cache[self.queries_posting_cache_queue.pop()]
        self.queries_posting_cache_queue.insert(0, itemid)
        return self.queries_posting_cache[itemid]

    def get_clicks_posting(self, itemid):
        if itemid in self.clicks_posting_cache:
            self.stats['clicks_posting_cache_hits'] += 1
            self.clicks_posting_cache_queue.remove(itemid)
        else:
            self.stats['clicks_posting_cache_misses'] += 1
            posting = idx.get_posting(self.index_clicks_fd,\
                                      self.posting_dict_clicks, itemid)
            self.clicks_posting_cache[itemid] = posting
            if len(self.clicks_posting_cache) > self._clicks_posting_cache_size:
                del self.clicks_posting_cache[self.clicks_posting_cache_queue.pop()]
        self.clicks_posting_cache_queue.insert(0, itemid)
        return self.clicks_posting_cache[itemid]

    def get_carts_posting(self, itemid):
        if itemid in self.carts_posting_cache:
            self.stats['carts_posting_cache_hits'] += 1
            self.carts_posting_cache_queue.remove(itemid)
        else:
            self.stats['carts_posting_cache_misses'] += 1
            posting = idx.get_posting(self.index_carts_fd,\
                                      self.posting_dict_carts, itemid)
            self.carts_posting_cache[itemid] = posting
            if len(self.carts_posting_cache) > self._carts_posting_cache_size:
                del self.carts_posting_cache[self.carts_posting_cache_queue.pop()]
        self.carts_posting_cache_queue.insert(0, itemid)
        return self.carts_posting_cache[itemid]

    def get_item_title_posting(self, itemid):
        if itemid in self.item_title_posting_cache:
            self.stats['item_title_posting_cache_hits'] += 1
            self.item_title_posting_cache_queue.remove(itemid)
        else:
            self.stats['item_title_posting_cache_misses'] += 1
            posting = idx.get_posting_raw(self.index_item_title_fd,\
                                          self.posting_dict_item_title, itemid)
            self.item_title_posting_cache[itemid] = posting
            if len(self.item_title_posting_cache) > self._item_title_posting_cache_size:
                del self.item_title_posting_cache[self.item_title_posting_cache_queue.pop()]
        self.item_title_posting_cache_queue.insert(0, itemid)
        return self.item_title_posting_cache[itemid]

    def similarity(self, itemid1, itemid2):

        # determine items score
        items_score = 0.0
        if self.items_score_dump_fname or self.coeff_items > 0:
            if self.items_score_dict_from_file:
                if (min(itemid1, itemid2), max(itemid1, itemid2)) in self.items_score_dict:
                    items_score =\
                        self.items_score_dict[(min(itemid1, itemid2), max(itemid1, itemid2))]
            elif self.items_score_dump_fname:
                if (min(itemid1, itemid2), max(itemid1, itemid2)) in self.items_score_dict:
                    self.stats['items_score_cache_hits'] += 1
                    items_score =\
                        self.items_score_dict[(min(itemid1, itemid2), max(itemid1, itemid2))]
                else:
                    self.stats['items_score_cache_misses'] += 1
                    items_score = self.simfunc(self.get_items_posting(itemid1),\
                                                 self.get_items_posting(itemid2))
                    if items_score > 0.0:
                        self.items_score_dict[(min(itemid1, itemid2), max(itemid1, itemid2))] =\
                            items_score
            elif self.index_items_fd:
                items_score = self.simfunc(self.get_items_posting(itemid1),\
                                             self.get_items_posting(itemid2))

        # determine queries score
        queries_score = 0.0
        if self.queries_score_dump_fname or self.coeff_queries > 0:
            if self.queries_score_dict_from_file:
                if (min(itemid1, itemid2), max(itemid1, itemid2)) in self.queries_score_dict:
                    queries_score =\
                        self.queries_score_dict[(min(itemid1, itemid2), max(itemid1, itemid2))]
            elif self.queries_score_dump_fname:
                if (min(itemid1, itemid2), max(itemid1, itemid2)) in self.queries_score_dict:
                    self.stats['queries_score_cache_hits'] += 1
                    queries_score =\
                        self.queries_score_dict[(min(itemid1, itemid2), max(itemid1, itemid2))]
                else:
                    self.stats['queries_score_cache_misses'] += 1
                    queries_score = self.simfunc(self.get_queries_posting(itemid1),\
                                                 self.get_queries_posting(itemid2))
                    if queries_score > 0.0:
                        self.queries_score_dict[(min(itemid1, itemid2), max(itemid1, itemid2))] =\
                            queries_score
            elif self.index_queries_fd:
                queries_score = self.simfunc(self.get_queries_posting(itemid1),\
                                             self.get_queries_posting(itemid2))

        # determine clicks score
        clicks_score = 0.0
        if self.clicks_score_dump_fname or self.coeff_clicks > 0:
            if self.clicks_score_dict_from_file:
                if (min(itemid1, itemid2), max(itemid1, itemid2)) in self.clicks_score_dict:
                    clicks_score =\
                        self.clicks_score_dict[(min(itemid1, itemid2), max(itemid1, itemid2))]
            elif self.clicks_score_dump_fname:
                if (min(itemid1, itemid2), max(itemid1, itemid2)) in self.clicks_score_dict:
                    self.stats['clicks_score_cache_hits'] += 1
                    clicks_score =\
                        self.clicks_score_dict[(min(itemid1, itemid2), max(itemid1, itemid2))]
                else:
                    self.stats['clicks_score_cache_misses'] += 1
                    clicks_score = self.simfunc(self.get_clicks_posting(itemid1),\
                                                self.get_clicks_posting(itemid2))
                    if clicks_score > 0.0:
                        self.clicks_score_dict[(min(itemid1, itemid2), max(itemid1, itemid2))] =\
                            clicks_score
            elif self.index_clicks_fd:
                clicks_score = self.simfunc(self.get_clicks_posting(itemid1),\
                                            self.get_clicks_posting(itemid2))

        # determine carts score
        carts_score = 0.0
        if self.carts_score_dump_fname or self.coeff_carts > 0:
            if self.carts_score_dict_from_file:
                if (min(itemid1, itemid2), max(itemid1, itemid2)) in self.carts_score_dict:
                    carts_score =\
                        self.carts_score_dict[(min(itemid1, itemid2), max(itemid1, itemid2))]
            elif self.carts_score_dump_fname:
                if (min(itemid1, itemid2), max(itemid1, itemid2)) in self.carts_score_dict:
                    self.stats['carts_score_cache_hits'] += 1
                    carts_score =\
                        self.carts_score_dict[(min(itemid1, itemid2), max(itemid1, itemid2))]
                else:
                    self.stats['carts_score_cache_misses'] += 1
                    carts_score = self.simfunc(self.get_carts_posting(itemid1),\
                                                self.get_carts_posting(itemid2))
                    if carts_score > 0.0:
                        self.carts_score_dict[(min(itemid1, itemid2), max(itemid1, itemid2))] =\
                            carts_score
            elif self.index_carts_fd:
                carts_score = self.simfunc(self.get_carts_posting(itemid1),\
                                            self.get_carts_posting(itemid2))

        # determine item_title score
        item_title_score = 0.0
        if self.item_title_score_dump_fname or self.coeff_item_title > 0:
            if self.item_title_score_dict_from_file:
                if (min(itemid1, itemid2), max(itemid1, itemid2)) in self.item_title_score_dict:
                    item_title_score =\
                        self.item_title_score_dict[(min(itemid1, itemid2), max(itemid1, itemid2))]
            elif self.item_title_score_dump_fname:
                if (min(itemid1, itemid2), max(itemid1, itemid2)) in self.item_title_score_dict:
                    self.stats['item_title_score_cache_hits'] += 1
                    item_title_score =\
                        self.item_title_score_dict[(min(itemid1, itemid2), max(itemid1, itemid2))]
                else:
                    self.stats['item_title_score_cache_misses'] += 1
                    item_title_score = self.simfunc(self.get_item_title_posting(itemid1).split(),\
                                                    self.get_item_title_posting(itemid2).split())
                    if item_title_score > 0.0:
                        self.item_title_score_dict[(min(itemid1, itemid2), max(itemid1, itemid2))] =\
                            item_title_score
            elif self.index_item_title_fd:
                item_title_score = self.simfunc(self.get_item_title_posting(itemid1),\
                                            self.get_item_title_posting(itemid2))

        return self.coeff_items*items_score**self.exp_items +\
               self.coeff_queries*queries_score**self.exp_queries +\
               self.coeff_clicks*clicks_score**self.exp_clicks +\
               self.coeff_carts*carts_score**self.exp_carts +\
               self.coeff_item_title*item_title_score**self.exp_item_title

    def simfunc(self, l1, l2):
        return self.jaccard(l1, l2)

    def jaccard(self, l1, l2):
        sl1 = set(l1)
        sl2 = set(l2)
        interSize = len(sl1.intersection(sl2))
        if interSize == 0:
            return 0.0
        else:
            return float(interSize)/(len(sl1) + len(sl2) - interSize)
              
    def cosineSim(self, l1, l2):
        sl1 = set(l1)
        sl2 = set(l2)
        dotProd = len(sl1.intersection(sl2))
        if dotProd == 0:
            return 0.0
        else:
            return dotProd/(math.sqrt(len(sl1))*math.sqrt(len(sl2)))

def parseArgs():
    from optparse import OptionParser, OptionGroup, HelpFormatter

    usage = "usage: %prog "\
            + "[--index_items <items index filename>] "\
            + "[--dict_items <items dictionary filename>] " \
            + "[--index_queries <queries index filename>] "\
            + "[--dict_queries <queries dictionary filename>] " \
            + "[--index_clicks <clicks index filename>] "\
            + "[--dict_clicks <clicks dictionary filename>] " \
            + "[--index_carts <carts index filename>] "\
            + "[--dict_carts <carts dictionary filename>] " \
            + "[--index_item_title <item_title index filename>] "\
            + "[--dict_item_title <item_title dictionary filename>] " \
            + "<item1> <item2>"

    parser = OptionParser(usage=usage)
    helpFormatter = HelpFormatter(indent_increment=2,\
                                  max_help_position=10,\
                                  width=80,\
                                  short_first=1)

    fileGroup = OptionGroup(parser, "Index options")
    fileGroup.add_option("--index_items", dest="index_items_fname",\
                         help="items index filename")
    fileGroup.add_option("--dict_items", dest="posting_dict_items_fname",\
                         help="items dictionary filename")
    fileGroup.add_option("--index_queries", dest="index_queries_fname",\
                         help="queries index filename")
    fileGroup.add_option("--dict_queries", dest="posting_dict_queries_fname",\
                         help="queries dictionary filename")
    fileGroup.add_option("--index_clicks", dest="index_clicks_fname",\
                         help="clicks index filename")
    fileGroup.add_option("--dict_clicks", dest="posting_dict_clicks_fname",\
                         help="clicks dictionary filename")
    fileGroup.add_option("--index_carts", dest="index_carts_fname",\
                         help="carts index filename")
    fileGroup.add_option("--dict_carts", dest="posting_dict_carts_fname",\
                         help="carts dictionary filename")
    fileGroup.add_option("--index_item_title", dest="index_item_title_fname",\
                         help="item_title index filename")
    fileGroup.add_option("--dict_item_title", dest="posting_dict_item_title_fname",\
                         help="item_title dictionary filename")
    parser.add_option_group(fileGroup)

    parser.set_defaults(index_items_fname=None, posting_dict_items_fname=None,\
                        index_queries_fname=None, posting_dict_queries_fname=None,\
                        index_clicks_fname=None, posting_dict_clicks_fname=None,\
                        index_carts_fname=None, posting_dict_carts_fname=None,\
                        index_item_title_fname=None, posting_dict_item_title_fname=None,\
                        items_score_dict_fname=None, items_score_dump_fname=None)

    (options, args) = parser.parse_args()

    if (len(args) != 2):
        parser.print_usage()
        sys.exit()

    return (options, args)

def main():
    (options, args) = parseArgs()
    item1 = int(args[0])
    item2 = int(args[1])

    simCalc = SimilarityCalculator(\
                      coeff_items=1.0,\
                      coeff_queries=1.0,\
                      coeff_clicks=1.0,\
                      coeff_carts=1.0,\
                      coeff_item_title=1.0,\
                      index_items_fname=options.index_items_fname,\
                      posting_dict_items_fname=options.posting_dict_items_fname,\
                      index_queries_fname=options.index_queries_fname,\
                      posting_dict_queries_fname=options.posting_dict_queries_fname,\
                      index_clicks_fname=options.index_clicks_fname,\
                      posting_dict_clicks_fname=options.posting_dict_clicks_fname,\
                      index_carts_fname=options.index_carts_fname,\
                      posting_dict_carts_fname=options.posting_dict_carts_fname,\
                      index_item_title_fname=options.index_item_title_fname,\
                      posting_dict_item_title_fname=options.posting_dict_item_title_fname)

    print str(simCalc.similarity(item1, item2))

if __name__ == '__main__':
    main()

