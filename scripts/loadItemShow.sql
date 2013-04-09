load data local infile '000000_0_itemshow.csv'
into table itemshow
fields terminated by ',' enclosed by '"' escaped by '\\'
lines terminated by '\n'
(pageviewid, Position, itemId);
