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
middleFont = matplotlib.font_manager.FontProperties(stretch='normal',weight='roman',size='large',family='monospace')
titleFont = matplotlib.font_manager.FontProperties(stretch='expanded',weight='demi',size='x-large',family='monospace')
labelpad = 12

def parameterInfoString(params, minus=""):
    s = "+--------------------------+\n"\
       +"|    k = %2d  insert = %2d   |\n" % ( params["k"], params["insert_position"] )\
       +"+------------+------+------+\n"
    if (minus != "rank"):
       s += "|       Rank | %.2f | %.2f |\n" % ( params["coeff_rank"], params["exp_rank"] )
    if (minus != "items"):
       s += "|      Items | %.2f | %.2f |\n" % ( params["coeff_items"], params["exp_items"] )
    if (minus != "clicks"):
       s += "|     Clicks | %.2f | %.2f |\n" % ( params["coeff_clicks"], params["exp_clicks"] )
    if (minus != "queries"):
       s += "|    Queries | %.2f | %.2f |\n" % ( params["coeff_queries"], params["exp_queries"] )
    if (minus != "carts"):
       s += "|      Carts | %.2f | %.2f |\n" % ( params["coeff_carts"], params["exp_carts"] )
    if (minus != "item_title"):
       s += "| Item title | %.2f | %.2f |\n" % ( params["coeff_item_title"], params["exp_item_title"] )

    s += "+------------+------+------+"

    return s

def parseArgs():
    from optparse import OptionParser, OptionGroup, HelpFormatter

    usage = "usage: %prog "\
            + "<filename> "\
            + "<coeff or exp> "\
            + "<parameter>"

    parser = OptionParser(usage=usage)
    helpFormatter = HelpFormatter(indent_increment=2,
                                  max_help_position=10,
                                  width=80,
                                  short_first=1)

    (options, args) = parser.parse_args()

    if (len(args) != 3):
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
    resultsFo.seek(0)
    
    NDCG_figure = plt.figure()
    plt.get_current_fig_manager().resize(1600,1000)
    ax = NDCG_figure.gca()
    ax.set_xlabel('# of results considered', labelpad=labelpad, fontproperties=middleFont)
    ax.set_ylabel('NDCG score', labelpad=labelpad, fontproperties=middleFont)

    for i, line in enumerate(resultsFo):
        marker = matplotlib.lines.Line2D.filled_markers[i]
        dataInfo, params, stats = json.loads(line)

        x = range(1,len(stats['avg_orig_NDCG_scores'])+1)

        # plot original scores
        if (i == 0):
            original = np.array(stats['avg_orig_NDCG_scores'])
            ax.plot(x, original, '-', label='original', linewidth=5)

        # plot next reordered data
        reordered = stats['avg_reordered_NDCG_scores']
        ax.plot(x, reordered, '-', label=parameterInfoString(params), marker=marker)

    legend = ax.legend(prop=smallFont, ncol=4, loc='lower right', fancybox=True, shadow=True)
    legend.draggable()

    NDCG_figure.suptitle('NDCG scores for %s' % dataInfo['dataFn'].split('/')[-1], fontproperties=titleFont)

def plotNDCG16Curve(resultsFo, param, which="coeff"):
    resultsFo.seek(0)

    NDCG16_figure = plt.figure()
    plt.get_current_fig_manager().resize(1600,1000)
    ax = NDCG16_figure.gca()

    frontPageNDCGScores = []
    for i, line in enumerate(resultsFo):
        marker = matplotlib.lines.Line2D.filled_markers[i]
        dataInfo, params, stats = json.loads(line)
        
        frontPageNDCGScores.append(
                tuple([params[which+"_"+param],
                    stats['avg_reordered_NDCG_scores'][15]]))

    frontPageNDCGScores.sort(key=lambda a: a[0])

    ax.plot([x[0] for x in frontPageNDCGScores],
            [x[1] for x in frontPageNDCGScores],
            'o-', label=parameterInfoString(params, minus=param),
            linewidth=2, markersize=8)

    xlabel = which+"_"+param+" = ???"
    if (which == "coeff"):
        xlabel += ", exp_"+param+" = "+str(params['exp_'+param])
    else:
        xlabel = "coeff_"+param+" = "+str(params['coeff_'+param])+", "+ xlabel
    ax.set_xlabel(xlabel, labelpad=labelpad, fontproperties=middleFont)
    ax.set_ylabel('front page NDCG score', labelpad=labelpad, fontproperties=middleFont)

    legend = ax.legend(prop=middleFont, ncol=4, loc='best',
                       fancybox=True, shadow=True)
    legend.draggable()

    NDCG16_figure.suptitle('Front Page NDCG Scores for %s'
                             % dataInfo['dataFn'].split('/')[-1],
                            fontproperties=titleFont)

def main():
    (options, args) = parseArgs()
    
    resultsFo = open(args[0])
    which = args[1]
    param = args[2]
    
    plotNDCGCurves(resultsFo)
    plotNDCG16Curve(resultsFo, param, which=which)

    plt.show()

if __name__ == '__main__':
    main()
