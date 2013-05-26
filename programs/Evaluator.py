#!/usr/bin/env python

import sys
import json
import math
from numbers import Number
from collections import OrderedDict
from collections import Iterable

MAX_FRONT_PAGE_ITEMS = 16
NUM_NDCG_SCORES = 32

class Evaluator:

    def __init__(self, k=1, stats=None):
        self.k = k
        if stats:
            self.stats = stats
        else:
            # dictionary that preserves order at cost in performance
            # do we want this?
            self.stats = OrderedDict() 
            self.initStats()

    def initStats(self):
        self.stats['total_orig_NDCG_32'] = 0.0
        self.stats['total_reordered_NDCG_32'] = 0.0
        self.stats['total_orig_NDCG_scores'] = [0.0 for x in range(NUM_NDCG_SCORES)]
        self.stats['total_reordered_NDCG_scores'] = [0.0 for x in range(NUM_NDCG_SCORES)]
        self.stats['avg_orig_NDCG_scores'] = [0.0 for x in range(NUM_NDCG_SCORES)]
        self.stats['avg_reordered_NDCG_scores'] = [0.0 for x in range(NUM_NDCG_SCORES)]
        self.stats['num_queries'] = 0
        self.stats['net_delta'] = 0
        self.stats['delta_promoted'] = 0
        self.stats['delta_demoted'] = 0
        self.stats['clicked_items'] = 0
        self.stats['total_clicked_positions'] = 0
        self.stats['reordered_clicked_items'] = 0
        self.stats['promoted_clicked_items'] = 0
        self.stats['demoted_clicked_items'] = 0
        self.stats['top_page_advantage'] = 0
        self.stats['total_shown_clicks_front_page'] = 0
        self.stats['total_shown_clicks_off_front_page'] = 0
        self.stats['total_reordered_clicks_front_page'] = 0
        self.stats['total_reordered_clicks_off_front_page'] = 0
        self.stats['total_moved_to_front_page'] = 0
        self.stats['total_moved_off_front_page'] = 0
        self.stats['total_stayed_on_front_page'] = 0
        self.stats['total_recall_front_orig'] = 0.0
        self.stats['total_recall_front_reordered'] = 0.0
        self.stats['precision_orig_subtotal'] = 0.0
        self.stats['recall_orig_subtotal'] = 0.0
        self.stats['f1_orig_subtotal'] = 0.0
        self.stats['precision_reordered_subtotal'] = 0.0
        self.stats['recall_reordered_subtotal'] = 0.0
        self.stats['f1_reordered_subtotal'] = 0.0
        self.stats['precision_orig_avg'] = 0.0
        self.stats['recall_orig_avg'] = 0.0
        self.stats['f1_orig_avg'] = 0.0
        self.stats['precision_reordered_avg'] = 0.0
        self.stats['recall_reordered_avg'] = 0.0
        self.stats['f1_reordered_avg'] = 0.0
        self.stats['total_items_on_front_page'] = 0
        self.stats['total_promoted_items'] = 0
        self.stats['total_promoted_items_approx'] = 0
        self.stats['total_clicks_in_topK_orig'] = 0
        self.stats['total_clicks_in_topK_reordered'] = 0

    def mergeStats(self, stats):
        for key, value in stats.items():
            if isinstance(value, Number):
                self.stats[key] += value
            elif isinstance(value, Iterable):
                for i in range(len(self.stats[key])):
                    self.stats[key][i] += value[i]
            else:
                raise 'Unrecognized type in stats.'

    def computeAverages(self):
        for i in range(NUM_NDCG_SCORES):
            self.stats['avg_orig_NDCG_scores'][i] = \
                self.stats['total_orig_NDCG_scores'][i]/self.stats['num_queries']
            self.stats['avg_reordered_NDCG_scores'][i] = \
                self.stats['total_reordered_NDCG_scores'][i]/self.stats['num_queries']
        self.stats['precision_orig_avg'] =\
             self.stats['precision_orig_subtotal']/self.stats['num_queries']
        self.stats['recall_orig_avg'] =\
             self.stats['recall_orig_subtotal']/self.stats['num_queries']
        self.stats['f1_orig_avg'] =\
             self.stats['f1_orig_subtotal']/self.stats['num_queries']
        self.stats['precision_reordered_avg'] =\
             self.stats['precision_reordered_subtotal']/self.stats['num_queries']
        self.stats['recall_reordered_avg'] =\
             self.stats['recall_reordered_subtotal']/self.stats['num_queries']
        self.stats['f1_reordered_avg'] =\
             self.stats['f1_reordered_subtotal']/self.stats['num_queries']
        self.stats['total_recall_front_orig'] =\
             float(self.stats['total_shown_clicks_front_page'])/self.stats['clicked_items']
        self.stats['total_recall_front_reordered'] =\
             float(self.stats['total_reordered_clicks_front_page'])/self.stats['clicked_items']

    def printStats(self, outFile=sys.stdout):
        for key, value in self.stats.items():
            print >> outFile, key + ' = ' + str(value)

    def printEvaluation(self, outFile=sys.stdout):
        print 'k = ' + str(self.k)
        print
        print '=== DELTA STATS ==='
        print 'percent_net_delta = ' + \
            str(float(self.stats['net_delta'])/self.stats['total_clicked_positions'])
        print 'net_delta = ' + str(self.stats['net_delta'])
        if self.stats['promoted_clicked_items'] > 0:
            print 'avg_promotion = ' + \
                str(float(self.stats['delta_promoted'])/self.stats['promoted_clicked_items'])
        if self.stats['demoted_clicked_items'] > 0:
            print 'avg_demotion = ' + \
                str(float(self.stats['delta_demoted'])/self.stats['demoted_clicked_items'])
        print

        print '=== NDCG SCORES ==='
        for i in range(NUM_NDCG_SCORES):
            print 'NDCG_k = ' + str(i+1)
            print 'orig: \t\t' + str(self.stats['avg_orig_NDCG_scores'][i])
            print 'reordered: \t' + str(self.stats['avg_reordered_NDCG_scores'][i])
        print 'avg_NDCG_orig_32 = \t\t' + \
            str(self.stats['total_orig_NDCG_32']/self.stats['num_queries'])
        print 'avg_NDCG_reordered_32 = \t' + \
            str(self.stats['total_reordered_NDCG_32']/self.stats['num_queries'])
        print

        print '=== PRECISION/RECALL STATS ==='
        print 'total_precision_orig = ' + \
            str(float(self.stats['total_clicks_in_topK_orig'])/(self.k*self.stats['num_queries']))
        print 'precision_orig_avg = ' + str(self.stats['precision_orig_avg'])
        if self.stats['total_promoted_items'] > 0:
            print 'total_precision_reordered_our_picks = ' + \
                str(float(self.stats['promoted_clicked_items'])/self.stats['total_promoted_items'])
        if self.stats['total_promoted_items'] > 0:
            print 'total_precision_reordered_top_k = ' + \
                str(float(self.stats['total_clicks_in_topK_reordered'])/\
                    self.stats['total_promoted_items'])
        print 'precision_reordered_avg = ' + str(self.stats['precision_reordered_avg'])
        print 'total_recall_orig = ' + \
            str(float(self.stats['total_clicks_in_topK_orig'])/self.stats['clicked_items'])
        print 'recall_orig_avg = ' + str(self.stats['recall_orig_avg'])
        print 'total_recall_reordered_our_picks = ' + \
            str(float(self.stats['promoted_clicked_items'])/self.stats['clicked_items'])
        print 'total_recall_reordered_top_k = ' + \
            str(float(self.stats['total_clicks_in_topK_reordered'])/self.stats['clicked_items'])
        print 'recall_reordered_avg = ' + str(self.stats['recall_reordered_avg'])
        print

        print '=== OTHER STATS ==='
        unmoved_clicked_items = \
            self.stats['clicked_items'] - self.stats['reordered_clicked_items']
        print 'clicked_items = ' + str(self.stats['clicked_items'])
        print 'percent_promoted = ' + \
            str(float(self.stats['promoted_clicked_items'])/self.stats['clicked_items'])
        print 'percent_demoted = ' + \
            str(float(self.stats['demoted_clicked_items'])/self.stats['clicked_items'])
        print 'percent_unmoved = ' + \
            str(float(unmoved_clicked_items)/self.stats['clicked_items'])
        print 'reordered_clicked_items = ' + str(self.stats['reordered_clicked_items'])
        #print 'promoted_clicked_items = ' + str(self.stats['promoted_clicked_items'])
        #print 'demoted_clicked_items = ' + str(self.stats['demoted_clicked_items'])
        #print 'unmoved_clicked_items = ' + str(unmoved_clicked_items)
        #print 'approx error of # promotions = ' + \
        #    str(float(self.stats['total_promoted_items'] - \
        #        self.stats['total_promoted_items_approx'])/self.stats['total_promoted_items'])
        print 'num_queries = ' + str(self.stats['num_queries'])
        print 'delta_promoted = ' + str(self.stats['delta_promoted'])
        print 'delta_demoted = ' + str(self.stats['delta_demoted'])
        print 'f1_orig_avg = ' + str(self.stats['f1_orig_avg'])
        print 'f1_reordered_avg = ' + str(self.stats['f1_reordered_avg'])
        print

        print '=== FRONT PAGE STATS ==='
        print 'total_precision_front_orig = ' + \
            str(float(self.stats['total_shown_clicks_front_page'])/\
                self.stats['total_items_on_front_page'])
        print 'total_recall_front_orig = ' + str(self.stats['total_recall_front_orig'])
        print 'total_precision_front_reordered = ' + \
            str(float(self.stats['total_reordered_clicks_front_page'])/\
                self.stats['total_items_on_front_page'])
        print 'total_recall_front_reordered = ' + str(self.stats['total_recall_front_reordered']) +\
            str(float(self.stats['total_reordered_clicks_front_page'])/self.stats['clicked_items'])
        print 'total_reordered_clicks_front_page = ' + \
            str(self.stats['total_reordered_clicks_front_page'])
        #print 'total_reordered_clicks_off_front_page = ' + \
        #    str(self.stats['total_reordered_clicks_off_front_page'])
        print 'total_shown_clicks_front_page = ' + str(self.stats['total_shown_clicks_front_page'])
        #print 'total_shown_clicks_off_front_page = ' + \
        #    str(self.stats['total_shown_clicks_off_front_page'])
        print 'total_moved_to_front_page = ' + str(self.stats['total_moved_to_front_page'])
        print 'total_moved_off_front_page = ' + str(self.stats['total_moved_off_front_page'])
        #print 'total_stayed_on_front_page = ' + str(self.stats['total_stayed_on_front_page'])
        #print 'top_page_advantage = ' + str(self.stats['top_page_advantage'])

    def isFrontPage(self, x):
        if x <= MAX_FRONT_PAGE_ITEMS:
            return 1
        return 0

    def DCGScore(self, i):
        if i == 0:
            return 1
        else:
            return 1.0/math.log((i+1), 2)

    def processRecord(self, record):
        try:
            self.stats['num_queries'] += 1
            shown_items = record['shown_items']
            reordered_shown_items = record['reordered_shown_items']
            clicked_shown_items = set(record['clicked_shown_items'])
            if len(shown_items) < 3:
                return
            self.stats['clicked_items'] += len(clicked_shown_items)
            if len(shown_items) < MAX_FRONT_PAGE_ITEMS:
                self.stats['total_items_on_front_page'] += len(shown_items)
            else:
                self.stats['total_items_on_front_page'] += MAX_FRONT_PAGE_ITEMS
            clicks_in_topK_orig = 0
            clicks_in_topK_reordered = 0

            # hopefully num_promoted_items passed in but if not we approximate (NEED k=3)
            if 'num_promoted_items' in record:
                promoted_items = record['num_promoted_items']
            else:
                # this approximation only works for k = 3
                index_of_first = reordered_shown_items.index(shown_items[0])
                index_of_second = reordered_shown_items.index(shown_items[1])
                index_of_third = reordered_shown_items.index(shown_items[2])
                if index_of_first == 3:
                    promoted_items = 3
                elif index_of_first == 2:
                    promoted_items = 2
                elif index_of_first == 1:
                    if index_of_second == 2 or index_of_third == 2:
                        promoted_items = 1
                    else:
                        promoted_items = 3
                elif index_of_first == 0:
                    if index_of_second == 1 and index_of_third == 2:
                        promoted_items = 0
                    elif index_of_third == 2:
                        promoted_items = 2
                    else:
                        promoted_items = 3
                else:
                    print >> sys.stderr, 'Error: top three reranked improperly'
            self.stats['total_promoted_items'] += promoted_items

            # calculate NDCG
            best_DCG = 0.0
            orig_DCG = 0.0
            reordered_DCG = 0.0
            for i in range(NUM_NDCG_SCORES):
                if i >= len(shown_items):
                    self.stats['total_orig_NDCG_scores'][i] += (orig_DCG/best_DCG)
                    self.stats['total_reordered_NDCG_scores'][i] += (reordered_DCG/best_DCG)
                    continue
                # get best_DCG
                if i < len(clicked_shown_items):
                    best_DCG += self.DCGScore(i)
                if shown_items[i] in clicked_shown_items:
                    orig_DCG += self.DCGScore(i)
                if reordered_shown_items[i] in clicked_shown_items:
                    reordered_DCG += self.DCGScore(i)
                self.stats['total_orig_NDCG_scores'][i] += (orig_DCG/best_DCG)
                self.stats['total_reordered_NDCG_scores'][i] += (reordered_DCG/best_DCG)
            orig_NDCG = orig_DCG/best_DCG
            reordered_NDCG = reordered_DCG/best_DCG
            self.stats['total_orig_NDCG_32'] += orig_NDCG
            self.stats['total_reordered_NDCG_32'] += reordered_NDCG

            for item in clicked_shown_items:
                assert(item in shown_items)
                reordered_index = reordered_shown_items.index(item)
                shown_index = shown_items.index(item)
                self.stats['total_clicked_positions'] += shown_index
                if shown_index < self.k:
                    clicks_in_topK_orig +=1
                assert(clicks_in_topK_orig <= self.k)
                if reordered_index < self.k:
                    clicks_in_topK_reordered +=1
                assert(clicks_in_topK_reordered <= self.k)
                delta = reordered_index - shown_index
                if delta != 0:
                    self.stats['reordered_clicked_items'] += 1
                if delta < 0:
                    self.stats['promoted_clicked_items'] += 1
                    self.stats['delta_promoted'] += delta
                elif delta > 0:
                    self.stats['demoted_clicked_items'] += 1
                    self.stats['delta_demoted'] += delta
                self.stats['net_delta'] += delta
                reordered_front_page = self.isFrontPage(reordered_index)
                shown_front_page = self.isFrontPage(shown_index)
                self.stats['top_page_advantage'] += reordered_front_page - shown_front_page 
                if reordered_front_page - shown_front_page > 0:
                    self.stats['total_moved_to_front_page'] += 1
                elif reordered_front_page - shown_front_page < 0:
                    self.stats['total_moved_off_front_page'] += 1
                elif reordered_front_page and shown_front_page:
                    self.stats['total_stayed_on_front_page'] += 1
                if reordered_front_page:
                    self.stats['total_reordered_clicks_front_page'] += 1
                else:
                    self.stats['total_reordered_clicks_off_front_page'] += 1
                if shown_front_page:
                    self.stats['total_shown_clicks_front_page'] += 1
                else:
                    self.stats['total_shown_clicks_off_front_page'] += 1

            self.stats['total_clicks_in_topK_orig'] += clicks_in_topK_orig
            self.stats['total_clicks_in_topK_reordered'] += clicks_in_topK_reordered

            precision_orig = float(clicks_in_topK_orig)/self.k
            assert(precision_orig <= 1.0)
            recall_orig = float(clicks_in_topK_orig)/len(clicked_shown_items)
            assert(recall_orig <= 1.0)
            if precision_orig + recall_orig > 0.0:
                f1_orig = 2*precision_orig*recall_orig/(precision_orig + recall_orig)
            else:
                f1_orig = 0.0
            precision_reordered = float(clicks_in_topK_reordered)/self.k
            assert(precision_reordered <= 1.0)
            recall_reordered = float(clicks_in_topK_reordered)/len(clicked_shown_items)
            assert(recall_reordered <= 1.0)
            if precision_reordered + recall_reordered > 0.0:
                 f1_reordered = 2*precision_reordered*recall_reordered/\
                                       (precision_reordered + recall_reordered)
            else:
                f1_reordered = 0.0
            self.stats['precision_orig_subtotal'] += precision_orig
            self.stats['recall_orig_subtotal'] += recall_orig
            self.stats['f1_orig_subtotal'] += f1_orig
            self.stats['precision_reordered_subtotal'] += precision_reordered
            self.stats['recall_reordered_subtotal'] += recall_reordered
            self.stats['f1_reordered_subtotal'] += f1_reordered
        except:
            self.printStats()
            print >> sys.stderr, 'Exception thrown for query #' + str(self.stats['num_queries'])
            print >> sys.stderr, record
            raise

