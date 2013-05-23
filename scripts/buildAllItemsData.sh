#!/bin/bash

echo 'zcat data/items.json.gz > data/items.json.raw'
zcat data/items.json.gz > data/items.json.raw
echo 'python scripts/reformatItems.py > data/items.json.1'
python scripts/reformatItems.py > data/items.json.1
echo 'tar xf data/item_main_attributes.tar'
tar xf data/item_main_attributes.tar
echo 'zcat data/item_main_attributes/* | uniq > data/items.json.2'
zcat data/item_main_attributes/* | uniq > data/items.json.2
echo 'python scripts/getItemData1.py | sort -k1,1n | uniq > data/items.data.1'
python scripts/getItemData1.py | sort -k1,1n | uniq > data/items.data.1
echo 'python scripts/getItemData2.py | sort -k1,1n | uniq > data/items.data.2'
python scripts/getItemData2.py | sort -k1,1n | uniq > data/items.data.2
echo 'cat data/items.data.{1,2}\
    | awk ''{ print $0 "\t" length($2) }''\
    | sort -t$'\t' -k1,1n -k3,3n\
    | uniq\
    | cut -f1,2 > data/allItems.data'
cat data/items.data.{1,2}\
    | awk -F '\t' '{ print $0 "\t" length($2) }'\
    | sort -t'	' -k1,1n -k3,3n\
    | uniq\
    | cut -f1,2 > data/allItems.data

