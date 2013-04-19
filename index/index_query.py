#!/usr/bin/python

import json

# import local modules
import compression

def get_posting_dict(fname):
    posting_dict_f = open(fname)
    line = posting_dict_f.readline()
    return json.loads(line, parse_int=int)

def get_posting(index_f, posting_dict, itemid):
    index_f.seek(posting_dict[str(itemid)])
    idx, plist = index_f.readline().split('\t')
    assert(idx == str(itemid))
    dgap_arr = [int(i) for i in plist.split(',')]
    return compression.dgap_decode(dgap_arr)
