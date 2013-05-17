#!/usr/bin/env python
"""reorders the shown itmes for a query based on a user's previously clicked
items

"""

__author__ = """Charles Celerier <cceleri@cs.stanford.edu>,
              Bill Chickering <bchick@cs.stanford.edu>,
              Jamie Irvine <jirvine@cs.stanford.edu>"""

__date__ = """16 April 2013"""

import sys
import json
import heapq
from collections import OrderedDict

# import local modules
from SimilarityCalculator import SimilarityCalculator
from Query import Query

class ReRanker:

    def __init__(self, simCalc, k=1, verbose=False):
        self.simCalc = simCalc
        self.k = k
        self.verbose = verbose
        self.stats = OrderedDict()
        self.initStats()

    def initStats(self):
        self.stats['num_queries'] = 0
        self.stats['num_reranks'] = 0
        self.stats['num_shown_items'] = 0
        self.stats['num_nonzero_scores'] = 0
        self.stats['num_unmodified_queries'] = 0

    def printStats(self, outFile=sys.stdout):
        for key, value in self.stats.items():
            print >> outFile, key + ' = ' + str(value)

    def makeRecord(self, query, top_scores_heap, reordered_shown_items):
        record = {}
        record['visitorid'] = query.visitorid
        record['wmsessionid'] = query.wmsessionid
        record['rawquery'] = query.rawquery
        record['searchattributes'] = query.searchattributes
        record['shown_items'] = query.shown_items
        record['clicked_shown_items'] = query.clicked_shown_items
        record['reordered_shown_items'] = reordered_shown_items
        record['num_promoted_items'] = len(top_scores_heap)
        return record

    # Determine the top k scores 
    def getTopScoresHeap(self, query):
        self.stats['num_queries'] += 1
        top_scores_heap = []
        for i in range(len(query.shown_items)):
            shownItem = query.shown_items[i]
            self.stats['num_shown_items'] += 1
            score = 0
            for j in range(len(query.previously_clicked_items)):
                # ignore previously clicked items themselves
                if query.previously_clicked_items[j] == shownItem:
                    score = 0
                    break
                score += self.simCalc.similarity(query.previously_clicked_items[j], \
                                                 query.shown_items[i])
            if score > 0:
                self.stats['num_nonzero_scores'] += 1
                heapq.heappush(top_scores_heap, (score, i))
                if len(top_scores_heap) > self.k:
                    heapq.heappop(top_scores_heap)

        if len(top_scores_heap) == 0:
            self.stats['num_unmodified_queries'] += 1
        self.stats['num_reranks'] += len(top_scores_heap)
        return top_scores_heap

    def reRankItems(self, query, top_scores_heap):
        if len(top_scores_heap) == 0:
            return query.shown_items
        top_scores = sorted(top_scores_heap, key=lambda tup: tup[0], reverse=True)
        top_score_idxs = sorted(top_scores_heap, key=lambda tup: tup[1])
        i = j = k = 0
        reranked_items = []
        while i < len(query.shown_items):
            if i < len(top_scores):
                index = top_scores[i][1]
                try:
                    item = query.shown_items[index]
                except IndexError:
                    print >> sys.stderr, 'index = ' + str(index)
                    print >> sys.stderr, 'len(query.shown_items) = ' + str(len(query.shown_items))
                    print >> sys.stderr, 'top_scores = ' + str(top_scores)
                    print >> sys.stderr, 'query.shown_items = ' + str(query.shown_items)
                    raise
                reranked_items.append(item)
                i += 1
            elif k < len(top_score_idxs):
                if j < top_score_idxs[k][1]:
                    reranked_items.append(query.shown_items[j])
                    i += 1
                    j += 1
                else:
                    j += 1
                    k += 1
            else:
                reranked_items.append(query.shown_items[j])
                i += 1
                j += 1
        return reranked_items

## stand-alone program ##

