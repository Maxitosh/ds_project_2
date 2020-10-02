from pymongo import MongoClient

import logging as log

log.basicConfig(filename="db.log", format='[DB] %(asctime)s - %(levelname)s - %(message)s', level=log.DEBUG)
client = MongoClient("mongodb://root:1234@mongodb:27017/?authSource=DFS")


def is_db_exists(db_name):
    db_list = client.list_database_names()
    if db_name in db_list:
        print("Database {} exists".format(db_name))
        log.info("Database {} exists".format(db_name))
        return True
    else:
        print("Database {} does not exist".format(db_name))
        log.error("Database {} does not exist".format(db_name))
        return False


def is_collection_exists(db_name, collection_name):
    if is_db_exists(db_name):
        collection_list = client[db_name].list_collection_names()
        if collection_name in collection_list:
            print("Collection {} exists".format(collection_name))
            log.info("Collection {} exists".format(collection_name))
            return True
        else:
            print("Collection {} does not exist".format(collection_name))
            log.error("Collection {} does not exist".format(collection_name))
            return False
    else:
        print("Database {} does not exist".format(db_name))
        log.error("Database {} does not exist".format(db_name))
        return False


def init_db(db_names, collections):
    for db in db_names:
        if not is_db_exists(db):
            db = client[db]
            blank = {"blank": "blank"}
            for col in collections:
                db[col].insert_one(blank)
                print("Database {} with collection {} created".format(db, col))
                log.info("Database {} with collection {} created".format(db, col))
        else:
            print("Database {0} already exists!".format(db))
            log.error("Database {0} already exists!".format(db))


def init_collection(db_name, collections):
    if is_db_exists(db_name):
        blank = {"blank": "blank"}
        for col in collections:
            client[db_name][col].insert_one(blank)
            print("Collection {} for database {} created".format(col, db_name))
            log.info("Collection {} for database {} created".format(col, db_name))

def drop_db(db_name):
    if is_db_exists(db_name):
        client.drop_database(db_name)
        print("Database {0} dropped".format(db_name))
        log.info("Database {0} dropped".format(db_name))


def drop_collection(db_name, collection_name):
    if is_collection_exists(db_name, collection_name):
        client[db_name].drop_collection(collection_name)
        print("Collection {0} dropped".format(db_name))
        log.info("Collection {0} dropped".format(db_name))


def insert_item(db_name, collection_name, file_data):
    if is_db_exists(db_name):
        selected_db = client[db_name]
        if is_collection_exists(db_name, collection_name):
            collection = selected_db[collection_name]
            collection.insert_one(file_data)
            print("Inserted file {}, in collection {}".format(file_data, collection_name))
            log.info("Inserted file {}, in collection {}".format(file_data, collection_name))
        else:
            print("Collection {0} for DB {1} does not exist!".format(collection_name, db_name))
            log.error("Collection {0} for DB {1} does not exist!".format(collection_name, db_name))
    else:
        print("Database {} does not exist!".format(db_name))
        log.error("Database {} does not exist!".format(db_name))


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


def get_db_snapshot(db_names):
    return_items = {}
    for db_name in db_names:
        return_items[db_name] = {}
        collections = client[db_name].list_collection_names()
        for col in collections:
            items = client[db_name][col].find()
            arr_items = []
            for item in items:
                arr_items.append(item)
            return_items[db_name][col] = arr_items

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
