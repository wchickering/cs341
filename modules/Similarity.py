#!/usr/bin/env python
"""Similarity module

Similarity implements several different similarity measures between two sets of
strings.
"""

__author__ = """Charles Celerier <cceleri@cs.stanford.edu>,
              Bill Chickering <bchick@cs.stanford.edu>,
              Jamie Irvine <jirvine@cs.stanford.edu>"""

__date__ = """13 April 2013"""

def unionSize(s1, s2, delim=',', verbose=False):
    """Returns the size of the union of tokens in the comma delimited strings

    Parameters
    ==========

    s1, s2: str
            comma delimited string of tokens

    Examples
    ========
    >>> import Similarity as sim
    >>> sim.unionSize("a,b","c,d")
    4
    >>> sim.unionSize("a,b","b,d")
    3
    """
    tokens_1 = set(s1.split(delim))
    tokens_2 = set(s2.split(delim))
    if verbose:
        print "union: " + str(list(tokens_1.union(tokens_2)))
    return len(tokens_1.union(tokens_2))

def intersectSize(s1, s2, delim=',', verbose=False):
    """Returns the number of tokens in both comma delimited strings

    Parameters
    ==========

    s1, s2: str
            comma delimited string of tokens

    Examples
    ========
    >>> import Similarity as sim
    >>> sim.intersectSize("a,b", "b,c")
    1
    """
    tokens_1 = set(s1.split(delim))
    tokens_2 = set(s2.split(delim))
    if verbose:
        print "intersection: " + str(list(tokens_1.intersection(tokens_2)))
    return len(tokens_1.intersection(tokens_2))

def jaccard(s1, s2, delim=',', verbose=False):
    """Returns the jaccard similarity of the two comma delimited token sets

    Parameters
    ==========

    s1, s2: str
                  comma delimited string of tokens
    delim: str
           token delimiter

    Examples
    ========
    >>> import Similarity as sim
    >>> sim.jaccard("a,b,c,d", "b,c,e,f,g,h")
    0.3333333333333333
    """
    if verbose:
        tokens_1 = set(s1.split(delim))
        tokens_2 = set(s2.split(delim))
        print "intersection: " + str(list(tokens_1.intersection(tokens_2)))
        print "union: " + str(list(tokens_1.union(tokens_2)))
    return (float)(intersectSize(s1, s2, delim=delim)) / unionSize(s1, s2, delim=delim)

def main():
    from optparse import OptionParser, OptionGroup, HelpFormatter
    import sys
    
    usage = "usage: %prog [options] <string> <string>"
    parser = OptionParser(usage=usage)
    helpFormatter = HelpFormatter(indent_increment=2,\
                                  max_help_position=10,\
                                  width=80,\
                                  short_first=1)

    verboseGroup = OptionGroup(parser, "Verbose")
    verboseGroup.add_option("-v", "--verbose", action="store_true",\
                            dest="verbose")
    verboseGroup.add_option("-q", "--quiet", action="store_false",\
                            dest="verbose")
    parser.add_option_group(verboseGroup)
                            
    metricsGroup = OptionGroup(parser, "Metrics")
    metricsGroup.add_option("-u", "--union", action="store_true",\
                      dest="UNION",\
                      help="size of union")
    metricsGroup.add_option("-i", "--intersect", action="store_true",\
                      dest="INTERSECT",\
                      help="size of intersection")
    metricsGroup.add_option("-j", "--jaccard", action="store_true",\
                      dest="JACCARD",\
                      help="Jaccard similarity")

    parser.add_option_group(metricsGroup)
    parser.set_defaults(verbose=False)
    
    (options, args) = parser.parse_args()

    if (len(args) != 2):
        parser.print_usage()
        sys.exit()

    label = False
    if ((1 if options.INTERSECT else 0) + (1 if options.UNION else 0)\
            + (1 if options.JACCARD else 0) > 1):
        label = True

    if (options.INTERSECT):
        if label:
            print "intersection size: "\
                  + str(intersectSize(args[0], args[1], verbose=options.verbose))
        else:
            print str(intersectSize(args[0], args[1], verbose=options.verbose))
    if (options.UNION):
        if label:
            print "union size: "\
                  + str(unionSize(args[0], args[1], verbose=options.verbose))
        else:
            print str(unionSize(args[0], args[1], verbose=options.verbose))
    if (options.JACCARD):
        if label:
            print "jaccard similarity: "\
                  + str(jaccard(args[0], args[1], verbose=options.verbose))
        else:
                  print str(jaccard(args[0], args[1], verbose=options.verbose))
    sys.exit(0)

if __name__ == '__main__':
    main()
