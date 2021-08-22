import configparser
import psycopg2

config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

connection = psycopg2.connect(
    dbname=config.get("postgres", "dbname"),
    user=config.get("postgres", "user"),
    password=config.get("postgres", "password"))
cursor = connection.cursor()
connection.autocommit = True

query_1 = 'SELECT brand_id FROM brand WHERE name ILIKE %(brand)s'
query_2 = 'SELECT lifestyle_id FROM lifestyle WHERE name ILIKE %(lifestyle)s'
query_3 = 'SELECT collection_id FROM collection WHERE name ILIKE %(collection)s'
query_4 = 'SELECT season_id FROM seasons WHERE name ILIKE %(season)s'


def addClothes(brand, name, description, price, lifestyle, collection, season):
    cursor.execute(query_1, {"brand": brand})
    brand_id = cursor.fetchall()
    cursor.execute(query_2, {"lifestyle": lifestyle})
    lifestyle_id = cursor.fetchall()
    cursor.execute(query_3, {"collection": collection})
    collection_id = cursor.fetchall()
    cursor.execute(query_4, {"season": season})
    season_id = cursor.fetchall()

    cursor.execute('INSERT INTO clothes VALUES (default, {}, \'{}\', \'{}\', \'{}\', {}, {}, {})'
                   .format(brand_id[0][0], name, description, price, lifestyle_id[0][0], collection_id[0][0],
                           season_id[0][0]))

