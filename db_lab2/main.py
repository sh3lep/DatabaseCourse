import datetime
import psycopg2
import psycopg2.extras
import random
import argparse
import configparser
import numpy as np

config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

connection = psycopg2.connect(
    dbname=config.get("postgres", "dbname"),
    user=config.get("postgres", "user"),
    password=config.get("postgres", "password"))

cursor = connection.cursor()

digits = '0123456789'
letters = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
lat_letters = 'qwertyuiopasdfghjklzxcvbnm'

today = datetime.datetime.today()

lifestyle_ids = ()
seasons_ids = ()
collections_ids = ()
brand_ids = ()
clothes_ids = ()
customer_ids = ()
employees_ids = ()
customer_addresses_ids = ()
loyalty_card_ids = ()
order_ids = []
order_ids_for_lab3 = []
pp_ids = ()
currier_list = ()
order_ids_delivery = []
rnd_in_stock = (1, 1, 1, 1, 1, 1, 1, 0, 0, 0)

lifestyles = open("input/lifestyle.txt", "r").readlines()
seasons = open("input/seasons.txt", "r").readlines()
collections = open("input/collections.txt", "r").readlines()
brands = open("input/brands.txt", "r").readlines()

clothes_desc = open("input/clothes_descriptions.txt", encoding='utf-8', mode="r").readlines()

names_male = open("input/names_male.txt", encoding='utf-8', mode='r').readlines()
names_female = open("input/names_female.txt", encoding='utf-8', mode='r').readlines()
surnames_male = open("input/surnames_male.txt", encoding='utf-8', mode='r').readlines()
surnames_female = open("input/surnames_female.txt", encoding='utf-8', mode='r').readlines()

cities = open("input/cities.txt", encoding='utf-8', mode='r').readlines()
countries = open("input/great.txt", encoding='utf-8', mode='r').readlines()
loyalty_names = open("input/loyalty.txt", encoding='utf-8', mode='r').readlines()

email_domains = open("input/email_domains.txt", "r").readlines()
courier_names = open("input/courrier_names.txt", encoding='utf-8', mode="r").readlines()


def truncate_restart():
    cursor.execute("truncate table emp_shoplist restart identity cascade;"
                   "truncate table emp_shoplist_item restart identity cascade;"
                   "truncate table \"subscription\" restart identity cascade;"
                   "truncate table ordered_clothes restart identity cascade;"
                   "truncate table clothes restart identity cascade;"
                   "truncate table brand restart identity cascade;"
                   "truncate table lifestyle restart identity cascade;"
                   "truncate table collection restart identity cascade;"
                   "truncate table seasons restart identity cascade;"
                   "truncate table currier_delivery restart identity cascade;"
                   "truncate table customer_address restart identity cascade;"
                   "truncate table pp_delivery restart identity cascade;"
                   "truncate table \"order\" restart identity cascade;"
                   "truncate table loyalty_card restart identity cascade;"
                   "truncate table customer restart identity cascade;"
                   "truncate table employee restart identity cascade;"
                   "truncate table pp_list restart identity cascade;"
                   "truncate table currier_list restart identity cascade;")


def generate_data(args):
    if args.nul == '1':
        truncate_restart()

    if args.clothes is not None and args.clothes != '0':
        generate_brands()
        generate_lifestyle()
        generate_seasons()
        generate_collections()
        generate_clothes(arguments.clothes)

    if args.customers is not None and args.customers != '0':
        generate_customer(arguments.customers)

    if args.employees is not None and args.employees != '0':
        generate_employees(arguments.employees)
        generate_loyalty_card()

    if args.orders is not None and args.orders != '0':
        generate_orders(arguments.orders)
        # generate_orders_for_lab3()

    if args.lab3:
        generate_orders_for_lab3()


def generate_brands():
    global brand_ids
    cursor.execute('SELECT name FROM brand')
    brand_names_raw = cursor.fetchall()
    brand_names = list(sum(brand_names_raw, ()))

    for element in brands:
        if element.replace("\n", "") not in brand_names:
            element = element.replace("\n", "")
            description = random_string(random.randint(5, 15))
            cursor.execute('INSERT INTO \"brand\" VALUES (default, \'{}\', \'{}\')'.format(element, description))

    cursor.execute('SELECT brand_id FROM brand')
    brand_ids = cursor.fetchall()


