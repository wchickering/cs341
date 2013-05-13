#!/usr/bin/env python

import sys
import json

CONST_MAX_FRONT_PAGE_ITEM = 16

# global stat variables
num_queries = 0
net_delta = 0
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

def printStats():
    print 'num_queries = ' + str(num_queries)
    print 'net_delta = ' + str(net_delta)
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

def isFrontPage(x):
    global CONST_MAX_FRONT_PAGE_ITEM
    if x <= CONST_MAX_FRONT_PAGE_ITEM:
        return 1
    return 0

def main():
    global num_queries
    global net_delta
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
    for line in sys.stdin:
        try:
            num_queries += 1
            record = json.loads(line)
            shown_items = record['shown_items']
            reordered_shown_items = record['reordered_shown_items']
            clicked_shown_items = record['clicked_shown_items']
            net_clicked_items += len(clicked_shown_items)
            for item in clicked_shown_items:
                assert(item in shown_items)
                reordered_index = reordered_shown_items.index(item)
                shown_index = shown_items.index(item)
                delta = reordered_index - shown_index
                if delta != 0:
                    net_reordered_clicked_items += 1
                if delta < 0:
                    net_promoted_clicked_items += 1
                elif delta > 0:
                    net_demoted_clicked_items += 1
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


        except:
            printStats()
            print >> sys.stderr, 'Exception thrown on line ' + str(num_queries)
            print >> sys.stderr, line
            raise
    printStats()

if __name__ == '__main__':
    main()
