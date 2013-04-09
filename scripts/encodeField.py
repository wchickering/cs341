#!/usr/bin/python

import unicodedata

def encode(field):
    if type(field) is unicode:
        return '"' + unicodedata.normalize('NFKD', field)\
                                .encode('ascii','ignore').replace('"','\"') + '"'
    elif type(field) is str:
        return '"' + field.replace('"','\"') + '"'
    elif type(field) is bool:
        if field:
            return '"1"'
        else:
            return '"0"'
    else:
        return encode(str(field))

def encodeNullable(record, key):
    if key in record.keys():
        return encode(record[key])
    else:
        return 'NULL'
