load data local infile __INFILE__
into table itemshow
fields terminated by ',' enclosed by '"' escaped by '\\'
lines terminated by '\n'
(queryid, pageviewid, QueryPosition, PagePosition, itemId);
