RAWDATA ?= DEADBEEFRAW
INDEX   ?= DEADBEEFINDEX

raw_data  := data/$(RAWDATA)
use_index := data/$(INDEX)
use_posting_dict := data/$(basename $(notdir $(use_index))).posting.dict

filtered_data      = $(raw_data).filtered
build_index        = $(raw_data).index
build_posting_dict = $(raw_data).posting.dict
test_data          = $(raw_data).test_data
reordered_queries  = $(raw_data).reordered_queries
filtered_test_data = $(test_data).filtered
evaluation         = $(raw_data).eval
histogram          = $(raw_data).histogram

# target for checking that RAWDATA was specified and existed
$(raw_data):
ifeq ($(RAWDATA), DEADBEEFRAW)
	$(error RAWDATA not specified!)
endif
ifeq ($(wildcard $@),)
	$(error $@ does not exist!)
endif

$(use_index):
ifeq ($(INDEX), DEADBEEFINDEX)
	$(error INDEX not specified!)
endif
	$(MAKE) RAWDATA=$(basename $(notdir $@)) build_index

$(filtered_data): $(raw_data) programs/filterData.py
	cat $(raw_data) | python programs/filterData.py $(raw_data) > $@

$(build_index): $(filtered_data) programs/index_mapper.py programs/index_reducer.py
	cat $(filtered_data) | python programs/index_mapper.py | sort -k1n -k2n | python programs/index_reducer.py > $@ && mv posting.dict $(build_posting_dict)

$(test_data): $(filtered_data) programs/testGenMapper.py programs/testGenReducer.py
	cat $(filtered_data) | python programs/testGenMapper.py | sort -k1,1n -k2,2 -k3,3 -k4,4n | python programs/testGenReducer.py > $@

$(filtered_test_data): $(use_index) $(test_data) programs/filterTestData.py
	cat $(test_data) | python programs/filterTestData.py $(use_index) $(use_posting_dict) > $@

$(reordered_queries): $(filtered_test_data) $(use_index) programs/reRank.py
	python programs/reRank.py --index $(use_index) --dict $(use_posting_dict) $(filtered_test_data) > $@

$(evaluation): $(reordered_queries) programs/evaluate.py
	cat $< | python programs/evaluate.py > $@

$(histogram): $(reordered_queries) programs/eval_mapper.py programs/eval_reducer.py
	cat $< | python programs/eval_mapper.py | python programs/eval_reducer.py > $@

# filter RAWDATA
filter_data : $(filtered_data) 

# build the index and posting.dict for RAWDATA
build_index : $(build_index)

filter_test_data : $(filtered_test_data)

reorder_queries : $(reordered_queries)

evaluate : $(evaluation)

histogram : $(histogram)

# Here we make empty targets for each program so that make can tell when a program
# has been modified and needs to rebuild a target
programs = index_mapper.py index_reducer.py filterData.py\
           testGenMapper.py testGenReducer.py reRank.py\
		   filterTestData.py eval_mapper.py eval_reducer.py

$(addprefix programs/, $(programs)):

clean : $(raw_data)
	rm -f $(raw_data).*

.PHONY : clean build_index filtered_data reorder_queries
