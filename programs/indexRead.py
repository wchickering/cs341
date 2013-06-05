#!/usr/bin/python

import json

# import local modules
import compression

def get_posting_dict(posting_dict_f):
    line = posting_dict_f.readline()
    return json.loads(line)

def get_posting(index_f, posting_dict, itemid):
    # must ensure itemid is a string.
    # this is because JSON stores all keys as strings.
    itemid = str(itemid)
    if itemid not in posting_dict:
        return []
    # THE FOLLOWING IS FOR READING A COMPRESSED INDEX
    #index_f.seek(posting_dict[itemid][0])
    #bytearray = index_f.read(posting_dict[itemid][1])
    #dgap_arr = compression.vb_decode(bytearray)
    #return compression.dgap_decode(dgap_arr)
    #################################################
    # THE FOLLOWING IS FOR READING A COMPRESSED INDEX
    index_f.seek(posting_dict[itemid])
    return [int(s) for s in index_f.readline().split(',')]
    #################################################

def get_posting_raw(index_f, posting_dict, itemid):
    itemid = str(itemid)
    if itemid not in posting_dict:
        return ''
    index_f.seek(posting_dict[itemid])
    return index_f.readline().rstrip()