def generate_seasons():
    global seasons_ids
    cursor.execute('SELECT name FROM seasons')
    season_names_raw = cursor.fetchall()
    season_names = list(sum(season_names_raw, ()))

    for element in seasons:
        if element.replace("\n", "") not in season_names:
            element = element.replace("\n", "")
            description = random_string(random.randint(5, 15))
            cursor.execute("INSERT INTO seasons VALUES (default, \'{}\', \'{}\')".format(element, description))

    cursor.execute('SELECT season_id FROM seasons')
    seasons_ids = cursor.fetchall()


def generate_lifestyle():
    global lifestyle_ids
    cursor.execute('SELECT name FROM lifestyle')
    lifestyle_names_raw = cursor.fetchall()
    lifestyle_names = list(sum(lifestyle_names_raw, ()))

    for element in lifestyles:
        if element.replace("\n", "") not in lifestyle_names:
            element = element.replace("\n", "")
            description = random_string(random.randint(5, 15))
            cursor.execute('INSERT INTO lifestyle VALUES (default, \'{}\', \'{}\')'.format(element, description))

    cursor.execute('SELECT lifestyle_id FROM lifestyle')
    lifestyle_ids = cursor.fetchall()


def generate_collections():
    global collections_ids
    cursor.execute('SELECT name FROM collection')
    collection_names_raw = cursor.fetchall()
    collection_names = list(sum(collection_names_raw, ()))

    for element in collections:
        if element.replace("\n", "") not in collection_names:
            element = element.replace("\n", "")
            description = random_string(random.randint(5, 15))
            cursor.execute('INSERT INTO collection VALUES (default, \'{}\', \'{}\')'.format(element, description))

    cursor.execute('SELECT collection_id FROM collection')
    collections_ids = cursor.fetchall()


def generate_clothes(amount):
    global clothes_ids
    temp = []
    for i in range(int(amount)):
        temp.append(tuple((random.choice(brand_ids),
                           random_string(random.randint(1, 25)),
                           random.choice(clothes_desc).replace("\n", ""),
                           random.randint(1, 3000),
                           random.choice(lifestyle_ids),
                           random.choice(collections_ids),
                           random.choice(seasons_ids)[0],
                           bool(random.choice(rnd_in_stock)))))

    clothes_rows = tuple(temp)
    query = "INSERT INTO clothes (brand_id, name, description, price, lifestyle_id, collection_id, season_id, in_stock) " \
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"

    psycopg2.extras.execute_batch(cursor, query, clothes_rows)

    cursor.execute('SELECT clothes_id FROM clothes')
    clothes_ids = cursor.fetchall()


def generate_customer(amount):
    global customer_ids
    temp = []
    for i in range(int(amount)):
        if i % 2 == 0:
            firstname = random.choice(names_male)
            lastname = random.choice(surnames_male)
            gender = "Male"
        else:
            firstname = random.choice(names_female)
            lastname = random.choice(surnames_female)
            gender = "Female"

        email_domain = random.choice(email_domains)
        email_domain = email_domain.replace("\n", "")
        email = random_latstring(random.randint(8, 20)) + email_domain

        birthday = random_date(today - datetime.timedelta(days=55 * 365),
                               today - datetime.timedelta(days=12 * 365))
        vk = 'vk.com/' + random_latstring(random.randint(20, 50))

        temp.append(tuple((firstname.replace("\n", ""),
                           lastname.replace("\n", ""),
                           gender,
                           random_phone_number(),
                           email,
                           birthday,
                           vk,)))

    customer_rows = tuple(temp)
    query = "INSERT INTO customer (firstname, lastname, gender, phone, email, birth_date, vk) " \
            "VALUES (%s, %s, %s, %s, %s, %s, %s)"
    # cursor.executemany(query, customer_rows)
    psycopg2.extras.execute_batch(cursor, query, customer_rows)
    cursor.execute('SELECT customer_id FROM customer')
    customer_ids = cursor.fetchall()

    generate_customer_address(amount)


