load data local infile '000000_0_pageview.csv'
into table pageView
fields terminated by ',' enclosed by '"' escaped by '\\'
lines terminated by '\n'
(pageviewid, visitorid, wmsessionid, rawquery, itemShowCount, itemClickCount, itemClickTopPosition);
