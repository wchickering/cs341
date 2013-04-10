drop table if exists itemclick;
create table itemclick (
    itemclickid int not null auto_increment,
    queryid int not null,
    pageviewid int not null,
    itemId int not null,
    Ordered boolean not null,
    InCart boolean not null,
    QueryPosition int not null,
    PagePosition int not null,
    primary key (itemclickid)
) engine=MyISAM;
