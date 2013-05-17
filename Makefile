SHELL := /bin/bash

RAWDATA ?= DEADBEEFRAW
INDEX   ?= DEADBEEFINDEX
CHUNK_PREFIX := data/CHUNK_
CHUNK_SUFFIX := _CHUNK
RAWDATA_LINES_PER_CHUNK ?= 300000
TESTDATA_LINES_PER_CHUNK ?= 150000
TESTDATA_FILTERED_LINES_PER_CHUNK ?= 7000
NUM_RERANK ?= 32
COEFF_QUERIES ?= 0.26
COEFF_CLICKS ?= 1.00
EXP_QUERIES ?= 0.4
EXP_CLICKS ?= 0.8

raw_data  := data/$(RAWDATA)
use_index_queries := data/$(INDEX).queries.index
use_posting_dict_queries := data/$(INDEX).queries.posting.dict
use_index_clicks := data/$(INDEX).clicks.index
use_posting_dict_clicks := data/$(INDEX).clicks.posting.dict

filtered_raw_data            = $(raw_data).filtered
query_data                   = $(raw_data).queries
test_data                    = $(raw_data).test_data
filtered_test_data           = $(test_data).$(INDEX).filtered
reordered_queries            = $(raw_data).$(INDEX).reordered_queries
evaluation                   = $(raw_data).$(INDEX).eval
histogram                    = $(raw_data).$(INDEX).histogram
unique_query_data            = $(raw_data).unique_queries
build_index_queries          = $(raw_data).queries.index
build_posting_dict_queries   = $(raw_data).queries.posting.dict
build_index_clicks           = $(raw_data).clicks.index
build_posting_dict_clicks    = $(raw_data).clicks.posting.dict

# target for checking that RAWDATA was specified and existed
$(raw_data):
ifeq ($(RAWDATA), DEADBEEFRAW)
	$(error RAWDATA not specified!)
endif
ifeq ($(wildcard $@),)
	$(error $@ does not exist!)
endif

$(use_index_queries):
ifeq ($(INDEX), DEADBEEFINDEX)
	$(error INDEX not specified!)
endif
	$(MAKE) RAWDATA=$(INDEX) build_index_queries

$(use_index_clicks):
ifeq ($(INDEX), DEADBEEFINDEX)
	$(error INDEX not specified!)
endif
	$(MAKE) RAWDATA=$(INDEX) build_index_clicks

