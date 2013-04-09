drop table if exists itemclick;
create table itemclick (
    itemclickid int not null auto_increment,
    pageviewid int not null,
    itemId int not null,
    Ordered boolean not null,
    InCart boolean not null,
    Position int not null,
    primary key (itemclickid)
) engine=MyISAM;
