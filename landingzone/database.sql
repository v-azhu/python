/*
###############################################################################
# name      : database.sql
# author    : awen.zhu@hotmail.com
# created   : 2017-10-10
# purpose   : mysql database objects 
# copyright : copyright (c) zhuyunsheng awen.zhu@hotmail.com all rights received  
################################################################################
*/

create database stdb;
create user 'stops'@'localhost' identified by 'stops';
grant all on stdb.* to 'stops'@'localhost';


use stdb;

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



/*==============================================================*/
/* Table: tb_stk_ipolog                                       */
/*==============================================================*/
create table tb_stk_ipolog
(   
   scode                char(8) comment '股票代码',
   sname				char(8) comment '股票名称',
   rcode                char(8) comment '申购代码',
   releasecnt           bigint  comment '发行总数（股）',
   releaseonlinecnt     bigint  comment '网上发行总数（股）',
   applycnt			    bigint  comment '申购上限（股）',
   rprice				decimal(10,6) comment '发行价格',
   applydate			datetime comment '申购日期',
   ipodate				datetime comment '上市日期',
   winrateonline    	decimal(10,6) comment '网上发行中签率',
   winrateoffline    	decimal(10,6) comment '网下配售中签率',
   enquiryamnt			decimal(10,6) comment '询价累计报价倍数',
   enquirycnt			bigint comment '询价累计报价股（股）',
   validacctsonline		bigint comment '网上有效申购户数(户)',
   validacctsoffline	bigint comment '网下有效申购户数(户)',
   validapplyonline		decimal(10,6) comment '网上有效申购股数(股)',
   validapplyoffline	decimal(10,6) comment '网下有效申购股数(股)',
   winnumberlast4		varchar(300) comment '末4位数',
   winnumberlast5		varchar(300) comment '末5位数',
   winnumberlast6		varchar(300) comment '末6位数',
   winnumberlast7		varchar(300) comment '末7位数',
   winnumberlast8		varchar(300) comment '末8位数',
   winnumberlast9		varchar(300) comment '末9位数'
   );

alter table tb_stk_ipolog comment '新股申购日志表';