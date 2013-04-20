#!/usr/bin/env python

import sys
import json

def printHistogram(histogram, scale):
    bins = len(histogram)
    for i in range(bins):
        if i < bins/2:
            print '|' + '-'*int(histogram[i]*scale)
        else:
            print '|' + '+'*int(histogram[i]*scale)

def main(bins=64, scale=0.1):
    net_delta = 0
    histogram = [0]*bins
    for line in sys.stdin:
        key, value_str = line.split('\t')
        value = int(value_str)
        if value == 0:
            continue
        if value > -bins/2 and value <= bins/2: 
            histogram[bins/2 + value - 1] += 1
        net_delta += value
    printHistogram(histogram, scale)
    print 'net_delta = ' + str(net_delta)

if __name__ == '__main__':
    main()
