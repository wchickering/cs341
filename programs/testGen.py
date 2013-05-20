#!/usr/bin/python
# To execute, do something like:
# > python testGen.py < 000000_0.queries > 000000_0.test_data

import sys
import json

def main():
    last_wmsessionid = None
    previously_clicked_items = None
    for line in sys.stdin:
        record = json.loads(line)
        if record['wmsessionid'] != last_wmsessionid:
            previously_clicked_items = []
            last_wmsessionid = record['wmsessionid']
 
        output = {}
        output['visitorid'] = record['visitorid']
        output['wmsessionid'] = record['wmsessionid']
        output['rawquery'] = record['rawquery']
        output['searchattributes'] = record['searchattributes']
        output['shown_items'] = record['shownitems']
        output['previously_clicked_items'] = previously_clicked_items
        output['clicked_shown_items'] = []
        for click in record['clicks']:
            if click['Position'] != '-1' and \
                    int(click['ItemId']) not in output['clicked_shown_items']:
                output['clicked_shown_items'].append(int(click['ItemId']))
        print json.dumps(output)
        
        for item in record['clickeditems']:
            if item not in previously_clicked_items:
                previously_clicked_items.append(item)

if __name__ == '__main__':
	main()