## stand-alone program ##

def parseArgs():
    from optparse import OptionParser, OptionGroup, HelpFormatter

    usage = "usage: %prog "\
            + "[-k N]"\
            + "<filename>"

    parser = OptionParser(usage=usage)
    helpFormatter = HelpFormatter(indent_increment=2,\
                                  max_help_position=10,\
                                  width=80,\
                                  short_first=1)

    optionGroup = OptionGroup(parser, "options")
    optionGroup.add_option("-k", type="int", dest="k", help="re-ranked top k items")
    parser.add_option_group(optionGroup)

    parser.set_defaults(k=1)

    (options, args) = parser.parse_args()

    if (len(args) > 1):
        parser.print_usage_usage()
        sys.exit()

    return (options, args)

def main():
    (options, args) = parseArgs()
    if len(args) == 1:
        inputFile = open(args[0])
    else:
        inputFile = sys.stdin

    evaluator = Evaluator(k=options.k)

    lineNum = 0
    for line in inputFile:
        lineNum += 1
        try:
            record = json.loads(line)
        except:
            evaluator.printStats()
            print >> sys.stderr, 'Failed to parse json line ' + str(lineNum)
            print >> sys.stderr, line
            raise
        evaluator.processRecord(record)

    evaluator.computeAverages()
    evaluator.printEvaluation()
            
if __name__ == '__main__':
    main()
