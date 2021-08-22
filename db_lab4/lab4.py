import psycopg2
import random
import threading
import time
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd
from datetime import datetime
import argparse
import configparser

config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

con = psycopg2.connect(dbname=config.get("postgres", "dbname"),
                       user=config.get("postgres", "user"),
                       password=config.get("postgres", "password"))
cur = con.cursor()

# cur.execute('SELECT name FROM brand;')
# brands = cur.fetchall()
cur.execute('SELECT firstname FROM customer;')
names = cur.fetchall()
# print(names)
cur.execute('SELECT description FROM clothes')
descriptions = cur.fetchall()
# print(descriptions)

con.close()

dates = pd.date_range('2002-03-01', datetime.now(), freq='M')
# genders = ['Male', 'Female']

threads = []
results = []

prepare = False

global threads_min
global threads_max
global const_queries
global const_threads
global queries_min
global queries_max
global seconds

queries = {
    # выбираем покупателей с опред. именем
    1: '''SELECT loyalty_card.customer_id, customer.firstname, customer.lastname, customer.birth_date,
    loyalty_card.points, employee.employee_id, employee.firstname, employee.lastname, loyalty_card.last_modified
    FROM loyalty_card
    JOIN customer ON customer.customer_id = loyalty_card.customer_id
    JOIN employee ON employee.employee_id = loyalty_card.employee_id
    WHERE customer.firstname = (%s)
    ORDER BY loyalty_card.customer_id, loyalty_card.last_modified DESC;''',
    # выбираем все курьерские доставки в СПб и курьерские службы их выполнявшие в определенную дату
    2: '''SELECT currier_delivery.order_id, customer_address.city, currier_list.name, "order".date_of_order 
    FROM currier_delivery
    JOIN customer_address ON currier_delivery.customer_address_id = customer_address.customer_address_id
    JOIN currier_list ON currier_delivery.currier_service_id = currier_list.id
    JOIN "order" ON currier_delivery.order_id = "order".order_id
    WHERE customer_address.city = 'Санкт-Петербург' AND "order".date_of_order = (%s)
    ORDER BY currier_delivery.order_id;''',
    # выбираем всех женщины, у которых на карте много баллов и у которых вкл оповещения по смс
    3: '''SELECT loyalty_card.customer_id, customer.firstname, customer.lastname, customer.gender, loyalty_card.points,
    "subscription".sms, loyalty_card.last_modified 
    FROM loyalty_card
    JOIN customer ON customer.customer_id = loyalty_card.customer_id
    JOIN "subscription" on "subscription".loyalty_card_id = loyalty_card.loyalty_card_id
    WHERE loyalty_card.points > (%s) AND customer.gender = 'Female' AND "subscription".sms = true
    ORDER BY loyalty_card.customer_id, loyalty_card.last_modified DESC;''',
    # выбираем все доставки в постоматы за последние несколько месяцев
    4: '''SELECT pp_delivery.order_id, pp_list.address, currier_list.name, "order".date_of_order 
    FROM pp_delivery
    JOIN pp_list ON pp_delivery.pp_id = pp_list.pp_id
    JOIN currier_list ON pp_delivery.currier_service_id = currier_list.id
    JOIN "order" ON pp_delivery.order_id = "order".order_id
    WHERE "order".date_of_order > ((%s)::date - '6 month'::interval)
    ORDER BY pp_delivery.order_id;''',
    # выбираем товары, цена которых больше опред. суммы
    5: '''SELECT clothes.name, b.name, l.name 
    FROM testgen.public.clothes
    INNER JOIN brand b on clothes.brand_id = b.brand_id
    INNER JOIN lifestyle l on clothes.lifestyle_id = l.lifestyle_id
    WHERE clothes.price > (%s);''',
    # товары с определенным описанием
    6: '''SELECT clothes.name, b.name, l.name
    FROM testgen.public.clothes
    INNER JOIN brand b on clothes.brand_id = b.brand_id
    INNER JOIN lifestyle l on clothes.lifestyle_id = l.lifestyle_id
    INNER JOIN collection on clothes.collection_id = collection.collection_id
    WHERE clothes.description = (%s);'''
}

