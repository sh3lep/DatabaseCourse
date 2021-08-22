import telebot
from telebot import types
import logging
import configparser
import psycopg2
import re
import database

logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)  # Outputs debug messages to console.

config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

API_TOKEN = config.get("bot", "API_TOKEN")  # @dbtg_testbot
bot = telebot.TeleBot(API_TOKEN)
bot.skip_pending = True

connection = psycopg2.connect(
    dbname=config.get("postgres", "dbname"),
    user=config.get("postgres", "user"),
    password=config.get("postgres", "password"))
cursor = connection.cursor()
connection.autocommit = True

global br
global name
global desc
global price
global lifestyle
global collection
global season

global brands
cursor.execute('SELECT name FROM brand ORDER BY name;')
brands_t = cursor.fetchall()
brands = list(sum(brands_t, ()))
brands = [x.lower() for x in brands]
print(brands)

global lifestyles
cursor.execute('SELECT name FROM lifestyle ORDER BY name;')
lifestyle_t = cursor.fetchall()
lifestyles = list(sum(lifestyle_t, ()))
lifestyles = [x.lower() for x in lifestyles]

global collections
cursor.execute('SELECT name FROM collection ORDER BY name;')
collections_t = cursor.fetchall()
collections = list(sum(collections_t, ()))
collections = [x.lower() for x in collections]

global seasons
cursor.execute('SELECT name FROM seasons ORDER BY name;')
seasons_t = cursor.fetchall()
seasons = list(sum(seasons_t, ()))
seasons = [x.lower() for x in seasons]

global tg_admins
cursor.execute('SELECT telegram FROM employee ORDER BY telegram;')
tg_admins_t = cursor.fetchall()
tg_admins_temp = list(sum(tg_admins_t, ()))
# tg_admins = [value for value in tg_admins if value != [None]]
tg_admins = list(filter(None, tg_admins_temp))
tg_admins = [x.lower() for x in tg_admins]
print(tg_admins)

global product_to_list
global prod_list_add
global list_name

# cursor.execute("SELECT employee_id FROM employee WHERE telegram = %(tg)s", {"tg": chat.username})
# # global current_emp_id
# global current_emp_id
# current_emp_id = cursor.fetchall()
# current_emp_id = str(current_emp_id[0]).replace('(', '').replace(')', '').replace(',', '')
# print(current_emp_id)
#
# global product_lists
# cursor.execute('SELECT name FROM emp_shoplist WHERE emp_shoplist.employee_id=%(id)s ORDER BY name;', {"id": current_emp_id})
# product_lists_t = cursor.fetchall()
# product_lists = list(sum(product_lists_t, ()))
# product_lists = [x.lower() for x in product_lists]

mark = u'\U00002705'
pencil = u'\U0000270F'
cross_mark = u'\U0000274C'
error = u'\U0000203C'
question = u'\U00002753'
plusik = u'\U00002795'

has_special = re.compile("|".join(map(re.escape, ".,:;!_*-+()/#¤%&)"))).search

# ----------------------------------------------------

# выбираем товары по бренду
query_1 = "SELECT clothes.clothes_id, clothes.name, brand.name, clothes.price, clothes.in_stock  " \
          "FROM clothes " \
          "JOIN brand ON brand.brand_id = clothes.brand_id " \
          "WHERE brand.name ILIKE %(brand)s ORDER BY clothes.clothes_id;"

# выбираем товары по сезону
query_2 = "SELECT clothes.clothes_id, clothes.name, seasons.name, clothes.price, clothes.in_stock " \
          "FROM clothes " \
          "JOIN seasons ON seasons.season_id = clothes.season_id " \
          "WHERE seasons.name ILIKE %(season)s ORDER BY clothes.clothes_id;"

# выбираем товары по коллекции
query_3 = "SELECT clothes.clothes_id, clothes.name, collection.name, clothes.price, clothes.in_stock " \
          "FROM clothes " \
          "JOIN collection ON collection.collection_id = clothes.collection_id " \
          "WHERE collection.name ILIKE %(collection)s ORDER BY clothes.clothes_id;"

# выбираем товары по стилю
query_4 = "SELECT clothes.clothes_id, clothes.name, lifestyle.name, clothes.price, clothes.in_stock " \
          "FROM clothes " \
          "JOIN lifestyle ON lifestyle.lifestyle_id = clothes.lifestyle_id " \
          "WHERE lifestyle.name ILIKE %(lifestyle)s ORDER BY clothes.clothes_id;"

