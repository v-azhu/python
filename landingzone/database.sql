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
   scode                char(8) comment '��Ʊ����',
   samt                 bigint comment '��Ʊ����',
   sprice               decimal(10,2) comment '��Ʊ�۸�'
);

alter table tb_stk_currstockhold comment '��ǰ�˺����ֹ�Ʊ';

drop table if exists tb_stk_tradelog;

/*==============================================================*/
/* Table: tb_stk_tradelog                                       */
/*==============================================================*/
create table tb_stk_tradelog
(
   tdate                datetime comment '��������',
   scode                char(8) comment '��Ʊ����',
   sprice               decimal(10,2) comment '��Ʊ����',
   samt                 bigint comment '�ɽ�����'
);

alter table tb_stk_tradelog comment '������־';



/*==============================================================*/
/* Table: tb_stk_ipolog                                       */
/*==============================================================*/
create table tb_stk_ipolog
(   
   scode                char(8) comment '��Ʊ����',
   sname				char(8) comment '��Ʊ����',
   rcode                char(8) comment '�깺����',
   releasecnt           bigint  comment '�����������ɣ�',
   releaseonlinecnt     bigint  comment '���Ϸ����������ɣ�',
   applycnt			    bigint  comment '�깺���ޣ��ɣ�',
   rprice				decimal(10,6) comment '���м۸�',
   applydate			datetime comment '�깺����',
   ipodate				datetime comment '��������',
   winrateonline    	decimal(10,6) comment '���Ϸ�����ǩ��',
   winrateoffline    	decimal(10,6) comment '����������ǩ��',
   enquiryamnt			decimal(10,6) comment 'ѯ���ۼƱ��۱���',
   enquirycnt			bigint comment 'ѯ���ۼƱ��۹ɣ��ɣ�',
   validacctsonline		bigint comment '������Ч�깺����(��)',
   validacctsoffline	bigint comment '������Ч�깺����(��)',
   validapplyonline		decimal(10,6) comment '������Ч�깺����(��)',
   validapplyoffline	decimal(10,6) comment '������Ч�깺����(��)',
   winnumberlast4		varchar(300) comment 'ĩ4λ��',
   winnumberlast5		varchar(300) comment 'ĩ5λ��',
   winnumberlast6		varchar(300) comment 'ĩ6λ��',
   winnumberlast7		varchar(300) comment 'ĩ7λ��',
   winnumberlast8		varchar(300) comment 'ĩ8λ��',
   winnumberlast9		varchar(300) comment 'ĩ9λ��'
   );

alter table tb_stk_ipolog comment '�¹��깺��־��';