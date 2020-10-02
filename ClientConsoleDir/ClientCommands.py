import json
import pickle
from socket import *
from bson.json_util import loads
import logging as log

log.basicConfig(filename="client.log", format='[CLIENTCOMMANDS] %(asctime)s - %(levelname)s - %(message)s',
                level=log.DEBUG)

host_name = "namingserver"
port = 8800
block_size = 1024


class ClientCommands:

    def dispatch_command(self, command):
        if command == "Initialize":
            self.initialize_dfs()
        elif command == "Create file":
            self.create_file()
        elif command == "Naming Server db snapshot":
            self.get_naming_server_db_snapshot()

    @staticmethod
    def initialize_dfs():
        print("Starting initialization of DFS")
        log.info("Starting initialization of DFS")
        sock = socket(AF_INET, SOCK_STREAM)
        sock.connect((host_name, port))

        message = {"command": "init"}
        data = pickle.dumps(message)
        sock.sendall(data)

        received = pickle.loads(sock.recv(block_size))
        print("{}".format(received))
        log.info("{}".format(received))
        sock.close()

    @staticmethod
    def create_file():
        print("Enter file name: ")
        log.info("Enter file name: ")
        filename = input()
        log.info("file: {}".format(filename))
        sock = socket(AF_INET, SOCK_STREAM)
        sock.connect((host_name, port))

        message = {"command": "create_file", "file_name": filename, "size": 0}
        data = pickle.dumps(message)
        sock.sendall(data)

        received = pickle.loads(sock.recv(block_size))
        print("{}".format(received))
        log.info("{}".format(received))
        sock.close()

    @staticmethod
    def get_naming_server_db_snapshot():
        print("Getting info about NamingServer ...")
        log.info("Getting info about NamingServer ...")
        sock = socket(AF_INET, SOCK_STREAM)
        sock.connect((host_name, port))

        message = {"command": "db_snapshot"}
        data = pickle.dumps(message)
        sock.sendall(data)

        received = pickle.loads(sock.recv(block_size))
        print("{}".format(received))
        log.info("{}".format(received))
        sock.close()
