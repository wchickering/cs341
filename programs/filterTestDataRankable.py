#!/usr/bin/env python

import sys

# import local modules
from Query import Query
from SimilarityCalculator import SimilarityCalculator

class BreakoutException(Exception):
    def __init__(self):
        pass
    def __str__(self):
        return ""

def parseArgs():
    from optparse import OptionParser, OptionGroup, HelpFormatter

    usage = "usage: %prog "\
            + "[--index_items <items index filename>] "\
            + "[--dict_items <items dictionary filename>] " \
            + "[--index_queries <queries index filename>] "\
            + "[--dict_queries <queries dictionary filename>] " \
            + "[--index_clicks <clicks index filename>] "\
            + "[--dict_clicks <clicks dictionary filename>] "\
            + "[--index_carts <carts index filename>] "\
            + "[--dict_carts <carts dictionary filename>] "\
            + "[--index_item_title <item_title index filename>] "\
            + "[--dict_item_title <item_title dictionary filename>] "\
            + "[--verbose] "\
            + "<filename>"

    parser = OptionParser(usage=usage)
    helpFormatter = HelpFormatter(indent_increment=2,\
                                  max_help_position=10,\
                                  width=80,\
                                  short_first=1)

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

    verboseGroup = OptionGroup(parser, "Verbose")
    verboseGroup.add_option("-v", "--verbose", action="store_true",\
                            dest="verbose")
    verboseGroup.add_option("-q", "--quiet", action="store_false",\
                            dest="verbose")
    parser.add_option_group(verboseGroup)

    parser.set_defaults(index_items_fname=None, posting_dict_items_fname=None,\
                        index_queries_fname=None, posting_dict_queries_fname=None,\
                        index_clicks_fname=None, posting_dict_clicks_fname=None,\
                        index_carts_fname=None, posting_dict_carts_fname=None,\
                        index_item_title_fname=None, posting_dict_item_title_fname=None,\
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

    # Only filter using provided indexes
    coeff_items = 1.0
    if not options.index_items_fname:
        coeff_items = 0.0
    coeff_queries = 1.0
    if not options.index_queries_fname:
        coeff_queries = 0.0
    coeff_clicks = 1.0
    if not options.index_clicks_fname:
        coeff_clicks = 0.0
    coeff_carts = 1.0
    if not options.index_carts_fname:
        coeff_carts = 0.0
    coeff_item_title = 1.0
    if not options.index_item_title_fname:
        coeff_item_title = 0.0
   
    # Instantiate Similarity Calculator
    simCalc = SimilarityCalculator(coeff_items=coeff_items,\
                                   coeff_queries=coeff_queries,\
                                   coeff_clicks=coeff_clicks,\
                                   coeff_carts=coeff_carts,\
                                   coeff_item_title=coeff_item_title,\
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
                                   verbose=options.verbose) 
    
    for line in inputFile:
        try:
            query = Query(line)
            if query.previously_clicked_items == []:
                continue
    
            for shownItem in query.shown_items:
                if shownItem in query.previously_clicked_items:
                    continue
                for prevItem in query.previously_clicked_items:
                    if simCalc.similarity(prevItem, shownItem) > 0.0:
                        print line.rstrip()
                        raise BreakoutException
        except BreakoutException:
            pass

if __name__ == '__main__':
    main()
