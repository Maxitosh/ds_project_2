import os
import pickle
import threading
from socket import *

import logging as log
from time import sleep

dir = "/usr/src/app/data/"


class StorageServerUtils:

    def __init__(self):
        log.basicConfig(filename="ss.log", format='[SSU] %(asctime)s - %(levelname)s - %(message)s', level=log.DEBUG)

    def mkdir(self, dir_name):
        os.system("mkdir {}".format(dir_name))

    def create_empty_file(self, file_name):
        os.system("touch {}".format(dir + file_name))

    def send_replicas_to_ss(self, file_name, storages_list):
        # # open file to read
        #
        #
        # sock = socket(AF_INET, SOCK_STREAM)
        # sock.connect((ss_name, 8800))
        # data = pickle.dumps(message)
        # sock.sendall(data)
        pass

    def send_replicas_of_empty_file_to_ss(self, file_name, storages_list):

        # generate message
        message = {"command": "create_file", "file_name": file_name, "replicas": []}

        for ss_name in storages_list:
            sock = socket(AF_INET, SOCK_STREAM)
            sock.connect((ss_name, 8800))
            data = pickle.dumps(message)
            sock.sendall(data)
            log.info('Sent replica of file {} to {} storage server'.format(file_name, ss_name))

    def extract_dirs_from_filename(self, file_name):
        dirs = []
        dir_append = ''
        for directory in file_name.split('/')[:len(file_name.split('/')) - 1]:
            dir_append += directory + '/'
            dirs.append(dir + dir_append)

        return dirs

    def init_heart_beat_system(self, name_server_hostname):
        heart_beat_thread = threading.Thread(target=self.send_heart_signal, args=(name_server_hostname,), daemon=True)
        heart_beat_thread.start()

    def send_heart_signal(self, name_server_hostname):
        ss_host_name = os.getenv('HOSTNAME').upper()
        # generate message
        message = {"command": "heart_signal", "ss": ss_host_name}

        while True:
            try:
                sock = socket(AF_INET, SOCK_STREAM)
                sock.connect((name_server_hostname, 8800))
                data = pickle.dumps(message)
                sock.sendall(data)
                log.info('Sent heart signal from {}'.format(ss_host_name))
                sock.close()
            except Exception as e:
                print(e)
            sleep(10)
