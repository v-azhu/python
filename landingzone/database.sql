/*
 sdx vipdoc data parser database instruc
 by zhuys 20170930
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
