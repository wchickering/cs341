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
EVAL_PROG=${PROGRAMS}/Evaluator.py
DATA=${WCODE}/data
SCORES=${DATA}/scores
TEST_DATA=${DATA}/${RAWDATA}.test_data
FILTERED_TEST_DATA_RANKABLE=${TEST_DATA}.${INDEX_I}.filtered.rankable
FILTERED_TEST_DATA=${TEST_DATA}.${INDEX_I}.filtered
RERANK_PROG_OUTPUT=${DATA}/${RAWDATA}.${INDEX_I}.k${K}.reordered_queries
EVAL_OUTPUT=${DATA}/${RAWDATA}.${INDEX_I}.k${K}.eval
INDEX_ITEMS=${DATA}/${INDEX_I}.items.index
DICT_ITEMS=${DATA}/${INDEX_I}.items.posting.dict
INDEX_QUERIES=${DATA}/${INDEX_Q}.queries.index
DICT_QUERIES=${DATA}/${INDEX_Q}.queries.posting.dict
INDEX_CLICKS=${DATA}/${INDEX_C}.clicks.index
DICT_CLICKS=${DATA}/${INDEX_C}.clicks.posting.dict
INDEX_CARTS=${DATA}/${INDEX_A}.carts.index
DICT_CARTS=${DATA}/${INDEX_A}.carts.posting.dict
#INDEX_ITEM_TITLE=${DATA}/item_title.index
#DICT_ITEM_TITLE=${DATA}/item_title.posting.dict
SCORES_ITEMS=${SCORES}/${RAWDATA}.${INDEX_I}.items.scores
SCORES_QUERIES=${SCORES}/${RAWDATA}.${INDEX_Q}.queries.scores
SCORES_CLICKS=${SCORES}/${RAWDATA}.${INDEX_C}.clicks.scores
SCORES_CARTS=${SCORES}/${RAWDATA}.${INDEX_A}.carts.scores
SCORES_ITEM_TITLE=${SCORES}/${RAWDATA}.item_title.scores
RERANK_LOG=${DATA}/rerank_log.txt
NUM_QUERIES=$(wc -l $TEST_DATA | awk '{print $1}')
NUM_RANKABLE=$(wc -l $FILTERED_TEST_DATA_RANKABLE | awk '{print $1}')

python $EVAL_PROG -k $K $IS_ALL_SETTING $REORDERED_ALL_SETTING --num_rankable_queries_all $NUM_RANKABLE --num_all_queries $NUM_QUERIES $1 > $EVAL_OUTPUT
cat $EVAL_OUTPUT