queries_prep = {
    1: "EXECUTE query1 (%s);",
    2: "EXECUTE query2 (%s);",
    3: "EXECUTE query3 (%s);",
    4: "EXECUTE query4 (%s);",
    5: "EXECUTE query5 (%s);",
    6: "EXECUTE query6 (%s);"
}


def start(arguments):
    print("\r\r" + str(arguments))
    # 1 - запросы в секунду, 0 - потоки
    mode = arguments.mode

    del_indexes()

    # минимальное кол-во потоков (мод 0)
    global threads_min
    threads_min = arguments.min_threads

    # максимальное кол-во потоков (мод 0)
    global threads_max
    threads_max = arguments.max_threads

    # кол-во запросов в секунду для потоков (мод 0)
    global const_queries
    const_queries = arguments.const_queries

    # константное кол-во потоков (мод 1)
    global const_threads
    const_threads = arguments.const_threads

    # минимальное кол-во запросов в сек (мод 1)
    global queries_min
    queries_min = arguments.min_queries

    # максимальное кол-во запросов в сек (мод 1)
    global queries_max
    queries_max = arguments.max_queries

    # количество секунд (мод 1)
    global seconds
    seconds = arguments.seconds

    if mode:
        plot_answer_queries()
    else:
        plot_answer_threads()

    del_indexes()


def optimize():
    ind_con = psycopg2.connect(dbname=config.get("postgres", "dbname"),
                               user=config.get("postgres", "user"),
                               password=config.get("postgres", "password"))
    ind_cur = ind_con.cursor()
    ind_cur.execute("CREATE INDEX IF NOT EXISTS i1 ON customer(firstname);")
    ind_cur.execute("CREATE INDEX IF NOT EXISTS i2 ON \"order\"(date_of_order);")
    ind_cur.execute("CREATE INDEX IF NOT EXISTS i3 ON loyalty_card(points);")
    ind_cur.execute("CREATE INDEX IF NOT EXISTS i4 ON \"order\"(date_of_order);")
    ind_cur.execute("CREATE INDEX IF NOT EXISTS i5 ON clothes(price);")
    ind_cur.execute("CREATE INDEX IF NOT EXISTS i6 ON clothes(description);")
    ind_con.commit()
    ind_con.close()


def del_indexes():
    ind_con = psycopg2.connect(dbname=config.get("postgres", "dbname"),
                               user=config.get("postgres", "user"),
                               password=config.get("postgres", "password"))
    ind_cur = ind_con.cursor()
    ind_cur.execute("DROP INDEX IF EXISTS i1;")
    ind_cur.execute("DROP INDEX IF EXISTS i2;")
    ind_cur.execute("DROP INDEX IF EXISTS i3;")
    ind_cur.execute("DROP INDEX IF EXISTS i4;")
    ind_cur.execute("DROP INDEX IF EXISTS i5;")
    ind_cur.execute("DROP INDEX IF EXISTS i6;")
    ind_con.commit()
    ind_con.close()


