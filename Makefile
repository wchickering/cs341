RAWDATA ?= DEADBEEFRAW
INDEX   ?= DEADBEEFINDEX

raw_data  := data/$(RAWDATA)
use_index := data/$(INDEX)
use_posting_dict := data/$(basename $(notdir $(use_index))).posting.dict

filtered_data      = $(raw_data).filtered
build_index        = $(raw_data).index
build_posting_dict = $(raw_data).posting.dict
linked_queries     = $(raw_data).linked_queries
reordered_queries  = $(raw_data).reordered_queries

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

$(linked_queries): $(filtered_data) programs/testGenMapper.py programs/testGenReducer.py
	cat $(filtered_data) | python programs/testGenMapper.py | sort -k1,1n -k2,2 -k3,3 -k4,4n | python programs/testGenReducer.py > $@

$(reordered_queries): $(linked_queries) $(use_index) programs/reRank.py
	python programs/reRank.py -j -m --index $(use_index) --dict $(use_posting_dict) $(linked_queries) > $@

# filter RAWDATA
filter_data : $(filtered_data) 

# build the index and posting.dict for RAWDATA
build_index : $(build_index)

reorder_queries : $(reordered_queries)

# Here we make empty targets for each program so that make can tell when a program
# has been modified and needs to rebuild a target
programs = index_mapper.py index_reducer.py filterData.py\
           testGenMapper.py testGenReducer.py reRank.py
$(addprefix programs/, $(programs)):

clean : $(raw_data)
	rm -f $(raw_data).*

.PHONY : clean build_index filtered_data reorder_queries