# выбираем конкретный товар по его идентификатору
query_5 = "SELECT clothes.clothes_id, clothes.name, brand.name, seasons.name, collection.name, lifestyle.name, " \
          "clothes.price, clothes.in_stock  " \
          "FROM clothes " \
          "JOIN brand ON brand.brand_id = clothes.brand_id " \
          "JOIN seasons ON seasons.season_id = clothes.season_id " \
          "JOIN collection ON collection.collection_id = clothes.collection_id " \
          "JOIN lifestyle ON lifestyle.lifestyle_id = clothes.lifestyle_id " \
          "WHERE clothes.clothes_id = %(product)s ORDER BY clothes.clothes_id;"

# меняем статус наличия товара
query_6 = "UPDATE clothes SET in_stock = %(status)s WHERE clothes_id = %(product)s;"

# проверка наличия товара
query_7 = "SELECT in_stock FROM testgen.public.clothes WHERE clothes_id = %(product)s"

# проверяем, существует ли товар с определенным идентификатором
query_8 = "SELECT COUNT(*) FROM testgen.public.clothes WHERE clothes_id = %(product)s"

# поиск по названию вещи, названию бренда и описанию
query_9 = "SELECT clothes.clothes_id, clothes.name, clothes.description, brand.name, clothes.price, clothes.in_stock " \
          "FROM clothes JOIN brand ON brand.brand_id = clothes.brand_id " \
          "WHERE (clothes.name ILIKE %(search)s) or (clothes.description ILIKE %(search)s) " \
          "or (brand.name ILIKE %(search)s) ORDER BY clothes.clothes_id"

# выбираем последний добавленный товар
query_10 = "SELECT clothes.clothes_id, clothes.name, brand.name, seasons.name, collection.name, lifestyle.name, " \
           "clothes.price, clothes.in_stock  " \
           "FROM clothes " \
           "JOIN brand ON brand.brand_id = clothes.brand_id " \
           "JOIN seasons ON seasons.season_id = clothes.season_id " \
           "JOIN collection ON collection.collection_id = clothes.collection_id " \
           "JOIN lifestyle ON lifestyle.lifestyle_id = clothes.lifestyle_id " \
           "ORDER BY clothes_id DESC LIMIT 1;"

# добавляем товар в таблицу emp_shoplist_item
query_11 = "INSERT INTO emp_shoplist_item VALUES (default, %(clothes)s, %(shoplist)s)"

# удаляем товар из таблицы emp_shoplist_item
query_12 = "DELETE FROM emp_shoplist_item WHERE (clothes_id = %(clothes)s) AND (emp_shoplist_id = %(shoplist)s)"

# удаляем записи из emp_shoplist, где emp_shoplist_id cоответствует опред. идентификатору
query_13 = "DELETE FROM emp_shoplist WHERE (id = %(shoplist)s)"

# подсчет кол-ва товаров в определенном списке
query_14 = "SELECT COUNT(*) FROM testgen.public.emp_shoplist_item WHERE clothes_id = %(product)s"

# query_15 = "SELECT * FROM testgen.public.emp_shoplist_item WHERE emp_shoplist_id = %(shoplist)s"

# выводит товары из определенного списка
query_15 = "SELECT clothes.clothes_id, clothes.name, brand.name, seasons.name, collection.name, lifestyle.name, " \
           "clothes.price, clothes.in_stock " \
           "FROM clothes " \
           "JOIN emp_shoplist_item ON emp_shoplist_item.clothes_id = clothes.clothes_id " \
           "JOIN brand ON brand.brand_id = clothes.brand_id " \
           "JOIN seasons ON seasons.season_id = clothes.season_id " \
           "JOIN collection ON collection.collection_id = clothes.collection_id " \
           "JOIN lifestyle ON lifestyle.lifestyle_id = clothes.lifestyle_id " \
           "WHERE emp_shoplist_id = %(shoplist)s " \
           "ORDER BY clothes_id; "


# ----------------------------------------------------


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    if message.text == '/start':
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        button1 = types.KeyboardButton("Каталог")
        button2 = types.KeyboardButton("Изменить товар")
        button3 = types.KeyboardButton("Поиск")
        button4 = types.KeyboardButton("Списки")

        markup.add(button1, button2, button3, button4)

        bot.send_message(message.chat.id,
                         "Выберите пункт из меню.\n"
                         "Если возникли проблемы, пишите /help".format(message.from_user, bot.get_me()),
                         reply_markup=markup)
    elif message.text == '/help':
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(
            telebot.types.InlineKeyboardButton(
                'Связаться с разработчиком', url='telegram.me/sh3lep'
            )
        )
        bot.send_message(message.chat.id, 'По любым техническим вопросам.', reply_markup=keyboard)