$(filtered_raw_data): $(raw_data) programs/filterRawData.py
	rm -f ${CHUNK_PREFIX}* data/*${CHUNK_SUFFIX}
	split -l $(RAWDATA_LINES_PER_CHUNK) $< $(CHUNK_PREFIX)
	for i in $(CHUNK_PREFIX)*; do \
		cat $$i | python programs/filterRawData.py > $${i}$(CHUNK_SUFFIX) && rm -f $$i & \
	done; \
	wait
	rm -f $@
	for i in data/*$(CHUNK_SUFFIX); do \
	    cat $$i >> $@ && rm -f $$i; \
	done

$(query_data): $(filtered_raw_data) programs/visitorQueryMapper.py programs/visitorQueryReducer.py
	rm -f ${CHUNK_PREFIX}* data/*${CHUNK_SUFFIX}
	split -l $(RAWDATA_LINES_PER_CHUNK) $< $(CHUNK_PREFIX)
	for i in $(CHUNK_PREFIX)*; do \
		cat $$i | python programs/visitorQueryMapper.py | sort -k1,1n -k2,2 -k3,3 -k4,4 -k5,5n | python programs/visitorQueryReducer.py > $${i}$(CHUNK_SUFFIX) && rm -f $$i & \
	done; \
	wait
	rm -f $@
	for i in data/*$(CHUNK_SUFFIX); do \
		cat $$i >> $@ && rm -f $$i; \
	done

$(test_data): $(query_data) programs/testGen.py
	cat $(query_data) | python programs/testGen.py > $@

$(filtered_test_data): $(test_data) $(use_index_queries) $(use_posting_dict_queries) $(use_index_clicks) $(use_posting_dict_clicks) programs/filterTestData.py programs/indexRead.py programs/SimilarityCalculator.py
	rm -f ${CHUNK_PREFIX}* data/*${CHUNK_SUFFIX}
	split -l $(TESTDATA_LINES_PER_CHUNK) $< $(CHUNK_PREFIX)
	for i in $(CHUNK_PREFIX)*; do \
	    cat $$i | python programs/filterTestData.py --index_queries $(use_index_queries) --dict_queries $(use_posting_dict_queries) --index_clicks $(use_index_clicks) --dict_clicks $(use_posting_dict_clicks) > $${i}$(CHUNK_SUFFIX) && rm -f $$i & \
	done; \
	wait
	rm -f $@
	for i in data/*$(CHUNK_SUFFIX); do \
	    cat $$i >> $@ && rm -f $$i; \
	done

$(reordered_queries): $(filtered_test_data) $(use_index_queries) $(use_posting_dict_queries) $(use_index_clicks) $(use_posting_dict_clicks) programs/ReRanker.py programs/indexRead.py programs/SimilarityCalculator.py
	rm -f ${CHUNK_PREFIX}* data/*${CHUNK_SUFFIX}
	split -l $(TESTDATA_FILTERED_LINES_PER_CHUNK) $< $(CHUNK_PREFIX)
	for i in $(CHUNK_PREFIX)*; do \
	    python programs/ReRanker.py --verbose -k $(NUM_RERANK) --coeff_queries $(COEFF_QUERIES) --coeff_clicks $(COEFF_CLICKS) --exp_queries $(EXP_QUERIES) --exp_clicks $(EXP_CLICKS) --index_queries $(use_index_queries) --dict_queries $(use_posting_dict_queries) --index_clicks  $(use_index_clicks) --dict_clicks $(use_posting_dict_clicks) $$i > $${i}$(CHUNK_SUFFIX) && rm -f $$i & \
	done; \
	wait
	rm -f $@
	for i in data/*$(CHUNK_SUFFIX); do \
	    cat $$i >> $@ && rm -f $$i; \
	done

$(evaluation): $(reordered_queries) programs/Evaluator.py
	cat $< | python programs/Evaluator.py > $@

$(histogram): $(reordered_queries) programs/eval_mapper.py programs/eval_reducer.py
	cat $< | python programs/eval_mapper.py | python programs/eval_reducer.py > $@

$(unique_query_data): $(query_data) programs/uniqueQueryMapper.py programs/uniqueQueryReducer.py
	cat $(query_data) | python programs/uniqueQueryMapper.py | sort | python programs/uniqueQueryReducer.py > $@

$(build_index_queries): $(unique_query_data) programs/indexMapperQueries.py programs/indexReducer.py
	cat $(unique_query_data) | python programs/indexMapperQueries.py | sort -k1,1n -k2,2n | python programs/indexReducer.py $(build_posting_dict_queries) > $@ 

$(build_index_clicks): $(query_data) programs/indexMapperClicks.py programs/indexReducer.py
	cat $(query_data) | python programs/indexMapperClicks.py | sort -k1,1n -k2,2n | python programs/indexReducer.py $(build_posting_dict_clicks) > $@ 

# filter out "bad" data (malformed JSON, missing columns, etc.)
filtered : $(filtered_raw_data) 

# group pageviews into whole queries
queries : $(query_data)

# generate test data
test_data : $(test_data)

# filter out queries our algorithm won't impact
test_data.filtered : $(filtered_test_data)

# re-rank query results
reordered_queries : $(reordered_queries)

# compute evaluation metric(s)
eval : $(evaluation)

# generate additional stats
histogram : $(histogram)

# group queries into unique queries
unique_queries : $(unique_query_data)

# build the queries index and posting.dict for RAWDATA
queries.index : $(build_index_queries)

# build the clicks index and posting.dict for RAWDATA
clicks.index : $(build_index_clicks)

# Here we make empty targets for each program so that make can tell when a program
# has been modified and needs to rebuild a target
programs = filterRawData.py visitorQueryMapper.py visitorQueryReducer.py\
           testGen.py filterTestData.py ReRanker.py Evaluator.py\
           eval_mapper.py eval_reducer.py\
           uniqueQueryMapper.py uniqueQueryReducer.py\
           indexMapperQueries.py indexMapperClicks.py indexReducer.py\

$(addprefix programs/, $(programs)):

clean : $(raw_data)
	rm -f $(raw_data).* ${CHUNK_PREFIX}* data/*${CHUNK_SUFFIX}

indexclean : 
	rm -f $(use_index_queries) $(use_posting_dict_queries) $(use_index_clicks) $(use_posting_dict_clicks)

.PHONY : clean filtered queries test_data test_data.filtered reorder_queries eval histogram unique_queries queries.index clicks.index
