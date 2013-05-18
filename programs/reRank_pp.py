#!/usr/bin/env python
"""reorders the shown itmes for a query based on a user's previously clicked
items

"""

__author__ = """Charles Celerier <cceleri@cs.stanford.edu>,
              Bill Chickering <bchick@cs.stanford.edu>,
              Jamie Irvine <jirvine@cs.stanford.edu>"""

__date__ = """16 April 2013"""

# import standard modules
import sys
import json

# import non-standard modules
import pp

# import local modules
import SimilarityCalculator
import Query
import ReRanker

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
    rankGroup.add_option("-k", type="int", dest="k", help="re-rank top k items")
    rankGroup.add_option("--coeff_queries", type="float", dest="coeff_queries",\
                         help="queries coefficient")
    rankGroup.add_option("--coeff_clicks", type="float", dest="coeff_clicks",\
                         help="clicks coefficient")
    rankGroup.add_option("--exp_queries", type="float", dest="exp_queries",\
                         help="queries exponent")
    rankGroup.add_option("--exp_clicks", type="float", dest="exp_clicks",\
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

    ppGroup = OptionGroup(parser, "Parallel processing options")
    ppGroup.add_option("-w", "--workers", type="int", dest="workers", \
                       help="maximum number of worker processes to spawn")
    parser.add_option_group(ppGroup)

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
                        workers=1, verbose=False)

    (options, args) = parser.parse_args()

    if (len(args) > 1):
        parser.print_usage()
        sys.exit()

    return (options, args)

def reRank(test_data, k=1, coeff_queries=1.0, coeff_clicks=1.0,\
           exp_queries=1.0, exp_clicks=1.0,\
           index_queries_fname=None, posting_dict_queries_fname=None,\
           index_clicks_fname=None, posting_dict_clicks_fname=None,\
           queries_score_dict_fname=None, queries_score_dump_fname=None,\
           clicks_score_dict_fname=None, clicks_score_dump_fname=None,\
           verbose=False):

    # Instantiate Similarity Calculator (expensive)
    simCalc = SimilarityCalculator.SimilarityCalculator(\
                      coeff_queries=coeff_queries,\
                      coeff_clicks=coeff_clicks,\
                      exp_queries=exp_queries,\
                      exp_clicks=exp_clicks,\
                      index_queries_fname=index_queries_fname,\
                      posting_dict_queries_fname=posting_dict_queries_fname,\
                      index_clicks_fname=index_clicks_fname,\
                      posting_dict_clicks_fname=posting_dict_clicks_fname,\
                      queries_score_dict_fname=queries_score_dict_fname,\
                      queries_score_dump_fname=queries_score_dump_fname,\
                      clicks_score_dict_fname=clicks_score_dict_fname,\
                      clicks_score_dump_fname=clicks_score_dump_fname,\
                      verbose=verbose)

    # Instantiate ReRanker (cheap)
    reRanker = ReRanker.ReRanker(simCalc, k=k, verbose=verbose)

    records = []
    for line in test_data:
        # Instantiate query object
        query = Query.Query(line)

        # Compute top scores
        top_scores_heap = reRanker.getTopScoresHeap(query)

        # re-rank shown items
        reordered_shown_items = reRanker.reRankItems(query, top_scores_heap)

        # construct reordered_query record
        records.append(reRanker.makeRecord(query, top_scores_heap, reordered_shown_items))

    return records

def main():
    (options, args) = parseArgs()
    if len(args) == 1:
        inputFile = open(args[0])
    else:
        inputFile = sys.stdin

    # read input into memory
    test_data = inputFile.readlines()

    # tuple of all parallel python servers to connect with
    ppservers = ()

    # create jobserver with four workers
    job_server = pp.Server(options.workers, ppservers=ppservers)

    # determine number of data per job
    data_per_job = len(test_data) / options.workers
    if len(test_data) % options.workers != 0:
        data_per_job += 1

    # submit reRank jobs for execution
    data_submitted = 0
    jobs = []
    workerNum = 0
    while data_submitted < len(test_data):
        workerNum += 1
        if len(test_data) - data_submitted >= data_per_job:
            data_this_job = data_per_job
        else:
            data_this_job = len(test_data) - data_submitted

        # construct workerNum-dependent scores filenames
        queries_score_dict_fname = None
        if options.queries_score_dict_fname:
            queries_score_dict_fname = options.queries_score_dict_fname + '.' + str(workerNum)
        queries_score_dump_fname = None
        if options.queries_score_dump_fname:
            queries_score_dump_fname = options.queries_score_dump_fname + '.' + str(workerNum)
        clicks_score_dict_fname = None
        if options.clicks_score_dict_fname:
            clicks_score_dict_fname = options.clicks_score_dict_fname + '.' + str(workerNum)
        clicks_score_dump_fname = None
        if options.clicks_score_dump_fname:
            clicks_score_dump_fname = options.clicks_score_dump_fname + '.' + str(workerNum)
        
        jobs.append(job_server.submit(reRank, \
                           (test_data[data_submitted:data_submitted + data_this_job],\
                            options.k,\
                            options.coeff_queries,\
                            options.coeff_clicks,\
                            options.exp_queries,\
                            options.exp_clicks,\
                            options.indexQueriesFn,\
                            options.dictionaryQueriesFn,\
                            options.indexClicksFn,\
                            options.dictionaryClicksFn,\
                            queries_score_dict_fname,\
                            queries_score_dump_fname,\
                            clicks_score_dict_fname,\
                            clicks_score_dump_fname,\
                            False),\
                                (), ('Query', 'SimilarityCalculator', 'ReRanker')))
        data_submitted += data_this_job

    # print output from jobs
    for job in jobs:
        for record in job():
            print json.dumps(record)

if __name__ == '__main__':
    main()
