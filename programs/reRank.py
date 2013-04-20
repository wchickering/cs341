#!/usr/bin/env python
"""reorders the shown itmes for a query based on a user's previously clicked
items

"""

__author__ = """Charles Celerier <cceleri@cs.stanford.edu>,
              Bill Chickering <bchick@cs.stanford.edu>,
              Jamie Irvine <jirvine@cs.stanford.edu>"""

__date__ = """16 April 2013"""

import sys
import re, json

# import local modules
import Similarity as sim
import index_query as idx

class Query:
    """Represents information about a query

    Instance attributes
    ===================

    shown_items : list
        items shown to the user in a query
    previously_clicked_items : list
        previously clicked items by the user
    clicked_shown_items : list
        items the user clicked in this query

    Examples
    ========
    >>> import reRank as rr
    """
    def __init__(self, jsonStr):
        record = json.loads(jsonStr, parse_int=str)
        self.shown_items = record['shown_items']
        self.previously_clicked_items=record['previously_clicked_items']
        self.clicked_shown_items=record['clicked_shown_items']

    def __repr__(self):
        return "Query(%s)" % repr(json.dumps({\
                     "shown_items":self.shown_items,\
                     "previously_clicked_items":self.previously_clicked_items,\
                     "clicked_shown_items":self.clicked_shown_items}))


def reorderShownItems(query, indexFd, posting_dict, options):
    reorderedShownItems = []
    for shownItem in query.shown_items:
        reorderedShownItems.append([shownItem, 0])
        for previouslyClickedItem in query.previously_clicked_items:
            prevRawQueryIds = idx.get_posting(indexFd, posting_dict, previouslyClickedItem)
            shownItemRawQueryIds = idx.get_posting(indexFd, posting_dict, shownItem)
            if (options.JACCARD):
                reorderedShownItems[-1][1] += sim.jaccard(prevRawQueryIds,\
                                                          shownItemRawQueryIds)
    return [x[0] for x in sorted(reorderedShownItems, key=lambda a: a[1])]

def main():
    from optparse import OptionParser, OptionGroup, HelpFormatter
    import sys
    
    usage = "usage: %prog [options] --index <index filename> --dict <dictionary filename> <filename>"
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
                            
    metricsGroup = OptionGroup(parser, "Metrics")
    metricsGroup.add_option("-j", "--jaccard", action="store_true",\
                      dest="JACCARD",\
                      help="Jaccard similarity")

    parser.add_option_group(metricsGroup)

    fileGroup = OptionGroup(parser, "Index options")
    fileGroup.add_option("--index", dest="indexFn", help="index filename")
    parser.add_option_group(fileGroup)
    fileGroup.add_option("--dict", dest="dictionaryFn", help="dictionary filename")
    parser.add_option_group(fileGroup)

    parser.set_defaults(verbose=False, indexFn=None, dictionaryFn=None)

    (options, args) = parser.parse_args()

    numMetrics = 1 if options.JACCARD else 0

    if (len(args) == 0):
        inputFile = sys.stdin
    elif (len(args) == 1):
        inputFile = open(args[0])
    else:
        parser.print_usage()
        sys.exit()

    if ((not options.indexFn) or (not options.dictionaryFn)):
        parser.print_usage()
        sys.exit()

    if (numMetrics != 1):
        parser.print_usage()
        sys.exit()


    posting_dict_f = open(options.dictionaryFn)
    posting_dict = idx.get_posting_dict(posting_dict_f)
    indexFd = open(options.indexFn)

    for line in inputFile:
        query = Query(line)
        print "\t".join([str(query.shown_items), str(reorderShownItems(query, indexFd, posting_dict, options)), str(query.clicked_shown_items)])

    sys.exit()

if __name__ == '__main__':
    main()
