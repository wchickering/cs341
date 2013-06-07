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

from pprint import pformat # prints dictionaries nicely

smallFont = matplotlib.font_manager.FontProperties(stretch='condensed',weight='book',size='small',family='monospace')
middleFont = matplotlib.font_manager.FontProperties(stretch='normal',weight='roman',size='large',family='monospace')
titleFont = matplotlib.font_manager.FontProperties(stretch='expanded',weight='demi',size='x-large',family='monospace')
kDefaultLegendSettings = dict(prop=middleFont, ncol=2, loc='best', fancybox=True, shadow=True)
labelpad = 12

class ref:
    def __init__(self, obj): self.obj=obj
    def get(self): return self.obj
    def set(self, obj): self.obj=obj

# takes a dictionary of defined parameter and a list of parameter name
# strings defining which ones will vary on the plot
class ParameterTable:
    def __init__(self, definedParameters, freeParameters=[]):
        self.__parameters = dict()
        for p in freeParameters:
            self.__parameters[p] = 'free or 0.00'
        for p in set(definedParameters.keys()).difference(set(self.__parameters)):
            p = p.encode('ascii', 'xmlcharrefreplace')
            if p in ['k', 'insert_position']:
                self.__parameters[p] = '%d' % definedParameters[p]
            elif p == 'ctr_by_position':
                self.__parameters[p] = definedParameters[p].encode('ascii', 'xmlcharrefreplace')
            else:
                self.__parameters[p] = '%.3f' % definedParameters[p]

    def __str__(self):
        return ('\n'.join(pformat(self.__parameters).split(', ')))[1:-1].replace('\'','')

def makeNDCGCurvePlot(resultsFn):
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
        ax.plot(x, reordered, '-', label=str(ParameterTable(params)), marker=marker)

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

def getMetricScores(resultsFn, metric, free_param, orig_score, orig_scores=[], multi=False):
    resultsFo = open(resultsFn)
    
    reordered_scores = []
    for line in resultsFo:
        dataInfo, params, stats = json.loads(line)
        
        if (metric == 'recall'):
            reordered_scores.append((params[str(free_param)],
                #(stats['recall_reordered_avg']-stats['recall_orig_avg'])\
                #        /stats['recall_orig_avg']*100))
                (stats['total_recall_front_reordered']-stats['total_recall_front_orig'])\
                        /stats['total_recall_front_orig']*100))
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
                orig_metric='_'.join(metric.split('_')[0:-1])+"_orig"
                try:
                    orig_scores.append((params[str(free_param)],
                        stats[orig_metric]))
                except KeyError:
                    orig_scores = []

    if (metric == 'NDCG16'):
        orig_score.set(stats['avg_orig_NDCG_scores'][15])

    resultsFo.close()

    reordered_scores.sort(key=lambda a: a[0])
    return reordered_scores, params, dataInfo 

def plotMetric(ax, resultsFn, metric, free_param, multi, smooth, orig_scores=[]): 
    orig_score_ref = ref(0)
    if multi:
        reordered_scores, params, dataInfo = getMetricScores(resultsFn, metric,
                                                             free_param, orig_score_ref,
                                                             orig_scores, True)
    else:
        reordered_scores, params, dataInfo = getMetricScores(resultsFn, metric,
                                                             free_param, orig_score_ref)

    if smooth:
        marker = None
        linestyle = '-'
    else:
        marker = 'o'
        linestyle = '-'

    ax.plot([x[0] for x in reordered_scores],
            [x[1] for x in reordered_scores],
            marker=marker, label=free_param, linestyle=linestyle,
            linewidth=2, markersize=8)

def makeOtherMetricPlot(resultsFn, options):
    # initialize figure
    metric_figure = plt.figure(figsize=(20,12))
    metric_figure.set_facecolor('w')
    ax = metric_figure.gca()

    # make a multi plot
    if options.multi:
        multiResultsFo = open(resultsFn)
        for line in multiResultsFo:
            line = line.rstrip()
            free_param, fn = line.split()
            orig_scores=[]
            plotMetric(ax, fn, options.metric, free_param, True, options.smooth, orig_scores)
        if orig_scores:
            if options.smooth:
                marker = None
            else:
                marker = '^'
            ax.plot([x[0] for x in orig_scores], [x[1] for x in orig_scores],
                    '-', marker=marker, label='original', linewidth=2, markersize=8)

        multiResultsFo.close()
        
        #metric_figure.subplots_adjust(right=0.50,left=0.08)
        #legend = ax.legend(prop=smallFont, ncol=2, loc=2,
        #                   fancybox=True, shadow=True,
        #                   bbox_to_anchor=(1.05,1), borderaxespad=0)
        if options.smooth:
            kDefaultLegendSettings['ncol'] = 1
        legend = ax.legend(**kDefaultLegendSettings)

    # make a plot with one curve
    else:
        plotMetric(ax, resultsFn, options.plot, options.free_param, False, options.smooth)
        #metric_figure.subplots_adjust(right=0.72)
        legend = ax.legend(**kDefaultLegendSettings)

    ## makes the legend draggable
    #legend.draggable()

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
    plotsGroup.add_option("--metric", dest="metric", \
                          help="type of plot (can be any key found in Evaluator.stats,\n"+\
                               "recall, NDCG, or NDCG16)",\
                          action="store", type="string", default=None)
    plotsGroup.add_option("--multi", dest="multi", \
                          help="multi output files in results file",\
                          action="store_true", default=False)
    plotsGroup.add_option("--smooth", dest="smooth", \
                          help="plot a line without markers",\
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

    ### heavy lifting for making the plots ###
    resultsFn = args[0]
    if options.metric == 'NDCG':
        ax = makeNDCGCurvePlot(resultsFn)
    else:
        ax = makeOtherMetricPlot(resultsFn, options)

    ### formatting details ###
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

    ax.yaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter('%.4f'))

    if options.multi:
        xlabel = 'C'
    else:
        xlabel = str(free_param)

    ax.set_xlabel(xlabel, labelpad=labelpad, fontproperties=middleFont)
    ax.set_ylabel('score', labelpad=labelpad, fontproperties=middleFont)
        
    #ax.text(1.2, 0.5, textstr, transform=ax.transAxes, fontsize=14,
    #        verticalalignment='top', bbox=props)

    title = options.metric + ' scores for '
    if options.metric == 'recall':
        title = '% increase in recall over original data for '
    elif options.metric == 'NDCG16':
        title = 'top page NDCG score for '
        if not options.multi:
            ax.text(0.4,0.95,'original NDCG score = %.3f' % orig_score_ref.get(),
                    transform=ax.transAxes, fontproperties=middleFont,
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    title += resultsFn.split('.')[0]

    metric_figure.suptitle(title, fontproperties=titleFont)

    plt.show()

if __name__ == '__main__':
    main()
