#!/usr/bin/python

import json

# import local modules
import compression

def get_posting_dict(posting_dict_f):
    line = posting_dict_f.readline()
    return json.loads(line)

def get_posting(index_f, posting_dict, itemid):
    if itemid not in posting_dict:
        return []
    index_f.seek(posting_dict[itemid])
    idx, plist = index_f.readline().split('\t')
    assert(idx == str(itemid))
    dgap_arr = [int(i) for i in plist.split(',')]
    return compression.dgap_decode(dgap_arr)
