load data local infile __INFILE__
into table pageView
fields terminated by ',' enclosed by '"' escaped by '\\'
lines terminated by '\n'
(pageviewid, queryid, visitorid, timestamp, wmsessionid, rawquery, itemShowCount, itemClickCount, itemClickTopPosition);
