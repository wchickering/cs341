#!/usr/bin/env python

import sys
import json
import unicodedata

def normalizeStr(s):
    return ' '.join(unicodedata.normalize('NFKD', s)\
                    .encode('ascii','ignore').replace('"','\"').strip().split())

def main():
    line_num = 0
    for line in sys.stdin:
        line_num += 1
        record = json.loads(line)
        visitorid = int(record['visitorid'])
        wmsessionid = normalizeStr(record['wmsessionid'])
        rawquery = normalizeStr(record['rawquery'])
        shown_items = record['shown_items']
        reordered_shown_items = record['reordered_shown_items']
        clicked_shown_items = record['clicked_shown_items']
        for item in clicked_shown_items:
            if item in shown_items:
                delta = reordered_shown_items.index(item) - shown_items.index(item)
                print 'delta\t%d\t%d\t%s\t%s' % (delta, visitorid, wmsessionid, rawquery) 

if __name__ == '__main__':
    main()