def generate_customer_address(amount):
    global customer_addresses_ids
    temp = []
    for i in range(int(amount) + random.randint(5, 25)):
        if i % 2 == 0:
            firstname = random.choice(names_male)
            lastname = random.choice(surnames_male)
        else:
            firstname = random.choice(names_female)
            lastname = random.choice(surnames_female)

        firstname = firstname.replace("\n", "")
        lastname = lastname.replace("\n", "")

        temp.append(tuple((firstname,
                           lastname,
                           random_string(random.randint(1, 20)),
                           random.randint(1, 100),
                           random.choice(countries).replace("\n", ""),
                           random.randint(100000, 999999),
                           random.choice(customer_ids)[0],
                           random.choice(cities).replace("\n", ""),
                           random.randint(1, 300))))

    customer_address_rows = tuple(temp)
    query = "INSERT INTO customer_address (firstname, lastname, street, building, country, postal_code, " \
            "customer_id, city, apartment) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    # cursor.executemany(query, customer_address_rows)
    psycopg2.extras.execute_batch(cursor, query, customer_address_rows)
    cursor.execute('SELECT customer_address_id FROM customer_address')
    customer_addresses_ids = cursor.fetchall()


def generate_employees(amount):
    global employees_ids
    temp = []
    for i in range(int(amount)):
        if i % 2 == 0:
            firstname = random.choice(names_male)
            lastname = random.choice(surnames_male)
        else:
            firstname = random.choice(names_female)
            lastname = random.choice(surnames_female)

        firstname = firstname.replace("\n", "")
        lastname = lastname.replace("\n", "")

        temp.append(tuple((firstname, lastname, random_string(random.randint(1, 30)),)))

    employee_rows = tuple(temp)
    query = "INSERT INTO employee (firstname, lastname, function) VALUES (%s, %s, %s)"
    # cursor.executemany(query, employee_rows)
    psycopg2.extras.execute_batch(cursor, query, employee_rows)
    cursor.execute('SELECT employee_id FROM employee')
    employees_ids = cursor.fetchall()


def generate_loyalty_card():
    global loyalty_card_ids
    temp = []
    customers_with_cards = int(arguments.customers) // (random.randint(2, 5))
    customers_temp = np.random.choice(sum(customer_ids, ()), customers_with_cards, replace=False)
    for i in range(customers_with_cards):
        customer_id = int(customers_temp[i])
        card_activation_date = random_date(today - datetime.timedelta(days=69 * 365),
                                           today - datetime.timedelta(days=27 * 365))
        points = random.randint(0, 20000)
        if points in range(0, 5000):
            loyalty_name = 'Bronze'
        elif points in range(5000, 10000):
            loyalty_name = 'Silver'
        elif points in range(10000, 15000):
            loyalty_name = 'Gold'
        elif points in range(15000, 20000):
            loyalty_name = 'Platinum'
        else:
            loyalty_name = random.choice(loyalty_names).replace("\n", "")
        employee_id = random.choice(employees_ids)[0]
        last_modified = random_date(today - datetime.timedelta(days=27 * 365),
                                    today - datetime.timedelta(days=50))

        temp.append(tuple((int(customer_id), loyalty_name, card_activation_date, points, employee_id, last_modified,)))

    lc_rows = tuple(temp)
    query = "INSERT INTO loyalty_card (customer_id, loyalty_name, card_activation_date, points, employee_id, " \
            "last_modified) VALUES (%s, %s, %s, %s, %s, %s)"
    # cursor.executemany(query, lc_rows)
    psycopg2.extras.execute_batch(cursor, query, lc_rows)

    cursor.execute('SELECT loyalty_card_id FROM loyalty_card')
    loyalty_card_ids = cursor.fetchall()
    generate_subscription(int(arguments.customers))


def generate_subscription(amount):
    temp = []
    for i in range(round(amount / random.uniform(1.1, 1.4))):
        loyalty_card_id = random.choice(loyalty_card_ids)[0]
        temp.append(tuple((loyalty_card_id, bool(random.randint(0, 1)), bool(random.randint(0, 1)),
                           bool(random.randint(0, 1)), bool(random.randint(0, 1)),)))

    subs_rows = tuple(temp)
    query = "INSERT INTO subscription (loyalty_card_id, sms, email, push, phone_calls) VALUES (%s, %s, %s, %s, %s)"
    # cursor.executemany(query, subs_rows)
    psycopg2.extras.execute_batch(cursor, query, subs_rows)


