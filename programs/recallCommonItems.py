import sys
import indexRead
from QueryPrinter import QueryPrinter

if len(sys.argv) != 4:
    print 'Usage: '+sys.argv[0]+' <index name (e.g. 48chunk)> <itemid 1> <itemid 2>'
    sys.exit(1)

def lookupFriends(itemId):
    return indexRead.get_posting(itemsIndex, itemsPostingDict, itemId)

itemsIndexFn = 'data/'+sys.argv[1]+'.items.index'
itemsPostingDictFn = 'data/'+sys.argv[1]+'.items.posting.dict'
itemsIndex = open(itemsIndexFn)
itemsPostingDict = indexRead.get_posting_dict(open(itemsPostingDictFn))

qp = QueryPrinter(index_item_title_fname='data/item_title.index', posting_dict_item_title_fname='data/item_title.posting.dict')

for id in set(lookupFriends(sys.argv[2])).intersection(set(lookupFriends(sys.argv[3]))):
    qp.printItem(id)

