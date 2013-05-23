#!/bin/bash

# This script assumes that reRank.sh has already been run with MODE=dump and
# the same values for WORKERS, RAWDATA, INDEX_I, INDEX_Q, INDEX_C, and INDEX_A
# that are used here.

# This script assumes WCODE and MULTIRERANK_PARAMS already defined and exported.
# MULTIRERANK_PARAMS should be the path to a file containing variable definitions
# like these:
#WORKERS=8
#
#RAWDATA=000050_0
#
#INDEX_I=000051_0
#INDEX_Q=000051_0
#INDEX_C=000051_0
#INDEX_A=000051_0
#
#PARAMS=multiReRank_example_params.json
#
#OUTPUT=multiReRank.out

source $MULTIRERANK_PARAMS

PROGRAMS=${WCODE}/programs
RERANK_PROG=${PROGRAMS}/multiReRank.py
DATA=${WCODE}/data
SCORES=${DATA}/scores
PARAMS_FILE=${PARAMS}
TEST_DATA=${DATA}/${RAWDATA}.test_data
FILTERED_TEST_DATA=${TEST_DATA}.${INDEX_I}.filtered
RERANK_PROG_OUTPUT=${DATA}/${RAWDATA}.${INDEX_I}.${OUTPUT}
SCORES_ITEMS=${SCORES}/${RAWDATA}.${INDEX_I}.items.scores
SCORES_QUERIES=${SCORES}/${RAWDATA}.${INDEX_Q}.queries.scores
SCORES_CLICKS=${SCORES}/${RAWDATA}.${INDEX_C}.clicks.scores
SCORES_CARTS=${SCORES}/${RAWDATA}.${INDEX_A}.carts.scores
SCORES_ITEM_TITLE=${SCORES}/${RAWDATA}.item_title.scores

python $RERANK_PROG --workers $WORKERS --score_dict_items $SCORES_ITEMS --score_dict_queries $SCORES_QUERIES --score_dict_clicks $SCORES_CLICKS --score_dict_carts $SCORES_CARTS --score_dict_item_title $SCORES_ITEM_TITLE $PARAMS_FILE $FILTERED_TEST_DATA > $RERANK_PROG_OUTPUT

