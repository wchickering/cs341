#!/bin/bash 

# This script assumes WCODE and RERANK_PARAMS already defined and exported.
# RERANK_PARAMS should be the path to a file containing variable definitions
# like these:
#WORKERS=8
#RAWDATA=000050_0
#N=0
#K=3
#INSERT_POSITION=0

source $RERANK_PARAMS

PROGRAMS=${WCODE}/programs
RERANK_PROG=${PROGRAMS}/reRank.py
FILTER_RANKABLE_PROG=${PROGRAMS}/filterTestDataRankable.py
FILTER_CLICKS_PROG=${PROGRAMS}/filterTestDataClicks.py
TEST_DATA_STATS_PROG=${PROGRAMS}/test_data_stats.py
EVAL_PROG=${PROGRAMS}/FinalEvaluator.py
DATA=${WCODE}/data
TEST_DATA=${DATA}/${RAWDATA}.test_data
TEST_DATA_STATS=${TEST_DATA}.stats
FILTERED_TEST_DATA_RANKABLE=${TEST_DATA}.filtered.rankable
FILTERED_TEST_DATA_RANKABLE_STATS=${FILTERED_TEST_DATA_RANKABLE}.stats
FILTERED_TEST_DATA=${TEST_DATA}.filtered
RERANK_PROG_OUTPUT=${DATA}/${RAWDATA}.RANDOM.k${K}.reordered_queries
EVAL_OUTPUT=${DATA}/${RAWDATA}.RANDOM.k${K}.eval
CTR_BY_POSITION_FILE=${PROGRAMS}/${CTR_BY_POSITION}
RERANK_LOG=${DATA}/rerank_log.txt

if [ ! -f $FILTERED_TEST_DATA ] || [ ! -f $FILTERED_TEST_DATA_RANKABLE ]
then
    echo "Filtering test data . . ."
    cat $TEST_DATA | python $FILTER_RANKABLE_PROG > $FILTERED_TEST_DATA_RANKABLE
    cat $FILTERED_TEST_DATA_RANKABLE | python $FILTER_CLICKS_PROG > $FILTERED_TEST_DATA
fi

if [ ! -f $TEST_DATA_STATS ]
then
    echo "Generating test data stats . . ."
    python $TEST_DATA_STATS_PROG $TEST_DATA > $TEST_DATA_STATS
fi

if [ ! -f $FILTERED_TEST_DATA_RANKABLE_STATS ]
then
    echo "Generating filtered test data stats . . ."
    python $TEST_DATA_STATS_PROG $FILTERED_TEST_DATA_RANKABLE > $FILTERED_TEST_DATA_RANKABLE_STATS
fi

echo "Randomly Reranking . . ."
python $RERANK_PROG --workers $WORKERS --verbose -n $N -k $K --insert_position $INSERT_POSITION --random $FILTERED_TEST_DATA > $RERANK_PROG_OUTPUT

echo "Evaluating . . ."
python $EVAL_PROG -k $K --test_data_fname $TEST_DATA_STATS --rankable_data_fname $FILTERED_TEST_DATA_RANKABLE_STATS --ctr_fname $CTR_BY_POSITION_FILE $RERANK_PROG_OUTPUT > $EVAL_OUTPUT
echo "***********************************************************" >> $RERANK_LOG
echo $(date) >> $RERANK_LOG
echo >> $RERANK_LOG
cat $RERANK_PARAMS $EVAL_OUTPUT >> $RERANK_LOG
tail -n 17 $EVAL_OUTPUT
