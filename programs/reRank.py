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

# global stats
num_reranks = 0
num_nonzero_scores = 0

def printStats():
    print >> sys.stderr, 'num reranks = ' + str(num_reranks)
    print >> sys.stderr, 'num_nonzero_scores = ' + str(num_nonzero_scores)

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
        record = json.loads(jsonStr)
        self.shown_items = record['shown_items']
        self.previously_clicked_items=record['previously_clicked_items']
        self.clicked_shown_items=record['clicked_shown_items']

    def __repr__(self):
        return "Query(%s)" % repr(json.dumps({\
                     "shown_items":self.shown_items,\
                     "previously_clicked_items":self.previously_clicked_items,\
                     "clicked_shown_items":self.clicked_shown_items}))

def reorderShownItems(query, indexFd, posting_dict, options):
    global num_reranks
    global num_nonzero_scores

    # Retrieve queryLists for previously clicked items
    prevQueryLists = []
    for previouslyClickedItem in query.previously_clicked_items:
        prevQueryLists.append(idx.get_posting(indexFd, posting_dict, str(previouslyClickedItem)))
    if prevQueryLists == []:
        return query.shown_items

    # Determine the top k scores 
    top_scores = []
    item_scores = []
    for shownItem in query.shown_items:
        shownItemQueryIds = idx.get_posting(indexFd, posting_dict, str(shownItem))
        score = 0
        for i in range(len(query.previously_clicked_items)):
            # ignore previously clicked items themselves
            if query.previously_clicked_items[i] == shownItem:
                score = 0
                break
            if (options.JACCARD):
                score += sim.jaccard(prevQueryLists[i], shownItemQueryIds)
        if score > 0:
            num_nonzero_scores += 1
            for i in range(len(top_scores)):
                if score > top_scores[i]:
                    top_scores.insert(i, score)
                    if len(top_scores) >= 5: # only re-rank top 5 (NEED TO REMOVE MAGIC NUMBER!!)
                        top_scores.pop()
            if len(top_scores) < 5: # (EEK!! ANOTHER ONE!!)
                top_scores.append(score)
        item_scores.append(score)
    if (len(top_scores) == 0):
        return query.shown_items

    # Re-rank query results based on top k scores
    reranked_items = list(query.shown_items)
    i = 0
    for j in range(len(reranked_items)):
        if i >= len(top_scores):
            break
        if item_scores[j] == top_scores[i]:
            item = reranked_items.pop(j)
            reranked_items.insert(i, item)
            num_reranks += 1
            i += 1
    return reranked_items

def main():
    from optparse import OptionParser, OptionGroup, HelpFormatter
    import sys
    
    usage = "usage: %prog [options] "\
            + "<-j> "\
            + "--index <index filename> "\
            + "--dict <dictionary filename> " \
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

    parser.set_defaults(verbose=False, indexFn=None, dictionaryFn=None,\
                        markReordered=False)

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

    try:
        for line in inputFile:
            query = Query(line)
            output = {}
            output['shown_items'] = query.shown_items
            output['reordered_shown_items'] =\
                reorderShownItems(query, indexFd, posting_dict, options)
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
