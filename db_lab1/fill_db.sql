TRUNCATE TABLE CUSTOMER CASCADE;
TRUNCATE TABLE employee CASCADE;
TRUNCATE TABLE brand CASCADE;
TRUNCATE TABLE lifestyle CASCADE;
TRUNCATE TABLE customer_address CASCADE;
TRUNCATE TABLE social_networks CASCADE;
TRUNCATE TABLE loyalty_card CASCADE;
TRUNCATE TABLE clothes CASCADE;
TRUNCATE TABLE "order" CASCADE;
TRUNCATE TABLE "subscription" CASCADE;
TRUNCATE TABLE ordered_clothes CASCADE;

ALTER SEQUENCE customer_customer_id_seq RESTART WITH 1;	
ALTER SEQUENCE customer_address_adress_id_seq RESTART WITH 1;	
ALTER SEQUENCE lifestyle_lifestyle_id_seq RESTART WITH 1;	
ALTER SEQUENCE brand_brand_id_seq RESTART WITH 1;	
ALTER SEQUENCE clothes_clothes_id_seq RESTART WITH 1;	
ALTER SEQUENCE employee_employee_id_seq RESTART WITH 1;	
ALTER SEQUENCE loyalty_program_loyalty_card_number_seq RESTART WITH 1;	
ALTER SEQUENCE order_order_id_seq RESTART WITH 1;		

INSERT INTO public.customer (firstname, lastname, gender, phone, email, birth_date)
	VALUES
	('name_1', 'surname_1', 'Male', 123456789123456, 'a@b.c', '2000-01-08'),
	('name_2', 'surname_2', 'Female', 123456789123457, 'b@c.d', '2000-01-09'),
	('name_3', 'surname_3', 'Unknown', 123456789123458, 'c@d.f', '2000-01-10');

INSERT INTO public.customer_address (firstname, lastname, street, building, country, postal_code, customer_id, city, apartment, main_address)
	VALUES
	('name_1', 'surname_1', 'street_1', 0, 'Ukraine', 282146, 1, 'Default city', 0, true),
	('name_2', 'surname_2', 'street_2', 0, 'Ukraine', 282146, 1, 'Default city', 0, false),
	('name_3', 'surname_3', 'street_3', 0, 'Ukraine', 282146, 1, 'Default city', 0, false);

INSERT INTO public.social_networks (customer_id,  vk, instagram, twitter, facebook)
	VALUES
	(1, 'vk.com/a', 'instagram.com/a', 'twitter.com/a', 'facebook.com/a'),
	(2, 'vk.com/b', 'instagram.com/b', 'twitter.com/b', 'facebook.com/b'),
	(3, 'vk.com/c', 'instagram.com/c', 'twitter.com/c', 'facebook.com/c');

INSERT INTO public.lifestyle (name, description)
	VALUES
	('zozh', 'footbolchik'),
	('pivo', 'letterball'),
	('levprotiv', 'potushisigaretu');

INSERT INTO public.brand (name, description)
	VALUES
	('Naik', 'Jast naik'),
	('Adik', 'Mama kupi izi'),
	('Demix', 'Na fizru');

INSERT INTO public.clothes (brand_id, name, description, price, lifestyle_id)
	VALUES
	(1, 'aaa', 'xxx', 111, 1),
	(2, 'bbb', 'yyy', 222, 2),
	(3, 'ccc', 'zzz', 333, 3);

INSERT INTO public.employee (firstname, lastname, function)
	VALUES
	('Allaniz', 'Bicycle', 'manager'),
	('Ccc', 'Ddd', 'administrator'),
	('Eee', 'Fff', 'consultant');

INSERT INTO public.loyalty_card (customer_id, loyalty_name, card_activation_date, points, employee_id)
	VALUES
	(1, 'Bronze', '2000-05-10', 100, 1),
	(2, 'Silver', '2000-06-10', 200, 2),
	(3, 'Platinum', '2000-07-10', 300, 3);

INSERT INTO public.order (customer_id, loyalty_card_id, customer_address_id, date_of_order)
	VALUES
	(1, 1, 1, '2000-01-21'),
	(2, 2, 2, '2000-01-22'),
	(3, 3, 3, '2000-01-23');

INSERT INTO public.ordered_clothes (clothes_id, quantity, order_id)
	VALUES
	(1, 11, 1),
	(2, 22, 2),
	(3, 33, 3);

INSERT INTO public.subscription (loyalty_card_id, sms, email, push, phone_calls)
	VALUES
	(1, true, true, true, true),
	(2, false, false, false, false),
	(3, true, false, true, false);