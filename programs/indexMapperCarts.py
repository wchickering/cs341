#!/usr/bin/python
# To execute, do something like:
# prompt$ python indexMapperCarts.py < 000000_0.queries | sort -k1,1n -k2,2n | python indexReducer.py 000000_0.carts.posting.dict > 000000_0.carts.index

import sys
import json

def main():
    sep = '\t'
    cartId = 0
    cartDict = {}
    for line in sys.stdin:
        record = json.loads(line)
        for click in record['clicks']:
            if click['InCart'] == 'true':
                # the idea here is to only create entries for sessions
                # in which at least two items are clicked
                key = record['visitorid'] + record['wmsessionid']
                itemid = int(click['ItemId'])
                if key in cartDict:
                    if cartDict[key][1]:
                        print '%d%s%d'%(cartDict[key][1], sep, cartDict[key][0])
                        cartDict[key][1] = None
                    print '%d%s%d'%(itemid, sep, cartDict[key][0])
                else:
                    cartId += 1
                    cartDict[key] = []
                    cartDict[key].append(cartId)
                    cartDict[key].append(itemid)

if __name__ == '__main__':
  main()
