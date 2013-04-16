load data local infile __INFILE__
into table itemclick
fields terminated by ',' enclosed by '"' escaped by '\\'
lines terminated by '\n'
(queryid, pageviewid, itemId, Ordered, InCart, QueryPosition, PagePosition);
