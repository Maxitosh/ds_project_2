import os
import pickle
import threading
from socket import *

import logging as log
from time import sleep

dir = "/usr/src/app/data/"
block_size = 1024


class StorageServerUtils:

    def __init__(self):
        log.basicConfig(filename="ss.log", format='[SSU] %(asctime)s - %(levelname)s - %(message)s', level=log.DEBUG)

    def mkdir(self, dir_name):
        os.system("mkdir {}".format(dir_name))

    def create_empty_file(self, file_name):
        os.system("touch {}".format(dir + file_name))

    def send_file_replicas_to_ss(self, file_name, storages_list):
        # generate message
        # TODO redo this for uniform command
        message = {"command": "write_file", "file_name": file_name, "replicas": []}

        for ss_name in storages_list:
            sock = socket(AF_INET, SOCK_STREAM)
            sock.connect((ss_name, 8800))
            data = pickle.dumps(message)
            sock.sendall(data)

            received = b""
            data = sock.recv(block_size)
            received += data
            while data:
                if len(data) < block_size: break
                data = sock.recv(block_size)
                received += data
            received = pickle.loads(received)

            if not received['command'] == 'ack':
                return

            file = open(dir + file_name, 'rb')  # open file
            total_sent = 0
            while True:
                bytes = file.read(block_size)  # read block_size at a time
                if not bytes:
                    break  # until file totally sent
                sent = sock.send(bytes)
                # update vars for progress bar
                total_sent += sent
                # debug
                assert sent == len(bytes)

            sock.close()
            log.info('Sent replica of file {} to {} storage server'.format(file_name, ss_name))

    def send_replicas_of_empty_file_to_ss(self, file_name, storages_list):

        # generate message
        message = {"command": "create_file", "file_name": file_name, "replicas": []}

        for ss_name in storages_list:
            print(self.send_message(ss_name, message))
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

    def get_file(self, sock, file_name):
        message = {'command': 'ack'}
        data = pickle.dumps(message)
        sock.sendall(data)

        file = open(file_name, 'wb')
        while 1:
            # receive data
            data = sock.recv(block_size)
            if not data:
                break  # till closed on server side
            file.write(data)

        file.close()
