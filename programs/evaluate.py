#!/usr/bin/env python

import sys
import json

# global stat variables
num_lines = 0
net_delta = 0
net_clicked_items = 0
net_reordered_clicked_items = 0
net_promoted_clicked_items = 0
net_demoted_clicked_items = 0

def printStats():
    global num_lines
    global net_delta
    global net_clicked_items
    global net_reordered_clicked_items
    global net_promoted_clicked_items
    global net_demoted_clicked_items
    print 'num_lines = ' + str(num_lines)
    print 'net_delta = ' + str(net_delta)
    print 'net_clicked_items = ' + str(net_clicked_items)
    print 'net_reordered_clicked_items = ' + str(net_reordered_clicked_items)
    print 'net_promoted_clicked_items = ' + str(net_promoted_clicked_items)
    print 'net_demoted_clicked_items = ' + str(net_demoted_clicked_items)

def main():
    global num_lines
    global net_delta
    global net_clicked_items
    global net_reordered_clicked_items
    global net_promoted_clicked_items
    global net_demoted_clicked_items
    for line in sys.stdin:
        try:
            num_lines += 1
            record = json.loads(line)
            shown_items = record['shown_items']
            reordered_shown_items = record['reordered_shown_items']
            clicked_shown_items = record['clicked_shown_items']
            net_clicked_items += len(clicked_shown_items)
            for item in clicked_shown_items:
                if item in shown_items:
                    delta = reordered_shown_items.index(item) - shown_items.index(item)
                    if delta != 0:
                        net_reordered_clicked_items += 1
                    if delta < 0:
                        net_promoted_clicked_items += 1
                    elif delta > 0:
                        net_demoted_clicked_items += 1
                    net_delta += delta
        except:
            printStats()
            print >> sys.stderr, 'Exception thrown on line ' + str(num_lines)
            print >> sys.stderr, line
            raise
    printStats()

if __name__ == '__main__':
    main()
