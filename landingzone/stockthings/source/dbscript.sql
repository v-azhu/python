drop table if exists tb_stk_baseinfo;

create table tb_stk_baseinfo(
	market                varchar(10) comment '交易所，上市或深市',
	module                varchar(10) comment '板块，主板，中小板，创业板，科创板等',
	scode				  varchar(10) comment '股票代码',
	short_name			  varchar(10) comment '股票简称',
	listed_date			  varchar(10) comment '上市日期',
	comp_name_cn	  	  varchar(100) comment '公司全称，中文名称',
	comp_name_en	  	  varchar(100) comment '公司全称，英文名称',
	registry_addr         varchar(100) comment '公司注册地址',
	web_addr         	  varchar(100) comment '公司网址',
	capital_total		  varchar(30) comment 'A股总股本',
	capital_circulation	  varchar(30) comment 'A股流通股本',
	area 	  		  	  varchar(10) comment '地区，华南，华北等',
	province 	  		  varchar(10) comment '省份',
	city 	  		      varchar(10) comment '城市',
	industry 			  varchar(10) comment '所属行业'
);
alter table tb_stk_baseinfo comment '股票基本信息(仅A股)';

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
   scode                varchar(10) comment '股票代码',
   chg_date             varchar(10) comment '变动日期',
   chg_scode            varchar(10) comment '变动代码',
   chg_sname            varchar(10) comment '股票名称',
   chg_person           varchar(30) comment '变动人',
   chg_cnt              varchar(30) comment '变动股数',
   chg_price_avg        varchar(10) comment '成交均价',
   chg_amt              varchar(30) comment '变动金额',
   chg_reason           varchar(300) comment '变动原因',
   chg_rate             varchar(10) comment '变动比例',
   stk_cnt_afterchg     varchar(10) comment '变动后持股',
   stk_typ              varchar(10) comment '持股种类',
   cxo_name             varchar(30) comment '董监高人员姓名',
   cxo_job_title        varchar(100) comment '职务',
   relation_chg_cxo     varchar(30) comment '变动人与董监高人员关系',
   load_date            timestamp default now() comment '装载日期'
);

alter table tb_stk_exholderchg comment '高管持股变动明细';

alter table tb_stk_exholderchg modify column chg_person varchar(300);
alter table tb_stk_exholderchg modify column cxo_name varchar(300);
