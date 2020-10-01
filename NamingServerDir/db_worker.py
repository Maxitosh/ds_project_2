from pymongo import MongoClient

import logging as log

log.basicConfig(filename="dfs.log", format='%(asctime)s - %(levelname)s - %(message)s', level=log.DEBUG)
client = MongoClient("mongodb://root:1234@mongodb:27017/?authSource=DFS")


def is_db_exists(db_name):
    db_list = client.list_database_names()
    if db_name in db_list:
        print("[DB] Database {} exists".format(db_name))
        log.info("[DB] Database {} exists".format(db_name))
        return True
    else:
        print("[DB] Database {} does not exist".format(db_name))
        log.info("[DB] Database {} does not exist".format(db_name))
        return False


def is_collection_exists(db_name, collection_name):
    if is_db_exists(db_name):
        collection_list = client[db_name].list_collection_names()
        if collection_name in collection_list:
            print("[DB] Collection {} exists".format(collection_name))
            log.info("[DB] Collection {} exists".format(collection_name))
            return True
        else:
            print("[DB] Collection {} does not exist".format(collection_name))
            log.info("[DB] Collection {} does not exist".format(collection_name))
            return False
    else:
        print("[DB] Database {} does not exist".format(db_name))
        log.info("[DB] Database {} does not exist".format(db_name))
        return False


def init_db(db_name, collections):
    if not is_db_exists(db_name):
        db = client[db_name]
        blank = {"blank": "blank"}
        for col in collections:
            db[col].insert_one(blank)
            print("[DB] Database {} with collection {} created".format(db_name, col))
            log.info("[DB] Database {} with collection {} created".format(db_name, col))
    else:
        print("[DB] Database {0} already exists!".format(db_name))
        log.info("[DB] Database {0} already exists!".format(db_name))


def drop_db(db_name):
    if is_db_exists(db_name):
        client.drop_database(db_name)
        print("[DB] Database {0} dropped".format(db_name))
        log.info("[DB] Database {0} dropped".format(db_name))


def drop_collection(db_name, collection_name):
    if is_collection_exists(db_name, collection_name):
        client[db_name].drop_collection(collection_name)
        print("[DB] Collection {0} dropped".format(db_name))
        log.info("[DB] Collection {0} dropped".format(db_name))


def insert_item(db_name, collection_name, file_data):
    if is_db_exists(db_name):
        selected_db = client[db_name]
        if is_collection_exists(db_name, collection_name):
            collection = selected_db[collection_name]
            collection.insert_one(file_data)
            print("Inserted file {}, in collection {}".format(file_data, collection_name))
        else:
            print("Collection {0} for DB {1} does not exist!".format(collection_name, db_name))
    else:
        print("Database does not exist!")


# def update_item(shop_name, collection_name, query, new_product_data):
#     if is_collection_exists(shop_name, collection_name):
#         client[shop_name][collection_name].update_one(query, {"$set": new_product_data})
#     else:
#         print("DB or Collection does not exist!")


# def is_item_exists(shop_name, collection_name, query):
#     if is_collection_exists(shop_name, collection_name):
#         item = 0
#         item = client[shop_name][collection_name].find(query)
#         if item.count():
#             return True
#         else:
#             return False


# def get_distinct_items(shop_name, collection_name, field):
#     if is_collection_exists(shop_name, collection_name):
#         return client[shop_name][collection_name].distinct(field)
#     else:
#         print("DB or Collection does not exist!")


def get_items(db_name, collection_name):
    return_items = {}
    if is_collection_exists(db_name, collection_name):
        items = client[db_name][collection_name].find()
        return_items[collection_name] = items

    return return_items


def get_all_items(db_name):
    return_items = {}
    collections = client[db_name].list_collection_names()
    for col in collections:
        items = client[db_name][col].find()
        arr_items = []
        for item in items:
            arr_items.append(item)
        return_items[col] = arr_items

    print("[DB] {}".format(return_items))
    log.info("[DB] {}".format(return_items))
    return return_items


# def get_item(shop_name, collection_name, query):
#     if is_collection_exists(shop_name, collection_name):
#         return client[shop_name][collection_name].find(query)
#     else:
#         print("DB or Collection does not exist!")
def print_dbs():
    db_list = client.list_database_names()
    print(db_list)
