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
import heapq

# import local modules
import Similarity as sim
import index_query as idx
from Query import Query

# global stats
num_reranks = 0
num_shown_items = 0
num_nonzero_scores = 0

class NoRerankException(Exception):
    def __init__(self):
        pass
    def __str__(self):
        return ""

def printStats():
    print >> sys.stderr, 'num reranks = ' + str(num_reranks)
    print >> sys.stderr, 'num_shown_items = ' + str(num_shown_items)
    print >> sys.stderr, 'num_nonzero_scores = ' + str(num_nonzero_scores)

def reorderShownItems(query, indexFd, posting_dict, options):
    global num_reranks
    global num_shown_items
    global num_nonzero_scores

    # Retrieve queryLists for previously clicked items
    prevQueryLists = []
    for previouslyClickedItem in query.previously_clicked_items:
        prevQueryLists.append(idx.get_posting(indexFd, posting_dict, str(previouslyClickedItem)))
    if prevQueryLists == []:
        raise NoRerankException
        return query.shown_items

    # Determine the top k scores 
    top_scores_heap = []
    for i in range(len(query.shown_items)):
        shownItem = query.shown_items[i]
        num_shown_items += 1
        shownItemQueryIds = idx.get_posting(indexFd, posting_dict, str(shownItem))
        score = 0
        for j in range(len(query.previously_clicked_items)):
            # ignore previously clicked items themselves
            if query.previously_clicked_items[j] == shownItem:
                score = 0
                break
            score += sim.jaccard(prevQueryLists[j], shownItemQueryIds)
        if score > 0:
            num_nonzero_scores += 1
            heapq.heappush(top_scores_heap, (score, i))
            if len(top_scores_heap) > int(options.k):
                heapq.heappop(top_scores_heap)
    if (len(top_scores_heap) == 0):
        raise NoRerankException
        return query.shown_items

    num_reranks += len(top_scores_heap)

    # transfer top k to simple list
    num_reranked = len(top_scores_heap)
    top_scores = sorted(top_scores_heap, key=lambda tup: tup[0], reverse=True)
    top_score_idxs = sorted(top_scores_heap, key=lambda tup: tup[1])
    
    i = 0
    j = 0
    k = 0
    reranked_items = []
    while i < len(query.shown_items):
        if i < len(top_scores):
            index = top_scores[i][1]
            try:
                item = query.shown_items[index]
            except IndexError:
                print >> sys.stderr, 'index = ' + str(index)
                print >> sys.stderr, 'len(query.shown_items) = ' + str(len(query.shown_items))
                print >> sys.stderr, 'top_scores = ' + str(top_scores)
                print >> sys.stderr, 'query.shown_items = ' + str(query.shown_items)
                raise
            reranked_items.append(item)
            i += 1
        elif k < len(top_score_idxs):
            if j < top_score_idxs[k][1]:
                reranked_items.append(query.shown_items[j])
                i += 1
                j += 1
            else:
                j += 1
                k += 1
        else:
            reranked_items.append(query.shown_items[j])
            i += 1
            j += 1
    return reranked_items

def main():
    from optparse import OptionParser, OptionGroup, HelpFormatter
    import sys
    
    usage = "usage: %prog [options] "\
            + "-k N "\
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

    rankGroup = OptionGroup(parser, "Ranking options")
    rankGroup.add_option("-k", dest="k", help="re-rank top k items")
    parser.add_option_group(rankGroup)

    fileGroup = OptionGroup(parser, "Index options")
    fileGroup.add_option("--index", dest="indexFn", help="index filename")
    parser.add_option_group(fileGroup)
    fileGroup.add_option("--dict", dest="dictionaryFn", help="dictionary filename")
    parser.add_option_group(fileGroup)

    parser.set_defaults(verbose=False, k=1, indexFn=None, dictionaryFn=None,\
                        markReordered=False)

    (options, args) = parser.parse_args()

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

    posting_dict_f = open(options.dictionaryFn)
    posting_dict = idx.get_posting_dict(posting_dict_f)
    indexFd = open(options.indexFn)

    try:
        for line in inputFile:
            query = Query(line)
            output = {}
            output['visitorid'] = query.visitorid
            output['wmsessionid'] = query.wmsessionid
            output['rawquery'] = query.rawquery
            output['searchattributes'] = query.searchattributes
            output['shown_items'] = query.shown_items
            try:
                output['reordered_shown_items'] =\
                    reorderShownItems(query, indexFd, posting_dict, options)
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
