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

# import local modules
from SimilarityCalculator import SimilarityCalculator
from Query import Query

# global stats
num_reranks = 0
num_shown_items = 0
num_nonzero_scores = 0
num_unmodified_queries = 0

def parseArgs():
    from optparse import OptionParser, OptionGroup, HelpFormatter
    
    usage = "usage: %prog [options] "\
            + "--index <index filename> "\
            + "--dict <dictionary filename> " \
            + "[-k N] "\
            + "[--score_dict <score dictionary upload filename> " \
            + "[--score_dump <score dictionary dump filename> " \
            + "[--verbose] " \
            + "<filename>"

    parser = OptionParser(usage=usage)
    helpFormatter = HelpFormatter(indent_increment=2,\
                                  max_help_position=10,\
                                  width=80,\
                                  short_first=1)

    verboseGroup = OptionGroup(parser, "Verbose")
    verboseGroup.add_option("-v", "--verbose", action="store_true",\
                            dest="verbose")
    verboseGroup.add_option("-q", "--quiet", action="store_false",\
                            dest="verbose")
    parser.add_option_group(verboseGroup)

    fileGroup = OptionGroup(parser, "Index options")
    fileGroup.add_option("--index", dest="indexFn", help="index filename")
    parser.add_option_group(fileGroup)
    fileGroup.add_option("--dict", dest="dictionaryFn", help="dictionary filename")
    parser.add_option_group(fileGroup)

    rankGroup = OptionGroup(parser, "Ranking options")
    rankGroup.add_option("-k", dest="k", help="re-rank top k items")
    parser.add_option_group(rankGroup)

    scoreGroup = OptionGroup(parser, "Score options")
    scoreGroup.add_option("--score_dict", dest="score_dict_fname", \
                          help="score dictionary upload filename")
    scoreGroup.add_option("--score_dump", dest="score_dump_fname", \
                          help="score dictionary dump filename")
    parser.add_option_group(scoreGroup)

    parser.set_defaults(verbose=False, k=1, indexFn=None, dictionaryFn=None,\
                        score_dict_fname=None, score_dump_fname=None)

    (options, args) = parser.parse_args()

    if (len(args) > 1):
        parser.print_usage()
        sys.exit()

    if ((not options.indexFn) or (not options.dictionaryFn)):
        parser.print_usage()
        sys.exit()

    return (options, args)

def printStats():
    print >> sys.stderr, 'num_reranks = ' + str(num_reranks)
    print >> sys.stderr, 'num_shown_items = ' + str(num_shown_items)
    print >> sys.stderr, 'num_nonzero_scores = ' + str(num_nonzero_scores)
    print >> sys.stderr, 'num_unmodified_queries = ' + str(num_unmodified_queries)

def getTopScoresHeap(simCalc, query, options):
    global num_reranks
    global num_shown_items
    global num_nonzero_scores

    # Determine the top k scores 
    top_scores_heap = []
    for i in range(len(query.shown_items)):
        shownItem = query.shown_items[i]
        num_shown_items += 1
        score = 0
        for j in range(len(query.previously_clicked_items)):
            # ignore previously clicked items themselves
            if query.previously_clicked_items[j] == shownItem:
                score = 0
                break
            score += simCalc.similarity(query.previously_clicked_items[j], \
                                        query.shown_items[i])
        if score > 0:
            num_nonzero_scores += 1
            heapq.heappush(top_scores_heap, (score, i))
            if len(top_scores_heap) > int(options.k):
                heapq.heappop(top_scores_heap)
    return top_scores_heap

def reRankItems(query, top_scores_heap):
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

def main():
    global num_reranks
    global num_unmodified_queries

    (options, args) = parseArgs()
    if len(args) == 1:
        inputFile = open(args[0])
    else:
        inputFile = sys.stdin

    # Instantiate Similarity Calculator
    simCalc = SimilarityCalculator(options.indexFn, options.dictionaryFn, \
                                   score_dict_fname=options.score_dict_fname, \
                                   score_dump_fname=options.score_dump_fname, \
                                   verbose=options.verbose)

    try:
        for line in inputFile:
            # Instantiate query object
            query = Query(line)

            # Compute top scores
            top_scores_heap = getTopScoresHeap(simCalc, query, options)
            if len(top_scores_heap) == 0:
                num_unmodified_queries += 1
            num_reranks += len(top_scores_heap)

            # re-rank shown items
            reordered_shown_items = reRankItems(query, top_scores_heap)

            # write output
            output = {}
            output['visitorid'] = query.visitorid
            output['wmsessionid'] = query.wmsessionid
            output['rawquery'] = query.rawquery
            output['searchattributes'] = query.searchattributes
            output['shown_items'] = query.shown_items
            output['clicked_shown_items'] = query.clicked_shown_items
            output['reordered_shown_items'] = reordered_shown_items
            print json.dumps(output)
    except:
        printStats()
        raise

    if options.verbose:
        printStats()

if __name__ == '__main__':
    main()
