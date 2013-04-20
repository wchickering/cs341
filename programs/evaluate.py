#!/usr/bin/env python

import sys
import json

def main():
    net_delta = 0
    for line in sys.stdin:
        record = json.loads(line)
        shown_items = record['shown_items']
        reordered_shown_items = record['reordered_shown_items']
        clicked_shown_items = record['clicked_shown_items']
        for item in clicked_shown_items:
            if item in shown_items:
                net_delta += reordered_shown_items.index(item) - shown_items.index(item)
    print str(net_delta)

if __name__ == '__main__':
    main()
