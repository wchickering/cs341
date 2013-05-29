#!/usr/bin/env python

import sys
import json
import math
from numbers import Number
from collections import OrderedDict
from collections import Iterable

MAX_FRONT_PAGE_ITEMS = 16
NUM_NDCG_SCORES = 16

def parseArgs():
    from optparse import OptionParser, OptionGroup, HelpFormatter

    usage = "usage: %prog "\
            + "[-k N]"\
            + "[--test_data_fname filename of unfiltered test data stats]"\
            + "[--rankable_data_fname filename of rankable test data stats]"\
            + "<filename>"

    parser = OptionParser(usage=usage)
    helpFormatter = HelpFormatter(indent_increment=2,\
                                  max_help_position=10,\
                                  width=80,\
                                  short_first=1)

    optionGroup = OptionGroup(parser, "options")
    optionGroup.add_option("--test_data_fname", type="string", dest="test_data_fname",\
            help="file name of unfiltered test data")
    optionGroup.add_option("--rankable_data_fname", type="string", dest="rankable_data_fname",\
            help="file name of test data filtered for rankability")
    optionGroup.add_option("-k", type="int", dest="k", help="re-ranked top k items")
    parser.add_option_group(optionGroup)

    parser.set_defaults(k=1, test_data_fname="", rankable_data_fname="")
    (options, args) = parser.parse_args()

    if (len(args) > 1):
        parser.print_usage_usage()
        sys.exit()

    return (options, args)


def isFrontPage(x):
    if x < MAX_FRONT_PAGE_ITEMS:
        return 1
    return 0

def DCGScore(i):
    if i == 0:
        return 1
    else:
        return 1.0/math.log((i+1), 2)

    
