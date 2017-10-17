/*
###############################################################################
# name      : database.sql
# author    : carl_zys@163.com
# created   : 2017-10-10
# purpose   : mysql database objects 
# copyright : copyright (c) zhuyunsheng carl_zys@163.com all rights received  
################################################################################
*/

create database stdb;
create user 'stops'@'localhost' identified by 'stops';
grant all on stdb.* to 'stops'@'localhost';



drop index idx_stk_1day_prim on tb_stk_1day;

drop table if exists tb_stk_1day;

/*==============================================================*/
/* Table: tb_stk_1day                                           */
/*==============================================================*/
create table tb_stk_1day
(
   scode                char(8),
   sdate                date,
   sopen                decimal(10,2),
   shigh                decimal(10,2),
   slow                 decimal(10,2),
   sclose               decimal(10,2),
   samt                 bigint,
   svol                 bigint
);

/*==============================================================*/
/* Index: idx_stk_1day_prim                                     */
/*==============================================================*/
create unique index idx_stk_1day_prim on tb_stk_1day
(
   scode,
   sdate
);


drop index idx_stk_1min on tb_stk_1min;

drop table if exists tb_stk_1min;

/*==============================================================*/
/* Table: tb_stk_1min                                           */
/*==============================================================*/
create table tb_stk_1min
(
   scode                char(8),
   sdate                datetime,
   ropen                decimal(10,2),
   rhigh                decimal(10,2),
   rlow                 decimal(10,2),
   rclose               decimal(10,2),
   ramt                 decimal(10,2),
   rvol                 bigint
);

/*==============================================================*/
/* Index: idx_stk_1min                                          */
/*==============================================================*/
create index idx_stk_1min on tb_stk_1min
(
   scode,
   sdate
);

drop table if exists tb_stk_currstockhold;

/*==============================================================*/
/* Table: tb_stk_currstockhold                                  */
/*==============================================================*/
create table tb_stk_currstockhold
(
   scode                char(8) comment '股票代码',
   samt                 bigint comment '股票数量',
   sprice               decimal(10,2) comment '股票价格'
);

alter table tb_stk_currstockhold comment '当前账号所持股票';

drop table if exists tb_stk_tradelog;

/*==============================================================*/
/* Table: tb_stk_tradelog                                       */
/*==============================================================*/
create table tb_stk_tradelog
(
   tdate                datetime comment '交易日期',
   scode                char(8) comment '股票代码',
   sprice               decimal(10,2) comment '股票单价',
   samt                 bigint comment '成交数量'
);

alter table tb_stk_tradelog comment '交易日志';

