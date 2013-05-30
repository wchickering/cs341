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
import ReRanker
import SimilarityCalculator
import Query

def parseArgs():
    from optparse import OptionParser, OptionGroup, HelpFormatter
    
    usage = "usage: %prog "\
            + "[--workers N] "\
            + "[-k N] "\
            + "[--insert_position N] "\
            + "[--random] "\
            + "[--coeff_rank X.X] "\
            + "[--coeff_items X.X] "\
            + "[--coeff_queries X.X] "\
            + "[--coeff_clicks X.X] "\
            + "[--coeff_carts X.X] "\
            + "[--coeff_item_title X.X] "\
            + "[--exp_rank X.X] "\
            + "[--exp_items X.X] "\
            + "[--exp_queries X.X] "\
            + "[--exp_clicks X.X] "\
            + "[--exp_carts X.X] "\
            + "[--exp_item_title X.X] "\
            + "[--index_items <items index filename>] "\
            + "[--dict_items <items dictionary filename>] " \
            + "[--index_queries <queries index filename>] "\
            + "[--dict_queries <queries dictionary filename>] " \
            + "[--index_clicks <clicks index filename>] "\
            + "[--dict_clicks <clicks dictionary filename>] " \
            + "[--index_carts <carts index filename>] "\
            + "[--dict_carts <carts dictionary filename>] " \
            + "[--index_item_title <item_title index filename>] "\
            + "[--dict_item_title <item_title dictionary filename>] " \
            + "[--score_dict_items <items score dictionary upload filename>] " \
            + "[--score_dump_items <items score dictionary dump filename>] " \
            + "[--score_dict_queries <queries score dictionary upload filename>] " \
            + "[--score_dump_queries <queries score dictionary dump filename>] " \
            + "[--score_dict_clicks <clicks score dictionary upload filename>] " \
            + "[--score_dump_clicks <clicks score dictionary dump filename>] " \
            + "[--score_dict_carts <carts score dictionary upload filename>] " \
            + "[--score_dump_carts <carts score dictionary dump filename>] " \
            + "[--score_dict_item_title <item_title score dictionary upload filename>] " \
            + "[--score_dump_item_title <item_title score dictionary dump filename>] " \
            + "[--verbose] " \
            + "<filename>"

    parser = OptionParser(usage=usage)
    helpFormatter = HelpFormatter(indent_increment=2,\
                                  max_help_position=10,\
                                  width=80,\
                                  short_first=1)

    rankGroup = OptionGroup(parser, "Ranking options")
    rankGroup.add_option("-k", type="int", dest="k", help="re-rank top k items")
    rankGroup.add_option("--insert_position", type="int", dest="insert_position",\
                         help="insert re-ranked items before this position")
    rankGroup.add_option("--random", action="store_true", dest="random",\
                         help="apply random scores to all shown items")
    rankGroup.add_option("--coeff_rank", type="float", dest="coeff_rank",\
                         help="rank coefficient")
    rankGroup.add_option("--coeff_items", type="float", dest="coeff_items",\
                         help="items coefficient")
    rankGroup.add_option("--coeff_queries", type="float", dest="coeff_queries",\
                         help="queries coefficient")
    rankGroup.add_option("--coeff_clicks", type="float", dest="coeff_clicks",\
                         help="clicks coefficient")
    rankGroup.add_option("--coeff_carts", type="float", dest="coeff_carts",\
                         help="carts coefficient")
    rankGroup.add_option("--coeff_item_title", type="float", dest="coeff_item_title",\
                         help="item_title coefficient")
    rankGroup.add_option("--exp_rank", type="float", dest="exp_rank",\
                         help="rank exponent")
    rankGroup.add_option("--exp_items", type="float", dest="exp_items",\
                         help="items exponent")
    rankGroup.add_option("--exp_queries", type="float", dest="exp_queries",\
                         help="queries exponent")
    rankGroup.add_option("--exp_clicks", type="float", dest="exp_clicks",\
                         help="clicks exponent")
    rankGroup.add_option("--exp_carts", type="float", dest="exp_carts",\
                         help="carts exponent")
    rankGroup.add_option("--exp_item_title", type="float", dest="exp_item_title",\
                         help="item_title exponent")
    parser.add_option_group(rankGroup)

    fileGroup = OptionGroup(parser, "Index options")
    fileGroup.add_option("--index_items", dest="index_items_fname",\
                         help="items index filename")
    fileGroup.add_option("--dict_items", dest="posting_dict_items_fname",\
                         help="items dictionary filename")
    fileGroup.add_option("--index_queries", dest="index_queries_fname",\
                         help="queries index filename")
    fileGroup.add_option("--dict_queries", dest="posting_dict_queries_fname",\
                         help="queries dictionary filename")
    fileGroup.add_option("--index_clicks", dest="index_clicks_fname",\
                         help="clicks index filename")
    fileGroup.add_option("--dict_clicks", dest="posting_dict_clicks_fname",\
                         help="clicks dictionary filename")
    fileGroup.add_option("--index_carts", dest="index_carts_fname",\
                         help="carts index filename")
    fileGroup.add_option("--dict_carts", dest="posting_dict_carts_fname",\
                         help="carts dictionary filename")
    fileGroup.add_option("--index_item_title", dest="index_item_title_fname",\
                         help="item_title index filename")
    fileGroup.add_option("--dict_item_title", dest="posting_dict_item_title_fname",\
                         help="item_title dictionary filename")
    parser.add_option_group(fileGroup)

    scoreGroup = OptionGroup(parser, "Score options")
    scoreGroup.add_option("--score_dict_items", dest="items_score_dict_fname", \
                          help="items score dictionary upload filename")
    scoreGroup.add_option("--score_dump_items", dest="items_score_dump_fname", \
                          help="items score dictionary dump filename")
    scoreGroup.add_option("--score_dict_queries", dest="queries_score_dict_fname", \
                          help="queries score dictionary upload filename")
    scoreGroup.add_option("--score_dump_queries", dest="queries_score_dump_fname", \
                          help="queries score dictionary dump filename")
    scoreGroup.add_option("--score_dict_clicks", dest="clicks_score_dict_fname", \
                          help="clicks score dictionary upload filename")
    scoreGroup.add_option("--score_dump_clicks", dest="clicks_score_dump_fname", \
                          help="clicks score dictionary dump filename")
    scoreGroup.add_option("--score_dict_carts", dest="carts_score_dict_fname", \
                          help="carts score dictionary upload filename")
    scoreGroup.add_option("--score_dump_carts", dest="carts_score_dump_fname", \
                          help="carts score dictionary dump filename")
    scoreGroup.add_option("--score_dict_item_title", dest="item_title_score_dict_fname", \
                          help="item_title score dictionary upload filename")
    scoreGroup.add_option("--score_dump_item_title", dest="item_title_score_dump_fname", \
                          help="item_title score dictionary dump filename")
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

    parser.set_defaults(k=1, insert_position=0, random=False,\
                        coeff_rank=0.0, coeff_items=0.0, coeff_queries=0.0,\
                        coeff_clicks=0.0, coeff_carts=0.0, coeff_item_title=0.0,\
                        exp_rank=1.0, exp_items=1.0, exp_queries=1.0,\
                        exp_clicks=1.0, exp_carts=1.0, exp_item_title=1.0,\
                        index_items_fname=None, posting_dict_items_fname=None,\
                        index_queries_fname=None, posting_dict_queries_fname=None,\
                        index_clicks_fname=None, posting_dict_clicks_fname=None,\
                        index_carts_fname=None, posting_dict_carts_fname=None,\
                        index_item_title_fname=None, posting_dict_item_title_fname=None,\
                        items_score_dict_fname=None, items_score_dump_fname=None,\
                        queries_score_dict_fname=None, queries_score_dump_fname=None,\
                        clicks_score_dict_fname=None, clicks_score_dump_fname=None,\
                        carts_score_dict_fname=None, carts_score_dump_fname=None,\
                        item_title_score_dict_fname=None, item_title_score_dump_fname=None,\
                        workers=1, verbose=False)

    (options, args) = parser.parse_args()

    if (len(args) > 1):
        parser.print_usage()
        sys.exit()

    return (options, args)

