#!/usr/bin/env python
"""plots the json serialized stats from Evaluator objects 
"""

__author__ = """Charles Celerier <cceleri@cs.stanford.edu>,
              Bill Chickering <bchick@cs.stanford.edu>,
              Jamie Irvine <jirvine@cs.stanford.edu>"""

__date__ = """24 May 2013"""

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

def parameterInfoString(params, free_param):
    s = "+---------------------------+\n"
    if str(free_param) == "k":
       s += "|  k = ??  insert_pos = %2d  |\n" % ( params["insert_position"] )
    elif str(free_param) == 'insert_position':
       s += "|  k = %2d  insert_pos = ??  |\n" % ( params["k"] )
    else:
       s += "|  k = %2d  insert_pos = %2d  |\n" % ( params["k"], params["insert_position"] )

    s += "+------------+-------+------+\n"\
       + "|   index    | coeff | exp  |\n"\
       + "+------------+-------+------+\n"

    for index in ['rank','items','clicks','queries','carts','item_title']:
        if (free_param[1] != index):
           s += "| %10s |  %.2f | %.2f |\n" % ( index, params["coeff_"+index], params["exp_"+index] )
        elif (free_param[0] == 'coeff'):
           s += "| %10s |  ???? | %.2f |\n" % ( index, params["exp_"+index] )
        elif (free_param[0] == 'exp'):
           s += "| %10s |  %.2f | ???? |\n" % ( index, params["coeff_"+index] )
    s += "+------------+------+------+\n"

    return s

def plotNDCGCurve(resultsFn):
    resultsFo = open(resultsFn)
    
    NDCG_figure = plt.figure(figsize=(20,12))
    ax = NDCG_figure.gca()
    NDCG_figure.set_facecolor('w')

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
        ax.plot(x, reordered, '-', label=parameterInfoString(params, FreeParam()), marker=marker)

    resultsFo.close()

    #######################
    ### PLOT FORMATTING ###
    #######################
    ax.set_xlabel('# of results considered', labelpad=labelpad, fontproperties=middleFont)
    ax.set_ylabel('NDCG score', labelpad=labelpad, fontproperties=middleFont)

    legend = ax.legend(prop=smallFont, ncol=4, loc='lower right', fancybox=True, shadow=True)
    legend.get_frame().set_alpha(0.92)
    #NDCG_figure.subplots_adjust(right=0.6,left=0.08)
    #legend = ax.legend(prop=smallFont, ncol=3, loc=2,
    #                   fancybox=True, shadow=True,
    #                   bbox_to_anchor=(1.05,1), borderaxespad=0)
    legend.draggable()

    NDCG_figure.suptitle('NDCG scores for %s' % dataInfo['dataFn'].split('/')[-1], fontproperties=titleFont)

    return ax

class ref:
    def __init__(self, obj): self.obj=obj
    def get(self): return self.obj
    def set(self, obj): self.obj=obj

def getMetricScores(resultsFn, metric, free_param, orig_score, orig_scores=[],
                    multi=False):
    resultsFo = open(resultsFn)
    
    reordered_scores = []
    for line in resultsFo:
        dataInfo, params, stats = json.loads(line)
        
        if (metric == 'recall'):
            reordered_scores.append((params[str(free_param)],
                (stats['recall_reordered_avg']-stats['recall_orig_avg'])\
                        /stats['recall_orig_avg']))
        elif (metric == 'NDCG16'):
            reordered_scores.append((params[str(free_param)],
                stats['avg_reordered_NDCG_scores'][15]))
            if multi:
                orig_scores.append((params[str(free_param)],
                    stats['avg_orig_NDCG_scores'][15]))
        else:
            reordered_scores.append((params[str(free_param)],
                stats[metric]))
            if multi:
                orig_scores.append((params[str(free_param)],
                    stats[metric]))

    if (metric == 'NDCG16'):
        orig_score.set(stats['avg_orig_NDCG_scores'][15])

    resultsFo.close()

    reordered_scores.sort(key=lambda a: a[0])
    return reordered_scores, params, dataInfo 

### messy class to deal with free paramters
class FreeParam:
    def __init__(self, p=""):
        if p:
            if p == 'k' or p == 'insert_position':
                self._p = p
            else:
                self._p = p.split('_',1)
        else:
            self._p = p

    def __str__(self):
        if type(self._p) != str:
            return '_'.join(self._p)
        return self._p

    def __getitem__(self, index):
        if type(self._p) == str:
            return self._p
        else:
            return self._p[index]

    def __repr__(self):
        return 'FreeParam(%r)' % repr(self._p)