def prepare_queries(thread_cursor):
    thread_cursor.execute(
        '''PREPARE query1 (varchar(50)) AS SELECT loyalty_card.customer_id, customer.firstname, customer.lastname, 
        customer.birth_date, loyalty_card.points,
        employee.employee_id, employee.firstname, employee.lastname, loyalty_card.last_modified FROM loyalty_card
        JOIN customer ON customer.customer_id = loyalty_card.customer_id
        JOIN employee ON employee.employee_id = loyalty_card.employee_id
        WHERE customer.firstname = $1 
        ORDER BY loyalty_card.customer_id, loyalty_card.last_modified DESC;''')
    thread_cursor.execute(
        '''PREPARE query2 (date) AS SELECT currier_delivery.order_id, customer_address.city, currier_list.name, 
        \"order\".date_of_order FROM currier_delivery 
        JOIN customer_address ON currier_delivery.customer_address_id = customer_address.customer_address_id 
        JOIN currier_list ON currier_delivery.currier_service_id = currier_list.id
        JOIN \"order\" ON currier_delivery.order_id = \"order\".order_id
        WHERE customer_address.city = 'Санкт-Петербург' AND \"order\".date_of_order = $1
        ORDER BY currier_delivery.order_id;''')
    thread_cursor.execute(
        '''PREPARE query3 (int) AS SELECT loyalty_card.customer_id, customer.firstname, customer.lastname, 
        customer.gender, loyalty_card.points, 
        \"subscription\".sms, loyalty_card.last_modified FROM loyalty_card 
        JOIN customer ON customer.customer_id = loyalty_card.customer_id 
        JOIN \"subscription\" on \"subscription\".loyalty_card_id = loyalty_card.loyalty_card_id 
        WHERE loyalty_card.points > $1 AND customer.gender = 'Female' AND \"subscription\".sms = true 
        ORDER BY loyalty_card.customer_id, loyalty_card.last_modified DESC;''')
    thread_cursor.execute(
        '''PREPARE query4 (date) AS SELECT pp_delivery.order_id, pp_list.address, currier_list.name, 
        \"order\".date_of_order FROM pp_delivery 
        JOIN pp_list ON pp_delivery.pp_id = pp_list.pp_id 
        JOIN currier_list ON pp_delivery.currier_service_id = currier_list.id 
        JOIN \"order\" ON pp_delivery.order_id = \"order\".order_id 
        WHERE \"order\".date_of_order > ($1::date - '6 month'::interval) 
        ORDER BY pp_delivery.order_id;''')
    thread_cursor.execute(
        '''PREPARE query5 (int) AS SELECT clothes.name, b.name, l.name FROM testgen.public.clothes 
        INNER JOIN brand b on clothes.brand_id = b.brand_id 
        INNER JOIN lifestyle l on clothes.lifestyle_id = l.lifestyle_id 
        WHERE clothes.price > $1;''')
    thread_cursor.execute(
        '''PREPARE query6 (varchar(50)) AS SELECT clothes.name, b.name, l.name 
        FROM testgen.public.clothes 
        INNER JOIN brand b on clothes.brand_id = b.brand_id 
        INNER JOIN lifestyle l on clothes.lifestyle_id = l.lifestyle_id 
        INNER JOIN collection on clothes.collection_id = collection.collection_id 
        WHERE clothes.description = $1;''')


def rnd_query(thread_cursor):
    global prepare

    query_number = random.randint(1, len(queries))
    if query_number == 1:
        query_args = random.choice(names)[0]
    elif query_number == 2:
        query_args = random.choice(dates)
    elif query_number == 3:
        query_args = random.randint(19500, 19999)
    elif query_number == 4:
        query_args = random.choice(dates)
    elif query_number == 5:
        query_args = random.randint(4600, 4900)
    elif query_number == 6:
        query_args = random.choice(descriptions)[0]
    else:
        return

    if prepare:
        thread_cursor.execute("EXPLAIN ANALYSE " + queries_prep[query_number], [query_args])
    else:
        thread_cursor.execute("EXPLAIN ANALYSE " + queries[query_number], [query_args])

    query_result = thread_cursor.fetchall()
    exec_time = float(query_result[-1][0].split()[2]) + float(query_result[-2][0].split()[2])

    return exec_time


def test_with_queries(x, y):
    for thread in range(const_threads):
        new_thread = ConstantQueryThread(queries_min, queries_max, seconds)
        new_thread.start()
        threads.append(new_thread)

    for t in threads:
        t.join()

    threads.clear()

    print('RESULTS', results)

    for second in range(seconds):
        queries_sum = 0
        threads_sum = 0
        avg_time_sum = 0
        for element in results:
            if element[0] == second:
                queries_sum += element[1]
                threads_sum += 1
                avg_time_sum += element[2]

        if len(x) == 0 or queries_sum > x[-1]:
            x.append(queries_sum)
            y.append(avg_time_sum / threads_sum)

    results.clear()

    print('x:', x)
    print('y:', y)


def test_with_threads(x, y):
    for step in range(threads_min, threads_max + 1):
        for thread in range(step):
            new_thread = DynamicQueryThread(const_queries)
            new_thread.start()
            threads.append(new_thread)

        for t in threads:
            t.join()

        threads.clear()

        print('RESULTS', results)

        x.append(len(results))
        y.append(sum(results) / len(results))

        results.clear()

    print('x:', x)
    print('y:', y)


