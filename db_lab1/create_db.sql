create table customer
(
	customer_id serial not null
		constraint customer_pk
			primary key,
	firstname varchar default ''::character varying not null,
	lastname varchar default ''::character varying not null,
	gender varchar,
	phone varchar(15),
	email varchar,
	birth_date date,
	vk varchar(100)
);

create unique index customer_customer_id_uindex
	on customer (customer_id);

create unique index customer_email_uindex
	on customer (email);

create unique index customer_vk_uindex
	on customer (vk);

create table customer_address
(
	customer_address_id serial not null
		constraint customer_address_pk
			primary key,
	firstname varchar default ''::character varying not null,
	lastname varchar default ''::character varying not null,
	street varchar default ''::character varying not null,
	building integer not null,
	country varchar default ''::character varying not null,
	postal_code integer not null,
	customer_id integer not null
		constraint customer_address_customer_customer_id_fk
			references customer
				on delete cascade,
	city varchar default ''::character varying not null,
	apartment integer,
	main_address boolean default false not null
);

create unique index customer_address_adress_id_uindex
	on customer_address (customer_address_id);

create table brand
(
	brand_id serial not null
		constraint brand_pk
			primary key,
	name varchar default ''::character varying not null,
	description varchar default ''::character varying
);

create unique index brand_brand_id_uindex
	on brand (brand_id);

create unique index brand_name_uindex
	on brand (name);

create table lifestyle
(
	lifestyle_id serial not null
		constraint lifestyle_pk
			primary key,
	name varchar default ''::character varying not null,
	description varchar
);

create unique index lifestyle_lifestyle_id_uindex
	on lifestyle (lifestyle_id);

create unique index lifestyle_name_uindex
	on lifestyle (name);

create table employee
(
	employee_id serial not null
		constraint employee_pk
			primary key,
	firstname varchar default ''::character varying not null,
	lastname varchar default ''::character varying not null,
	function varchar default ''::character varying not null
);

create unique index employee_employee_id_uindex
	on employee (employee_id);

create table loyalty_card
(
	loyalty_card_id serial not null
		constraint loyalty_program_pk
			primary key,
	customer_id integer not null
		constraint loyalty_program_customer_customer_id_fk
			references customer
				on delete cascade,
	loyalty_name varchar(8) default 'Bronze'::character varying not null,
	card_activation_date date,
	points integer,
	employee_id integer
		constraint loyalty_card_employee_employee_id_fk
			references employee,
	last_modified date
);

create unique index loyalty_program_loyalty_card_number_uindex
	on loyalty_card (loyalty_card_id);

create table subscription
(
	loyalty_card_id integer not null
		constraint subscription_loyalty_card_loyalty_card_id_fk
			references loyalty_card
				on delete cascade,
	sms boolean default true,
	email boolean default true not null,
	push boolean default true not null,
	phone_calls boolean default true not null
);

create table "order"
(
	order_id serial not null
		constraint order_pk
			primary key,
	customer_id integer not null
		constraint order_customer_customer_id_fk
			references customer,
	loyalty_card_id integer
		constraint order_loyalty_card_loyalty_card_id_fk
			references loyalty_card,
	date_of_order date
);

create unique index order_order_id_uindex
	on "order" (order_id);

create table collection
(
	collection_id serial not null
		constraint collection_pk
			primary key,
	name varchar not null,
	description varchar
);

create unique index collection_name_uindex
	on collection (name);

create table seasons
(
	season_id serial not null
		constraint seasons_pk
			primary key,
	name varchar not null,
	description varchar
);

create unique index seasons_name_uindex
	on seasons (name);

create table clothes
(
	clothes_id serial not null
		constraint clothes_pk
			primary key,
	brand_id integer not null
		constraint clothes_brand_brand_id_fk
			references brand
				on delete cascade,
	name varchar default ''::character varying not null,
	description varchar default ''::character varying not null,
	price integer not null,
	lifestyle_id integer not null
		constraint clothes_lifestyle_lifestyle_id_fk
			references lifestyle,
	collection_id integer not null
		constraint collection_id
			references collection
				on delete cascade,
	season_id integer not null
		constraint season_id
			references seasons
				on delete cascade
);

create unique index clothes_clothes_id_uindex
	on clothes (clothes_id);

create table ordered_clothes
(
	clothes_id integer not null
		constraint ordered_clothes_clothes_clothes_id_fk
			references clothes,
	quantity integer,
	order_id integer not null
		constraint ordered_clothes_order_order_id_fk
			references "order"
				on delete cascade
);

create table pp_list
(
	pp_id serial not null
		constraint pp_list_pk
			primary key,
	address varchar not null
);

create table currier_list
(
	id serial not null
		constraint currier_list_pk
			primary key,
	name varchar not null,
	description varchar
);

create table currier_delivery
(
	id serial not null
		constraint currier_delivery_pk
			primary key,
	order_id integer not null
		constraint order_id
			references "order"
				on delete cascade,
	currier_service_id integer not null
		constraint currier_delivery_id
			references currier_list
				on delete cascade,
	customer_address_id integer not null
		constraint customer_address_id
			references customer_address
				on delete cascade
);

create table pp_delivery
(
	id serial not null
		constraint pp_delivery_pk
			primary key,
	order_id integer not null
		constraint order_id
			references "order"
				on delete cascade,
	pp_id integer not null
		constraint pp_id
			references pp_list
				on delete cascade,
	currier_service_id integer not null
		constraint currier_service_id
			references currier_list
				on delete cascade
);

