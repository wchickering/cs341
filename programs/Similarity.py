#!/usr/bin/env python
"""Similarity module

Similarity implements several different similarity measures between two sets of
strings.
"""

__author__ = """Charles Celerier <cceleri@cs.stanford.edu>,
              Bill Chickering <bchick@cs.stanford.edu>,
              Jamie Irvine <jirvine@cs.stanford.edu>"""

__date__ = """13 April 2013"""

import sys
import json

# local modules
import index_query as idx

class SimilarityCalculator:

    # params
    max_posting_cache_size = 100000
    max_score_cache_size = 1000000

    # stats
    num_posting_hits = 0
    num_posting_misses = 0
    num_score_hits = 0
    num_score_misses = 0

    def __init__(self, index_fname, posting_dict_fname, \
                 posting_cache_fname, posting_cache_queue_fname):
        self.index_fd = open(index_fname)
        dict_fd = open(posting_dict_fname)
        self.posting_dict = idx.get_posting_dict(dict_fd)
        self.posting_cache_queue = []
        self.posting_cache = {}
        self.score_cache_queue = []
        self.score_cache = {}
        if posting_cache_fname and posting_cache_queue_fname:
            try:
                posting_cache_f = open(posting_cache_fname)
                self.posting_cache = json.loads(posting_cache_f.readline())
                posting_cache_queue_f = open(posting_cache_queue_fname)
                self.posting_cache_queue = json.loads(posting_cache_queue_f.readline())
                print >> sys.stderr, 'len(posting_cache) = ' + str(len(self.posting_cache))
                print >> sys.stderr, 'len(posting_cache_queue) = ' + str(len(self.posting_cache_queue))
                while self.posting_cache_queue[-1] not in self.posting_cache:
                    print >> sys.stderr, 'Removing invalid key from queue.'
                    self.posting_cache_queue.pop()
            except:
                print >> sys.stderr, 'Failed to read posting cache from disk.'
                self.posting_cache = {}
                self.posting_cache_queue = []

    def __del__(self):
        print >> sys.stderr, 'SimilarityCalculator cache:' + \
                             '\nnum_posting_hits = ' + str(self.num_posting_hits) + \
                             ', num_posting_misses = ' + str(self.num_posting_misses) + \
                             '\nnum_score_hits = ' + str(self.num_score_hits) + \
                             ', num_score_misses = ' + str(self.num_score_misses)
        posting_cache_queue_f = open('simcalc.posting_cache_queue.json', 'w')
        print >> posting_cache_queue_f, json.dumps(self.posting_cache_queue)
        posting_cache_f = open('simcalc.posting_cache.json', 'w')
        print >> posting_cache_f, json.dumps(self.posting_cache)
        #score_cache_queue_f = open('simcalc.score_cache_queue.json', 'w')
        #print >> score_cache_queue_f, json.dumps(self.score_cache_queue)
        #score_cache_f = open('simcalc.score_cache.json', 'w')
        #print >> score_cache_f, json.dumps(self.score_cache)

    def get_posting(self, itemid):
        if itemid in self.posting_cache:
            self.num_posting_hits += 1
            self.posting_cache_queue.remove(itemid)
            self.posting_cache_queue.insert(0, itemid)
        else:
            self.num_posting_misses += 1
            self.posting_cache[itemid] = \
                    idx.get_posting(self.index_fd, self.posting_dict, itemid)
            self.posting_cache_queue.insert(0, itemid)
            if len(self.posting_cache_queue) > self.max_posting_cache_size:
                del self.posting_cache[self.posting_cache_queue.pop()]
        return self.posting_cache[itemid]

    def similarity(self, itemid1, itemid2):
        key = frozenset([itemid1, itemid2])
        if key in self.score_cache:
            self.num_score_hits += 1
            self.score_cache_queue.remove(key)
            self.score_cache_queue.insert(0, key)
        else:
            self.num_score_misses += 1
            self.score_cache[key] = \
                    self.jaccard(self.get_posting(itemid1), self.get_posting(itemid2))
            self.score_cache_queue.insert(0, key)
            if len(self.score_cache_queue) > self.max_score_cache_size:
                del self.score_cache[self.score_cache_queue.pop()]
        return self.score_cache[key]

    def jaccard(self, l1, l2):
        """Returns the jaccard similarity of the two lists of elements
    
        Parameters
        ==========
    
        l1, l2: lists
                      lists of elements
    
        Examples
        ========
        >>> import Similarity as sim
        >>> sim.jaccard([1, 2, 3], [1, 2, 4])
        0.5
        """
        interSize = 0
        unionSize = 0
        i = 0
        j = 0
        while i < len(l1) and j < len(l2):
            if l1[i] == l2[j]:
                interSize += 1
                unionSize += 1
                i += 1
                j += 1
                continue
            if l1[i] > l2[j]:
                unionSize += 1
                j += 1
                continue
            else:
                unionSize += 1
                i += 1
                continue
        while i < len(l1):
            unionSize += 1
            i += 1
        while j < len(l2):
            unionSize += 1
            j += 1
        if unionSize == 0:
            return 0.0
        else:
            return float(interSize)/unionSize
              