def plotMetric(metric_figure, resultsFn, metric, free_param, multi, orig_scores=[]):
    
    orig_score_ref = ref(0)
    if multi:
        reordered_scores, params, dataInfo = getMetricScores(resultsFn, metric,
                                                          free_param, orig_score_ref,
                                                          orig_scores, True)
    else:
        reordered_scores, params, dataInfo = getMetricScores(resultsFn, metric, free_param, orig_score_ref)

    ax = metric_figure.gca()

    if multi:
        ax.plot([x[0] for x in reordered_scores],
                [x[1] for x in reordered_scores],
                'o-', label=parameterInfoString(params, free_param),
                linewidth=2, markersize=8)
    else:
        ax.plot([x[0] for x in reordered_scores],
                [x[1] for x in reordered_scores],
                'o-', label=parameterInfoString(params, free_param),
                linewidth=2, markersize=8)

    #######################
    ### PLOT FORMATTING ###
    #######################
    if multi:
        xlabel = 'free parameter'
    else:
        xlabel = str(free_param)

    ax.set_xlabel(xlabel, labelpad=labelpad, fontproperties=middleFont)
    if metric == 'recall':
        ax.set_ylabel('% increase in recall over original data', labelpad=labelpad, fontproperties=middleFont)
    elif metric == 'NDCG16':
        ax.set_ylabel('top page NDCG score', labelpad=labelpad, fontproperties=middleFont)
        
        if not multi:
            ax.text(0.4,0.95,'original NDCG score = %.3f' % orig_score_ref.get(),
                    transform=ax.transAxes, fontproperties=middleFont,
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    else:
        ax.set_ylabel(metric, labelpad=labelpad, fontproperties=middleFont)

    metric_figure.suptitle(metric + ' scores for %s'
                             % dataInfo['dataFn'].split('/')[-1],
                            fontproperties=titleFont)

    return ax

def parseArgs():
    from optparse import OptionParser, OptionGroup, HelpFormatter

    usage = "usage: %prog "\
            + "<multiReRank.sh json output file>"\

    parser = OptionParser(usage=usage)
    helpFormatter = HelpFormatter(indent_increment=2,
                                  max_help_position=10,
                                  width=80,
                                  short_first=1)
    
    plotsGroup = OptionGroup(parser, "Plot Settings")
    plotsGroup.add_option("--plot", dest="plot", \
                          help="type of plot (can be any key found in Evaluator.stats,\n"+\
                               "recall, NDCG, or NDCG16)",\
                          action="store", type="string", default=None)
    plotsGroup.add_option("--multi", dest="multi", \
                          help="multi output files in results file",\
                          action="store_true", default=False)
    plotsGroup.add_option("--free-param", dest="free_param", \
                          help="free parameter",\
                          action="store", type="string", default=None)
    parser.add_option_group(plotsGroup)

    plotSettingsGroup = OptionGroup(parser, "Plot Settings")
    plotSettingsGroup.add_option("--xmin", dest="xmin", \
                          help="minimum value on x axis",\
                          action="store", type="float", default=None)
    plotSettingsGroup.add_option("--xmax", dest="xmax", \
                          help="maximum value on x axis",\
                          action="store", type="float", default=None)
    plotSettingsGroup.add_option("--ymin", dest="ymin", \
                          help="minimum value on y axis",\
                          action="store", type="float", default=None)
    plotSettingsGroup.add_option("--ymax", dest="ymax", \
                          help="maximum value on y axis",\
                          action="store", type="float", default=None)
    parser.add_option_group(plotSettingsGroup)

    (options, args) = parser.parse_args()

    if (len(args) != 1):
        parser.print_usage()
        sys.exit()

    return (options, args)

def main():
    (options, args) = parseArgs()

    resultsFn = args[0]

    if options.plot == 'NDCG':
        ax = plotNDCGCurve(resultsFn)
    else:
        metric_figure = plt.figure(figsize=(20,12))
        metric_figure.set_facecolor('w')
        if options.multi:
            multiResultsFo = open(resultsFn)
            for line in multiResultsFo:
                line = line.rstrip()
                free_param, fn = line.split()
                free_param = FreeParam(free_param)
                orig_scores=[]
                ax = plotMetric(metric_figure, fn, options.plot, free_param, True, orig_scores)
            if not (options.plot == 'recall'):
                ax.plot([x[0] for x in orig_scores],
                        [x[1] for x in orig_scores],
                        '^-', label='original',
                        linewidth=2, markersize=8)

            multiResultsFo.close()
            
            metric_figure.subplots_adjust(right=0.50,left=0.08)
            legend = ax.legend(prop=middleFont, ncol=2, loc=2,
                               fancybox=True, shadow=True,
                               bbox_to_anchor=(1.05,1), borderaxespad=0)
        else:
            ax = plotMetric(metric_figure, resultsFn, options.plot, FreeParam(options.free_param), False)
            metric_figure.subplots_adjust(right=0.72)
            legend = ax.legend(prop=middleFont, ncol=2, loc=2,
                               fancybox=True, shadow=True,
                               bbox_to_anchor=(1.05,1), borderaxespad=0)

        #legend.draggable()

    xlim = list(ax.get_xlim())
    ylim = list(ax.get_ylim())
    if options.xmin:
        xlim[0] = options.xmin
    if options.xmax:
        xlim[1] = options.xmax
    if options.ymin:
        ylim[0] = options.ymin
    if options.ymax:
        ylim[1] = options.ymax
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)

    ax.yaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter('%.5f'))

    plt.show()

if __name__ == '__main__':
    main()
