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
            + "[--index_queries <queries index filename>] "\
            + "[--dict_queries <queries dictionary filename>] " \
            + "[--index_clicks <clicks index filename>] "\
            + "[--dict_clicks <clicks dictionary filename>] "\
            + "[--verbose] "\
            + "<filename>"

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

    verboseGroup = OptionGroup(parser, "Verbose")
    verboseGroup.add_option("-v", "--verbose", action="store_true",\
                            dest="verbose")
    verboseGroup.add_option("-q", "--quiet", action="store_false",\
                            dest="verbose")
    parser.add_option_group(verboseGroup)

    parser.set_defaults(indexQueriesFn=None, dictionaryQueriesFn=None,\
                        indexClicksFn=None, dictionaryClicksFn=None,\
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
   
    # Instantiate Similarity Calculator
    simCalc = SimilarityCalculator(index_queries_fname=options.indexQueriesFn,\
                                   posting_dict_queries_fname=options.dictionaryQueriesFn,\
                                   index_clicks_fname=options.indexClicksFn,\
                                   posting_dict_clicks_fname=options.dictionaryClicksFn, \
                                   verbose=options.verbose) 
    
    for line in inputFile:
        try:
            query = Query(line)
            if query.previously_clicked_items == []:
                continue
            if query.clicked_shown_items == []:
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
