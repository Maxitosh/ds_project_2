from pymongo import MongoClient
import json
import os
import configparser

client = MongoClient("mongodb://root:1234@mongodb:27017/?authSource=DFS")


def test():
    pass


def is_db_exists(db_name):
    db_list = client.list_database_names()
    if db_name in db_list:
        return 1
    else:
        return 0


def print_dbs():
    db_list = client.list_database_names()
    print(db_list)


def is_collection_exists(shop_name, collection_name):
    if is_db_exists(shop_name):
        collection_list = client[shop_name].list_collection_names()
        if collection_name in collection_list:
            return 1
        else:
            return 0


def create_db(db_name):
    if not is_db_exists(db_name):
        db = client[db_name]
        files = db["Files"]
        dirs = db["Directories"]
        blank = {"blank": "blank"}
        files.insert_one(blank)
        dirs.insert_one(blank)
    else:
        print("Database {0} already exists!".format(db_name))


def insert_item(shop_name, collection_name, product_data):
    if is_db_exists(shop_name):
        selected_db = client[shop_name]
        if is_collection_exists(shop_name, collection_name):
            collection = selected_db[collection_name]
            collection.insert_one(product_data)
        else:
            print("Collection {0} for DB {1} does not exist!".format(collection_name, shop_name))
    else:
        print("Database does not exist!")


# query = {sharp_id:"DATA"}
def update_item(shop_name, collection_name, query, new_product_data):
    if is_collection_exists(shop_name, collection_name):
        client[shop_name][collection_name].update_one(query, {"$set": new_product_data})
    else:
        print("DB or Collection does not exist!")


def is_item_exists(shop_name, collection_name, query):
    if is_collection_exists(shop_name, collection_name):
        item = 0
        item = client[shop_name][collection_name].find(query)
        if item.count():
            return True
        else:
            return False


def get_distinct_items(shop_name, collection_name, field):
    if is_collection_exists(shop_name, collection_name):
        return client[shop_name][collection_name].distinct(field)
    else:
        print("DB or Collection does not exist!")


def list_items(shop_name, collection_name):
    if is_collection_exists(shop_name, collection_name):
        items = client[shop_name][collection_name].find()
        for item in items:
            print(item)


def get_item(shop_name, collection_name, query):
    if is_collection_exists(shop_name, collection_name):
        return client[shop_name][collection_name].find(query)
    else:
        print("DB or Collection does not exist!")


def export_databases():
    import datetime
    directory = "{0}-{1}-{2}".format(datetime.datetime.now().year, datetime.datetime.now().month,
                                     datetime.datetime.now().day)
    if not os.path.exists("/usr/local/bin/kznexprbot/DB/{}".format(directory)):
        os.makedirs("/usr/local/bin/kznexprbot/DB/{}".format(directory))
    cmd = "mongodump -o /usr/local/bin/kznexprbot/DB/{}".format(directory)
    os.system(cmd)
