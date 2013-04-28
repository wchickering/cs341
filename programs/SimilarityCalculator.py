#!/usr/bin/env python

__author__ = """Charles Celerier <cceleri@cs.stanford.edu>,
              Bill Chickering <bchick@cs.stanford.edu>,
              Jamie Irvine <jirvine@cs.stanford.edu>"""

__date__ = """13 April 2013"""

import sys

# local modules
import index_query as idx

class SimilarityCalculator:

    # params
    _score_dump_separator = '\t'
    _posting_cache_size = 100

    # stats
    _posting_cache_hits = 0
    _posting_cache_misses = 0
    _score_cache_hits = 0
    _score_cache_misses = 0
    
    def __init__(self, index_fname, posting_dict_fname, score_dict_fname=None, \
                 score_dump_fname=None, verbose=False):

        # misc options
        self.verbose = verbose

        # posting index
        self.index_fd = open(index_fname)
        dict_fd = open(posting_dict_fname)
        self.posting_dict = idx.get_posting_dict(dict_fd)
        if self.verbose:
            print >> sys.stderr, 'Posting dictionary contains ' + \
                       str(len(self.posting_dict)) + ' items.'
        self.posting_cache = {}
        self.posting_cache_queue = []

        # score dictionary
        self.score_dump_fname = score_dump_fname
        self.score_dict = {}
        self.score_dict_from_file = False
        if score_dict_fname:
            if self.verbose:
                print >> sys.stderr, 'Uploading scores from ' + \
                                      score_dict_fname + ' . . .'
            self.score_dict_from_file = True
            score_dict_f = open(score_dict_fname)
            for line in score_dict_f:
                fields = line.rstrip().split(self._score_dump_separator)
                self.score_dict[(int(fields[0]), int(fields[1]))] = float(fields[2])
            if self.verbose:
                print >> sys.stderr, 'Uploaded ' + str(len(self.score_dict)) + \
                                     ' scores.'

    def __del__(self):
        if self.verbose:
            if not self.score_dict_from_file:
                print >> sys.stderr, 'SimilarityCalculator cache stats:\n' + \
                    '\tposting cache hits: ' + str(self._posting_cache_hits) + \
                    '\tposting cache misses: ' + str(self._posting_cache_misses)
                if self.score_dump_fname:
                    print >> sys.stderr, \
                        '\tscore cache hits: ' + str(self._score_cache_hits) + \
                        '\tscore cache misses: ' + str(self._score_cache_misses)
            
        if self.score_dump_fname:
            print >> sys.stderr, 'Dumping similarity scores to \'%s\'. . .' % \
                                 self.score_dump_fname
            score_dict_f = open(self.score_dump_fname, 'w')
            for (itemid1, itemid2) in self.score_dict:
                print >> score_dict_f, self._score_dump_separator.join(\
                         [itemid1, itemid2, str(self.score_dict[(itemid1, itemid2)])])

    # handles caching
    def get_posting(self, itemid):
        if itemid in self.posting_cache:
            self._posting_cache_hits += 1
            self.posting_cache_queue.remove(itemid)
        else:
            self._posting_cache_misses += 1
            posting = idx.get_posting(self.index_fd, self.posting_dict, itemid)
            # MISSING ITEMS ARE A FACT OF LIFE
            #if self.verbose and len(posting) == 0:
            #    print >> sys.stderr, 'WARNING: No postings found for itemid = ' + str(itemid)
            self.posting_cache[itemid] = posting
            if len(self.posting_cache) > self._posting_cache_size:
                del self.posting_cache[self.posting_cache_queue.pop()]
        self.posting_cache_queue.insert(0, itemid)
        return self.posting_cache[itemid]

    def similarity(self, itemid1, itemid2):
        if self.score_dict_from_file:
            if (min(itemid1, itemid2), max(itemid1, itemid2)) in self.score_dict:
                return self.score_dict[(min(itemid1, itemid2), max(itemid1, itemid2))]
            else:
                return 0.0
        elif self.score_dump_fname:
            if (min(itemid1, itemid2), max(itemid1, itemid2)) in self.score_dict:
                self._score_cache_hits += 1
                return self.score_dict[(min(itemid1, itemid2), max(itemid1, itemid2))]
            else:
                self._score_cache_misses += 1
                score = self.jaccard(self.get_posting(itemid1), self.get_posting(itemid2))
                if score > 0.0:
                    self.score_dict[(min(itemid1, itemid2), max(itemid1, itemid2))] = score
                return score
        else:
            return self.jaccard(self.get_posting(itemid1), self.get_posting(itemid2))

    def jaccard(self, l1, l2):
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
              
