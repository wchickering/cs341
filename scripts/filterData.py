#!/usr/bin/python
# To execute, enter something like:
# python filterData.py < 000000_0 > 000000_0_filt.json

import sys
import json

def main():
    lineNum = 0
    last_line = None
    duplicates = 0
    parseErrors = 0
    dataErrors = 0
    #constrainedQueries = 0
    for line in sys.stdin:
        lineNum = lineNum + 1
        if last_line == line:
            # skip duplicates
            duplicates += 1
            continue
        else:
            last_line = line
        try:
            record = json.loads(line)
            search_attributes = record['searchattributes']
        except:
            # skip malformed json 
            parseErrors += 1
            continue
        try:
            visitorid = int(record['visitorid'])
            assert(visitorid > 0)
            clickeditems = record['clickeditems']
            clicks = record['clicks']
            searchtimestamp = int(record['searchtimestamp'])
            assert(searchtimestamp > 0)
            searchattributes = record['searchattributes']
            shownitems = record['shownitems']
            assert(len(shownitems) > 0)
            shownitems_int = [int(item) for item in shownitems]
            wmsessionid = record['wmsessionid']
            assert(wmsessionid != '')
            rawquery = record['rawquery']
            assert(rawquery != '')
        except:
            # skip missing data/format errors
            dataErrors += 1
            continue
        #if len(search_attributes) != 1 or\
        #   'search_constraint' not in search_attributes or\
        #   search_attributes['search_constraint'] != '0':
        #    # skip if search constraints used
        #    constrainedQueries += 1
        #    sys.stderr.write(line)
        #    continue
        sys.stdout.write(line)
    # display statistics
    print >> sys.stderr, 'duplicates = ' + str(duplicates) +\
                       ', parseErrors = ' + str(parseErrors) +\
                       ', dataErrors = ' + str(dataErrors) #+\
                       #', constrainedQueries = ' + str(constrainedQueries)

if __name__ == '__main__':
    main()