@bot.message_handler(regexp="(Каталог)|(Изменить товар)|(Поиск)|(Списки)")
def path_step(message):
    if message.chat.username in tg_admins:
        cursor.execute("SELECT employee_id FROM employee WHERE telegram = %(tg)s", {"tg": message.chat.username})
        # global current_emp_id
        global current_emp_id
        current_emp_id = cursor.fetchall()
        current_emp_id = str(current_emp_id[0]).replace('(', '').replace(')', '').replace(',', '')
        print(current_emp_id)

        global product_lists
        cursor.execute('SELECT name FROM emp_shoplist WHERE emp_shoplist.employee_id=%(id)s ORDER BY name;',
                       {"id": current_emp_id})
        product_lists_t = cursor.fetchall()
        product_lists = list(sum(product_lists_t, ()))
        product_lists = [x.lower() for x in product_lists]

    if message.text == 'Каталог':
        keyboard_for_catalog = types.InlineKeyboardMarkup(row_width=1)

        key_brand = types.InlineKeyboardButton(text="По бренду", callback_data='1')
        key_collection = types.InlineKeyboardButton(text="По коллекции", callback_data='2')
        key_style = types.InlineKeyboardButton(text="По стилю", callback_data='3')
        key_season = types.InlineKeyboardButton(text="По сезону", callback_data='4')

        keyboard_for_catalog.add(key_brand, key_collection, key_style, key_season)

        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        bot.send_message(message.chat.id, "Выберите метод сортировки каталога.", reply_markup=keyboard_for_catalog)

    if message.text == 'Изменить товар':
        print(message.chat.username)
        if message.chat.username not in tg_admins:
            bot.send_message(message.chat.id, "У вас нет прав на эти функции. Обратитесь к администратору.")
            return

        keyboard_for_catalog = types.InlineKeyboardMarkup(row_width=1)

        key_add = types.InlineKeyboardButton(text=mark + " Добавить товар в каталог", callback_data='5')
        key_delete = types.InlineKeyboardButton(text=pencil + " Изменить наличие", callback_data='6')

        keyboard_for_catalog.add(key_add, key_delete)

        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        bot.send_message(message.chat.id, "Выберите, что сделать с товаром.", reply_markup=keyboard_for_catalog)

    if message.text == 'Поиск':
        msg = bot.send_message(message.chat.id, 'Для поиска введите название вещи, бренда или описание.')
        bot.register_next_step_handler(msg, search_clothes)

    if message.text == 'Списки':
        print(message.chat.username)
        if message.chat.username not in tg_admins:
            bot.send_message(message.chat.id, "У вас нет прав на эти функции. Обратитесь к администратору.")
            return

        keyboard_for_lists = types.InlineKeyboardMarkup(row_width=1)
        # Добавить товар в список
        key_show = types.InlineKeyboardButton(text=mark + " Просмотреть cписки", callback_data='15')
        key_add = types.InlineKeyboardButton(text=plusik + " Добавить списки", callback_data='17')
        key_edit = types.InlineKeyboardButton(text=pencil + " Изменить списки", callback_data='8')

        keyboard_for_lists.add(key_show, key_add, key_edit)

        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        bot.send_message(message.chat.id, "Выберите действие со списком.", reply_markup=keyboard_for_lists)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    bot.send_message(message.chat.id,
                     "Вы ввели некорректные данные.\n\n"
                     "Выберите пункт из меню.\n"
                     "Если возникли проблемы, пишите /help".format(message.from_user, bot.get_me()))
    return


def search_clothes(message):
    if message.text == 'Каталог' or message.text == 'Изменить товар':
        path_step(message)
        return
    elif message.text == '/start' or message.text == '/help':
        send_welcome(message)
        return

    chat_id = message.chat.id
    search = message.text
    if search.isdigit() or bool(has_special(search)):
        msg = bot.send_message(chat_id, error + ' Название вещи, бренда или описание не может состоять только из цифр '
                                                'или содержать специальные '
                                                'символы. Попробуйте еще раз.')
        bot.register_next_step_handler(msg, search_clothes)
        return

    search_final = '%' + search + '%'
    print(search_final)

    cursor.execute(query_9, {"search": search_final})
    clothes_t = cursor.fetchall()

    clothes_string = ''
    for i in range(len(clothes_t)):
        clothes_string = clothes_string + str(clothes_t[i]) \
            .replace('(', '').replace(')', '').replace('\'', '') + "\n"

    # bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    bot.send_message(message.chat.id, "Позиции по запросу " + search + ":")
    if len(clothes_string) > 4096:
        for x in range(0, len(clothes_string), 4096):
            bot.send_message(message.chat.id, clothes_string[x:x + 4096])
    elif len(clothes_string) == 0:
        bot.send_message(message.chat.id, 'По вашему запросу ничего не найдено.')
        return
    else:
        bot.send_message(message.chat.id, clothes_string)


