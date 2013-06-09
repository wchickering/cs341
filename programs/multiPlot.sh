#!/bin/bash

while getopts "c" opt
do
    case $opt in
        c)
            plotAgain=1
            ;;
    esac
done
shift $((OPTIND-1))

if [ ! $# -eq 7 ]
then
    echo "Usage: multiPlot.sh [-c] <plot type> <k> <insert_position> <n> <xmin> <xmax> <resolution>"
    exit 1
fi

RAWDATA=000050_0
INDEX=48chunk
export WCODE=`pwd`
mkdir -p data/tmp

plot=$1
k=$2
insert_position=$3
n=$4
xmin=$5
xmax=$6
inc=$7

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
multiplotFn=data/tmp/${RAWDATA}.${INDEX}.k${k}.i${insert_position}.n${n}.${xmin}-${xmax}.multiplot
if [ ! -f $multiplotFn ] || [ $plotAgain ]
then
    rm -f $multiplotFn
    i=0
    for param in {clicks,items,queries,titles,carts}
    do
        echo "Getting data for $param curve..."

        # start the watch for estimating running time
        starttime=`date +%s`
    
        # generate necessary files to configure multiReRank.sh
        templateFn=plot_templates/k${k}.i${insert_position}.n${n}.optimal.json
        paramsFn=tmp/k${k}.i${insert_position}.n${n}.${xmin}-${xmax}.coeff_${param}.json
        if [ ! -f $templateFn ]
        then
            exit 1
        fi
        cat $templateFn \
            | python programs/optimize.py coeff_$param $xmin $xmax $inc \
            > data/$paramsFn
    
        rcFn=data/${RAWDATA}.${INDEX}.multiReRankrc.k${k}.i${insert_position}.n${n}.${xmin}-${xmax}.coeff_${param}
        outFn=multiReRank.k${k}.i${insert_position}.n${n}.${xmin}-${xmax}.coeff_${param}.out
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

