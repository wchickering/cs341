load data local infile '000000_0_itemclick.csv'
into table itemclick
fields terminated by ',' enclosed by '"' escaped by '\\'
lines terminated by '\n'
(queryid, pageviewid, itemId, Ordered, InCart, PagePosition);
