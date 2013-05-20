SHELL := /bin/bash
.DEFAULT_GOAL := default

RAWDATA ?= DEADBEEFRAW
INDEX   ?= DEADBEEFINDEX
CHUNK_PREFIX := data/CHUNK_
CHUNK_SUFFIX := _CHUNK
RAWDATA_LINES_PER_CHUNK ?= 300000
TESTDATA_LINES_PER_CHUNK ?= 150000
NUM_WORKERS ?= 8
NUM_RERANK ?= 3
INSERT_POSITION ?= 1
COEFF_RANK ?= 0.0
COEFF_QUERIES ?= 0.0
COEFF_CLICKS ?= 1.0
COEFF_CARTS ?= 0.0
EXP_RANK ?= 1.0
EXP_QUERIES ?= 1.0
EXP_CLICKS ?= 1.0
EXP_CARTS ?= 1.0

# raw data variables
raw_data                   := data/$(RAWDATA)
filtered_raw_data           = $(raw_data).filtered
query_raw_data              = $(raw_data).queries
test_data                   = $(raw_data).test_data
reordered_queries           = $(raw_data).$(INDEX).reordered_queries
evaluation                  = $(raw_data).$(INDEX).eval
histogram                   = $(raw_data).$(INDEX).histogram
filtered_test_data          = $(test_data).$(INDEX).filtered

# index data variables
index_data  		       := data/$(INDEX)
index_queries              := data/$(INDEX).queries.index
posting_dict_queries       := data/$(INDEX).queries.posting.dict
index_clicks               := data/$(INDEX).clicks.index
posting_dict_clicks        := data/$(INDEX).clicks.posting.dict
index_carts                := data/$(INDEX).carts.index
posting_dict_carts         := data/$(INDEX).carts.posting.dict
filtered_index_data         = $(index_data).filtered
query_index_data            = $(index_data).queries
unique_query_index_data     = $(index_data).unique_queries

default : $(filtered_test_data) $(index_queries) $(index_clicks)

# gunzip all the data files you want to use
# make the .queries for each data chunk
#

# target for checking that RAWDATA was specified and existed
$(raw_data):
ifeq ($(RAWDATA), DEADBEEFRAW)
	$(error RAWDATA not specified!)
endif
ifeq ($(wildcard $@),)
	$(error $@ does not exist!)
endif

$(index_data):
ifeq ($(INDEX), DEADBEEFINDEX)
	$(error INDEX not specified!)
endif
ifeq ($(wildcard $@),)
	$(error $@ does not exist!)
endif

$(filtered_raw_data) $(filtered_index_data): %.filtered : % programs/filterRawData.py
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

$(query_raw_data) $(query_index_data): %.queries : %.filtered programs/visitorQueryMapper.py programs/visitorQueryReducer.py
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

$(test_data): $(query_raw_data) programs/testGen.py
	cat $< | python programs/testGen.py > $@

