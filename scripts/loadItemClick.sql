load data local infile '000000_0_itemclick.csv'
into table itemclick
fields terminated by ',' enclosed by '"' escaped by '\\'
lines terminated by '\n'
(pageviewid, itemId, Ordered, InCart, Position);
