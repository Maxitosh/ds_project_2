import json
import os
import pickle
from socket import *
import base64
from bson.json_util import loads
import logging as log
from ClientUtils import ClientUtils

log.basicConfig(filename="client.log", format='[CCM] %(asctime)s - %(levelname)s - %(message)s',
                level=log.DEBUG, force=True)

ns_host = "namingserver"
port = 8800
block_size = 1024

CUtils = ClientUtils()





class ClientCommands:

    def dispatch_command(self, command):
        if command == "Initialize":
            self.initialize_dfs()
        elif command == "Create file":
            self.create_file()
        elif command == "Write file":
            self.write_file()
        elif command == "Naming Server db snapshot":
            self.get_naming_server_db_snapshot()

    @staticmethod
    def initialize_dfs():
        print("Starting initialization of DFS")
        log.info("Starting initialization of DFS")

        message = {"command": "init"}
        received = CUtils.send_message(ns_host, message)
        print("{}".format(received))
        log.info("{}".format(received))

    @staticmethod
    def create_file():
        print("Enter file name: ")
        filename = input()

        message = {"command": "create_file", "file_name": filename, "size": 0}
        received = CUtils.send_message(ns_host, message)
        print("{}".format(received))
        log.info("{}".format(received))

    @staticmethod
    def write_file():
        # get input from user
        file_name, dfs_file_name = CUtils.get_filename_and_dfs_filename()

        # get size of file
        file_size = CUtils.get_file_size_in_bits(file_name)

        # generate message for NS
        message = {'command': 'write_file', 'file_name': dfs_file_name, 'size': file_size}
        response_code = CUtils.send_message(ns_host, message)
        if not response_code['status'] == 'OK':
            print(response_code['status'])
            return

        # get selected SS and replicas list
        selected_ss = response_code['ss']
        replicas_list = response_code['replicas']

        # # send message to selected SS
        # file_data = []
        # with open(file_name, 'rb') as file:
        #     file_data.append(base64.b64encode(file.read()))

        message = {'command': 'write_file', 'file_name': dfs_file_name, 'size': file_size, 'replicas': replicas_list}
        # response_code = CUtils.send_message(selected_ss, message)
        response_code = CUtils.send_file(selected_ss, message, file_name)

        # check if response is OK and start sending file
        if not response_code['status'] == 'OK':
            print(response_code['status'])
            return

        print(response_code)


    @staticmethod
    def get_naming_server_db_snapshot():
        print("Getting info about NamingServer ...")
        log.info("Getting info about NamingServer ...")

        message = {"command": "db_snapshot"}
        received = CUtils.send_message(ns_host, message)
        print("{}".format(received))
        log.info("{}".format(received))
