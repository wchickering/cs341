#!/usr/bin/python
# To execute, enter something like:
# python dumpCTRs.py 000000_0.test_data > CTRs.json

import sys
import fileinput
import json

POSITIONS = 1000

def main():
    num_queries = 0
    num_clicks_by_position = [0]*POSITIONS
    CTR_by_position = [0.0]*POSITIONS
    for line in fileinput.input(sys.argv[1]):
        record = json.loads(line)
        shown_items = record['shown_items']
        clicked_shown_items = record['clicked_shown_items']
        num_queries += 1
        for i in range(POSITIONS):
            if i >= len(shown_items):
                break
            if shown_items[i] in clicked_shown_items:
                num_clicks_by_position[i] += 1
    for i in range(POSITIONS):
        CTR_by_position[i] = float(num_clicks_by_position[i])/num_queries
    print json.dumps(CTR_by_position)

if __name__ == '__main__':
    main()
