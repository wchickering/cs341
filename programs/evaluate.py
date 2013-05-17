#!/usr/bin/env python


import sys
import json
import math

CONST_MAX_FRONT_PAGE_ITEM = 16

# global stat variables
num_queries = 0
net_delta = 0
delta_promoted = 0
delta_demoted = 0
clicked_items = 0
total_clicked_positions = 0
reordered_clicked_items = 0
promoted_clicked_items = 0
demoted_clicked_items = 0
top_page_advantage = 0
total_shown_clicks_front_page = 0
total_shown_clicks_off_front_page = 0
total_reordered_clicks_front_page = 0
total_reordered_clicks_off_front_page = 0
total_moved_to_front_page = 0
total_moved_off_front_page = 0
total_stayed_on_front_page = 0
precision_orig_subtotal = 0.0
recall_orig_subtotal = 0.0
f1_orig_subtotal = 0.0
precision_reordered_subtotal = 0.0
recall_reordered_subtotal = 0.0
f1_reordered_subtotal = 0.0
total_items_on_front_page = 0
total_promoted_items = 0
total_promoted_items_approx = 0
total_clicks_in_topK_orig = 0
total_clicks_in_topK_reordered = 0
total_orig_NDCG_32 = 0.0
total_reordered_NDCG_32 = 0.0
num_NDCG_scores = 32
total_orig_NDCG_scores = [0.0 for x in range(num_NDCG_scores)]
total_reordered_NDCG_scores = [0.0 for x in range(num_NDCG_scores)]
avg_orig_NDCG_scores = [0.0 for x in range(num_NDCG_scores)]
avg_reordered_NDCG_scores = [0.0 for x in range(num_NDCG_scores)]

def printStats(options):
    unmoved_clicked_items = clicked_items - reordered_clicked_items
    print 'k = ' + options.k
    print
    print '=== DELTA STATS ==='
    print 'percent_net_delta = ' + str(float(net_delta)/total_clicked_positions)
    print 'net_delta = ' + str(net_delta)
    print 'avg_promotion = ' + str(float(delta_promoted)/promoted_clicked_items)
    print 'avg_demotion = ' + str(float(delta_demoted)/demoted_clicked_items)
    print

    print '=== NDCG SCORES ==='
    for i in range(num_NDCG_scores):
        avg_orig_NDCG_scores[i] = total_orig_NDCG_scores[i]/num_queries
        avg_reordered_NDCG_scores[i] = total_reordered_NDCG_scores[i]/num_queries
        print 'NDCG_k = ' + str(i+1)
        print 'orig: \t\t' + str(avg_orig_NDCG_scores[i])
        print 'reordered: \t' + str(avg_reordered_NDCG_scores[i])
    print 'avg_NDCG_orig_32 = \t\t' + str(total_orig_NDCG_32/num_queries)
    print 'avg_NDCG_reordered_32 = \t' + str(total_reordered_NDCG_32/num_queries)
    print

    print '=== PRECISION/RECALL STATS ==='
    print 'total_precision_orig = ' + \
            str(float(total_clicks_in_topK_orig)/(int(options.k)*num_queries))
    print 'avg_precision_orig = ' + str(precision_orig_subtotal/num_queries)
    print 'total_precision_reordered_our_picks = ' + \
            str(float(promoted_clicked_items)/total_promoted_items)
    print 'total_precision_reordered_top_k = ' + \
            str(float(total_clicks_in_topK_reordered)/total_promoted_items)
    print 'avg_precision_reordered = ' + str(precision_reordered_subtotal/num_queries)
    print 'total_recall_orig = ' + str(float(total_clicks_in_topK_orig)/clicked_items)
    print 'avg_recall_orig = ' + str(recall_orig_subtotal/num_queries)
    print 'total_recall_reordered_our_picks = ' + \
            str(float(promoted_clicked_items)/clicked_items)
    print 'total_recall_reordered_top_k = ' + \
            str(float(total_clicks_in_topK_reordered)/clicked_items)
    print 'avg_recall_reordered = ' + str(recall_reordered_subtotal/num_queries)
    print

    print '=== OTHER STATS ==='
    print 'clicked_items = ' + str(clicked_items)
    print 'percent_promoted = ' + str(float(promoted_clicked_items)/clicked_items)
    print 'percent_demoted = ' + str(float(demoted_clicked_items)/clicked_items)
    print 'percent_unmoved = ' + str(float(unmoved_clicked_items)/clicked_items)
    print 'reordered_clicked_items = ' + str(reordered_clicked_items)
    #print 'promoted_clicked_items = ' + str(promoted_clicked_items)
    #print 'demoted_clicked_items = ' + str(demoted_clicked_items)
    #print 'unmoved_clicked_items = ' + str(unmoved_clicked_items)
    #print 'approx error of # promotions = ' + \
    #        str(float(total_promoted_items - total_promoted_items_approx)/total_promoted_items)
    print 'num_queries = ' + str(num_queries)
    print 'delta_promoted = ' + str(delta_promoted)
    print 'delta_demoted = ' + str(delta_demoted)
    print 'avg_f1_orig = ' + str(f1_orig_subtotal/num_queries)
    print 'avg_f1_reordered = ' + str(f1_reordered_subtotal/num_queries)
    print

    print '=== FRONT PAGE STATS ==='
    print 'total_precision_front_orig = ' + \
        str(float(total_shown_clicks_front_page)/total_items_on_front_page)
    print 'total_recall_front_orig = ' + \
        str(float(total_shown_clicks_front_page)/clicked_items)
    print 'total_precision_front_reordered = ' + \
        str(float(total_reordered_clicks_front_page)/total_items_on_front_page)
    print 'total_recall_front_reordered = ' + \
        str(float(total_reordered_clicks_front_page)/clicked_items)
    print 'total_reordered_clicks_front_page = ' + str(total_reordered_clicks_front_page)
    #print 'total_reordered_clicks_off_front_page = ' + str(total_reordered_clicks_off_front_page)
    print 'total_shown_clicks_front_page = ' + str(total_shown_clicks_front_page)
    #print 'total_shown_clicks_off_front_page = ' + str(total_shown_clicks_off_front_page)
    print 'total_moved_to_front_page = ' + str(total_moved_to_front_page)
    print 'total_moved_off_front_page = ' + str(total_moved_off_front_page)
    #print 'total_stayed_on_front_page = ' + str(total_stayed_on_front_page)
    #print 'top_page_advantage = ' + str(top_page_advantage)

