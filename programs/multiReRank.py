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
import ReRanker
import Evaluator
import Query

def parseArgs():
    from optparse import OptionParser, OptionGroup, HelpFormatter
    
    usage = "usage: %prog "\
            + "[--workers N] "\
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

    parser.set_defaults(indexQueriesFn=None, dictionaryQueriesFn=None,\
                        indexClicksFn=None, dictionaryClicksFn=None,\
                        queries_score_dict_fname=None, queries_score_dump_fname=None,\
                        clicks_score_dict_fname=None, clicks_score_dump_fname=None,\
                        workers=1, verbose=False)

    (options, args) = parser.parse_args()

    if (len(args) < 1 or len(args) > 2):
        parser.print_usage()
        sys.exit()

    return (options, args)

def multiReRank(test_data, paramsList,\
                index_queries_fname=None, posting_dict_queries_fname=None,\
                index_clicks_fname=None, posting_dict_clicks_fname=None,\
                queries_score_dict_fname=None, queries_score_dump_fname=None,\
                clicks_score_dict_fname=None, clicks_score_dump_fname=None,\
                verbose=False):

    # Instantiate Similarity Calculator (expensive)
    simCalc = SimilarityCalculator.SimilarityCalculator(\
                      index_queries_fname=index_queries_fname,\
                      posting_dict_queries_fname=posting_dict_queries_fname,\
                      index_clicks_fname=index_clicks_fname,\
                      posting_dict_clicks_fname=posting_dict_clicks_fname,\
                      queries_score_dict_fname=queries_score_dict_fname,\
                      queries_score_dump_fname=queries_score_dump_fname,\
                      clicks_score_dict_fname=clicks_score_dict_fname,\
                      clicks_score_dump_fname=clicks_score_dump_fname,\
                      verbose=verbose)

    statsList = []
    runNum = 0
    for params in paramsList:
        runNum += 1

        simCalc.setParams(coeff_queries = params['coeff_queries'],\
                          coeff_clicks = params['coeff_clicks'],\
                          exp_queries = params['exp_queries'],\
                          exp_clicks = params['exp_clicks'])

        # Instantiate ReRanker (cheap)
        reRanker = ReRanker.ReRanker(simCalc, k=params['k'], verbose=verbose)

        # Instantiate Evaluator (cheap)
        evaluator = Evaluator.Evaluator(k=params['k'])

        try:
            lineNum = 0
            for line in test_data:
                lineNum += 1

                # Instantiate query object
                query = Query.Query(line)

                # Compute top scores
                top_scores_heap = reRanker.getTopScoresHeap(query)

                # re-rank shown items
                reordered_shown_items = reRanker.reRankItems(query, top_scores_heap)

                # construct reordered_query record
                record = reRanker.makeRecord(query, top_scores_heap, reordered_shown_items)

                # evaluate reordered_query record
                evaluator.processRecord(record)
        except:
            reRanker.printStats(sys.stderr)
            evaluator.printStats(sys.stderr)
            raise

        statsList.append(evaluator.stats)

    return statsList

def main():
    (options, args) = parseArgs()
    paramFile = open(args[0])
    if len(args) == 2:
        inputFile = open(args[1])
    else:
        inputFile = sys.stdin

    # read params into memory
    paramsList = []
    for line in paramFile:
        paramsList.append(json.loads(line))

    # read test data into memory
    test_data = inputFile.readlines()

    if options.workers == 1: #### single process ####

        statsList = multiReRank(test_data,\
                                paramsList,\
                                index_queries_fname=options.indexQueriesFn,\
                                posting_dict_queries_fname=options.dictionaryQueriesFn,\
                                index_clicks_fname=options.indexClicksFn,\
                                posting_dict_clicks_fname=options.dictionaryClicksFn,\
                                queries_score_dict_fname=options.queries_score_dict_fname,\
                                queries_score_dump_fname=options.queries_score_dump_fname,\
                                clicks_score_dict_fname=options.clicks_score_dict_fname,\
                                clicks_score_dump_fname=options.clicks_score_dump_fname,\
                                verbose=options.verbose)

        evaluators = []
        for i in range(len(paramsList)):
            evaluators.append(Evaluator.Evaluator(k=paramsList[i]['k'], stats=statsList[i]))
            evaluators[i].computeAverages()

        # output results
        for i in range(len(paramsList)):
            print json.dumps([paramsList[i], evaluators[i].stats])

    else: #### multi-process ####

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

            # submit job
            jobs.append(job_server.submit(multiReRank, \
                               (test_data[data_submitted:data_submitted + data_this_job],\
                                paramsList,\
                                options.indexQueriesFn,\
                                options.dictionaryQueriesFn,\
                                options.indexClicksFn,\
                                options.dictionaryClicksFn,\
                                queries_score_dict_fname,\
                                queries_score_dump_fname,\
                                clicks_score_dict_fname,\
                                clicks_score_dump_fname,\
                                False),\
                        (),\
                        ('ReRanker', 'Evaluator', 'SimilarityCalculator', 'Query')))
            data_submitted += data_this_job

        # aggregate results
        evaluators = []
        for params in paramsList:
            evaluators.append(Evaluator.Evaluator(k=params['k']))
        for job in jobs:
            statsList = job()
            if not statsList:
                print >> sys.stderr, 'ERROR: Job failure!'
            for i in range(len(paramsList)):
                evaluators[i].mergeStats(statsList[i])
        for i in range(len(paramsList)):
            evaluators[i].computeAverages()

        # output results
        for i in range(len(paramsList)):
            print json.dumps([paramsList[i], evaluators[i].stats])

if __name__ == '__main__':
    main()
