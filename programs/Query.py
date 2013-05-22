#!/usr/bin/env python
"""Defines the Query class

"""

__author__ = """Charles Celerier <cceleri@cs.stanford.edu>,
              Bill Chickering <bchick@cs.stanford.edu>,
              Jamie Irvine <jirvine@cs.stanford.edu>"""

__date__ = """16 April 2013"""

import json

class Query:
    """Represents information about a query

    Instance attributes
    ===================

    shown_items : list
        items shown to the user in a query
    previously_shown_items : list
        previously shown items to the user
    previously_clicked_items : list
        previously clicked items by the user
    clicked_shown_items : list
        items the user clicked in this query

    """
    def __init__(self, jsonStr):
        record = json.loads(jsonStr)
        self.visitorid = record['visitorid']
        self.wmsessionid = record['wmsessionid']
        self.rawquery = record['rawquery']
        self.searchattributes = record['searchattributes']
        self.shown_items = record['shown_items']
        self.previously_shown_items=record['previously_shown_items']
        self.previously_clicked_items=record['previously_clicked_items']
        self.clicked_shown_items=record['clicked_shown_items']

    def __repr__(self):
        return "Query(%s)" % repr(json.dumps({\
                     "visitorid":self.visitorid,\
                     "wmsessionid":self.wmsessionid,\
                     "rawquery":self.rawquery,\
                     "searchattributes":self.searchattributes,\
                     "shown_items":self.shown_items,\
                     "previously_shown_items":self.previously_shown_items,\
                     "previously_clicked_items":self.previously_clicked_items,\
                     "clicked_shown_items":self.clicked_shown_items}))

    def __str__(self):
        return json.dumps({\
                     "visitorid":self.visitorid,\
                     "wmsessionid":self.wmsessionid,\
                     "rawquery":self.rawquery,\
                     "searchattributes":self.searchattributes,\
                     "shown_items":self.shown_items,\
                     "previously_shown_items":self.previously_shown_items,\
                     "previously_clicked_items":self.previously_clicked_items,\
                     "clicked_shown_items":self.clicked_shown_items})

def main():
    return

if __name__ == '__main__':
    main()
