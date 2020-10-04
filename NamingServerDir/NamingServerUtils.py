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

    def insert_dirs_into_db(self, db_name, file_name):
        dirs = self.__extract_dirs_from_filename(file_name)
        for directory in dirs:
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
                if (datetime.now() - db.ss_life[ss]).seconds < 60:
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