def add_clothes_brand(message):
    if message.text == 'Каталог' or message.text == 'Изменить товар' or message.text == 'Поиск' \
            or message.text == 'Списки':
        path_step(message)
        return
    elif message.text == '/start' or message.text == '/help':
        send_welcome(message)
        return

    global br
    br = message.text
    chat_id = message.chat.id
    if br.lower() not in brands:
        msg = bot.send_message(chat_id, error + ' Неверно задан бренд либо его не существует. Попробуйте еще раз.')
        bot.register_next_step_handler(msg, add_clothes_brand)
        return
    msg = bot.send_message(chat_id, 'Введите название вещи бренда ' + br + '.')
    bot.register_next_step_handler(msg, add_clothes_name)


def add_clothes_name(message):
    if message.text == 'Каталог' or message.text == 'Изменить товар' or message.text == 'Поиск' \
            or message.text == 'Списки':
        path_step(message)
        return
    elif message.text == '/start' or message.text == '/help':
        send_welcome(message)
        return

    chat_id = message.chat.id
    global name
    name = message.text
    if name.isdigit() or bool(has_special(name)):
        msg = bot.send_message(chat_id, error + ' Название не может состоять только из цифр или содержать специальные '
                                                'символы. Попробуйте еще раз.')
        bot.register_next_step_handler(msg, add_clothes_name)
        return
    msg = bot.send_message(chat_id, 'Введите описание вещи ' + name + '.')
    bot.register_next_step_handler(msg, add_clothes_desc)


def add_clothes_desc(message):
    if message.text == 'Каталог' or message.text == 'Изменить товар' or message.text == 'Поиск' \
            or message.text == 'Списки':
        path_step(message)
        return
    elif message.text == '/start' or message.text == '/help':
        send_welcome(message)
        return

    chat_id = message.chat.id
    global desc
    desc = message.text
    if desc.isdigit() or bool(has_special(desc)):
        msg = bot.send_message(chat_id, error + ' Описание не может состоять только из цифр или содержать специальные '
                                                'символы. Попробуйте еще раз.')
        bot.register_next_step_handler(msg, add_clothes_desc)
        return
    msg = bot.send_message(chat_id, 'Введите цену вещи.')
    bot.register_next_step_handler(msg, add_clothes_price)


def add_clothes_price(message):
    if message.text == 'Каталог' or message.text == 'Изменить товар' or message.text == 'Поиск' \
            or message.text == 'Списки':
        path_step(message)
        return
    elif message.text == '/start' or message.text == '/help':
        send_welcome(message)
        return

    chat_id = message.chat.id
    global price
    price = message.text
    if not price.isdigit() or int(price) > 5000:
        msg = bot.send_message(chat_id, error + ' Неверно задана цена, она не может превышать 5000 р. '
                                                'Попробуйте еще раз.')
        bot.register_next_step_handler(msg, add_clothes_price)
        return
    msg = bot.send_message(chat_id, 'Введите стиль вещи.')
    bot.register_next_step_handler(msg, add_clothes_ls)


def add_clothes_ls(message):
    if message.text == 'Каталог' or message.text == 'Изменить товар' or message.text == 'Поиск' \
            or message.text == 'Списки':
        path_step(message)
        return
    elif message.text == '/start' or message.text == '/help':
        send_welcome(message)
        return

    chat_id = message.chat.id
    global lifestyle
    lifestyle = message.text
    if lifestyle.lower() not in lifestyles:
        msg = bot.send_message(chat_id, error + ' Неверно задан стиль. Попробуйте еще раз.\nДоступные стили:\n'
                               + str(lifestyles)
                               .replace('(', '').replace(')', '').replace('\'', '').replace(']', '').replace('[', ''))
        bot.register_next_step_handler(msg, add_clothes_ls)
        return
    msg = bot.send_message(chat_id, 'Введите коллекцию вещи.')
    bot.register_next_step_handler(msg, add_clothes_col)


