#!/usr/bin/env python

import sys
import json

CONST_MAX_FRONT_PAGE_ITEM = 16

# global stat variables
num_queries = 0
net_delta = 0
net_delta_promoted = 0
net_delta_demoted = 0
net_clicked_items = 0
net_reordered_clicked_items = 0
net_promoted_clicked_items = 0
net_demoted_clicked_items = 0
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

def printStats(options):
    print 'num_queries = ' + str(num_queries)
    print 'net_delta = ' + str(net_delta)
    print 'net_delta_promoted = ' + str(net_delta_promoted)
    print 'net_delta_demoted = ' + str(net_delta_demoted)
    print 'net_clicked_items = ' + str(net_clicked_items)
    print 'net_reordered_clicked_items = ' + str(net_reordered_clicked_items)
    print 'net_promoted_clicked_items = ' + str(net_promoted_clicked_items)
    print 'net_demoted_clicked_items = ' + str(net_demoted_clicked_items)
    print 'top_page_advantage = ' + str(top_page_advantage)
    print 'total_reordered_clicks_front_page = ' + str(total_reordered_clicks_front_page)
    print 'total_reordered_clicks_off_front_page = ' + str(total_reordered_clicks_off_front_page)
    print 'total_shown_clicks_front_page = ' + str(total_shown_clicks_front_page)
    print 'total_shown_clicks_off_front_page = ' + str(total_shown_clicks_off_front_page)
    print 'total_moved_to_front_page = ' + str(total_moved_to_front_page)
    print 'total_moved_off_front_page = ' + str(total_moved_off_front_page)
    print 'total_stayed_on_front_page = ' + str(total_stayed_on_front_page)
    print 'k = ' + options.k
    print 'avg_precision_orig = ' + str(precision_orig_subtotal/num_queries)
    print 'avg_recall_orig = ' + str(recall_orig_subtotal/num_queries)
    print 'avg_f1_orig = ' + str(f1_orig_subtotal/num_queries)
    print 'avg_precision_reordered = ' + str(precision_reordered_subtotal/num_queries)
    print 'avg_recall_reordered = ' + str(recall_reordered_subtotal/num_queries)
    print 'avg_f1_reordered = ' + str(f1_reordered_subtotal/num_queries)

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

def main():
    global num_queries
    global net_delta
    global net_delta_promoted
    global net_delta_demoted
    global net_clicked_items
    global net_reordered_clicked_items
    global net_promoted_clicked_items
    global net_demoted_clicked_items
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
            net_clicked_items += len(clicked_shown_items)
            clicks_in_topK_orig = 0
            clicks_in_topK_reordered = 0
            for item in clicked_shown_items:
                assert(item in shown_items)
                reordered_index = reordered_shown_items.index(item)
                shown_index = shown_items.index(item)
                if shown_index < int(options.k):
                    clicks_in_topK_orig +=1
                if reordered_index < int(options.k):
                    clicks_in_topK_reordered +=1
                delta = reordered_index - shown_index
                if delta != 0:
                    net_reordered_clicked_items += 1
                if delta < 0:
                    net_promoted_clicked_items += 1
                    net_delta_promoted += delta
                elif delta > 0:
                    net_demoted_clicked_items += 1
                    net_delta_demoted += delta
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
            printStats(options)
            print >> sys.stderr, 'Exception thrown on line ' + str(num_queries)
            print >> sys.stderr, line
            raise
    printStats(options)

if __name__ == '__main__':
    main()
