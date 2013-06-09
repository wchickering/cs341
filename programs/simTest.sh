#!/bin/bash

# This script assumes WCODE and RERANK_PARAMS already defined and exported.
# RERANK_PARAMS should be the path to a file containing variable definitions
# like these:
#INDEX_I=000051_0
#INDEX_Q=000051_0
#INDEX_C=000051_0
#INDEX_A=000051_0

source $RERANK_PARAMS

PROGRAMS=${WCODE}/programs
SIMCALC_PROG=${PROGRAMS}/SimilarityCalculator.py
DATA=${WCODE}/data
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

ITEM1=$1
ITEM2=$2

python $SIMCALC_PROG --index_items $INDEX_ITEMS --dict_items $DICT_ITEMS --index_queries $INDEX_QUERIES --dict_queries $DICT_QUERIES --index_clicks $INDEX_CLICKS --dict_clicks $DICT_CLICKS --index_carts $INDEX_CARTS --dict_carts $DICT_CARTS --index_item_title $INDEX_ITEM_TITLE --dict_item_title $DICT_ITEM_TITLE $ITEM1 $ITEM2
