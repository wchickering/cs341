#!/bin/bash

plotAgain=false
while getopts "c" opt
do
    case $opt in
        c)
            plotAgain=true
            ;;
    esac
done
shift $((OPTIND-1))

if [ ! $# -eq 5 ]
then
    echo "Usage: multiPlot.sh [-c] <plot type> <regime (e.g 3, 15, or 1000)> <xmin> <xmax> <resolution>"
    exit 1
fi

RAWDATA=000050_0
INDEX=48chunk
export WCODE=`pwd`
mkdir -p data/tmp

plot=$1
regime=$2
xmin=$3
xmax=$4
inc=$5

totalRuns=5
paceSoFar=0
function estimateTimeRemaining() {
    latestStartTime=$1
    latestEndTime=$2
    runsRemaining=$3

    paceSoFar=`echo "scale=5; ($paceSoFar*($totalRuns-$runsRemaining-1)+($endtime-$starttime))/($totalRuns-$runsRemaining)" | bc` 
    eval "$4=$(echo "scale=2; $paceSoFar*(5-$i)/60" | bc)"
}

## make multiple multiReRank json files from a skeleton
multiplotFn=data/tmp/${RAWDATA}.${INDEX}.k${regime}.${xmin}-${xmax}.multiplot
if [ ! -f $multiplotFn ] || [ $plotAgain ]
then
    rm -f $multiplotFn
    i=0
    for param in {clicks,item_title,carts,items,queries}
    do
        echo "Getting data for $param curve..."

        # start the watch for estimating running time
        starttime=`date +%s`
    
        # generate necessary files to configure multiReRank.sh
        paramsFn=tmp/k${regime}.${xmin}-${xmax}.coeff_${param}.json
        cat plot_templates/k${regime}.optimal.json \
            | python programs/optimize.py coeff_$param $xmin $xmax $inc \
            > data/$paramsFn
    
        rcFn=data/${RAWDATA}.${INDEX}.multiReRankrc.k${regime}.${xmin}-${xmax}.coeff_${param}
        outFn=multiReRank.k${regime}.${xmin}-${xmax}.coeff_${param}.out
        rm -f $rcFn
        cp plot_templates/multiReRankrc $rcFn
        echo PARAMS=$paramsFn >> $rcFn
        echo OUTPUT=$outFn >> $rcFn
    
        # run multiReRank.sh
        export MULTIRERANK_PARAMS=$rcFn
        programs/multiReRank.sh
    
        # append line to multiplot file
        echo coeff_$param data/$RAWDATA.$INDEX.$outFn >> $multiplotFn

        ## DOES NOT WORK
        ## print the estimated time remaining
        #endtime=`date +%s`
        #estimateTimeRemaining $startTime $endTime "$totalRuns-$i" timeRemaining
        #echo "Estimated time remaining: $timeremaining minutes"
        i=$i+1
    done
fi

python programs/simplePlot.py --smooth --multi --metric $plot $multiplotFn

