#!/usr/bin/python
# To execute, do something like:
# prompt$ python indexMapperCarts.py < 000000_0.queries | sort -k1,1n -k2,2n | python indexReducer.py 000000_0.carts.posting.dict > 000000_0.carts.index

import sys
import json

def main():
    sep = '\t'
    cartId = 0
    carts = {}
    for line in sys.stdin:
        record = json.loads(line)
        for click in record['clicks']:
            if click['InCart'] == 'true':
                # the idea here is to only create entries for sessions
                # in which at least two items are clicked
                key = record['visitorid'] + record['wmsessionid']
                itemid = int(click['ItemId'])
                if key in carts:
                    if carts[key][1]:
                        print '%d%s%d'%(carts[key][1], sep, carts[key][0])
                        carts[key][1] = None
                    print '%d%s%d'%(itemid, sep, carts[key][0])
                else:
                    cartId += 1
                    carts[key] = []
                    carts[key].append(cartId)
                    carts[key].append(itemid)

if __name__ == '__main__':
  main()