def reRank(reRanker, test_data, random=False):
    records = []
    for line in test_data:
        # Instantiate query object
        query = Query.Query(line)

        # Compute top scores
        if random:
            top_scores_heap = reRanker.getRandomTopScoresHeap(query)
        else:
            top_scores_heap = reRanker.getTopScoresHeap(query)

        # re-rank shown items
        (num_reranks, reordered_shown_items) =\
                                   reRanker.reRankItems(query, top_scores_heap)

        # construct reordered_query record
        records.append(reRanker.makeRecord(query, num_reranks, reordered_shown_items))

    return records

def singleReRank(test_data, k=1, insert_position=0, coeff_rank=0.0, coeff_items=0.0,\
           coeff_queries=0.0, coeff_clicks=0.0, coeff_carts=0.0, coeff_item_title=0.0,\
           exp_rank=1.0, exp_items=1.0, exp_queries=1.0,\
           exp_clicks=1.0, exp_carts=1.0, exp_item_title=1.0,\
           index_items_fname=None, posting_dict_items_fname=None,\
           index_queries_fname=None, posting_dict_queries_fname=None,\
           index_clicks_fname=None, posting_dict_clicks_fname=None,\
           index_carts_fname=None, posting_dict_carts_fname=None,\
           index_item_title_fname=None, posting_dict_item_title_fname=None,\
           items_score_dict_fname=None, items_score_dump_fname=None,\
           queries_score_dict_fname=None, queries_score_dump_fname=None,\
           clicks_score_dict_fname=None, clicks_score_dump_fname=None,\
           carts_score_dict_fname=None, carts_score_dump_fname=None,\
           item_title_score_dict_fname=None, item_title_score_dump_fname=None,\
           random=False, verbose=False):

    # Instantiate Similarity Calculator (expensive)
    simCalc = SimilarityCalculator.SimilarityCalculator(\
                      coeff_items=coeff_items,\
                      coeff_queries=coeff_queries,\
                      coeff_clicks=coeff_clicks,\
                      coeff_carts=coeff_carts,\
                      coeff_item_title=coeff_item_title,\
                      exp_items=exp_items,\
                      exp_queries=exp_queries,\
                      exp_clicks=exp_clicks,\
                      exp_carts=exp_carts,\
                      exp_item_title=exp_item_title,\
                      index_items_fname=index_items_fname,\
                      posting_dict_items_fname=posting_dict_items_fname,\
                      index_queries_fname=index_queries_fname,\
                      posting_dict_queries_fname=posting_dict_queries_fname,\
                      index_clicks_fname=index_clicks_fname,\
                      posting_dict_clicks_fname=posting_dict_clicks_fname,\
                      index_carts_fname=index_carts_fname,\
                      posting_dict_carts_fname=posting_dict_carts_fname,\
                      index_item_title_fname=index_item_title_fname,\
                      posting_dict_item_title_fname=posting_dict_item_title_fname,\
                      items_score_dict_fname=items_score_dict_fname,\
                      items_score_dump_fname=items_score_dump_fname,\
                      queries_score_dict_fname=queries_score_dict_fname,\
                      queries_score_dump_fname=queries_score_dump_fname,\
                      clicks_score_dict_fname=clicks_score_dict_fname,\
                      clicks_score_dump_fname=clicks_score_dump_fname,\
                      carts_score_dict_fname=carts_score_dict_fname,\
                      carts_score_dump_fname=carts_score_dump_fname,\
                      item_title_score_dict_fname=item_title_score_dict_fname,\
                      item_title_score_dump_fname=item_title_score_dump_fname,\
                      verbose=verbose)

    # Instantiate ReRanker (cheap)
    reRanker = ReRanker.ReRanker(simCalc, k=k, insert_position=insert_position,\
                      coeff_rank=coeff_rank, exp_rank=exp_rank, verbose=verbose)

    return reRank(reRanker, test_data, random)

