Scripts Description
===================

Create and populate the pageViewTable
-------------------------------------

Page view begins with the raw Walmart data (e.g. 000000_0). Each line in the
raw Walmart data represents a page view.

The first command to run is::

    $ python createPageViewImport.py 000000_0 >000000_0_pageView.csv 2>000000_0_pageView.err

``000000_0_pageView.err`` contains every line from the raw Walmart data file
where the JSON parsing failed. This file should be identical to every error file
that parses the same raw Walmart data file

Now that we have the .csv, we need to create the table in the MySQL database::

    $ mysql -u <username> <walmartdb> --local-infile < pageViewTable.sql

If the table ``pageView`` exists in <walmartdb>, then it will be dropped and
recreated.

Now we need to put the data in the table::

    $ sed "s/__INFILE__/\\'000000_0_pageview.csv\\'/" loadPageView.sql | mysql -u <username> <walmartdb> --local-infile

That's it! It takes a few minutes (forever!!) on Bill's machine.


