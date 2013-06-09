import sys
import os

try: 
    coeff_items = float(os.environ['COEFF_ITEMS'])
    coeff_queries = float(os.environ['COEFF_QUERIES'])
    coeff_clicks = float(os.environ['COEFF_CLICKS'])
    coeff_carts = float(os.environ['COEFF_CARTS'])
    coeff_item_title = float(os.environ['COEFF_ITEM_TITLE'])
    exp_items = float(os.environ['EXP_ITEMS'])
    exp_queries = float(os.environ['EXP_QUERIES'])
    exp_clicks = float(os.environ['EXP_CLICKS'])
    exp_carts = float(os.environ['EXP_CARTS'])
    exp_item_title = float(os.environ['EXP_ITEM_TITLE'])
except KeyError:
    print 'Error: You need to export the coefficients and exponents to your environment!'
    sys.exit(1)

if len(sys.argv) != 7:
    print 'Usage: ' + sys.argv[0] + '<CTR> <clicks> <items> <carts> <queries> <item_title>'
    sys.exit(1)

CTR = float(sys.argv[1])
clicks_score = coeff_clicks   * float(sys.argv[2]) ** exp_clicks
items_score = coeff_items     * float(sys.argv[3]) ** exp_items
carts_score = coeff_carts     * float(sys.argv[4]) ** exp_carts
queries_score = coeff_queries * float(sys.argv[5]) ** exp_queries
item_title_score = coeff_item_title * float(sys.argv[6]) ** exp_item_title
final_score = CTR + clicks_score + items_score + carts_score + queries_score + item_title_score

#print "clicks score: " + str(clicks_score)
#print "items score: " + str(items_score)
#print "carts score: " + str(carts_score)
#print "queries score: " + str(queries_score)
#print "item_title score: " + str(item_title_score)
#print "final score: " + str(final_score)

print " & ".join(map(str, [final_score,CTR,clicks_score,items_score,carts_score,queries_score,item_title_score]))
