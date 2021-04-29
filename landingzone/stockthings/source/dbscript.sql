drop table if exists tb_stk_baseinfo;

create table tb_stk_baseinfo(
	market                varchar(10) comment '�����������л�����',
	module                varchar(10) comment '��飬���壬��С�壬��ҵ�壬�ƴ����',
	scode				  varchar(10) comment '��Ʊ����',
	short_name			  varchar(10) comment '��Ʊ���',
	listed_date			  varchar(10) comment '��������',
	comp_name_cn	  	  varchar(100) comment '��˾ȫ�ƣ���������',
	comp_name_en	  	  varchar(100) comment '��˾ȫ�ƣ�Ӣ������',
	registry_addr         varchar(100) comment '��˾ע���ַ',
	web_addr         	  varchar(100) comment '��˾��ַ',
	capital_total		  varchar(30) comment 'A���ܹɱ�',
	capital_circulation	  varchar(30) comment 'A����ͨ�ɱ�',
	area 	  		  	  varchar(10) comment '���������ϣ�������',
	province 	  		  varchar(10) comment 'ʡ��',
	city 	  		      varchar(10) comment '����',
	industry 			  varchar(10) comment '������ҵ'
);
alter table tb_stk_baseinfo comment '��Ʊ������Ϣ(��A��)';

-- load data
load data infile 'tb_stk_baseinfo.csv' into table tb_stk_baseinfo 
fields terminated by ','
optionally enclosed by '"'
escaped by '"'
lines terminated by '\r\n';


drop table if exists tb_stk_companyprofile;

/*==============================================================*/
/* Table: tb_stk_companyprofile                                 */
/*==============================================================*/
create table tb_stk_companyprofile
(
   scode                varbinary(10) not null,
   comp_name_cn         varchar(200),
   comp_name_en         varchar(200),
   former_name          varchar(200),
   A_code               varchar(10),
   A_short_name         varchar(30),
   B_code               varchar(10),
   B_short_name         varchar(30),
   H_code               varchar(10),
   H_short_name         varchar(30),
   Invest_category      varchar(30),
   Buss_category_em     varchar(30),
   IPO_Exchange         varchar(30),
   Buss_category_csrc   varchar(30),
   GM                   varchar(30),
   legal_representative varchar(30),
   secretary            varchar(30),
   chairman             varchar(30),
   invest_buss_agent    varchar(30),
   Independent_directors varchar(300),
   contact_tel          varbinary(100),
   contact_email        varbinary(100),
   contact_fax          varchar(100),
   company_website      varchar(100),
   buss_addr            varchar(100),
   registry_addr        varchar(100),
   region               varchar(30),
   contact_postcode     varchar(10),
   registered_capital   varchar(30),
   IC_Reg_num           varchar(30),
   emp_num              varchar(30),
   manager_num          varchar(30),
   law_firm             varchar(100),
   accounting_firm      varchar(100),
   About_us             varchar(3000),
   buss_scope           varchar(3000),
   load_date            timestamp default now(),
   primary key (scode)
);
alter table tb_stk_companyprofile modify column contact_postcode varchar(30);
alter table tb_stk_companyprofile modify column About_us varchar(10000);


drop table if exists tb_stk_shareholder_top10;

/*==============================================================*/
/* Table: tb_stk_shareholder_top10                              */
/*==============================================================*/
create table tb_stk_shareholder_top10
(
   scode                varchar(10),
   report_date          varchar(10),
   top10_acct_typ       varchar(30),
   order_no             varchar(10),
   acct_name_cn         varchar(100),
   acct_typ             varchar(30),
   stk_typ              varchar(30),
   stk_cnt              varchar(30),
   stk_cnt_rate         varchar(30),
   isincrease           varchar(100),
   chg_rate             varchar(30),
   load_date            timestamp default now()
);

alter table tb_stk_shareholder_top10 modify column acct_name_cn varchar(300);

drop table if exists tb_stk_execs;

/*==============================================================*/
/* Table: tb_stk_execs                                          */
/*==============================================================*/
create table tb_stk_execs
(
   scode                varchar(10),
   seq                  varchar(10),
   ename                varchar(30),
   gender               varchar(10),
   age                  varchar(10),
   edu                  varchar(30),
   job_title            varchar(100),
   job_date             varchar(30),
   cv                   varchar(3000),
   load_date            timestamp default now()
);
alter table tb_stk_execs modify column ename varchar(100);



drop table if exists tb_stk_exholderchg;

/*==============================================================*/
/* Table: tb_stk_exholderchg                                    */
/*==============================================================*/
create table tb_stk_exholderchg
(
   scode                varchar(10) comment '��Ʊ����',
   chg_date             varchar(10) comment '�䶯����',
   chg_scode            varchar(10) comment '�䶯����',
   chg_sname            varchar(10) comment '��Ʊ����',
   chg_person           varchar(30) comment '�䶯��',
   chg_cnt              varchar(30) comment '�䶯����',
   chg_price_avg        varchar(10) comment '�ɽ�����',
   chg_amt              varchar(30) comment '�䶯���',
   chg_reason           varchar(300) comment '�䶯ԭ��',
   chg_rate             varchar(10) comment '�䶯����',
   stk_cnt_afterchg     varchar(10) comment '�䶯��ֹ�',
   stk_typ              varchar(10) comment '�ֹ�����',
   cxo_name             varchar(30) comment '�������Ա����',
   cxo_job_title        varchar(100) comment 'ְ��',
   relation_chg_cxo     varchar(30) comment '�䶯���붭�����Ա��ϵ',
   load_date            timestamp default now() comment 'װ������'
);

alter table tb_stk_exholderchg comment '�߹ֹܳɱ䶯��ϸ';

alter table tb_stk_exholderchg modify column chg_person varchar(300);
alter table tb_stk_exholderchg modify column cxo_name varchar(300);