def generate_orders(amount):
    global order_ids
    temp = []

    for i in range(int(amount)):
        customer_id = random.choice(customer_ids)[0]
        if i % 3 == 0:
            loyalty_card_id = random.choice(loyalty_card_ids)[0]
        else:
            loyalty_card_id = None
        if i % 2 == 0:
            date_of_order = random_date(today - datetime.timedelta(days=5 * 365), today)
        else:
            date_of_order = random_date(today - datetime.timedelta(days=20 * 365),
                                        today - datetime.timedelta(days=5 * 365))
        temp.append(tuple((customer_id, loyalty_card_id, date_of_order,)))

    ord_rows = tuple(temp)
    query = "INSERT INTO \"order\" (customer_id, loyalty_card_id, date_of_order) VALUES (%s, %s, %s)"
    # cursor.executemany(query, ord_rows)
    psycopg2.extras.execute_batch(cursor, query, ord_rows)

    query = "SELECT order_id FROM \"order\" ORDER BY order_id DESC LIMIT ({})"
    cursor.execute(query.format(amount))
    order_ids = cursor.fetchall()
    global order_ids_delivery
    order_ids_delivery = order_ids
    random.shuffle(order_ids_delivery)
    generate_pp_list()
    generate_currier_list()
    generate_pp_delivery(amount)
    generate_currier_delivery(amount)
    generate_ordered_clothes(amount)


