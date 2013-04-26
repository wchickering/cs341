#!/usr/bin/python
# To execute, do something like:
# > python testGen.py < 000000_0.queries > 000000_0.test_data

import sys
import json

def main():
    last_visitorid = None
    previously_clicked_items = None
    for line in sys.stdin:
        record = json.loads(line)
        if record['visitorid'] != last_visitorid:
            previously_clicked_items = []
            last_visitorid = record['visitorid']
 
        output = {}
        output['visitorid'] = record['visitorid']
        output['wmsessionid'] = record['wmsessionid']
        output['rawquery'] = record['rawquery']
        output['searchattributes'] = record['searchattributes']
        output['shown_items'] = record['shownitems']
        output['previously_clicked_items'] = previously_clicked_items
        output['clicked_shown_items'] = record['clickeditems']
        print json.dumps(output)
        
        for item in record['clickeditems']:
            if item not in previously_clicked_items:
                previously_clicked_items.append(item)

if __name__ == '__main__':
	main()
