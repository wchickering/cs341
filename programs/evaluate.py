#!/usr/bin/env python

import sys
import json

def main():
    net_delta = 0
    num_lines = 0
    for line in sys.stdin:
        try:
            num_lines += 1
            record = json.loads(line)
            shown_items = record['shown_items']
            reordered_shown_items = record['reordered_shown_items']
            clicked_shown_items = record['clicked_shown_items']
            for item in clicked_shown_items:
                if item in shown_items:
                    net_delta += reordered_shown_items.index(item) - shown_items.index(item)
        except:
            print >> sys.stderr, 'Exception thrown on line ' + str(num_lines)
            print >> sys.stderr, line
            raise
    print str(net_delta)

if __name__ == '__main__':
    main()
