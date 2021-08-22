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
	
alter table clothes add column collection_id integer not null
		constraint collection_id
			references collection
				on delete cascade

alter table clothes add column season_id integer not null
		constraint season_id
			references seasons
				on delete cascade

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