def main():
    (options, args) = parseArgs()
    if len(args) == 1:
        inputFile = open(args[0])
    else:
        inputFile = sys.stdin

    if options.workers == 1: #### single process ####

        records = singleReRank(inputFile, options.k, options.insert_position,\
                       coeff_rank=options.coeff_rank,\
                       coeff_items=options.coeff_items,\
                       coeff_queries=options.coeff_queries,\
                       coeff_clicks=options.coeff_clicks,\
                       coeff_carts=options.coeff_carts,\
                       coeff_item_title=options.coeff_item_title,\
                       exp_rank=options.exp_rank,\
                       exp_items=options.exp_items,\
                       exp_queries=options.exp_queries,\
                       exp_clicks=options.exp_clicks,\
                       exp_carts=options.exp_carts,\
                       exp_item_title=options.exp_item_title,\
                       index_items_fname=options.index_items_fname,\
                       posting_dict_items_fname=options.posting_dict_items_fname,\
                       index_queries_fname=options.index_queries_fname,\
                       posting_dict_queries_fname=options.posting_dict_queries_fname,\
                       index_clicks_fname=options.index_clicks_fname,\
                       posting_dict_clicks_fname=options.posting_dict_clicks_fname,\
                       index_carts_fname=options.index_carts_fname,\
                       posting_dict_carts_fname=options.posting_dict_carts_fname,\
                       index_item_title_fname=options.index_item_title_fname,\
                       posting_dict_item_title_fname=options.posting_dict_item_title_fname,\
                       items_score_dict_fname=options.items_score_dict_fname,\
                       items_score_dump_fname=options.items_score_dump_fname,\
                       queries_score_dict_fname=options.queries_score_dict_fname,\
                       queries_score_dump_fname=options.queries_score_dump_fname,\
                       clicks_score_dict_fname=options.clicks_score_dict_fname,\
                       clicks_score_dump_fname=options.clicks_score_dump_fname,\
                       carts_score_dict_fname=options.carts_score_dict_fname,\
                       carts_score_dump_fname=options.carts_score_dump_fname,\
                       item_title_score_dict_fname=options.item_title_score_dict_fname,\
                       item_title_score_dump_fname=options.item_title_score_dump_fname,\
                       random=options.random,\
                       verbose=options.verbose)
        for record in records:
            print json.dumps(record)

    else: #### multi-process ####
       
        # read input into memory
        test_data = inputFile.readlines()

        # tuple of all parallel python servers to connect with
        ppservers = ()

        # create jobserver with four workers
        job_server = pp.Server(options.workers, ppservers=ppservers, secret="")

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
            items_score_dump_fname = None
            if options.items_score_dump_fname:
                items_score_dump_fname =\
                    options.items_score_dump_fname + '.' + str(workerNum)
            queries_score_dict_fname = None
            if options.queries_score_dict_fname:
                queries_score_dict_fname =\
                    options.queries_score_dict_fname + '.' + str(workerNum)
            queries_score_dump_fname = None
            if options.queries_score_dump_fname:
                queries_score_dump_fname =\
                    options.queries_score_dump_fname + '.' + str(workerNum)
            clicks_score_dict_fname = None
            if options.clicks_score_dict_fname:
                clicks_score_dict_fname =\
                    options.clicks_score_dict_fname + '.' + str(workerNum)
            clicks_score_dump_fname = None
            if options.clicks_score_dump_fname:
                clicks_score_dump_fname =\
                    options.clicks_score_dump_fname + '.' + str(workerNum)
            carts_score_dict_fname = None
            if options.carts_score_dict_fname:
                carts_score_dict_fname =\
                    options.carts_score_dict_fname + '.' + str(workerNum)
            carts_score_dump_fname = None
            if options.carts_score_dump_fname:
                carts_score_dump_fname =\
                    options.carts_score_dump_fname + '.' + str(workerNum)
            item_title_score_dict_fname = None
            if options.item_title_score_dict_fname:
                item_title_score_dict_fname =\
                    options.item_title_score_dict_fname + '.' + str(workerNum)
            item_title_score_dump_fname = None
            if options.item_title_score_dump_fname:
                item_title_score_dump_fname =\
                    options.item_title_score_dump_fname + '.' + str(workerNum)

            jobs.append(job_server.submit(singleReRank, \
                               (test_data[data_submitted:data_submitted + data_this_job],\
                                options.k,\
                                options.insert_position,\
                                options.coeff_rank,\
                                options.coeff_items,\
                                options.coeff_queries,\
                                options.coeff_clicks,\
                                options.coeff_carts,\
                                options.coeff_item_title,\
                                options.exp_rank,\
                                options.exp_items,\
                                options.exp_queries,\
                                options.exp_clicks,\
                                options.exp_carts,\
                                options.exp_item_title,\
                                options.index_items_fname,\
                                options.posting_dict_items_fname,\
                                options.index_queries_fname,\
                                options.posting_dict_queries_fname,\
                                options.index_clicks_fname,\
                                options.posting_dict_clicks_fname,\
                                options.index_carts_fname,\
                                options.posting_dict_carts_fname,\
                                options.index_item_title_fname,\
                                options.posting_dict_item_title_fname,\
                                items_score_dict_fname,\
                                items_score_dump_fname,\
                                queries_score_dict_fname,\
                                queries_score_dump_fname,\
                                clicks_score_dict_fname,\
                                clicks_score_dump_fname,\
                                carts_score_dict_fname,\
                                carts_score_dump_fname,\
                                item_title_score_dict_fname,\
                                item_title_score_dump_fname,\
                                options.random,\
                                False),\
                        (reRank,),\
                        ('ReRanker', 'SimilarityCalculator', 'Query')))
            data_submitted += data_this_job

        # print output from jobs
        for job in jobs:
            for record in job():
                print json.dumps(record)

if __name__ == '__main__':
    main()
