RAWDATA ?= DEADBEEF
rd := data/$(RAWDATA)

filtered_data = $(rd).filtered
index_file    = $(rd).corpus.index
posting_dict  = $(rd).posting.dict

# target for checking that RAWDATA was specified and existed
$(rd):
ifeq ($(RAWDATA), DEADBEEF)
	$(error RAWDATA not specified!)
endif
ifeq ($(wildcard $@),)
	$(error $@ does not exist!)
endif

$(filtered_data): $(rd) programs/filterData.py
	cat $(rd) | python programs/filterData.py $(rd) > $(filtered_data)

$(index_file): $(filtered_data) programs/index_mapper.py programs/index_reducer.py
	cat $(filtered_data) | python programs/index_mapper.py | sort -k1n -k2n | python programs/index_reducer.py > $(index_file) && mv posting.dict $(posting_dict)

# filter RAWDATA
filtered_data : $(filtered_data) 

# build the index and posting.dict for RAWDATA
index_file : $(index_file)

# Here we make empty targets for each program so that make can tell when a program
# has been modified and needs to rebuild a target
programs = index_mapper.py index_reducer.py filterData.py
$(addprefix programs/, $(programs)):

.PHONY : index_file filtered_data all
