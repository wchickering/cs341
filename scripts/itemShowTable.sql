drop table if exists itemshow;
create table itemshow (
    itemshowid int not null auto_increment,
    queryid int not null,
    pageviewid int not null,
    PagePosition int not null,
    itemId int not null,
    primary key (itemshowid)
) engine=MyISAM;