$(filtered_test_data): $(test_data) $(index_queries) $(posting_dict_queries) $(index_clicks) $(posting_dict_clicks) $(index_carts) $(posting_dict_carts) programs/filterTestData.py programs/indexRead.py programs/SimilarityCalculator.py
	rm -f ${CHUNK_PREFIX}* data/*${CHUNK_SUFFIX}
	split -l $(TESTDATA_LINES_PER_CHUNK) $< $(CHUNK_PREFIX)
	for i in $(CHUNK_PREFIX)*; do \
	    cat $$i | python programs/filterTestData.py --index_queries $(index_queries) --dict_queries $(posting_dict_queries) --index_clicks $(index_clicks) --dict_clicks $(posting_dict_clicks) --index_carts $(index_carts) --dict_carts $(posting_dict_carts) > $${i}$(CHUNK_SUFFIX) && rm -f $$i & \
	done; \
	wait
	rm -f $@
	for i in data/*$(CHUNK_SUFFIX); do \
	    cat $$i >> $@ && rm -f $$i; \
	done

$(reordered_queries): $(filtered_test_data) $(index_queries) $(posting_dict_queries) $(index_clicks) $(posting_dict_clicks) $(index_carts) $(posting_dict_carts) programs/reRank.py programs/indexRead.py programs/SimilarityCalculator.py
	cat $< | python programs/reRank.py --verbose --workers $(NUM_WORKERS) -k $(NUM_RERANK) --insert_position $(INSERT_POSITION) --coeff_rank $(COEFF_RANK) --coeff_queries $(COEFF_QUERIES) --coeff_clicks $(COEFF_CLICKS) --coeff_carts $(COEFF_CARTS) --exp_rank $(EXP_RANK) --exp_queries $(EXP_QUERIES) --exp_clicks $(EXP_CLICKS) --exp_carts $(EXP_CARTS) --index_queries $(index_queries) --dict_queries $(posting_dict_queries) --index_clicks  $(index_clicks) --dict_clicks $(posting_dict_clicks) --index_carts $(index_carts) --dict_carts $(posting_dict_carts) > $@

$(evaluation): $(reordered_queries) programs/Evaluator.py
	cat $< | python programs/Evaluator.py -k $(NUM_RERANK) > $@

$(histogram): $(reordered_queries) programs/eval_mapper.py programs/eval_reducer.py
	cat $< | python programs/eval_mapper.py | python programs/eval_reducer.py > $@

$(unique_query_index_data): $(query_index_data) programs/uniqueQueryMapper.py programs/uniqueQueryReducer.py
	cat $< | python programs/uniqueQueryMapper.py | sort | python programs/uniqueQueryReducer.py > $@

$(posting_dict_queries) : $(index_queries)

$(index_queries): $(unique_query_index_data) programs/indexMapperQueries.py programs/indexReducer.py
	cat $< | python programs/indexMapperQueries.py | sort -k1,1n -k2,2n | python programs/indexReducer.py $(posting_dict_queries) > $@ 

$(posting_dict_clicks) : $(index_clicks)

$(index_clicks): $(query_index_data) programs/indexMapperClicks.py programs/indexReducer.py
	cat $< | python programs/indexMapperClicks.py | sort -k1,1n -k2,2n | python programs/indexReducer.py $(posting_dict_clicks) > $@ 

$(posting_dict_carts) : $(index_carts)

$(index_carts): $(query_index_data) programs/indexMapperCarts.py programs/indexReducer.py
	cat $< | python programs/indexMapperCarts.py | sort -k1,1n -k2,2n | python programs/indexReducer.py $(posting_dict_carts) > $@ 

# filter out "bad" data (malformed JSON, missing columns, etc.)
.PHONY : filtered
filtered : $(filtered_raw_data) 

# group pageviews into whole queries
.PHONY : queries
queries : $(query_index_data)

# generate test data
.PHONY : test_data
test_data : $(test_data)

# filter out queries our algorithm won't impact
.PHONY : test_data.filtered
test_data.filtered : $(filtered_test_data)

# re-rank query results
.PHONY : reordered_queries
reordered_queries : $(reordered_queries)

# compute evaluation metric(s)
.PHONY : eval
eval : $(evaluation)

# generate additional stats
.PHONY : histogram
histogram : $(histogram)

# group queries into unique queries
.PHONY : unique_queries
unique_queries : $(unique_query_index_data)

# build the queries index and posting.dict for RAWDATA
.PHONY : queries.index
queries.index : $(index_queries)

# build the clicks index and posting.dict for RAWDATA
.PHONY : clicks.index
clicks.index : $(index_clicks)

# build the carts index and posting.dict for RAWDATA
.PHONY : carts.index
carts.index : $(index_carts)

# Here we make empty targets for each program so that make can tell when a program
# has been modified and needs to rebuild a target
programs = filterRawData.py visitorQueryMapper.py visitorQueryReducer.py\
           testGen.py filterTestData.py reRank.py Evaluator.py\
           eval_mapper.py eval_reducer.py\
           uniqueQueryMapper.py uniqueQueryReducer.py\
           indexMapperQueries.py indexMapperClicks.py indexMapperCarts.py\
           indexReducer.py\

$(addprefix programs/, $(programs)):

.PHONY : clean
clean : $(raw_data)
	rm -f $(raw_data).* ${CHUNK_PREFIX}* data/*${CHUNK_SUFFIX}

.PHONY : indexclean
indexclean : 
	rm -f $(index_queries) $(posting_dict_queries) $(index_clicks) $(posting_dict_clicks) $(index_carts) $(posting_dict_carts)

