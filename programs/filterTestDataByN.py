#!/usr/bin/env python

import sys

# import local modules
from Query import Query

def parseArgs():
    from optparse import OptionParser, OptionGroup, HelpFormatter

    usage = "usage: %prog -n N <filename>"

    parser = OptionParser(usage=usage)
    helpFormatter = HelpFormatter(indent_increment=2,\
                                  max_help_position=10,\
                                  width=80,\
                                  short_first=1)

    optionGroup = OptionGroup(parser, "Options")
    optionGroup.add_option("-n", type="int", dest="n", help="filter away results less than n")
    parser.add_option_group(optionGroup)

    parser.set_defaults(n=0)

    (options, args) = parser.parse_args()

    if (len(args) > 1):
        parser.print_usage()
        sys.exit()

    return (options, args)

def main():
    (options, args) = parseArgs()
    if len(args) == 1:
        inputFile = open(args[0])
    else:
        inputFile = sys.stdin

    for line in inputFile:
        query = Query(line)
        if len(query.shown_items) < options.n:
            continue
    
        print line.rstrip()

if __name__ == '__main__':
    main()
