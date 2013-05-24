#!/usr/bin/env python
"""plots the json serialized stats from Evaluator objects 
"""

__author__ = """Charles Celerier <cceleri@cs.stanford.edu>,
              Bill Chickering <bchick@cs.stanford.edu>,
              Jamie Irvine <jirvine@cs.stanford.edu>"""

__date__ = """16 April 2013"""

# import standard modules
import sys
import json
import math

# import non-standard modules
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

smallFont = matplotlib.font_manager.FontProperties(stretch='condensed',weight='book',size='small',family='monospace')
middleFont = matplotlib.font_manager.FontProperties(stretch='normal',weight='roman',size='large')
titleFont = matplotlib.font_manager.FontProperties(stretch='expanded',weight='demi',size='x-large')

def parameterInfoString(params):
    s = "+--------------------------+\n"\
       +"|    k = %2d  insert = %2d   |\n" % ( params["k"], params["insert_position"] )\
       +"+------------+------+------+\n"\
       +"|       Rank | %.2f | %.2f |\n" % ( params["coeff_rank"], params["exp_rank"] )\
       +"|      Items | %.2f | %.2f |\n" % ( params["coeff_items"], params["exp_items"] )\
       +"|     Clicks | %.2f | %.2f |\n" % ( params["coeff_clicks"], params["exp_clicks"] )\
       +"|    Queries | %.2f | %.2f |\n" % ( params["coeff_queries"], params["exp_queries"] )\
       +"|      Carts | %.2f | %.2f |\n" % ( params["coeff_carts"], params["exp_carts"] )\
       +"| Item title | %.2f | %.2f |\n" % ( params["coeff_item_title"], params["exp_item_title"] )\
       +"+------------+------+------+"

    return s

def parseArgs():
    from optparse import OptionParser, OptionGroup, HelpFormatter

    usage = "usage: %prog "\
            + "<filename>"

    parser = OptionParser(usage=usage)
    helpFormatter = HelpFormatter(indent_increment=2,
                                  max_help_position=10,
                                  width=80,
                                  short_first=1)

    (options, args) = parser.parse_args()

    if (len(args) != 1):
        parser.print_usage()
        sys.exit()

    return (options, args)

def getLineCount(Fo):
    savedOffset = Fo.tell()
    Fo.seek(0)
    for i, l in enumerate(Fo):
        pass
    Fo.seek(savedOffset)
    return i + 1

def plotNDCGCurves(resultsFo):
    numResults = getLineCount(resultsFo)

    nrows  = numResults/3 + 1 if numResults % 3 else numResults / 3
    ncols = 3
    
    NDCG_figure = plt.figure()
    plt.get_current_fig_manager().resize(1600,250*nrows)
    ax = NDCG_figure.gca()
    ax.set_xlabel('# of results considered', labelpad=10, fontproperties=middleFont)
    ax.set_ylabel('NDCG score', labelpad=8, fontproperties=middleFont)

    row = -1 
    col = 0
    newLabels = ["original"]
    for i, line in enumerate(resultsFo):
        marker = matplotlib.lines.Line2D.filled_markers[i]
        dataInfo, params, stats = json.loads(line)
        newLabels.append(parameterInfoString(params))

        x = np.arange(1,len(stats['avg_orig_NDCG_scores'])+1)

        # plot original scores
        if (i == 0):
            original = np.array(stats['avg_orig_NDCG_scores'])
            ax.plot(x, original, '-', label='original', linewidth=5)

        # plot next reordered data
        reordered = np.array(stats['avg_reordered_NDCG_scores'])
        ax.plot(x, reordered, '-', label='reordered ' + str(i), marker=marker)

        ## red between if losing, green between if winning
        #ax.fill_between(x, original, reordered, where=original>=reordered, facecolor='red', interpolate=True)
        #ax.fill_between(x, original, reordered, where=original<=reordered, facecolor='green', interpolate=True)

        # add the boxes on the graph
        #addParameterBox(ax, params, 0.95, 0.12)

    handles, _ = ax.get_legend_handles_labels()
    legend = ax.legend(handles, newLabels, prop=smallFont, ncol=4, loc='lower right', fancybox=True, shadow=True)
    legend.draggable()

    NDCG_figure.subplots_adjust(hspace=0.35,wspace=0.2,left=0.05,right=0.95,top=0.93,bottom=0.07)
    NDCG_figure.suptitle('NDCG scores for %s' % dataInfo['dataFn'].split('/')[-1], fontproperties=titleFont)

def main():
    (options, args) = parseArgs()
    
    resultsFo = open(args[0])
    
    plotNDCGCurves(resultsFo)

    plt.show()

if __name__ == '__main__':
    main()