def parseArgs():
    from optparse import OptionParser, OptionGroup, HelpFormatter
    
    usage = "usage: %prog "\
            + "[-k N] "\
            + "[--coeff_queries X.X] "\
            + "[--coeff_clicks X.X] "\
            + "[--exp_queries X.X] "\
            + "[--exp_clicks X.X] "\
            + "[--index_queries <queries index filename>] "\
            + "[--dict_queries <queries dictionary filename>] " \
            + "[--index_clicks <clicks index filename>] "\
            + "[--dict_clicks <clicks dictionary filename>] " \
            + "[--score_dict_queries <queries score dictionary upload filename>] " \
            + "[--score_dump_queries <queries score dictionary dump filename>] " \
            + "[--score_dict_clicks <clicks score dictionary upload filename>] " \
            + "[--score_dump_clicks <clicks score dictionary dump filename>] " \
            + "[--verbose] " \
            + "<filename>"

    parser = OptionParser(usage=usage)
    helpFormatter = HelpFormatter(indent_increment=2,\
                                  max_help_position=10,\
                                  width=80,\
                                  short_first=1)

    rankGroup = OptionGroup(parser, "Ranking options")
    rankGroup.add_option("-k", dest="k", help="re-rank top k items")
    rankGroup.add_option("--coeff_queries", dest="coeff_queries",\
                         help="queries coefficient")
    rankGroup.add_option("--coeff_clicks", dest="coeff_clicks",\
                         help="clicks coefficient")
    rankGroup.add_option("--exp_queries", dest="exp_queries",\
                         help="queries exponent")
    rankGroup.add_option("--exp_clicks", dest="exp_clicks",\
                         help="clicks exponent")
    parser.add_option_group(rankGroup)

    fileGroup = OptionGroup(parser, "Index options")
    fileGroup.add_option("--index_queries", dest="indexQueriesFn",\
                         help="queries index filename")
    fileGroup.add_option("--dict_queries", dest="dictionaryQueriesFn",\
                         help="queries dictionary filename")
    fileGroup.add_option("--index_clicks", dest="indexClicksFn",\
                         help="clicks index filename")
    fileGroup.add_option("--dict_clicks", dest="dictionaryClicksFn",\
                         help="clicks dictionary filename")
    parser.add_option_group(fileGroup)

    scoreGroup = OptionGroup(parser, "Score options")
    scoreGroup.add_option("--score_dict_queries", dest="queries_score_dict_fname", \
                          help="queries score dictionary upload filename")
    scoreGroup.add_option("--score_dump_queries", dest="queries_score_dump_fname", \
                          help="queries score dictionary dump filename")
    scoreGroup.add_option("--score_dict_clicks", dest="clicks_score_dict_fname", \
                          help="clicks score dictionary upload filename")
    scoreGroup.add_option("--score_dump_clicks", dest="clicks_score_dump_fname", \
                          help="clicks score dictionary dump filename")
    parser.add_option_group(scoreGroup)

    verboseGroup = OptionGroup(parser, "Verbose")
    verboseGroup.add_option("-v", "--verbose", action="store_true",\
                            dest="verbose")
    verboseGroup.add_option("-q", "--quiet", action="store_false",\
                            dest="verbose")
    parser.add_option_group(verboseGroup)

    parser.set_defaults(k=1, coeff_queries=1.0, coeff_clicks=1.0,\
                        exp_queries=1.0, exp_clicks=1.0,\
                        indexQueriesFn=None, dictionaryQueriesFn=None,\
                        indexClicksFn=None, dictionaryClicksFn=None,\
                        queries_score_dict_fname=None, queries_score_dump_fname=None,\
                        clicks_score_dict_fname=None, clicks_score_dump_fname=None,\
                        verbose=False)

    (options, args) = parser.parse_args()

    if (len(args) > 1):
        parser.print_usage()
        sys.exit()

    return (options, args)

def main():
    (options, args) = parseArgs()
    if len(args) == 1:
        inputFile = open(args[0])
    else:
        inputFile = sys.stdin

    # Instantiate Similarity Calculator (expensive)
    simCalc = SimilarityCalculator(coeff_queries=float(options.coeff_queries),\
                                   coeff_clicks=float(options.coeff_clicks),\
                                   exp_queries=float(options.exp_queries),\
                                   exp_clicks=float(options.exp_clicks),\
                                   index_queries_fname=options.indexQueriesFn,\
                                   posting_dict_queries_fname=options.dictionaryQueriesFn,\
                                   index_clicks_fname=options.indexClicksFn,\
                                   posting_dict_clicks_fname=options.dictionaryClicksFn,\
                                   queries_score_dict_fname=options.queries_score_dict_fname,\
                                   queries_score_dump_fname=options.queries_score_dump_fname,\
                                   clicks_score_dict_fname=options.clicks_score_dict_fname,\
                                   clicks_score_dump_fname=options.clicks_score_dump_fname,\
                                   verbose=options.verbose)

    # Instantiate ReRanker (cheap)
    reRanker = ReRanker(simCalc, k=int(options.k), verbose=options.verbose)

    try:
        for line in inputFile:
            # Instantiate query object
            query = Query(line)

            # Compute top scores
            top_scores_heap = reRanker.getTopScoresHeap(query)

            # re-rank shown items
            reordered_shown_items = reRanker.reRankItems(query, top_scores_heap)

            # construct and print reordered_query record
            output = reRanker.makeRecord(query, top_scores_heap, reordered_shown_items)
            print json.dumps(output)
    except:
        reRanker.printStats(sys.stderr)
        raise

    if options.verbose:
        reRanker.printStats(sys.stderr)

if __name__ == '__main__':
    main()
