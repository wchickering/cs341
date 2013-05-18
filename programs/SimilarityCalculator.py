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
    _queries_posting_cache_size = 100
    _clicks_posting_cache_size = 100

    def __init__(self,\
                 coeff_queries=1.0, coeff_clicks=1.0,\
                 exp_queries=1.0, exp_clicks=1.0,\
                 index_queries_fname=None, posting_dict_queries_fname=None,\
                 index_clicks_fname=None, posting_dict_clicks_fname=None,\
                 queries_score_dict_fname=None, queries_score_dump_fname=None,\
                 clicks_score_dict_fname=None, clicks_score_dump_fname=None,\
                 verbose=False):

        # misc options
        self.verbose = verbose

        # coefficients and exponents
        self.coeff_queries = coeff_queries
        self.coeff_clicks = coeff_clicks
        self.exp_queries = exp_queries
        self.exp_clicks = exp_clicks

        # posting indexes
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

        # queries score dictionary
        self.queries_score_dump_fname = queries_score_dump_fname
        self.queries_score_dict = {}
        self.queries_score_dict_from_file = False
        if queries_score_dict_fname:
            if self.verbose:
                print >> sys.stderr, 'Uploading queries scores from ' + \
                                      queries_score_dict_fname + ' . . .'
            self.queries_score_dict_from_file = True
            queries_score_dict_f = open(queries_score_dict_fname)
            for line in queries_score_dict_f:
                fields = line.rstrip().split(self._score_dump_separator)
                self.queries_score_dict[(int(fields[0]), int(fields[1]))] = float(fields[2])
            if self.verbose:
                print >> sys.stderr, 'Uploaded ' + str(len(self.queries_score_dict)) + \
                                     ' queries scores.'

        # clicks score dictionary
        self.clicks_score_dump_fname = clicks_score_dump_fname
        self.clicks_score_dict = {}
        self.clicks_score_dict_from_file = False
        if clicks_score_dict_fname:
            if self.verbose:
                print >> sys.stderr, 'Uploading clicks scores from ' + \
                                      clicks_score_dict_fname + ' . . .'
            self.clicks_score_dict_from_file = True
            clicks_score_dict_f = open(clicks_score_dict_fname)
            for line in clicks_score_dict_f:
                fields = line.rstrip().split(self._score_dump_separator)
                self.clicks_score_dict[(int(fields[0]), int(fields[1]))] = float(fields[2])
            if self.verbose:
                print >> sys.stderr, 'Uploaded ' + str(len(self.clicks_score_dict)) + \
                                     ' clicks scores.'

        # stats
        self.stats = OrderedDict()
        self.initStats()

    def setParams(self, coeff_queries=None, coeff_clicks=None, exp_queries=None, exp_clicks=None):
        if coeff_queries:
            self.coeff_queries = coeff_queries
        if coeff_clicks:
            self.coeff_clicks = coeff_clicks
        if exp_queries:
            self.exp_queries = exp_queries
        if exp_clicks:
            self.exp_clicks = exp_clicks

    def initStats(self):
        self.stats['queries_posting_cache_hits'] = 0
        self.stats['queries_posting_cache_misses'] = 0
        self.stats['queries_score_cache_hits'] = 0
        self.stats['queries_score_cache_misses'] = 0
        self.stats['clicks_posting_cache_hits'] = 0
        self.stats['clicks_posting_cache_misses'] = 0
        self.stats['clicks_score_cache_hits'] = 0
        self.stats['clicks_score_cache_misses'] = 0

    def printStats(self, outFile):
        for key, value in self.stats.items():
            print >> outFile, key + ' = ' + str(value)
    
    def __del__(self):
        if self.verbose:
            if (self.index_queries_fd and not self.queries_score_dict_from_file) or\
               (self.index_clicks_fd and not self.clicks_score_dict_from_file):
                print >> sys.stderr, 'SimilarityCalculator cache stats:'
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

    def similarity(self, itemid1, itemid2):

        # determine queries score
        queries_score = 0.0
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

        return self.coeff_queries*queries_score**self.exp_queries +\
               self.coeff_clicks*clicks_score**self.exp_clicks

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
              
