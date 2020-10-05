from datetime import datetime

from pymongo import MongoClient

import logging as log

log.basicConfig(filename="db.log", format='%(asctime)s - %(levelname)s - [DB] %(message)s', level=log.DEBUG, force=True)
client = MongoClient("mongodb://root:1234@mongodb:27017/?authSource=DFS")

ss_life = {}


def is_db_exists(db_name):
    db_list = client.list_database_names()
    if db_name in db_list:
        return True
    else:
        return False


def is_collection_exists(db_name, collection_name):
    if is_db_exists(db_name):
        collection_list = client[db_name].list_collection_names()
        if collection_name in collection_list:
            return True
        else:
            return False
    else:
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


def insert_item(db_name, collection_name, item_data):
    if is_db_exists(db_name):
        selected_db = client[db_name]
        if is_collection_exists(db_name, collection_name):
            collection = selected_db[collection_name]
            collection.insert_one(item_data)
            print("Inserted file {}, in collection {}".format(item_data, collection_name))
            log.info("Inserted file {}, in collection {}".format(item_data, collection_name))
        else:
            print("Collection {0} for DB {1} does not exist!".format(collection_name, db_name))
            log.error("Collection {0} for DB {1} does not exist!".format(collection_name, db_name))
    else:
        print("Database {} does not exist!".format(db_name))
        log.error("Database {} does not exist!".format(db_name))


def update_item(db_name, collection_name, query, new_data):
    if is_collection_exists(db_name, collection_name):
        client[db_name][collection_name].update_one(query, {"$set": new_data})
    else:
        print("DB or Collection does not exist!")


def delete_document(db_name, collection_name, query):
    client[db_name][collection_name].delete_one(query)


def is_item_exists(db_name, collection_name, query):
    if is_collection_exists(db_name, collection_name):
        item = client[db_name][collection_name].find(query)
        if item.count():
            return True
        else:
            return False


# def get_distinct_items(shop_name, collection_name, field):
#     if is_collection_exists(shop_name, collection_name):
#         return client[shop_name][collection_name].distinct(field)
#     else:
#         print("DB or Collection does not exist!")


def get_items(db_name, collection_name):
    return_items = []
    if is_collection_exists(db_name, collection_name):
        items = client[db_name][collection_name].find()
        for item in items:
            return_items.append(item)

    return return_items


def get_item(db_name, collection_name, query):
    return_items = []
    if is_collection_exists(db_name, collection_name):
        items = client[db_name][collection_name].find(query)
        for item in items:
            return_items.append(item)
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

    print("{}".format(return_items))
    log.info("{}".format(return_items))
    return return_items


def print_dbs():
    db_list = client.list_database_names()
    print(db_list)


def update_ss_life_status(ss_name):
    global ss_life
    ss_life[ss_name] = datetime.now()
