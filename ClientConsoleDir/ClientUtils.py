import logging as log
import os
import pickle
from socket import *

log.basicConfig(filename="client.log", format='[CU] %(asctime)s - %(levelname)s - %(message)s',
                level=log.DEBUG, force=True)

block_size = 1024


class ClientUtils:

    def get_filename_and_dfs_filename(self):
        print("Enter local file name and name of file to write in DFS: ")
        inp = input().split(' ')
        file_name = inp[0]
        dfs_file_name = inp[1]

        return file_name, dfs_file_name

    def get_file_size_in_bits(self, file_name):
        try:
            # return file size in bits
            file_size = os.path.getsize(file_name) * 8
            print("File {} of size {}".format(file_name, file_size))
            return file_size
        except Exception as e:
            print(e)
            log.error(e)

    def send_message(self, host_name, message):
        sock = socket(AF_INET, SOCK_STREAM)
        sock.connect((host_name, 8800))
        data = pickle.dumps(message)
        sock.sendall(data)

        data = b""
        while True:
            packet = sock.recv(block_size)
            if not packet: break
            data += packet
        received = pickle.loads(data)
        return received