def add_clothes_col(message):
    if message.text == 'Каталог' or message.text == 'Изменить товар' or message.text == 'Поиск' \
            or message.text == 'Списки':
        path_step(message)
        return
    elif message.text == '/start' or message.text == '/help':
        send_welcome(message)
        return

    chat_id = message.chat.id
    global collection
    collection = message.text
    if collection.lower() not in collections:
        msg = bot.send_message(chat_id, error + ' Неверно задана коллекция. Попробуйте еще раз.\nДоступные коллекции:\n'
                               + str(collections)
                               .replace('(', '').replace(')', '').replace('\'', '').replace(']', '').replace('[', ''))
        bot.register_next_step_handler(msg, add_clothes_col)
        return
    msg = bot.send_message(chat_id, 'Введите сезон вещи.')
    bot.register_next_step_handler(msg, add_clothes_season)


def add_clothes_season(message):
    if message.text == 'Каталог' or message.text == 'Изменить товар' or message.text == 'Поиск' \
            or message.text == 'Списки':
        path_step(message)
        return
    elif message.text == '/start' or message.text == '/help':
        send_welcome(message)
        return

    chat_id = message.chat.id
    global season
    season = message.text
    if season.lower() not in seasons:
        msg = bot.send_message(chat_id, error + ' Неверно задан сезон. Попробуйте еще раз.\nДоступные сезона:\n'
                               + str(seasons)
                               .replace('(', '').replace(')', '').replace('\'', '').replace(']', '').replace('[', ''))
        bot.register_next_step_handler(msg, add_clothes_season)
        return
    bot.send_message(chat_id, 'Все введено корректно.')
    database.addClothes(br, name, desc, price, lifestyle, collection, season)
    # bot.send_message(chat_id, 'Товар добавлен.')

    cursor.execute(query_10)
    product_new = cursor.fetchall()
    bot.send_message(chat_id, mark + " Товар добавлен:\n\n"
                     + str(product_new)
                     .replace('(', '')
                     .replace(')', '')
                     .replace('\'', '')
                     .replace('[', '')
                     .replace(']', ''))
    return


def change_product_status(message):
    if message.text == 'Каталог' or message.text == 'Изменить товар' or message.text == 'Поиск' \
            or message.text == 'Списки':
        path_step(message)
        return
    elif message.text == '/start' or message.text == '/help':
        send_welcome(message)
        return

    chat_id = message.chat.id
    product = message.text

    if not product.isdigit():
        msg = bot.send_message(chat_id,
                               error + ' Неверно задан ID товара. ID должен быть целым числом. Попробуйте еще раз.')
        bot.register_next_step_handler(msg, change_product_status)
        return

    cursor.execute(query_8, {"product": product})
    product_e = cursor.fetchall()
    product_exists = str(product_e[0]).replace('(', '').replace(')', '').replace(',', '')
    if not product_exists == '1':
        msg = bot.send_message(chat_id, error + ' Товара с таким ID '
                                                'не существует. Попробуйте ввести другой ID.')
        bot.register_next_step_handler(msg, change_product_status)
        return

    cursor.execute(query_5, {"product": product})
    product_t = cursor.fetchall()

    cursor.execute(query_7, {"product": product})
    product_s = cursor.fetchall()
    product_status = str(product_s[0]).replace('(', '').replace(')', '').replace(',', '')
    if product_status == 'True':
        add_msg = 'c \'В наличии\' на \'Не в наличии\'?'
    else:
        add_msg = 'c \'Не в наличии\' на \'В наличии\'?'

    product_string = ''
    for i in range(len(product_t)):
        product_string = product_string + str(product_t[i]) \
            .replace('(', '').replace(')', '').replace('\'', '') + "\n"

    keyboard = types.InlineKeyboardMarkup(row_width=2)
    yes = types.InlineKeyboardButton(text='Да', callback_data='yes_' + product)
    no = types.InlineKeyboardButton(text='Нет', callback_data='no__' + product)
    keyboard.add(yes, no)
    bot.send_message(chat_id, question + " Вы хотите изменить статус наличия данного товара " + add_msg + "\n\n"
                     + product_string, reply_markup=keyboard)
    return


def add_product_to_list(message):
    if message.text == 'Каталог' or message.text == 'Изменить товар' or message.text == 'Поиск' \
            or message.text == 'Списки':
        path_step(message)
        return
    elif message.text == '/start' or message.text == '/help':
        send_welcome(message)
        return

    chat_id = message.chat.id

    global product_to_list
    product_to_list = message.text

    if not product_to_list.isdigit():
        msg = bot.send_message(chat_id,
                               error + ' Неверно задан ID товара. ID должен быть целым числом. Попробуйте еще раз.')
        bot.register_next_step_handler(msg, add_product_to_list)
        return

    cursor.execute(query_8, {"product": product_to_list})
    product_e = cursor.fetchall()
    product_exists = str(product_e[0]).replace('(', '').replace(')', '').replace(',', '')
    if not product_exists == '1':
        msg = bot.send_message(chat_id, error + ' Товара с таким ID '
                                                'не существует. Попробуйте ввести другой ID.')
        bot.register_next_step_handler(msg, add_product_to_list)
        return
    # msg = bot.send_message(chat_id, "")
    # bot.register_next_step_handler()

    cursor.execute(query_11, {"clothes": product_to_list, "shoplist": prod_list_add})
    bot.send_message(chat_id, 'Товар добавлен.')
    return


