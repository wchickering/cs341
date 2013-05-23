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
            + "[--index_items <items index filename>] "\
            + "[--score_dict_items <items score dictionary upload filename>] " \
            + "[--score_dict_queries <queries score dictionary upload filename>] " \
            + "[--score_dict_clicks <clicks score dictionary upload filename>] " \
            + "[--score_dict_carts <carts score dictionary upload filename>] " \
            + "[--score_dict_item_title <item_title score dictionary upload filename>] " \
            + "<param_filename>" \
            + "<data_filename>"

    parser = OptionParser(usage=usage)
    helpFormatter = HelpFormatter(indent_increment=2,\
                                  max_help_position=10,\
                                  width=80,\
                                  short_first=1)

    scoreGroup = OptionGroup(parser, "Score options")
    scoreGroup.add_option("--score_dict_items", dest="items_score_dict_fname", \
                          help="items score dictionary upload filename")
    scoreGroup.add_option("--score_dict_queries", dest="queries_score_dict_fname", \
                          help="queries score dictionary upload filename")
    scoreGroup.add_option("--score_dict_clicks", dest="clicks_score_dict_fname", \
                          help="clicks score dictionary upload filename")
    scoreGroup.add_option("--score_dict_carts", dest="carts_score_dict_fname", \
                          help="carts score dictionary upload filename")
    scoreGroup.add_option("--score_dict_item_title", dest="item_title_score_dict_fname", \
                          help="item_title score dictionary upload filename")
    parser.add_option_group(scoreGroup)

    ppGroup = OptionGroup(parser, "Parallel processing options")
    ppGroup.add_option("-w", "--workers", type="int", dest="workers", \
                       help="maximum number of worker processes to spawn")
    parser.add_option_group(ppGroup)

    parser.set_defaults(items_score_dict_fname=None,\
                        queries_score_dict_fname=None,\
                        clicks_score_dict_fname=None,\
                        carts_score_dict_fname=None,\
                        item_title_score_dict_fname=None,\
                        workers=1)

    (options, args) = parser.parse_args()

    if (len(args) < 1 or len(args) > 2):
        parser.print_usage()
        sys.exit()

    return (options, args)

def multiReRank(test_data, paramsList,\
                items_score_dict_fname=None,\
                queries_score_dict_fname=None,\
                clicks_score_dict_fname=None,\
                carts_score_dict_fname=None,\
                item_title_score_dict_fname=None):

    # Instantiate Similarity Calculator (expensive)
    try:
        simCalc = SimilarityCalculator.SimilarityCalculator(\
                          items_score_dict_fname=items_score_dict_fname,\
                          queries_score_dict_fname=queries_score_dict_fname,\
                          clicks_score_dict_fname=clicks_score_dict_fname,\
                          carts_score_dict_fname=carts_score_dict_fname,\
                          item_title_score_dict_fname=item_title_score_dict_fname)
    except IOError:
        print >> sys.stderr, 'ERROR: Are you using the correct number of workers?'
        raise

    statsList = []
    runNum = 0
    for params in paramsList:
        runNum += 1

        simCalc.setParams(coeff_items = params['coeff_items'],\
                          coeff_queries = params['coeff_queries'],\
                          coeff_clicks = params['coeff_clicks'],\
                          coeff_carts = params['coeff_carts'],\
                          coeff_item_title = params['coeff_item_title'],\
                          exp_items = params['exp_items'],\
                          exp_queries = params['exp_queries'],\
                          exp_clicks = params['exp_clicks'],\
                          exp_carts = params['exp_carts'],\
                          exp_item_title = params['exp_item_title'])

        # Instantiate ReRanker (cheap)
        reRanker = ReRanker.ReRanker(simCalc,\
                          k=params['k'],\
                          insert_position=params['insert_position'],\
                          coeff_rank=params['coeff_rank'],\
                          exp_rank=params['exp_rank'])

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
                (num_reranks, reordered_shown_items) =\
                    reRanker.reRankItems(query, top_scores_heap)

                # construct reordered_query record
                record = reRanker.makeRecord(query, num_reranks, reordered_shown_items)

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

        statsList = \
            multiReRank(test_data,\
                        paramsList,\
                        items_score_dict_fname=options.items_score_dict_fname,\
                        queries_score_dict_fname=options.queries_score_dict_fname,\
                        clicks_score_dict_fname=options.clicks_score_dict_fname,\
                        carts_score_dict_fname=options.carts_score_dict_fname,\
                        item_title_score_dict_fname=options.item_title_score_dict_fname)

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
            items_score_dict_fname = None
            if options.items_score_dict_fname:
                items_score_dict_fname =\
                    options.items_score_dict_fname + '.' + str(workerNum)
            queries_score_dict_fname = None
            if options.queries_score_dict_fname:
                queries_score_dict_fname =\
                    options.queries_score_dict_fname + '.' + str(workerNum)
            clicks_score_dict_fname = None
            if options.clicks_score_dict_fname:
                clicks_score_dict_fname =\
                    options.clicks_score_dict_fname + '.' + str(workerNum)
            carts_score_dict_fname = None
            if options.carts_score_dict_fname:
                carts_score_dict_fname =\
                    options.carts_score_dict_fname + '.' + str(workerNum)
            item_title_score_dict_fname = None
            if options.item_title_score_dict_fname:
                item_title_score_dict_fname =\
                    options.item_title_score_dict_fname + '.' + str(workerNum)

            # submit job
            jobs.append(job_server.submit(multiReRank, \
                               (test_data[data_submitted:data_submitted + data_this_job],\
                                paramsList,\
                                items_score_dict_fname,\
                                queries_score_dict_fname,\
                                clicks_score_dict_fname,\
                                carts_score_dict_fname,\
                                item_title_score_dict_fname),\
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
