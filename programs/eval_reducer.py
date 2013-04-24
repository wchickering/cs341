#!/usr/bin/env python

import sys
import json
import math

def printHistogram(histogram, offset, scale):
    bins = len(histogram)
    for i in range(bins):
        if i < bins/2 - 1 + offset:
            print '|' + '-'*int(math.ceil(histogram[i]*scale))
        elif i == bins/2 - 1 + offset:
            print '|' + '0'*int(math.ceil(histogram[i]*scale))
        else:
            print '|' + '+'*int(math.ceil(histogram[i]*scale))

def main(bins=64, offset=27, scale=0.1):
    net_delta = 0
    histogram = [0]*bins
    for line in sys.stdin:
        values = line.split('\t')
        delta = int(values[1])
        if delta > -(bins/2 + offset) and delta <= (bins/2 - offset): 
            histogram[bins/2 - 1 + offset + delta] += 1
        net_delta += delta
    printHistogram(histogram, offset, scale)
    print 'net_delta = ' + str(net_delta)

if __name__ == '__main__':
    main()
