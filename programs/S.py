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
print str(CTR + (  coeff_clicks *     float(sys.argv[2]) ** exp_clicks\
                 + coeff_items *      float(sys.argv[3]) ** exp_items\
                 + coeff_carts *      float(sys.argv[4]) ** exp_carts\
                 + coeff_queries *    float(sys.argv[5]) ** exp_queries\
                 + coeff_item_title * float(sys.argv[6]) ** exp_item_title))
