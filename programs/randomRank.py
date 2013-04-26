#!/usr/bin/env python
"""randomly reorders the shown itmes for a query 

"""

__author__ = """Charles Celerier <cceleri@cs.stanford.edu>,
              Bill Chickering <bchick@cs.stanford.edu>,
              Jamie Irvine <jirvine@cs.stanford.edu>"""

__date__ = """16 April 2013"""

import sys
import json
import random

# import local modules
from Query import Query

# global stats
num_reranks = 0
num_shown_items = 0

class NoRerankException(Exception):
    def __init__(self):
        pass
    def __str__(self):
        return ""

def printStats():
    print >> sys.stderr, 'num reranks = ' + str(num_reranks)
    print >> sys.stderr, 'num_shown_items = ' + str(num_shown_items)

def reorderShownItems(query, options):
    global num_reranks
    global num_shown_items

    num_shown_items += len(query.shown_items)

    # Choose an item at random and move to top.
    reranked_items = list(query.shown_items)
    for i in range(min(int(options.k), len(query.shown_items))):
        reranked_items.insert(0, reranked_items.pop(random.randint(0,len(reranked_items)-1)))
        num_reranks += 1

    return reranked_items

def main():
    from optparse import OptionParser, OptionGroup, HelpFormatter
    import sys
    
    usage = "usage: %prog [options] "\
            + "-k N " \
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
    verboseGroup.add_option("-m", "--markReordered", action="store_true",\
                            dest="markReordered")
    parser.add_option_group(verboseGroup)

    rankGroup = OptionGroup(parser, "Ranking options")
    rankGroup.add_option("-k", dest="k", help="re-rank top k items")
    parser.add_option_group(rankGroup)

    parser.set_defaults(verbose=False, k=1, markReordered=False)

    (options, args) = parser.parse_args()

    if (len(args) == 0):
        inputFile = sys.stdin
    elif (len(args) == 1):
        inputFile = open(args[0])
    else:
        parser.print_usage()
        sys.exit()

    try:
        for line in inputFile:
            query = Query(line)
            output = {}
            output['visitorid'] = query.visitorid
            output['wmsessionid'] = query.wmsessionid
            output['rawquery'] = query.rawquery
            output['shown_items'] = query.shown_items
            try:
                output['reordered_shown_items'] = reorderShownItems(query, options)
            except NoRerankException:
                print >>sys.stderr, "NoRerankException caught"
                print >>sys.stderr, line
                raise
            output['clicked_shown_items'] = query.clicked_shown_items
            if (options.markReordered):
                if (output['shown_items'] != output['reordered_shown_items']):
                    print '*',
            print json.dumps(output)
    except:
        printStats()
        raise

    printStats()
    sys.exit()

if __name__ == '__main__':
    main()