def parseArgs():
    from optparse import OptionParser, OptionGroup, HelpFormatter

    usage = "usage: %prog "\
            + "[-k N]"\
            + "<filename>"

    parser = OptionParser(usage=usage)
    helpFormatter = HelpFormatter(indent_increment=2,\
                                  max_help_position=10,\
                                  width=80,\
                                  short_first=1)

    optionGroup = OptionGroup(parser, "options")
    optionGroup.add_option("-k", dest="k", help="re-ranked top k items")
    parser.add_option_group(optionGroup)

    parser.set_defaults(k='1')

    (options, args) = parser.parse_args()

    if (len(args) > 1):
        parser.print_usage_usage()
        sys.exit()

    return (options, args)

def isFrontPage(x):
    global CONST_MAX_FRONT_PAGE_ITEM
    if x <= CONST_MAX_FRONT_PAGE_ITEM:
        return 1
    return 0

def DCGScore(i):
    if i == 0:
        return 1
    else:
        return 1.0/math.log((i+1), 2)

def main():
    global num_queries
    global net_delta
    global delta_promoted
    global delta_demoted
    global clicked_items
    global reordered_clicked_items
    global promoted_clicked_items
    global demoted_clicked_items
    global top_page_advantage
    global total_shown_clicks_front_page
    global total_shown_clicks_off_front_page
    global total_reordered_clicks_front_page
    global total_reordered_clicks_off_front_page
    global total_moved_to_front_page
    global total_moved_off_front_page
    global total_stayed_on_front_page
    global precision_orig_subtotal
    global recall_orig_subtotal
    global f1_orig_subtotal
    global precision_reordered_subtotal
    global recall_reordered_subtotal
    global f1_reordered_subtotal
    global total_clicked_positions
    global total_items_on_front_page 
    global CONST_MAX_FRONT_PAGE_ITEM
    global total_promoted_items
    global total_promoted_items_approx
    global total_clicks_in_topK_orig
    global total_clicks_in_topK_reordered
    global total_orig_NDCG_32
    global total_reordered_NDCG_32
    global total_orig_NDCG_scores
    global total_reordered_NDCG_scores
    global num_NDCG_scores

    (options, args) = parseArgs()
    if len(args) == 1:
        inputFile = open(args[0])
    else:
        inputFile = sys.stdin

    for line in inputFile:
        try:
            num_queries += 1
            record = json.loads(line)
            shown_items = record['shown_items']
            reordered_shown_items = record['reordered_shown_items']
            clicked_shown_items = record['clicked_shown_items']
            if len(shown_items) < 3:
                continue
            clicked_items += len(clicked_shown_items)
            if len(shown_items) < CONST_MAX_FRONT_PAGE_ITEM:
                total_items_on_front_page += len(shown_items)
            else:
                total_items_on_front_page += CONST_MAX_FRONT_PAGE_ITEM
            clicks_in_topK_orig = 0
            clicks_in_topK_reordered = 0
            # hopefully num_promoted_items passed in but if not we approximate (NEED k=3)
            if 'num_promoted_items' in record:
                promoted_items = record['num_promoted_items']
            else:
                # this approximation only works for k = 3
            	index_of_first = reordered_shown_items.index(shown_items[0])
            	index_of_second = reordered_shown_items.index(shown_items[1])
            	index_of_third = reordered_shown_items.index(shown_items[2])
            	if index_of_first == 3:
            	    promoted_items = 3 
            	elif index_of_first == 2:
            	    promoted_items = 2
            	elif index_of_first == 1:
            	    if index_of_second == 2 or index_of_third == 2:
            	        promoted_items = 1
            	    else:
            	        promoted_items = 3
            	elif index_of_first == 0:
            	    if index_of_second == 1 and index_of_third == 2:
            	        promoted_items = 0
            	    elif index_of_third == 2:
            	        promoted_items = 2
            	    else:
            	        promoted_items = 3
            	else:
            	    print 'Error: top three reranked improperly'
            total_promoted_items += promoted_items

            # calculate NDCG
            best_DCG = 0.0
            orig_DCG = 0.0
            reordered_DCG = 0.0
            for i in range(num_NDCG_scores):
                if i >= len(shown_items):
                    total_orig_NDCG_scores[i] += (orig_DCG/best_DCG)
                    total_reordered_NDCG_scores[i] += (reordered_DCG/best_DCG)
                    continue
                # get best_DCG
                if i < len(clicked_shown_items):
                    best_DCG += DCGScore(i)
                if shown_items[i] in clicked_shown_items:
                    orig_DCG += DCGScore(i)
                if reordered_shown_items[i] in clicked_shown_items:
                    reordered_DCG += DCGScore(i)
                total_orig_NDCG_scores[i] += (orig_DCG/best_DCG)
                total_reordered_NDCG_scores[i] += (reordered_DCG/best_DCG)
            orig_NDCG = orig_DCG/best_DCG
            reordered_NDCG = reordered_DCG/best_DCG
            total_orig_NDCG_32 += orig_NDCG
            total_reordered_NDCG_32 += reordered_NDCG
                     
            for item in clicked_shown_items:
                assert(item in shown_items)
                reordered_index = reordered_shown_items.index(item)
                shown_index = shown_items.index(item)
                total_clicked_positions += shown_index
                if shown_index < int(options.k):
                    clicks_in_topK_orig +=1
                if reordered_index < int(options.k):
                    clicks_in_topK_reordered +=1
                delta = reordered_index - shown_index
                if delta != 0:
                    reordered_clicked_items += 1
                if delta < 0:
                    promoted_clicked_items += 1
                    delta_promoted += delta
                elif delta > 0:
                    demoted_clicked_items += 1
                    delta_demoted += delta
                net_delta += delta

                reordered_front_page = isFrontPage(reordered_index)
                shown_front_page = isFrontPage(shown_index)
                top_page_advantage += reordered_front_page - shown_front_page 
                if reordered_front_page - shown_front_page > 0:
                    total_moved_to_front_page += 1
                elif reordered_front_page - shown_front_page < 0:
                    total_moved_off_front_page += 1
                elif reordered_front_page and shown_front_page:
                    total_stayed_on_front_page += 1
                if reordered_front_page:
                    total_reordered_clicks_front_page += 1
                else:
                    total_reordered_clicks_off_front_page += 1
                if shown_front_page:
                    total_shown_clicks_front_page += 1
                else:
                    total_shown_clicks_off_front_page += 1

            total_clicks_in_topK_orig += clicks_in_topK_orig
            total_clicks_in_topK_reordered += clicks_in_topK_reordered
            precision_orig = float(clicks_in_topK_orig)/int(options.k)
            recall_orig = float(clicks_in_topK_orig)/len(clicked_shown_items)
            if precision_orig + recall_orig > 0.0:
                f1_orig = 2*precision_orig*recall_orig/(precision_orig + recall_orig)
            else:
                f1_orig = 0.0
            precision_reordered = float(clicks_in_topK_reordered)/int(options.k)
            recall_reordered = float(clicks_in_topK_reordered)/len(clicked_shown_items)
            if precision_reordered + recall_reordered > 0.0:
                 f1_reordered = 2*precision_reordered*recall_reordered/\
                                       (precision_reordered + recall_reordered)
            else:
                f1_reordered = 0.0
            precision_orig_subtotal += precision_orig
            recall_orig_subtotal += recall_orig
            f1_orig_subtotal += f1_orig
            precision_reordered_subtotal += precision_reordered
            recall_reordered_subtotal += recall_reordered
            f1_reordered_subtotal += f1_reordered
            

        except:
    #        printStats(options)
            print >> sys.stderr, 'Exception thrown on line ' + str(num_queries)
            print >> sys.stderr, line
            raise
    printStats(options)

    
if __name__ == '__main__':
    main()
