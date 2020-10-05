import pickle
from datetime import datetime
from socket import *
from time import sleep

import db_worker as db
import logging as log

dir = "/usr/src/app/data/"
log.basicConfig(filename="dfs.log", format='%(asctime)s - %(levelname)s - [NSU] %(message)s', level=log.DEBUG,
                force=True)

block_size = 1024


class NamingServerUtils:

    def insert_dirs_into_db_using_file_name(self, db_name, file_name):
        dirs = self.__extract_dirs_from_filename(file_name)
        for directory in dirs:
            if not db.is_item_exists(db_name, "Directories", {"directory_name": directory}):
                db.insert_item(db_name, "Directories", {"directory_name": directory})
                log.info("Inserted directory {} to {}".format(directory, db_name))

    def insert_dirs_into_db(self, db_name, dir_names):
        for directory in dir_names:
            if not db.is_item_exists(db_name, "Directories", {"directory_name": directory}):
                db.insert_item(db_name, "Directories", {"directory_name": directory})
                log.info("Inserted directory {} to {}".format(directory, db_name))

    def insert_file_into_db(self, db_name, file_data):
        upd_file_data = file_data.copy()
        upd_file_data['file_name'] = dir + file_data['file_name']
        db.insert_item(db_name, "Files", upd_file_data)
        log.info("Inserted file {} to {}".format(upd_file_data, db_name))

    def is_dir_exists(self, dir_name):
        if db.is_item_exists("DFS", "Directories", {"directory_name": dir_name}):
            return True
        else:
            return False

    def is_file_exists(self, file_name):
        if db.is_item_exists("DFS", "Files", {"file_name": file_name}):
            return True
        else:
            return False

    def __extract_dirs_from_filename(self, file_name):
        dirs = []
        dir_append = ''
        for directory in file_name.split('/')[:len(file_name.split('/')) - 1]:
            dir_append += directory + '/'
            dirs.append(dir + dir_append)

        return dirs

    def get_full_path(self, path):
        return dir + path

    def send_message_to_ss(self, ss_name, message):
        sock = socket(AF_INET, SOCK_STREAM)
        sock.connect((ss_name, 8800))
        data = pickle.dumps(message)
        sock.sendall(data)

    def get_ss_for_replicas(self, picked_ss, ss_list):
        ss_to_replicas = []
        for ss in ss_list:
            if ss != picked_ss:
                ss_to_replicas.append(ss)
        return ss_to_replicas

    def get_alive_ss(self, ss_list):
        alive_nodes = []
        for ss in ss_list:
            try:
                if (datetime.now() - db.ss_life[ss]).seconds < 15:
                    print("Node {} is alive".format(ss))
                    alive_nodes.append(ss)
            except:
                pass

        return alive_nodes

    def get_fit_nodes(self, ss_list, file_size):
        fit_nodes = []
        storages = db.get_items('DFS', 'Storages')
        for ss in storages:
            # skip blank item
            try:
                if (int(ss['storage_size']) - file_size) >= 0 and ss['storage_name'] in ss_list:
                    fit_nodes.append(ss['storage_name'])
            except:
                pass

        return fit_nodes

    def get_storage_size(self, storage_name):
        storages = db.get_items('DFS', 'Storages')
        for ss in storages:
            try:
                if ss['storage_name'] == storage_name:
                    return ss['storage_size']
            except:
                pass

    def get_file_size(self, file_name):
        items = db.get_items("DFS", 'Files')
        print(items)
        for item in items:
            try:
                if item['file_name'] == self.get_full_path(file_name):
                    return item['size']
            except:
                pass

    def get_entry_from_db(self, db_name, collection_name, query):
        try:
            return db.get_item(db_name, collection_name, query)[0]
        except Exception as e:
            print(e)
            log.error(e)
            return 0

    def delete_entry_from_db(self, db_name, collection_name, query):
        db.delete_document(db_name, collection_name, query)
        print("Deleted file {}".format(query))
        log.info("Deleted file {}".format(query))

    def delete_all_sub_entries_of_directory(self, db_name, collection_name, directory_name):
        items = db.get_items(db_name, collection_name)
        file_total_size_deleted = 0
        if collection_name == "Files":
            for item in items:
                try:
                    if directory_name in item['file_name']:
                        db.delete_document(db_name, collection_name, item)
                        print("Deleted file {}".format(item))
                        log.info("Deleted file {}".format(item))
                        file_total_size_deleted += item['size']
                except:
                    pass
        else:
            for item in items:
                try:
                    if directory_name in item['directory_name']:
                        db.delete_document(db_name, collection_name, item)
                        print("Deleted directory {}".format(item))
                        log.info("Deleted directory {}".format(item))
                except:
                    pass
        return file_total_size_deleted

    def update_storages_size(self, ss_list, file_size):
        for ss in ss_list:
            storage_size = self.get_storage_size(ss)
            db.update_item('DFS', 'Storages', {'storage_name': ss},
                           {'storage_size': (storage_size - file_size)})
            print("Updated storage size of {} from {} to {}".format(ss, storage_size, storage_size - file_size))
            log.info("Updated storage size of {} from {} to {}".format(ss, storage_size, storage_size - file_size))

    def send_message(self, host_name, message):
        sock = socket(AF_INET, SOCK_STREAM)
        sock.connect((host_name, 8800))
        data = pickle.dumps(message)
        sock.sendall(data)
        # print('123')

        rec = b""
        while True:
            packet = sock.recv(block_size)
            if not packet: break
            rec += packet
        received = pickle.loads(rec)
        sock.close()
        return received

    def send_message_using_socket(self, sock, message):
        data = pickle.dumps(message)
        sock.sendall(data)

    def send_message_using_socket_with_response(self, sock, message):
        data = pickle.dumps(message)
        sock.sendall(data)

        data = sock.recv(block_size)
        received = pickle.loads(data)
        sock.close()
        return received

    def read_directory(self, directory_name):
        data = []

        # get all files
        files = db.get_items('DFS', 'Files')

        # get all dirs
        dirs = db.get_items('DFS', 'Directories')

        # work with dirs
        for dir in dirs:
            try:
                if directory_name in dir['directory_name'] and directory_name != dir['directory_name']:
                    item = dir['directory_name'].replace(directory_name, '').split('/')[0] + '/'
                    # check if such dir already counted
                    if item not in data:
                        data.append(item)
            # skip exception, because there are blank files
            except:
                pass

        # work with files
        for file in files:
            try:
                if directory_name in file['file_name']:
                    item = file['file_name'].replace(directory_name, '')
                    # check if there file nested in another dir, we don't need it
                    if '/' not in item:
                        data.append(item)
            # skip exception, because there are blank files
            except:
                pass

        return data
