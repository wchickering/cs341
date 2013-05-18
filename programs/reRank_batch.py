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

# import local modules
from SimilarityCalculator import SimilarityCalculator
from ReRanker import ReRanker
from Evaluator import Evaluator
from Query import Query

def parseArgs():
    from optparse import OptionParser, OptionGroup, HelpFormatter
    
    usage = "usage: %prog "\
            + "[--index_queries <queries index filename>] "\
            + "[--dict_queries <queries dictionary filename>] " \
            + "[--index_clicks <clicks index filename>] "\
            + "[--dict_clicks <clicks dictionary filename>] " \
            + "[--score_dict_queries <queries score dictionary upload filename>] " \
            + "[--score_dump_queries <queries score dictionary dump filename>] " \
            + "[--score_dict_clicks <clicks score dictionary upload filename>] " \
            + "[--score_dump_clicks <clicks score dictionary dump filename>] " \
            + "[--in_memory] " \
            + "[--verbose] " \
            + "<param_filename>" \
            + "<data_filename>"

    parser = OptionParser(usage=usage)
    helpFormatter = HelpFormatter(indent_increment=2,\
                                  max_help_position=10,\
                                  width=80,\
                                  short_first=1)

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

    batchGroup = OptionGroup(parser, "Batch options")
    batchGroup.add_option("--in_memory", action="store_true",\
                            dest="in_memory")
    parser.add_option_group(batchGroup)

    verboseGroup = OptionGroup(parser, "Verbose")
    verboseGroup.add_option("-v", "--verbose", action="store_true",\
                            dest="verbose")
    verboseGroup.add_option("-q", "--quiet", action="store_false",\
                            dest="verbose")
    parser.add_option_group(verboseGroup)

    parser.set_defaults(indexQueriesFn=None, dictionaryQueriesFn=None,\
                        indexClicksFn=None, dictionaryClicksFn=None,\
                        queries_score_dict_fname=None, queries_score_dump_fname=None,\
                        clicks_score_dict_fname=None, clicks_score_dump_fname=None,\
                        in_memory=False, verbose=False)

    (options, args) = parser.parse_args()

    if (len(args) < 1 or len(args) > 2):
        parser.print_usage()
        sys.exit()

    return (options, args)

def main():
    (options, args) = parseArgs()
    paramFile = open(args[0])
    if len(args) == 2:
        inputFile = open(args[1])
    else:
        inputFile = sys.stdin

    if options.in_memory:
        test_data = inputFile.readlines()
        output = []
    else:
        test_data = inputFile

    # Instantiate Similarity Calculator (expensive)
    simCalc = SimilarityCalculator(index_queries_fname=options.indexQueriesFn,\
                                   posting_dict_queries_fname=options.dictionaryQueriesFn,\
                                   index_clicks_fname=options.indexClicksFn,\
                                   posting_dict_clicks_fname=options.dictionaryClicksFn,\
                                   queries_score_dict_fname=options.queries_score_dict_fname,\
                                   queries_score_dump_fname=options.queries_score_dump_fname,\
                                   clicks_score_dict_fname=options.clicks_score_dict_fname,\
                                   clicks_score_dump_fname=options.clicks_score_dump_fname,\
                                   verbose=options.verbose)

    lineNum = 0
    for line in paramFile:
        lineNum += 1
        try:
            params = json.loads(line)
        except:
            print >> sys.stderr, 'Failed to parse params on line ' + str(lineNum) + ': '
            print >> sys.stderr, line
            raise

        simCalc.setParams(coeff_queries = params['coeff_queries'],\
                          coeff_clicks = params['coeff_clicks'],\
                          exp_queries = params['exp_queries'],\
                          exp_clicks = params['exp_clicks'])

        # Instantiate ReRanker (cheap)
        reRanker = ReRanker(simCalc, k=params['k'], verbose=options.verbose)

        # Instantiate Evaluator (cheap)
        evaluator = Evaluator(k=params['k'])

        # If not processing test_data entirely in memory, fseek to beginning of file.
        if not options.in_memory:
            inputFile.seek(0)

        try:
            lineNum = 0
            for line in test_data:
                lineNum += 1

                # Instantiate query object
                query = Query(line)

                # Compute top scores
                top_scores_heap = reRanker.getTopScoresHeap(query)
                assert(reRanker.stats['num_queries'] == lineNum)

                # re-rank shown items
                reordered_shown_items = reRanker.reRankItems(query, top_scores_heap)

                # construct reordered_query record
                record = reRanker.makeRecord(query, top_scores_heap, reordered_shown_items)

                # evaluate reordered_query record
                evaluator.processRecord(record)
                assert(evaluator.stats['num_queries'] == lineNum)
        except:
            reRanker.printStats(sys.stderr)
            evaluator.printStats(sys.stderr)
            raise

        evaluator.computeAverages()

        # print stats
        if options.in_memory:
            output.append(json.dumps(params))
            output.append(json.dumps(reRanker.stats))
            output.append(json.dumps(evaluator.stats))
        else:
            print json.dumps(params)
            print json.dumps(reRanker.stats)
            print json.dumps(evaluator.stats)

    if options.in_memory:
        for line in output:
            print line 

if __name__ == '__main__':
    main()
