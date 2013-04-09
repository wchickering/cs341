drop table if exists itemshow;
create table itemshow (
    itemshowid int not null auto_increment,
    pageviewid int not null,
    Position int not null,
    itemId int not null,
    primary key (itemshowid)
) engine=MyISAM;