def main():
    print "Parsing args..."
    (options, args) = parseArgs()
    print "Starting..."
    if len(args) == 1:
        print "args == 1"
        inputFile = open(args[0])
    else:
        print "args != 1"
        inputFile = sys.stdin
    k = options.k

    print "Initializing..." 
    ### INITIALIZE ###
    total_orig_NDCG_16 = 0.0
    total_reordered_NDCG_16 = 0.0
    total_orig_NDCG_scores = [0.0 for x in range(NUM_NDCG_SCORES)]
    total_reordered_NDCG_scores = [0.0 for x in range(NUM_NDCG_SCORES)]
    avg_orig_NDCG_scores = [0.0 for x in range(NUM_NDCG_SCORES)]
    avg_reordered_NDCG_scores = [0.0 for x in range(NUM_NDCG_SCORES)]
    num_queries = 0
    net_delta = 0
    delta_promoted = 0
    delta_demoted = 0
    clicked_items = 0
    purchased_items = 0
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
    total_purchases_moved_to_front_page = 0
    total_purchases_moved_off_front_page = 0
    total_stayed_on_front_page = 0
    precision_orig_subtotal = 0.0
    recall_orig_subtotal = 0.0
    f1_orig_subtotal = 0.0
    precision_reordered_subtotal = 0.0
    recall_reordered_subtotal = 0.0
    f1_reordered_subtotal = 0.0
    precision_orig_avg = 0.0
    recall_orig_avg = 0.0
    f1_orig_avg = 0.0
    precision_reordered_avg = 0.0
    recall_reordered_avg = 0.0
    f1_reordered_avg = 0.0
    total_items_on_front_page = 0
    total_promoted_items = 0
    total_affected_queries = 0
    total_promoted_items_approx = 0
    total_clicks_in_topK_orig = 0
    total_clicks_in_topK_reordered = 0
    total_purchased_front_page_orig = 0
    total_purchased_front_page_reordered = 0
    total_sqr_clicks_front_page_orig = 0
    total_sqr_clicks_front_page_reordered = 0
    total_sqr_purchases_front_page_orig = 0
    total_sqr_purchases_front_page_reordered = 0
    total_shown_items = 0

    print "Processing Data..."
    ### PROCESS DATA ###
    lineNum = 0
    for line in inputFile:
        lineNum += 1
        try: 
            record = json.loads(line)
        except:
            print >> sys.stderr, 'Failed to parse json line ' + str(lineNum)
            print >> sys.stderr, line
            raise
        
        num_queries += 1
        shown_items = record['shown_items']
        reordered_shown_items = record['reordered_shown_items']
        clicked_shown_items = set(record['clicked_shown_items'])
        purchased_shown_items = set(record['purchased_shown_items'])

        total_shown_items += len(shown_items)
        clicked_items += len(clicked_shown_items)
        purchased_items += len(purchased_shown_items)
        if len(shown_items) < MAX_FRONT_PAGE_ITEMS:
            total_items_on_front_page += len(shown_items)
        else:
            total_items_on_front_page += MAX_FRONT_PAGE_ITEMS
        clicks_in_topK_orig = 0
        clicks_in_topK_reordered = 0

        promoted_items = record['num_promoted_items']
        total_promoted_items += promoted_items
        if promoted_items > 0:
            total_affected_queries += 1

        # calculate NDCG
        best_DCG = 0.0
        orig_DCG = 0.0
        reordered_DCG = 0.0
        for i in range(NUM_NDCG_SCORES):
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
        total_orig_NDCG_16 += orig_NDCG
        total_reordered_NDCG_16 += reordered_NDCG
        
        front_page_purchases_orig = 0
        front_page_purchases_reordered = 0
        for purchase in purchased_shown_items:
            reordered_index = reordered_shown_items.index(purchase)
            shown_index = shown_items.index(purchase)
            reordered_front_page = isFrontPage(reordered_index)
            shown_front_page = isFrontPage(shown_index)
            if reordered_front_page:
                front_page_purchases_reordered += 1
                total_purchased_front_page_reordered+=1
            if shown_front_page:
                front_page_purchases_orig += 1
                total_purchased_front_page_orig += 1
            if reordered_front_page - shown_front_page > 0:
                total_purchases_moved_to_front_page += 1
            elif reordered_front_page - shown_front_page < 0:
                total_purchases_moved_off_front_page += 1

        total_sqr_purchases_front_page_orig += \
            front_page_purchases_orig * front_page_purchases_orig 
        total_sqr_purchases_front_page_reordered += \
            front_page_purchases_reordered * front_page_purchases_reordered 
        
        front_page_clicks_orig = 0 
        front_page_clicks_reordered = 0
        for item in clicked_shown_items:
            assert(item in shown_items)
            reordered_index = reordered_shown_items.index(item)
            shown_index = shown_items.index(item)
            total_clicked_positions += shown_index
            if shown_index < k:
                clicks_in_topK_orig +=1
            assert(clicks_in_topK_orig <= k)
            if reordered_index < k:
                clicks_in_topK_reordered +=1
            assert(clicks_in_topK_reordered <= k)
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
                front_page_clicks_reordered += 1
                total_reordered_clicks_front_page += 1
            else:
                total_reordered_clicks_off_front_page += 1
            if shown_front_page:
                front_page_clicks_orig += 1
                total_shown_clicks_front_page += 1
            else:
                total_shown_clicks_off_front_page += 1

        total_sqr_clicks_front_page_orig += \
            front_page_clicks_orig * front_page_clicks_orig 
        total_sqr_clicks_front_page_reordered += \
            front_page_clicks_reordered * front_page_clicks_reordered 
        #diff_clicks_front_page = front_page_clicks_reordered - front_page_clicks_orig
        #total_sqr_diff_clicks_front_page += (diff_clicks_front_page * diff_clicks_front_page)
        #total_clicks_in_topK_orig += clicks_in_topK_orig
        #total_clicks_in_topK_reordered += clicks_in_topK_reordered

        precision_orig = float(clicks_in_topK_orig)/k
        assert(precision_orig <= 1.0)
        recall_orig = float(clicks_in_topK_orig)/len(clicked_shown_items)
        assert(recall_orig <= 1.0)
        if precision_orig + recall_orig > 0.0:
            f1_orig = 2*precision_orig*recall_orig/(precision_orig + recall_orig)
        else:
            f1_orig = 0.0
        precision_reordered = float(clicks_in_topK_reordered)/k
        assert(precision_reordered <= 1.0)
        recall_reordered = float(clicks_in_topK_reordered)/len(clicked_shown_items)
        assert(recall_reordered <= 1.0)
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

    print "Reading stats on data files..."
    test_data_file = open(options.test_data_fname, 'r')
    rankable_data_file = open(options.rankable_data_fname, 'r')
    for line in test_data_file:
        record = json.loads(line)
        test_data_queries = record['num_queries']
        test_data_clicks = record['num_clicks']
        test_data_purchases = record['num_purchases']
        test_data_items = record['num_shown_items']
        test_data_queries_with_clicks = record['num_queries_with_clicks']
        test_data_one_page_queries = record['num_one_page_queries']
        test_data_front_page_clicks = record['num_front_page_clicks']
        test_data_front_page_purchases = record['num_front_page_purchases']
        test_data_front_page_items = record['num_front_page_items'] 
    for line in rankable_data_file:
        record = json.loads(line)
        rankable_data_queries = record['num_queries']
        rankable_data_clicks = record['num_clicks']
        rankable_data_purchases = record['num_purchases']
        rankable_data_items = record['num_shown_items']
        rankable_data_queries_with_clicks = record['num_queries_with_clicks']
        rankable_data_one_page_queries = record['num_one_page_queries']
        rankable_data_front_page_clicks = record['num_front_page_clicks']
        rankable_data_front_page_purchases = record['num_front_page_purchases']
        rankable_data_front_page_items = record['num_front_page_items'] 
    test_data_file.close()
    rankable_data_file.close()

    test_data_users = 1
    test_data_users_with_clicks = 1

    print "Calculating stats..."
    # data stats
    test_data_queries_per_user = float(test_data_queries) / test_data_users
    test_data_clicks_per_user = float(test_data_clicks) / test_data_users
    perc_users_with_clicks_test_data = float(test_data_users_with_clicks)/test_data_users
    perc_data_affectable_all = float(rankable_data_queries)/test_data_queries
    test_data_avg_query_length = float(test_data_items)/test_data_queries
    rankable_data_avg_query_length = float(rankable_data_items)/rankable_data_queries
    perc_queries_with_clicks_test_data = float(test_data_queries_with_clicks)/test_data_queries
    perc_queries_with_clicks_rankable_data = float(rankable_data_queries_with_clicks) / \
            rankable_data_queries
    test_data_conversion = float(test_data_purchases) / test_data_clicks
    rankable_data_conversion = float(rankable_data_purchases) / rankable_data_clicks
    test_data_front_page_conversion = float(test_data_front_page_purchases) / \
            test_data_front_page_clicks
    rankable_data_front_page_conversion = float(rankable_data_front_page_purchases) / \
            rankable_data_front_page_clicks
    front_page_CTR_test_data = float(test_data_front_page_clicks) / \
            test_data_front_page_items
    front_page_CTR_rankable_data = float(rankable_data_front_page_clicks) / \
            rankable_data_front_page_items
    test_data_other_page_clicks = test_data_clicks - test_data_front_page_clicks
    test_data_other_page_purchases = test_data_purchases - test_data_front_page_purchases
    test_data_other_page_items = test_data_items - test_data_front_page_items
    rankable_data_other_page_clicks = rankable_data_clicks - rankable_data_front_page_clicks
    rankable_data_other_page_purchases = rankable_data_purchases - \
            rankable_data_front_page_purchases
    rankable_data_other_page_items = rankable_data_items - rankable_data_front_page_items
    other_page_CTR_test_data = float(test_data_other_page_clicks) / \
            test_data_other_page_items
    other_page_CTR_rankable_data = float(rankable_data_other_page_clicks) / \
            rankable_data_other_page_items
    front_page_click_recall_test_data = float(test_data_front_page_clicks)/test_data_clicks
    front_page_click_recall_rankable_data = \
            float(rankable_data_front_page_clicks)/rankable_data_clicks
    front_page_purchase_rate_test_data = float(test_data_front_page_purchases) / \
            test_data_front_page_items
    front_page_purchase_rate_rankable_data = float(rankable_data_front_page_purchases) / \
            rankable_data_front_page_items
    front_page_purchase_recall_test_data = float(test_data_front_page_purchases) / \
            test_data_purchases
    front_page_purchase_recall_rankable_data = float(rankable_data_front_page_purchases) / \
            rankable_data_purchases
    other_page_purchase_rate_test_data = float(test_data_other_page_purchases)/\
            test_data_other_page_items
    other_page_purchase_rate_rankable_data = float(rankable_data_other_page_purchases)/\
            rankable_data_other_page_items
    test_data_other_pages_conversion = float(test_data_other_page_purchases) / \
            test_data_other_page_clicks
    rankable_data_other_pages_conversion = float(rankable_data_other_page_purchases) / \
            rankable_data_other_page_clicks
    perc_one_page_queries_test_data = float(test_data_one_page_queries) / test_data_queries
    perc_one_page_queries_rankable_data = float(rankable_data_one_page_queries) /\
            rankable_data_queries

    #other_page_clicks = clicked_items - front_page_clicks_orig 
    #other_page_purchases = purchased_items - front_page_purchases_orig 
    #other_page_items = total_shown_items - total_items_on_front_page
    #other_page_CTR = float(other_page_clicks)/other_page_items
    #other_page_purchase_rate = float(other_page_purchases)/other_page_items

    perc_clicks_in_rankable = float(rankable_data_clicks)/test_data_clicks
    perc_purchases_in_rankable = float(rankable_data_purchases)/test_data_purchases
   
    # calculate averages, etc
    for i in range(NUM_NDCG_SCORES):
        avg_orig_NDCG_scores[i] = total_orig_NDCG_scores[i]/num_queries
        avg_reordered_NDCG_scores[i] = total_reordered_NDCG_scores[i]/num_queries
    precision_orig_avg = precision_orig_subtotal/num_queries
    recall_orig_avg = recall_orig_subtotal/num_queries
    f1_orig_avg = f1_orig_subtotal/num_queries
    precision_reordered_avg = precision_reordered_subtotal/num_queries
    recall_reordered_avg = recall_reordered_subtotal/num_queries
    f1_reordered_avg = f1_reordered_subtotal/num_queries
    unmoved_clicked_items = clicked_items - reordered_clicked_items
    purch_front_orig = total_purchased_front_page_orig
    purch_front_reordered = total_purchased_front_page_reordered
    front_page_diff = total_reordered_clicks_front_page - total_shown_clicks_front_page
    front_page_purchase_diff = total_purchased_front_page_reordered - \
        total_purchased_front_page_orig
    percent_increase_front_page = float(front_page_diff)/total_shown_clicks_front_page
    percent_increase_total_clicks = float(front_page_diff)/test_data_clicks
    percent_increase_total_purchases = float(purch_front_reordered-purch_front_orig) / \
            test_data_purchases
    front_page_CTR_orig = float(total_shown_clicks_front_page)/total_items_on_front_page

    # convertsion rates
    filtered_data_conversion = float(purchased_items)/clicked_items
    front_page_conversion = float(total_purchased_front_page_orig) / \
            total_shown_clicks_front_page
    our_front_page_conversion = float(total_purchased_front_page_reordered) / \
            total_reordered_clicks_front_page
    promoted_to_front_conversion = float(total_purchases_moved_to_front_page)/ \
            total_moved_to_front_page
    bumped_off_front_conversion = float(total_purchases_moved_off_front_page)/ \
            total_moved_off_front_page

    # standard deviation calculations
    # clicks:
    click_var_orig = total_sqr_clicks_front_page_orig - \
        (total_shown_clicks_front_page * total_shown_clicks_front_page / num_queries)
    click_var_reordered = total_sqr_clicks_front_page_reordered - \
        (total_reordered_clicks_front_page * total_reordered_clicks_front_page / num_queries)
    click_diff_variance = click_var_reordered + click_var_orig
    click_diff_std_dev = math.sqrt(click_diff_variance)
    perc_click_ratio_95 = 1.96*click_diff_std_dev / front_page_diff
    # purchases:
    purchase_var_orig = total_sqr_purchases_front_page_orig - \
        (total_purchased_front_page_orig * total_purchased_front_page_orig / num_queries)
    purchase_var_reordered = total_sqr_purchases_front_page_reordered - \
        (total_purchased_front_page_reordered*total_purchased_front_page_reordered/num_queries)
    purchase_diff_variance = purchase_var_reordered + purchase_var_orig
    purchase_diff_std_dev = math.sqrt(purchase_diff_variance)
    perc_purchase_ratio_95 = 1.96*purchase_diff_std_dev / front_page_purchase_diff


    ### PRINT STATS ###
    print 'k = ' + str(k)
    print
    print '=== DELTA STATS ==='
    print 'percent_net_delta = ', float(net_delta)/total_clicked_positions
    print 'net_delta = ', net_delta
    if promoted_clicked_items > 0:
        print 'avg_promotion = ', float(delta_promoted)/promoted_clicked_items
    if demoted_clicked_items > 0:
        print 'avg_demotion = ', float(delta_demoted)/demoted_clicked_items
    print

    print '=== NDCG SCORES ==='
    for i in range(NUM_NDCG_SCORES):
        print 'NDCG_k = ', i+1
        print 'orig: \t\t', avg_orig_NDCG_scores[i]
        print 'reordered: \t', avg_reordered_NDCG_scores[i]
    print 'avg_NDCG_orig_16 = \t\t', total_orig_NDCG_16/num_queries
    print 'avg_NDCG_reordered_16 = \t', total_reordered_NDCG_16/num_queries
    print

    print '=== PRECISION/RECALL STATS ==='
    print 'total_precision_orig = ', float(total_clicks_in_topK_orig)/(k*num_queries)
    print 'precision_orig_avg = ', precision_orig_avg
    if total_promoted_items > 0:
        print 'total_precision_reordered_our_picks = ', \
                float(promoted_clicked_items)/total_promoted_items
    if total_promoted_items > 0:
        print 'total_precision_reordered_top_k = ',  \
            float(total_clicks_in_topK_reordered)/total_promoted_items
    print 'precision_reordered_avg = ', precision_reordered_avg
    print 'total_recall_orig = ', float(total_clicks_in_topK_orig)/clicked_items
    print 'recall_orig_avg = ', recall_orig_avg
    print 'total_recall_reordered_our_picks = ', float(promoted_clicked_items)/clicked_items
    print 'total_recall_reordered_top_k = ', float(total_clicks_in_topK_reordered) / \
            clicked_items
    print 'recall_reordered_avg = ', recall_reordered_avg
    print 'f1_orig_avg = ', f1_orig_avg
    print 'f1_reordered_avg = ', f1_reordered_avg
    print

    print '=== OTHER STATS ==='
    print 'num_queries = ', num_queries
    print 'clicked_items = ', clicked_items
    print 'purchased_items = ', purchased_items
    print 'percent_promoted = ', float(promoted_clicked_items)/clicked_items
    print 'percent_demoted = ', float(demoted_clicked_items)/clicked_items
    print 'percent_unmoved = ', float(unmoved_clicked_items)/clicked_items
    print 'reordered_clicked_items = ', reordered_clicked_items
    print 'num_queries_affected = ', total_affected_queries
    print

    print '=== FRONT PAGE CLICKS ==='
    print 'total_precision_front_orig = ',\
        float(total_shown_clicks_front_page)/total_items_on_front_page
    print 'total_precision_front_reordered = ', \
        float(total_reordered_clicks_front_page)/total_items_on_front_page
    print 'total_recall_front_orig = ', float(total_shown_clicks_front_page)/clicked_items
    print 'total_recall_front_reordered = ', \
        float(total_reordered_clicks_front_page)/clicked_items
    print 'total_original_clicks_front_page = ', total_shown_clicks_front_page
    print 'total_reordered_clicks_front_page = ', total_reordered_clicks_front_page
    print 'total_moved_to_front_page = ', total_moved_to_front_page
    print 'total_moved_off_front_page = ', total_moved_off_front_page
    print
 
    print '=== FRONT PAGE PURCHASES ==='
    print 'total_purchase_precision_front_orig = ',\
        float(total_purchased_front_page_orig)/total_items_on_front_page
    print 'total_purchase_recall_front_orig = ', \
            float(total_purchased_front_page_orig)/purchased_items
    print 'total_purchase_precision_front_reordered = ', \
        float(total_purchased_front_page_reordered)/total_items_on_front_page
    print 'total_purchase_recall_front_reordered = ', \
        float(total_purchased_front_page_reordered)/purchased_items
    print 'total_original_purchases_front_page = ', total_purchased_front_page_orig
    print 'total_reordered_purchases_front_page = ', total_purchased_front_page_reordered
    print 'total_purchases_moved_to_front_page = ', total_purchases_moved_to_front_page
    print 'total_purchases_moved_off_front_page = ', total_purchases_moved_off_front_page
    print

    print '=== THE DATA ==='
    print 'queries_in_test_data = ', test_data_queries
    print 'clicks_in_test_data = ', test_data_clicks
    print 'purchases_in_test_data = ', test_data_purchases
    print 'queries_in_rankable_data = ', rankable_data_queries
    print 'clicks_in_rankable_data = ', rankable_data_clicks
    print 'purchases_in_rankable_data = ', rankable_data_purchases
    print 'queries_in_filtered_data = ', num_queries
    print 'clicks_in_filtered_data = ', clicked_items
    print 'purchases_in_filtered_data = ', purchased_items
    print 'percent_data_rankable = ', perc_data_affectable_all
    print
    
    print '=== TEST DATA vs RANKABLE DATA ==='
    print 'queries per user = ?'
    print 'clicks per user = ?'
    print 'users with no clicks = ?'
    print 'clicks per query in test data = ', float(test_data_clicks)/test_data_queries
    print 'clicks per query in rankable = ', float(rankable_data_clicks)/rankable_data_queries
    print 'purchases per query in test data = ', float(test_data_purchases)/test_data_queries
    print 'purchases per query in rankable = ', float(rankable_data_purchases)/\
            rankable_data_queries
    print 'percent queries with clicks in test data = ', perc_queries_with_clicks_test_data
    print 'percent queries with clicks in rankable data = ', \
            perc_queries_with_clicks_rankable_data
    print 'average length of query in test data = ', test_data_avg_query_length
    print 'average length of query in rankable data = ', rankable_data_avg_query_length
    print 'percent of one-page queries in test data = ', perc_one_page_queries_test_data
    print 'percent of one-page queries in rankable = ', perc_one_page_queries_rankable_data
    print 'front page CTR in test data = ', front_page_CTR_test_data
    print 'front page CTR in rankable data = ', front_page_CTR_rankable_data
    print 'other page CTR in test data = ', other_page_CTR_test_data
    print 'other page CTR in rankable data = ', other_page_CTR_rankable_data
    print 'percent of clicks on front page in test data = ', front_page_click_recall_test_data
    print 'percent of clicks on front page in rankable data = ', \
            front_page_click_recall_rankable_data
    print 'front page purchase rate in test data = ', front_page_purchase_rate_test_data
    print 'front page purchase rate in rankable data = ',front_page_purchase_rate_rankable_data
    print 'other page purchase rate in test data = ', other_page_purchase_rate_test_data
    print 'other page purchase rate in rankable data = ',other_page_purchase_rate_rankable_data
    print 'percent of purchases on front page in test data = ', \
            front_page_purchase_recall_test_data
    print 'percent of purchases on front page in rankable data = ', \
            front_page_purchase_recall_rankable_data
    print 'percent of clicks in rankable = ', perc_clicks_in_rankable
    print 'percent of purchases in rankable = ', perc_purchases_in_rankable
    print
           
    print '=== CONVERSION RATES ==='
    print 'conversion_rate_test_data = ', test_data_conversion
    print 'conversion_rate_test_data_front_page = ', test_data_front_page_conversion
    print 'conversion_rate_test_data_other_pages = ', test_data_other_pages_conversion
    print 'conversion_rate_filtered_data = ', filtered_data_conversion
    print 'conversion_rate_filtered_front_page = ', front_page_conversion
    print 'conversion_rate_filtered_other_pages = ', rankable_data_other_pages_conversion
    print 'conversion_rate_our_front_page = ', our_front_page_conversion
    print 'conversion_rate_promoted_to_front_items = ', promoted_to_front_conversion
    print 'conversion_rate_bumped_off_front_items = ', bumped_off_front_conversion
    print
    
    print
    print '=== KEY STATS ==='
    print 'percent_increase_NDCG_16 = \t\t', \
        "{0:.4f}".format(float(avg_reordered_NDCG_scores[15] - \
        avg_orig_NDCG_scores[15])/avg_orig_NDCG_scores[15])
    print 'percent_net_delta = \t\t\t', \
        "{0:.4f}".format(float(net_delta)/total_clicked_positions)
    print 'clicks:'
    print 'front_page_difference = \t\t', front_page_diff, " / ", total_shown_clicks_front_page
    #print 'click_diff_std_dev = \t\t\t', click_diff_std_dev
    print 'percent_increase_front_page = \t\t', \
        "{0:.4f}".format(float(front_page_diff)/total_shown_clicks_front_page)
    print 'percent_increase_total_clicks = \t', \
        "{0:.4f}".format(percent_increase_total_clicks)
    print '95_perc_confidence_interval = \t\t[', \
        "{0:.4f}".format((1-perc_click_ratio_95)*percent_increase_total_clicks), \
        ",", "{0:.4f}".format((1+perc_click_ratio_95)*percent_increase_total_clicks), "]"
           
    print 'purchases:'
    print 'first_purchase_difference = \t\t', \
        purch_front_reordered - purch_front_orig, ' / ', purch_front_orig
    #print 'purchase_diff_std_dev = \t\t', math.sqrt(purchase_diff_variance)
    print 'percent_increase_purchases = \t\t', \
        "{0:.4f}".format(float(purch_front_reordered-purch_front_orig)/purch_front_orig)
    print 'precent_increase_total_purchases = \t', \
        "{0:.4f}".format(float(purch_front_reordered - purch_front_orig)/test_data_purchases)
    print '95_perc_confidence_interval = \t\t[', \
        "{0:.4f}".format((1-perc_purchase_ratio_95)*percent_increase_total_purchases), \
        ",", "{0:.4f}".format((1+perc_purchase_ratio_95)*percent_increase_total_purchases), "]"
    #print '95_perc_confidence_interval = \t'
    print

if __name__ == '__main__':
    main()
