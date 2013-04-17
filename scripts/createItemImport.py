#!/usr/bin/python
# To execute, enter something like:
# python createItemImport.py items_reformatted.json > items.csv

import sys
import fileinput
import json

# Locally defined modules
import encodeField

def main():
    lineNum = 0
    numErrors = 0
    for line in fileinput.input(sys.argv[1]):
        lineNum = lineNum + 1
        try:
            record = json.loads(line)
            output = encodeField.encode(record['itemId']) + ',' + \
                     encodeField.encodeNullable(record, 'parentItemId') + ',' + \
                     encodeField.encode(record['name']) + ',' + \
                     encodeField.encode(record['baseItemPrice']) + ',' + \
                     encodeField.encode(record['salePrice']) + ',' + \
                     encodeField.encode(record['upc']) + ',' + \
                     encodeField.encode(record['categoryPath']) + ',' + \
                     encodeField.encodeNullable(record, 'shortDescription') + ',' + \
                     encodeField.encodeNullable(record, 'longDescription') + ',' + \
                     encodeField.encode(record['brandName']) + ',' + \
                     encodeField.encode(record['thumbnailImage']) + ',' + \
                     encodeField.encode(record['mediumImage']) + ',' + \
                     encodeField.encode(record['largeImage']) + ',' + \
                     encodeField.encode(record['productTrackingUrl']) + ',' + \
                     encodeField.encode(record['freeShipping']) + ',' + \
                     encodeField.encode(record['ninetySevenCentShipping']) + ',' + \
                     encodeField.encodeNullable(record, 'standardShipRate') + ',' + \
                     encodeField.encodeNullable(record, 'twoThreeDayShippingRate') + ',' + \
                     encodeField.encodeNullable(record, 'overnightShippingRate') + ',' + \
                     encodeField.encodeNullable(record, 'size') + ',' + \
                     encodeField.encodeNullable(record, 'color') + ',' + \
                     encodeField.encode(record['availableOnline'])
            print output
        except:
            numErrors = numErrors + 1
            sys.stderr.write('Error occurred on line: ' + str(lineNum) + '\n')
            raise

if __name__ == '__main__':
    main()