def plot_answer_queries():
    global prepare

    del_indexes()
    x1 = []
    y1 = []
    test_with_queries(x1, y1)

    optimize()
    x2 = []
    y2 = []
    test_with_queries(x2, y2)

    prepare = True
    x3 = []
    y3 = []
    test_with_queries(x3, y3)

    fig, ax = plt.subplots()
    ax.plot(x1, y1, label='Без оптимизации')
    ax.plot(x2, y2, label='С индексами')
    ax.plot(x3, y3, label='Индексы и prepare')
    ax.grid(which='major', linewidth=0.5, color='k')
    ax.legend()
    plt.xlabel('Запросы в секунду')
    plt.ylabel('Ср. время ответа на один запрос, мс')
    plt.title(f'''Зависимость времени ответа от кол-ва запросов в сек
    Кол-во потоков: {const_threads}''')
    plt.show()


def plot_answer_threads():
    global prepare

    del_indexes()
    x1 = []
    y1 = []
    test_with_threads(x1, y1)

    optimize()
    x2 = []
    y2 = []
    test_with_threads(x2, y2)

    prepare = True
    x3 = []
    y3 = []
    test_with_threads(x3, y3)

    fig, ax = plt.subplots()
    ax.plot(x1, y1, label='Без оптимизации')
    ax.plot(x2, y2, label='С индексами')
    ax.plot(x3, y3, label='Индексы и prepare')
    ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
    ax.minorticks_on()
    ax.grid(which='major', linewidth=0.5, color='k')
    ax.legend()
    plt.xlabel('Кол-во потоков')
    plt.ylabel('Ср. время ответа на один запрос, мс')
    plt.title('Зависимость времени ответа от кол-ва потоков')
    plt.show()


class ConstantQueryThread(threading.Thread):
    def __init__(self, q_min, q_max, work_seconds):
        super().__init__()
        self.work_seconds = work_seconds
        self.queries_min = q_min
        self.queries_max = q_max
        self.query_con = psycopg2.connect(dbname=config.get("postgres", "dbname"),
                                          user=config.get("postgres", "user"),
                                          password=config.get("postgres", "password"))
        self.query_cur = self.query_con.cursor()

    def run(self):
        global prepare
        if prepare:
            prepare_queries(self.query_cur)
            self.query_con.commit()
        step_length = (self.queries_max - self.queries_min) // (seconds - 1)
        for second, curr_q_num in enumerate(range(self.queries_min, self.queries_max + 1, step_length)):
            thread_results = []
            start_time = time.time()
            for query in range(curr_q_num):
                thread_results.append(rnd_query(self.query_cur))
                if time.time() - start_time >= 1:
                    break

            if time.time() - start_time <= 1:
                time.sleep(1 - (time.time() - start_time))

            queries_amount = len(thread_results)
            avg_time = sum(thread_results) / queries_amount

            results.append((second, queries_amount, avg_time))

        self.query_con.close()


class DynamicQueryThread(threading.Thread):
    def __init__(self, q_amount):
        super().__init__()
        self.queries_amount = q_amount
        self.query_con = psycopg2.connect(dbname=config.get("postgres", "dbname"),
                                          user=config.get("postgres", "user"),
                                          password=config.get("postgres", "password"))
        self.query_cur = self.query_con.cursor()

    def run(self):
        global prepare
        if prepare:
            prepare_queries(self.query_cur)
            self.query_con.commit()
        thread_results = []
        for query in range(self.queries_amount):
            thread_results.append(rnd_query(self.query_cur))

        queries_amount = len(thread_results)
        avg_time = sum(thread_results) / queries_amount

        results.append(avg_time)

        self.query_con.close()


if __name__ == '__main__':
    args = argparse.ArgumentParser()
    args.add_argument('--mode', '-m', default=1, type=int)
    args.add_argument('--min_threads', '-t_min', default=1, type=int)
    args.add_argument('--max_threads', '-t_max', default=10, type=int)
    args.add_argument('--const_threads', '-t_const', default=1, type=int)
    args.add_argument('--min_queries', '-q_min', default=10, type=int)
    args.add_argument('--max_queries', '-q_max', default=250, type=int)
    args.add_argument('--const_queries', '-q_const', default=100, type=int)
    args.add_argument('--seconds', '-s', default=20, type=int)

    start_args = args.parse_args()

    start(start_args)
