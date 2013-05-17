#!/usr/bin/env python

import sys
import json
from collections import OrderedDict

CONST_MAX_FRONT_PAGE_ITEM = 16

class Evaluator:

    def __init__(self, k=1):
        self.k = k
        self.stats = OrderedDict()
        self.resetStats()

    def resetStats(self):
        self.stats['num_queries'] = 0
        self.stats['total_delta'] = 0
        self.stats['total_delta_promoted'] = 0
        self.stats['total_delta_demoted'] = 0
        self.stats['total_clicked_items'] = 0
        self.stats['total_reordered_clicked_items'] = 0
        self.stats['total_promoted_clicked_items'] = 0
        self.stats['total_demoted_clicked_items'] = 0
        self.stats['top_page_advantage'] = 0
        self.stats['total_shown_clicks_front_page'] = 0
        self.stats['total_shown_clicks_off_front_page'] = 0
        self.stats['total_reordered_clicks_front_page'] = 0
        self.stats['total_reordered_clicks_off_front_page'] = 0
        self.stats['total_moved_to_front_page'] = 0
        self.stats['total_moved_off_front_page'] = 0
        self.stats['total_stayed_on_front_page'] = 0
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

    def printStats(self, outFile=sys.stdout):
        for key, value in self.stats.items():
            print >> outFile, key + ' = ' + str(value)

    def isFrontPage(self, x):
        if x <= CONST_MAX_FRONT_PAGE_ITEM:
            return 1
        return 0

    def computeAverages(self):
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

    def processRecord(self, record):
        try:
            self.stats['num_queries'] += 1
            shown_items = record['shown_items']
            reordered_shown_items = record['reordered_shown_items']
            clicked_shown_items = set(record['clicked_shown_items'])
            self.stats['total_clicked_items'] += len(clicked_shown_items)
            clicks_in_topK_orig = 0
            clicks_in_topK_reordered = 0
            for item in clicked_shown_items:
                assert(item in shown_items)
                reordered_index = reordered_shown_items.index(item)
                shown_index = shown_items.index(item)
                if shown_index < self.k:
                    clicks_in_topK_orig +=1
                assert(clicks_in_topK_orig <= self.k)
                if reordered_index < self.k:
                    clicks_in_topK_reordered +=1
                assert(clicks_in_topK_reordered <= self.k)
                delta = reordered_index - shown_index
                if delta != 0:
                    self.stats['total_reordered_clicked_items'] += 1
                if delta < 0:
                    self.stats['total_promoted_clicked_items'] += 1
                    self.stats['total_delta_promoted'] += delta
                elif delta > 0:
                    self.stats['total_demoted_clicked_items'] += 1
                    self.stats['total_delta_demoted'] += delta
                self.stats['total_delta'] += delta
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
    optionGroup.add_option("-k", dest="k", help="re-ranked top k items")
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

    evaluator = Evaluator(int(options.k))

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
    evaluator.printStats()
            
if __name__ == '__main__':
    main()
