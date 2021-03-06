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

port = 8800
block_size = 1024

CUtils = ClientUtils()


class ClientCommands:
    ns_host = ""

    def __init__(self, ip):
        self.ns_host = ip

    def dispatch_command(self, command):
        if command == "Initialize":
            self.initialize_dfs()
        elif command == "Create file":
            self.create_file()
        elif command == "Read file":
            self.read_file()
        elif command == "Write file":
            self.write_file()
        elif command == "Delete file":
            self.delete_file()
        elif command == "Info file":
            self.info_file()
        elif command == "Copy file":
            self.copy_file()
        elif command == "Move file":
            self.move_file()
        elif command == "Read directory":
            self.read_directory()
        elif command == "Make directory":
            self.make_directory()
        elif command == "Delete directory":
            self.delete_directory()
        elif command == "Naming Server db snapshot":
            self.get_naming_server_db_snapshot()

    def initialize_dfs(self):
        print("Starting initialization of DFS")
        log.info("Starting initialization of DFS")

        message = {"command": "init"}
        received = CUtils.send_message(self.ns_host, message)
        print("{}".format(received))
        log.info("{}".format(received))

    def create_file(self):
        print("Enter file name: ")
        filename = input()

        message = {"command": "create_file", "file_name": filename, "size": 0}
        received = CUtils.send_message(self.ns_host, message)
        print("{}".format(received))
        log.info("{}".format(received))

    def read_file(self):
        print("Enter DFS file name and file name after downloading...")
        log.info("Enter DFS file name and file name after downloading...")
        dfs_file_name, file_name = CUtils.get_filename_and_dfs_filename()  # inverse here
        message = {"command": "read_file", "file_name": dfs_file_name}
        received = CUtils.send_message(self.ns_host, message)

        if not received['status'] == 'OK':
            print(received)
            log.error(received)
            return
        print(received)
        log.info(received)

        # send message to SS to read file
        message = {"command": "read_file", "file_name": dfs_file_name}
        received = CUtils.read_file(received['ss'], message, file_name, received['file_size'])

        print("{}".format(received))
        log.info("{}".format(received))

    def write_file(self):
        # get input from user
        print("Enter local file name and name of file to write in DFS: ")
        file_name, dfs_file_name = CUtils.get_filename_and_dfs_filename()

        # get size of file
        file_size = CUtils.get_file_size_in_bits(file_name)

        # generate message for NS
        message = {'command': 'write_file', 'file_name': dfs_file_name, 'size': file_size}
        response_code = CUtils.send_message(self.ns_host, message)
        if not response_code['status'] == 'OK':
            print(response_code['status'])
            return

        # get selected SS and replicas list
        selected_ss = response_code['ss']
        replicas_list = response_code['replicas']

        message = {'command': 'write_file', 'file_name': dfs_file_name, 'size': file_size, 'replicas': replicas_list}
        # response_code = CUtils.send_message(selected_ss, message)
        response_code = CUtils.send_file(selected_ss, message, file_name)

        # check if response is OK and start sending file
        if not response_code['status'] == 'OK':
            print(response_code['status'])
            return

        print(response_code)

    def delete_file(self):
        print("Enter DFS file name")
        log.info("Enter DFS file name")
        file_name = input()

        # generate message for NS
        message = {'command': 'delete_file', 'file_name': file_name}
        response_code = CUtils.send_message(self.ns_host, message)
        if not response_code['status'] == 'OK':
            print(response_code['status'])
            return

        print(response_code)

    def info_file(self):
        print("Enter DFS filename... ")
        log.info("Enter DFS filename... ")
        dfs_file_name = input()

        # generate message for NS
        message = {'command': 'info_file', 'file_name': dfs_file_name}
        response_code = CUtils.send_message(self.ns_host, message)
        if not response_code['status'] == 'OK':
            print(response_code['status'])
            return

        # TODO add pretty output here
        print(response_code)

    def copy_file(self):
        print("Enter DFS filename and target directory...")
        log.info("Enter DFS filename and target directory...")
        str = input().split(' ')
        dfs_file_name = str[0]
        directory = str[1]

        # generate message for NS
        message = {'command': 'copy_file', 'file_name': dfs_file_name, 'directory': directory}
        response_code = CUtils.send_message(self.ns_host, message)
        if not response_code['status'] == 'OK':
            print(response_code['status'])
            return

        print(response_code)

    def move_file(self):
        print("Enter DFS filename and target directory...")
        log.info("Enter DFS filename and target directory...")
        str = input().split(' ')
        dfs_file_name = str[0]
        directory = str[1]

        # generate message for NS
        message = {'command': 'move_file', 'file_name': dfs_file_name, 'directory': directory}
        response_code = CUtils.send_message(self.ns_host, message)
        if not response_code['status'] == 'OK':
            print(response_code['status'])
            return

        print(response_code)

    def read_directory(self):
        print("Enter directory name to read...")
        log.info("Enter directory name to read...")
        directory_name = input()

        # generate message for NS
        message = {'command': 'read_directory', 'directory_name': directory_name}
        response_code = CUtils.send_message(self.ns_host, message)
        if not response_code['status'] == 'OK':
            print(response_code['status'])
            return

        # TODO add pretty output here
        print(response_code)

    def make_directory(self):
        print("Enter directory name to make...")
        log.info("Enter directory name to make...")
        directory_name = input()

        # generate message for NS
        message = {'command': 'make_directory', 'directory_name': directory_name}
        response_code = CUtils.send_message(self.ns_host, message)
        if not response_code['status'] == 'OK':
            print(response_code['status'])
            return

        print(response_code)

    def delete_directory(self):
        print("Enter directory name to delete...")
        log.info("Enter directory name to delete...")
        directory_name = input()

        # generate message for NS
        message = {'command': 'delete_directory', 'directory_name': directory_name}
        response_code = CUtils.send_delete_dir(self.ns_host, message)

        if not response_code['status'] == 'OK':
            print(response_code['status'])
            return

        print(response_code)

    def get_naming_server_db_snapshot(self):
        print("Getting info about NamingServer ...")
        log.info("Getting info about NamingServer ...")

        message = {"command": "db_snapshot"}
        print("Host", self.ns_host)
        received = CUtils.send_message(self.ns_host, message)

        for db_name, db_data in received.items():
            print(db_name)
            log.info(db_name)
            for coll, coll_data in db_data.items():
                print("  {}".format(coll))
                log.info("  {}".format(coll))
                for item in coll_data:
                    print("    {}".format(item))
                    log.info("    {}".format(item))
