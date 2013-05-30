#!/usr/bin/python
# To execute, enter something like:
# python createPageViewImport.py 000000_0_filt.json > 000000_0_pageview.csv

import sys
import fileinput
import json


def main():
    num_queries = 0
    num_shown_items = 0
    num_clicks = 0
    num_purchases = 0
    num_carted = 0
    num_queries_with_clicks = 0
    num_queries_with_prev_clicks = 0
    num_queries_with_clicks_and_prev_clicks = 0
    num_front_page_items = 0
    num_front_page_clicks = 0
    num_front_page_purchases = 0
    sum_of_click_positions = 0
    num_clicks_with_prev_clicks = 0
    num_purchases_with_prev_clicks = 0
    num_front_page_clicks_with_prev = 0
    num_front_page_purchase_with_prev = 0
    num_queries_with_front_page_and_prev = 0
    num_one_page_queries = 0

    for line in fileinput.input(sys.argv[1]):
        record = json.loads(line)
        shownitems = record['shown_items']
        clickeditems = record['clicked_shown_items']
        carteditems = record['carted_shown_items']
        purchaseditems = record['purchased_shown_items']
        prevclickeditems = record['previously_clicked_items']
        num_queries+=1
        num_shown_items += len(shownitems)
        num_clicks += len(clickeditems)
        num_carted += len(carteditems)
        num_purchases += len(purchaseditems)
        has_clicks = False
        has_prev_clicks = False
        if len(shownitems) <= 16:
            num_one_page_queries += 1
            num_front_page_items += len(shownitems)
        else:
            num_front_page_items += 16
        if len(clickeditems) > 0:
            num_queries_with_clicks+=1
            has_clicks = True
        if len(prevclickeditems) > 0:
            num_queries_with_prev_clicks+=1
            has_prev_clicks = True
        if has_clicks and has_prev_clicks:
            num_queries_with_clicks_and_prev_clicks+=1
        has_front_page_click = False
        for click in clickeditems:
            position = shownitems.index(click) + 1
            sum_of_click_positions += position 
            if has_prev_clicks:
                num_clicks_with_prev_clicks+=1
                if click in purchaseditems:
                    num_purchases_with_prev_clicks+=1
                if position <= 16:
                    num_front_page_clicks_with_prev+=1
                    if click in purchaseditems:
                        num_front_page_purchase_with_prev+=1
            if position <= 16:
                has_front_page_click = True
                num_front_page_clicks+=1
                if click in purchaseditems:
                    num_front_page_purchases+=1
        if has_front_page_click and has_prev_clicks:
            num_queries_with_front_page_and_prev+=1
   
    perc_clicks = float(num_clicks)/num_shown_items
    clicks_per_query = float(num_clicks)/num_queries
    items_per_query = float(num_shown_items)/num_queries
    purchase_conversion = float(num_purchases)/num_clicks
    avg_click_position = float(sum_of_click_positions)/num_clicks
    purchase_conversion_front_page = float(num_front_page_purchases)/num_front_page_clicks
    purchase_conversion_prev_clicks = float(num_purchases_with_prev_clicks)/num_clicks_with_prev_clicks
    purchase_conversion_front_page_prev_clicks = float(num_front_page_purchase_with_prev)/num_front_page_clicks_with_prev
    perc_queries_with_clicks = float(num_queries_with_clicks)/num_queries
    perc_queries_with_prev_clicks = float(num_queries_with_prev_clicks)/num_queries
    perc_queries_with_clicks_and_prev_clicks = float(num_queries_with_clicks_and_prev_clicks)/num_queries
    perc_clicks_front_page = float(num_front_page_clicks)/num_clicks
    perc_clicks_with_prev_front_page = float(num_front_page_clicks_with_prev)/num_clicks_with_prev_clicks
    perc_purchases_with_prev_front_page = float(num_front_page_purchase_with_prev)/num_purchases
    perc_clicks_with_prev_front_page = float(num_front_page_clicks_with_prev)/num_clicks
    perc_queries_with_prev_front_page = float(num_queries_with_front_page_and_prev)/num_queries

    output = {}
    output['num_queries'] = num_queries
    output['num_shown_items'] = num_shown_items
    output['num_clicks'] = num_clicks
    output['num_carted'] = num_carted
    output['num_purchases'] = num_purchases
    output['num_front_page_clicks'] = num_front_page_clicks
    output['num_front_page_purchases'] = num_front_page_purchases
    output['num_front_page_items'] = num_front_page_items
    output['num_queries_with_clicks'] = num_queries_with_clicks
    output['num_queries_with_prev_clicks'] = num_queries_with_prev_clicks
    output['num_queries_with_clicks_and_prev_clicks'] = num_queries_with_clicks_and_prev_clicks
    output['num_queries_with_prev_clicks'] = num_queries_with_prev_clicks
    output['num_one_page_queries'] = num_one_page_queries
    print json.dumps(output)

    #print "TOTALS:"
    #print "Number of queries: ", num_queries
    #print "Number of shown items: ", num_shown_items
    #print "Number of clicks: ", num_clicks
    #print "Number of carted items: ", num_carted
    #print "Number of purchases: ", num_purchases
    #print "Number of front page clicks: ", num_front_page_clicks
    #print "Number of front page purchases: ", num_front_page_purchases
    #print "Queries with clicks: ", num_queries_with_clicks
    #print "Queries with previous clicks: ", num_queries_with_prev_clicks
    #print "Queries with clicks and prev clicks: ", num_queries_with_clicks_and_prev_clicks
    #print "Clicks with previous clicks: ", num_clicks_with_prev_clicks
    #print "One-page queries: ", num_one_page_queries
    #print "STATS:"
    #print "Items per query: ", items_per_query
    #print "Clicks per query: ", clicks_per_query
    #print "Percent of items clicked: ", perc_clicks
    #print "Percent of queries with clicks: ", perc_queries_with_clicks
    #print "Percent of queries with prev clicks: ", perc_queries_with_prev_clicks
    #print "Percent of queries with clicks and prev clicks: ", perc_queries_with_clicks_and_prev_clicks
    #print "Average click position: ", avg_click_position
    #print "Percent of clicks that are on front page: ", perc_clicks_front_page
    #print "Percent of clicks with prev clicks that are on front page: ", perc_clicks_with_prev_front_page
    #print "Conversion rate to purchase from click: ", purchase_conversion
    #print "Conversion rate for front page clicks: ", purchase_conversion_front_page
    #print "Conversion rate when there are prev clicks: ", purchase_conversion_prev_clicks
    #print "Conversion rate for front page when there are prev clicks: ", \
    #        purchase_conversion_front_page_prev_clicks
    #print "Percent of purchases that are on front page and have prev clicks: ", \
    #        perc_purchases_with_prev_front_page
    #print "Percent of clicks that are on front page and have prev clicks: ", \
    #        perc_clicks_with_prev_front_page
    #print "Old estimate = perc clicks on front * perc affectable queries: ", \
    #        perc_clicks_front_page*perc_queries_with_prev_clicks
 


if __name__ == '__main__':
    main()