def delete_product_from_list(message):
    if message.text == 'Каталог' or message.text == 'Изменить товар' or message.text == 'Поиск' \
            or message.text == 'Списки':
        path_step(message)
        return
    elif message.text == '/start' or message.text == '/help':
        send_welcome(message)
        return

    chat_id = message.chat.id

    global product_to_list
    product_to_list = message.text

    if not product_to_list.isdigit():
        msg = bot.send_message(chat_id,
                               error + ' Неверно задан ID товара. ID должен быть целым числом. Попробуйте еще раз.')
        bot.register_next_step_handler(msg, delete_product_from_list)
        return

    cursor.execute(query_14, {"product": product_to_list})
    product_e = cursor.fetchall()
    product_exists = str(product_e[0]).replace('(', '').replace(')', '').replace(',', '')
    if not product_exists == '1':
        msg = bot.send_message(chat_id, error + ' Товара с таким ID '
                                                'не существует. Попробуйте ввести другой ID.')
        bot.register_next_step_handler(msg, delete_product_from_list)
        return

    cursor.execute(query_12, {"clothes": product_to_list, "shoplist": prod_list_add})
    bot.send_message(chat_id, 'Товар удален.')
    return


def add_list(message):
    if message.text == 'Каталог' or message.text == 'Изменить товар' or message.text == 'Поиск' \
            or message.text == 'Списки':
        path_step(message)
        return
    elif message.text == '/start' or message.text == '/help':
        send_welcome(message)
        return

    chat_id = message.chat.id
    name_for_list = message.text
    if name_for_list.isdigit() or bool(has_special(name_for_list)):
        msg = bot.send_message(chat_id, error + ' Название не может состоять только из цифр или содержать специальные '
                                                'символы. Попробуйте еще раз.')
        bot.register_next_step_handler(msg, add_list)
        return

    # cursor.execute("SELECT employee_id FROM employee WHERE telegram = %(tg)s", {"tg": message.chat.username})
    # global current_emp_id
    # current_emp_id = cursor.fetchall()
    # current_emp_id = str(current_emp_id[0]).replace('(', '').replace(')', '').replace(',', '')
    # print(current_emp_id)

    cursor.execute("INSERT INTO emp_shoplist VALUES (default, %(listname)s, %(id)s)",
                   {"listname": name_for_list, "id": current_emp_id})

    bot.send_message(chat_id, 'Список ' + '\'' + name_for_list + '\'' + ' создан.')

    # msg = bot.send_message(chat_id, 'Введите описание вещи ' + name + '.')
    # bot.register_next_step_handler(msg, add_clothes_desc)
    return


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == '1':
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        for b in brands:
            keyboard.add(types.InlineKeyboardButton(text=b, callback_data=b))

        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(call.message.chat.id, "Выберите бренд.", reply_markup=keyboard)

    if call.data == '2':
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        for col in collections:
            keyboard.add(types.InlineKeyboardButton(text=col, callback_data=col))

        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(call.message.chat.id, "Выберите коллекцию.", reply_markup=keyboard)

    if call.data == '3':
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        for ls in lifestyles:
            keyboard.add(types.InlineKeyboardButton(text=ls, callback_data=ls))

        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(call.message.chat.id, "Выберите стиль.", reply_markup=keyboard)

    if call.data == '4':
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        for s in seasons:
            keyboard.add(types.InlineKeyboardButton(text=s, callback_data=s))

        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(call.message.chat.id, "Выберите сезон.", reply_markup=keyboard)

    if call.data in brands:
        cursor.execute(query_1, {"brand": call.data})
        clothes_t = cursor.fetchall()

        clothes_string = ''
        for i in range(len(clothes_t)):
            clothes_string = clothes_string + str(clothes_t[i]) \
                .replace('(', '').replace(')', '').replace('\'', '') + "\n"

        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(call.message.chat.id, "Позиции по бренду " + call.data + ":")
        if len(clothes_string) > 4096:
            for x in range(0, len(clothes_string), 4096):
                bot.send_message(call.message.chat.id, clothes_string[x:x + 4096])
        elif len(clothes_string) == 0:
            bot.send_message(call.message.chat.id, 'Позиций нет.')
        else:
            bot.send_message(call.message.chat.id, clothes_string)

    if call.data in seasons:
        cursor.execute(query_2, {"season": call.data})
        clothes_t = cursor.fetchall()

        clothes_string = ''
        for i in range(len(clothes_t)):
            clothes_string = clothes_string + str(clothes_t[i]) \
                .replace('(', '').replace(')', '').replace('\'', '') + "\n"

        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(call.message.chat.id, "Позиции по сезону " + call.data + ":")
        if len(clothes_string) > 4096:
            for x in range(0, len(clothes_string), 4096):
                bot.send_message(call.message.chat.id, clothes_string[x:x + 4096])
        elif len(clothes_string) == 0:
            bot.send_message(call.message.chat.id, 'Позиций нет.')
        else:
            bot.send_message(call.message.chat.id, clothes_string)

    if call.data in collections:
        cursor.execute(query_3, {"collection": call.data})
        clothes_t = cursor.fetchall()
        print(clothes_t)

        clothes_string = ''
        for i in range(len(clothes_t)):
            clothes_string = clothes_string + str(clothes_t[i]) \
                .replace('(', '').replace(')', '').replace('\'', '') + "\n"

        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(call.message.chat.id, "Позиции по коллекции " + call.data + ":")
        if len(clothes_string) > 4096:
            for x in range(0, len(clothes_string), 4096):
                bot.send_message(call.message.chat.id, clothes_string[x:x + 4096])
        elif len(clothes_string) == 0:
            bot.send_message(call.message.chat.id, 'Позиций нет.')
        else:
            bot.send_message(call.message.chat.id, clothes_string)

    if call.data in lifestyles:
        cursor.execute(query_4, {"lifestyle": call.data})
        clothes_t = cursor.fetchall()

        clothes_string = ''
        for i in range(len(clothes_t)):
            clothes_string = clothes_string + str(clothes_t[i]) \
                .replace('(', '').replace(')', '').replace('\'', '') + "\n"

        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(call.message.chat.id, "Позиции по стилю " + call.data + ":")
        if len(clothes_string) > 4096:
            for x in range(0, len(clothes_string), 4096):
                bot.send_message(call.message.chat.id, clothes_string[x:x + 4096])
        elif len(clothes_string) == 0:
            bot.send_message(call.message.chat.id, 'Позиций нет.')
        else:
            bot.send_message(call.message.chat.id, clothes_string)

    if call.data == '5':
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=None)
        bot.send_message(call.message.chat.id, 'Выбрано добавление товара в каталог.')
        msg = bot.send_message(call.message.chat.id, 'Какого бренда добавить товар?')
        bot.register_next_step_handler(msg, add_clothes_brand)

    if call.data == '6':
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=None)
        bot.send_message(call.message.chat.id, 'Выбрано изменение товара.')
        msg = bot.send_message(call.message.chat.id, 'Введите ID товара, чтобы изменить статус его наличия.')
        bot.register_next_step_handler(msg, change_product_status)

    if call.data == '8':
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=None)
        bot.send_message(call.message.chat.id, 'Выбрано изменение списков.')
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)

        keyboard = types.InlineKeyboardMarkup(row_width=2)
        print(product_lists)
        for prod_l in product_lists:
            keyboard.add(types.InlineKeyboardButton(text=prod_l, callback_data='9' + prod_l))

        bot.send_message(call.message.chat.id, "Выберите список, который хотите изменить:", reply_markup=keyboard)

    if call.data[0:1] == '9':
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=None)
        global list_name
        list_name = call.data[1:]
        cursor.execute("SELECT id FROM emp_shoplist WHERE name ILIKE %(list)s", {"list": call.data[1:]})
        global prod_list_add
        prod_list_add = cursor.fetchall()
        prod_list_add = str(prod_list_add[0]).replace('(', '').replace(')', '').replace(',', '')
        # prod_list_add = call.data[1:]
        print(prod_list_add)
        bot.send_message(call.message.chat.id, 'Выбрано изменение списка.')
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        key_add = types.InlineKeyboardButton(text='Добавить товар в список', callback_data='11')
        key_del = types.InlineKeyboardButton(text='Удалить товар из списка', callback_data='12')
        # key_add1 = types.InlineKeyboardButton(text='Добавить список', callback_data='13')
        key_del1 = types.InlineKeyboardButton(text='Удалить список', callback_data='14')
        keyboard.add(key_add, key_del, key_del1)
        bot.send_message(call.message.chat.id, 'Выберите действие со списком ' + '\'' + list_name + '\'',
                         reply_markup=keyboard)

    if call.data == '10':
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=None)
        bot.send_message(call.message.chat.id, 'Выбрано удаление товара из списка.')
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)

    if call.data == '11':
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=None)
        msg = bot.send_message(call.message.chat.id, 'Введите ID товара, чтобы добавить его в список ' + '\'' +
                               list_name + '\'.')
        bot.register_next_step_handler(msg, add_product_to_list)

    if call.data == '12':
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=None)
        msg = bot.send_message(call.message.chat.id, 'Введите ID товара, чтобы удалить его из списка ' + '\'' +
                               list_name + '\'.')
        bot.register_next_step_handler(msg, delete_product_from_list)

    if call.data == '14':
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=None)
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        key_yes = types.InlineKeyboardButton(text='Да', callback_data='delete')
        key_no = types.InlineKeyboardButton(text='Нет', callback_data='donotdelete')
        # bot.register_next_step_handler(msg, delete_product_from_list)
        keyboard.add(key_yes, key_no)
        bot.send_message(call.message.chat.id, 'Вы уверены, что хотите удалить список ' + list_name + "?",
                         reply_markup=keyboard)

    if call.data == '15':
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=None)
        bot.send_message(call.message.chat.id, 'Выбран просмотр списков.')
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)

        keyboard = types.InlineKeyboardMarkup(row_width=2)
        print(product_lists)
        for prod_l in product_lists:
            keyboard.add(types.InlineKeyboardButton(text=prod_l, callback_data='16' + prod_l))

        bot.send_message(call.message.chat.id, "Выберите список, который хотите просмотреть:", reply_markup=keyboard)

    if call.data[0:2] == '16':
        list_name = call.data[2:]
        cursor.execute("SELECT id FROM emp_shoplist WHERE name ILIKE %(list)s", {"list": call.data[2:]})
        prod_list_add = cursor.fetchall()
        prod_list_add = str(prod_list_add[0]).replace('(', '').replace(')', '').replace(',', '')
        # prod_list_add = call.data[1:]
        print(prod_list_add)

        cursor.execute(query_15, {"shoplist": prod_list_add})
        clothes_t = cursor.fetchall()

        clothes_string = ''
        for i in range(len(clothes_t)):
            clothes_string = clothes_string + str(clothes_t[i]) \
                .replace('(', '').replace(')', '').replace('\'', '') + "\n"

        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(call.message.chat.id, "Позиции из списка " + '\'' + list_name + '\'' + ":")
        if len(clothes_string) > 4096:
            for x in range(0, len(clothes_string), 4096):
                bot.send_message(call.message.chat.id, clothes_string[x:x + 4096])
        elif len(clothes_string) == 0:
            bot.send_message(call.message.chat.id, 'Список пуст')
        else:
            bot.send_message(call.message.chat.id, clothes_string)

    if call.data == '17':
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=None)
        bot.send_message(call.message.chat.id, 'Выбрано добавление списка.')
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)

        msg = bot.send_message(call.message.chat.id, "Введите название списка, который хотите добавить.")
        bot.register_next_step_handler(msg, add_list)

    if call.data == 'delete':
        cursor.execute(query_13, {"shoplist": prod_list_add})
        bot.send_message(call.message.chat.id, 'Список ' + list_name + " был удален.")
        return

    if call.data == 'donotdelete':
        bot.send_message(call.message.chat.id, 'Отмена удаления списка')
        return

    if call.data[0:4] == 'yes_':
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=None)
        product = call.data[4:]
        print(product)

        cursor.execute(query_7, {"product": product})
        product_s = cursor.fetchall()
        product_status = str(product_s[0]).replace('(', '').replace(')', '').replace(',', '')
        if product_status == 'True':
            cursor.execute(query_6, {"status": False, "product": product})
            add_msg = 'на \'Не в наличии\''
        else:
            cursor.execute(query_6, {"status": True, "product": product})
            add_msg = 'на \'В наличии\''

        cursor.execute(query_5, {"product": product})
        product_new = cursor.fetchall()
        bot.send_message(call.message.chat.id, mark + " Статус товара обновлен " + add_msg + ":\n\n"
                         + str(product_new)
                         .replace('(', '')
                         .replace(')', '')
                         .replace('\'', '')
                         .replace('[', '')
                         .replace(']', ''))
        return

    if call.data[0:4] == 'no__':
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=None)
        bot.send_message(call.message.chat.id, 'Отмена изменения статуса наличия товара.')
        return


bot.polling(none_stop=True, interval=0)