def generate_ordered_clothes(amount):
    temp = []
    for i in range(int(amount) + random.randint(0, int(amount) // 2)):
        if i < len(order_ids):
            order_id = order_ids[i][0]
        else:
            order_id = random.choice(order_ids[0])

        clothes_id = random.choice(clothes_ids)[0]
        quantity = random.randint(1, 5)
        temp.append(tuple((clothes_id, quantity, order_id,)))
    ord_clo_rows = tuple(temp)
    query = "INSERT INTO ordered_clothes (clothes_id, quantity, order_id) VALUES (%s, %s, %s)"
    # cursor.executemany(query, ord_clo_rows)
    psycopg2.extras.execute_batch(cursor, query, ord_clo_rows)


def generate_pp_list():
    global pp_ids
    temp = []
    for i in range(random.randint(50, 100)):
        address = random_string(random.randint(5, 15))
        temp.append(tuple((address,)))
    pp_list_rows = tuple(temp)
    query = "INSERT INTO pp_list (address) VALUES (%s)"
    # cursor.executemany(query, pp_list_rows)
    psycopg2.extras.execute_batch(cursor, query, pp_list_rows)

    cursor.execute('SELECT pp_id FROM pp_list')
    pp_ids = cursor.fetchall()


def generate_currier_list():
    global currier_list
    temp = []
    for i in range(random.randint(3, 10)):
        name = random.choice(courier_names)
        name = name.replace("\n", "")
        description = random_string(random.randint(5, 30))
        temp.append(tuple((name, description,)))
    cur_list_rows = tuple(temp)
    query = "INSERT INTO currier_list (name, description) VALUES (%s, %s)"
    # cursor.executemany(query, cur_list_rows)
    psycopg2.extras.execute_batch(cursor, query, cur_list_rows)

    cursor.execute('SELECT id FROM currier_list')
    currier_list = cursor.fetchall()


def generate_pp_delivery(amount):
    global r
    r = int(amount) - random.randint(0, int(amount))
    temp = []
    for i in range(r):
        order_id = order_ids_delivery[i][0]
        pp_id = random.choice(pp_ids)[0]
        currier_service_id = random.choice(currier_list)[0]
        temp.append(tuple((order_id, pp_id, currier_service_id,)))
    pp_del_rows = tuple(temp)
    query = "INSERT INTO pp_delivery (order_id, pp_id, currier_service_id) VALUES (%s, %s, %s)"
    # cursor.executemany(query, pp_del_rows)
    psycopg2.extras.execute_batch(cursor, query, pp_del_rows)


def generate_currier_delivery(amount):
    temp = []
    for i in range(r, int(amount)):
        order_id = order_ids_delivery[i][0]
        currier_service_id = random.choice(currier_list)[0]
        customer_address_id = random.choice(customer_addresses_ids)[0]
        temp.append(tuple((order_id, currier_service_id, customer_address_id,)))
    cur_del_rows = tuple(temp)
    query = "INSERT INTO currier_delivery (order_id, currier_service_id, customer_address_id) VALUES (%s, %s, %s)"
    # cursor.executemany(query, cur_del_rows)
    psycopg2.extras.execute_batch(cursor, query, cur_del_rows)


def random_date(start_date, end_date):
    date_delta = end_date - start_date
    days_delta = date_delta.days
    days_random = random.randrange(days_delta)
    rnd_date = start_date + datetime.timedelta(days=days_random)
    return rnd_date


def random_phone_number():
    phone_number = "9"
    for i in range(9):
        phone_number += random.choice(digits)
    return phone_number


def random_string(length):
    rnd_str = ''
    for i in range(int(length)):
        rnd_str += random.choice(letters)
    return rnd_str


def random_latstring(length):
    rnd_str = ''
    for i in range(int(length)):
        rnd_str += random.choice(lat_letters)
    return rnd_str


def random_number(length):
    num = ''
    for i in range(int(length)):
        num += random.choice(digits)
    return num


# 2 функции для 3 лабороторной
def generate_orders_for_lab3():
    global order_ids_for_lab3
    temp = []

    cursor.execute('INSERT INTO \"brand\" VALUES (default, \'{}\', \'{}\')'.format('LAB3_BRAND', 'LAB3_BRAND'))
    cursor.execute("INSERT INTO clothes VALUES (default, 19, 'lab3', 'lab3', 228, 1, 1, 1, True)")

    for i in range(99):
        customer_id = random.choice(customer_ids)[0]
        if i < 5:
            date_of_order = '2021-05-10'
        elif 5 <= i < 15:
            date_of_order = '2021-04-10'
        elif 15 <= i < 30:  #
            date_of_order = '2021-03-10'
        elif 30 <= i < 50:
            date_of_order = '2021-02-10'
        elif 50 <= i < 72:
            date_of_order = '2021-01-10'
        elif 72 <= i < 100:
            date_of_order = '2020-12-10'
        else:
            date_of_order = '2021-12-10'

        temp.append(tuple((customer_id, None, date_of_order,)))

    ord_rows = tuple(temp)
    query = "INSERT INTO \"order\" (customer_id, loyalty_card_id, date_of_order) VALUES (%s, %s, %s)"
    # cursor.executemany(query, ord_rows)
    psycopg2.extras.execute_batch(cursor, query, ord_rows)

    query = "SELECT order_id FROM \"order\" ORDER BY order_id DESC LIMIT ({})"
    cursor.execute(query.format(99))
    order_ids_for_lab3 = cursor.fetchall()

    generate_ordered_clothes_for_lab3()


def generate_ordered_clothes_for_lab3():
    query = "SELECT clothes_id FROM clothes ORDER BY clothes_id DESC LIMIT 1"
    cursor.execute(query.format(99))
    clothes_ids_for_lab3 = cursor.fetchall()

    temp = []
    for i in range(99):
        order_id = order_ids_for_lab3[i][0]
        # order_id = random.choice(order_ids[0])
        clothes_id = clothes_ids_for_lab3[0]
        quantity = random.randint(1, 5)
        temp.append(tuple((clothes_id, quantity, order_id,)))
    ord_clo_rows = tuple(temp)
    query = "INSERT INTO ordered_clothes (clothes_id, quantity, order_id) VALUES (%s, %s, %s)"
    # cursor.executemany(query, ord_clo_rows)
    psycopg2.extras.execute_batch(cursor, query, ord_clo_rows)


if __name__ == '__main__':
    args = argparse.ArgumentParser(description="Details of data generation")
    args.add_argument('--nul', action="store", dest="nul")
    args.add_argument('--clo', action="store", dest="clothes")
    args.add_argument('--cust', action="store", dest="customers")
    args.add_argument('--emp', action="store", dest="employees")
    args.add_argument('--ord', action="store", dest="orders")
    args.add_argument('--lab3', action="store", dest="lab3", default=0, type=int)
    arguments = args.parse_args()

    generate_data(arguments)

    connection.commit()
    cursor.close()
    connection.close()
