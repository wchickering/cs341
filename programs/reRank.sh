#!/bin/bash 

# This script assumes WCODE and RERANK_PARAMS already defined and exported.
# RERANK_PARAMS should be the path to a file containing variable definitions
# like these:
#MODE=load  # set to 'dump' or 'load'
#
#WORKERS=8
#
#RAWDATA=000050_0
#
#K=3
#INSERT_POSITION=0
#COEFF_CTR=0.0
#CTR_BY_POSITION=16chunk.CTRs.json
#COEFF_RANK=0.0
#EXP_RANK=1.0
#INDEX_I=000051_0
#INDEX_Q=000051_0
#INDEX_C=000051_0
#INDEX_A=000051_0
#COEFF_ITEMS=0.0
#COEFF_QUERIES=0.0
#COEFF_CLICKS=0.0
#COEFF_CARTS=1.0
#COEFF_ITEM_TITLE=0.0
#EXP_ITEMS=1.0
#EXP_QUERIES=1.0
#EXP_CLICKS=1.0
#EXP_CARTS=1.0
#EXP_ITEM_TITLE=1.0

source $RERANK_PARAMS

PROGRAMS=${WCODE}/programs
RERANK_PROG=${PROGRAMS}/reRank.py
FILTER_RANKABLE_PROG=${PROGRAMS}/filterTestDataRankable.py
FILTER_CLICKS_PROG=${PROGRAMS}/filterTestDataClicks.py
TEST_DATA_STATS_PROG=${PROGRAMS}/test_data_stats.py
EVAL_PROG=${PROGRAMS}/FinalEvaluator.py
DATA=${WCODE}/data
SCORES=${DATA}/scores
TEST_DATA=${DATA}/${RAWDATA}.test_data
TEST_DATA_STATS=${TEST_DATA}.stats
FILTERED_TEST_DATA_RANKABLE=${TEST_DATA}.filtered.rankable
FILTERED_TEST_DATA_RANKABLE_STATS=${FILTERED_TEST_DATA_RANKABLE}.stats
FILTERED_TEST_DATA=${TEST_DATA}.filtered
RERANK_PROG_OUTPUT=${DATA}/${RAWDATA}.${INDEX_I}.k${K}.reordered_queries
EVAL_OUTPUT=${DATA}/${RAWDATA}.${INDEX_I}.k${K}.eval
CTR_BY_POSITION_FILE=${PROGRAMS}/${CTR_BY_POSITION}
INDEX_ITEMS=${DATA}/${INDEX_I}.items.index
DICT_ITEMS=${DATA}/${INDEX_I}.items.posting.dict
INDEX_QUERIES=${DATA}/${INDEX_Q}.queries.index
DICT_QUERIES=${DATA}/${INDEX_Q}.queries.posting.dict
INDEX_CLICKS=${DATA}/${INDEX_C}.clicks.index
DICT_CLICKS=${DATA}/${INDEX_C}.clicks.posting.dict
INDEX_CARTS=${DATA}/${INDEX_A}.carts.index
DICT_CARTS=${DATA}/${INDEX_A}.carts.posting.dict
INDEX_ITEM_TITLE=${DATA}/item_title.index
DICT_ITEM_TITLE=${DATA}/item_title.posting.dict
SCORES_ITEMS=${SCORES}/${RAWDATA}.${INDEX_I}.items.scores
SCORES_QUERIES=${SCORES}/${RAWDATA}.${INDEX_Q}.queries.scores
SCORES_CLICKS=${SCORES}/${RAWDATA}.${INDEX_C}.clicks.scores
SCORES_CARTS=${SCORES}/${RAWDATA}.${INDEX_A}.carts.scores
SCORES_ITEM_TITLE=${SCORES}/${RAWDATA}.item_title.scores
RERANK_LOG=${DATA}/rerank_log.txt

if [ ! -d ${SCORES} ]
then
    mkdir ${SCORES}
fi

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

echo "Reranking . . ."
if [ "$MODE" == "dump" ]
then
    python $RERANK_PROG --workers $WORKERS --verbose -k $K --insert_position $INSERT_POSITION --coeff_ctr $COEFF_CTR --ctr_by_position $CTR_BY_POSITION_FILE --coeff_rank $COEFF_RANK --coeff_items $COEFF_ITEMS --coeff_queries $COEFF_QUERIES --coeff_clicks $COEFF_CLICKS --coeff_carts $COEFF_CARTS --coeff_item_title $COEFF_ITEM_TITLE --exp_rank $EXP_RANK --exp_items $EXP_ITEMS --exp_queries $EXP_QUERIES --exp_clicks $EXP_CLICKS --exp_carts $EXP_CARTS --exp_item_title $EXP_ITEM_TITLE --index_items $INDEX_ITEMS --dict_items $DICT_ITEMS --index_queries $INDEX_QUERIES --dict_queries $DICT_QUERIES --index_clicks $INDEX_CLICKS --dict_clicks $DICT_CLICKS --index_carts $INDEX_CARTS --dict_carts $DICT_CARTS --index_item_title $INDEX_ITEM_TITLE --dict_item_title $DICT_ITEM_TITLE --score_dump_items $SCORES_ITEMS --score_dump_queries $SCORES_QUERIES --score_dump_clicks $SCORES_CLICKS --score_dump_carts $SCORES_CARTS --score_dump_item_title $SCORES_ITEM_TITLE $FILTERED_TEST_DATA > $RERANK_PROG_OUTPUT
elif [ "$MODE" == "load" ]
then
    python $RERANK_PROG --workers $WORKERS --verbose -k $K --insert_position $INSERT_POSITION --coeff_ctr $COEFF_CTR --ctr_by_position $CTR_BY_POSITION_FILE --coeff_rank $COEFF_RANK --coeff_items $COEFF_ITEMS --coeff_queries $COEFF_QUERIES --coeff_clicks $COEFF_CLICKS --coeff_carts $COEFF_CARTS --coeff_item_title $COEFF_ITEM_TITLE --exp_rank $EXP_RANK --exp_items $EXP_ITEMS --exp_queries $EXP_QUERIES --exp_clicks $EXP_CLICKS --exp_carts $EXP_CARTS --exp_item_title $EXP_ITEM_TITLE --score_dict_items $SCORES_ITEMS --score_dict_queries $SCORES_QUERIES --score_dict_clicks $SCORES_CLICKS --score_dict_carts $SCORES_CARTS --score_dict_item_title $SCORES_ITEM_TITLE $FILTERED_TEST_DATA > $RERANK_PROG_OUTPUT
else
    echo "Invalid mode."
fi

echo "Evaluating . . ."
python $EVAL_PROG -k $K --test_data_fname $TEST_DATA_STATS --rankable_data_fname $FILTERED_TEST_DATA_RANKABLE_STATS $RERANK_PROG_OUTPUT > $EVAL_OUTPUT
echo "***********************************************************" >> $RERANK_LOG
echo $(date) >> $RERANK_LOG
echo >> $RERANK_LOG
cat $RERANK_PARAMS $EVAL_OUTPUT >> $RERANK_LOG
tail -n 15 $EVAL_OUTPUT
