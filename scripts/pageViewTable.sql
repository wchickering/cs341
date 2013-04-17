drop table if exists pageview;
create table pageview (
    pageviewid int not null,
    queryid int not null,
    visitorid bigint not null,
    timestamp bigint not null,
    wmsessionid char(73) not null,
    rawquery varchar(100) not null,
    itemShowCount int not null,
    itemClickCount int not null,
    itemClickTopPosition int not null,
    primary key (pageviewid)
) engine=MyISAM;
