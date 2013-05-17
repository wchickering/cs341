#!/bin/bash

# set to 'dump' or 'load'
MODE=load

RAWDATA=000050_0
INDEX_Q=8chunk
INDEX_C=8chunk
K=3
COEFF_QUERIES=0.14
COEFF_CLICKS=1.00
EXP_QUERIES=0.4
EXP_CLICKS=0.8

#INDEX_Q=16chunk
#INDEX_C=16chunk
#K=3
#COEFF_QUERIES=0.04
#COEFF_CLICKS=1.00
#EXP_QUERIES=0.4
#EXP_CLICKS=0.8

# Assumes WCODE already defined and exported
PROGRAMS=${WCODE}/programs
RERANK=${PROGRAMS}/ReRanker.py
EVALUATE=${PROGRAMS}/Evaluator.py
DATA=${WCODE}/data
INPUT=${DATA}/${RAWDATA}.test_data.${INDEX_C}.filtered
RERANK_OUTPUT=${DATA}/${RAWDATA}.${INDEX_C}.k${K}.reordered_queries
EVAL_OUTPUT=${DATA}/${RAWDATA}.${INDEX_C}.k${K}.eval
INDEX_QUERIES=${DATA}/${INDEX_Q}.queries.index
DICT_QUERIES=${DATA}/${INDEX_Q}.queries.posting.dict
INDEX_CLICKS=${DATA}/${INDEX_C}.clicks.index
DICT_CLICKS=${DATA}/${INDEX_C}.clicks.posting.dict
SCORES_QUERIES=${DATA}/${RAWDATA}.${INDEX_Q}.queries.scores
SCORES_CLICKS=${DATA}/${RAWDATA}.${INDEX_C}.clicks.scores

if [ "$MODE" == "dump" ]
then
    python $RERANK --verbose -k $K --coeff_queries $COEFF_QUERIES --coeff_clicks $COEFF_CLICKS --exp_queries $EXP_QUERIES --exp_clicks $EXP_CLICKS --index_queries $INDEX_QUERIES --dict_queries $DICT_QUERIES --index_clicks $INDEX_CLICKS --dict_clicks $DICT_CLICKS --score_dump_queries $SCORES_QUERIES --score_dump_clicks $SCORES_CLICKS $INPUT > $RERANK_OUTPUT
elif [ "$MODE" == "load" ]
then
    python $RERANK --verbose -k $K --coeff_queries $COEFF_QUERIES --coeff_clicks $COEFF_CLICKS --exp_queries $EXP_QUERIES --exp_clicks $EXP_CLICKS --score_dict_queries $SCORES_QUERIES --score_dict_clicks $SCORES_CLICKS $INPUT > $RERANK_OUTPUT
else
    echo "Invalid mode."
fi

python $EVALUATE -k $K $RERANK_OUTPUT > $EVAL_OUTPUT
cat $EVAL_OUTPUT
