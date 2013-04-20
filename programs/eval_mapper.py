#!/usr/bin/env python

import sys
import json

def main():
    for line in sys.stdin:
        record = json.loads(line)
        shown_items = record['shown_items']
        reordered_shown_items = record['reordered_shown_items']
        clicked_shown_items = record['clicked_shown_items']
        for item in clicked_shown_items:
            if item in shown_items:
                delta = reordered_shown_items.index(item) - shown_items.index(item)
                print 'delta\t%d' % (delta)

if __name__ == '__main__':
    main()
