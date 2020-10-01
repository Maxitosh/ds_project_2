import json
import pickle
from socket import *
from bson.json_util import loads
import logging as log

log.basicConfig(filename="dfs.log", format='%(asctime)s - %(levelname)s - %(message)s', level=log.DEBUG)

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
        print("[CLIENTCOMMANDS] {}".format(received))
        log.info("[CLIENTCOMMANDS] {}".format(received))
        sock.close()

    @staticmethod
    def create_file():
        print("[CLIENTCOMMANDS] Enter file name: ")
        log.info("[CLIENTCOMMANDS] Enter file name: ")
        filename = input()
        log.info("[CLIENTCOMMANDS] file: {}".format(filename))
        sock = socket(AF_INET, SOCK_STREAM)
        sock.connect((host_name, port))

        message = {"command": "create_file", "file_name": filename}
        data = pickle.dumps(message)
        sock.sendall(data)

        received = pickle.loads(sock.recv(block_size))
        print("[CLIENTCOMMANDS] {}".format(received))
        log.info("[CLIENTCOMMANDS] {}".format(received))
        sock.close()

    @staticmethod
    def get_naming_server_db_snapshot():
        print("[CLIENTCOMMANDS] Getting info about NamingServer ...")
        log.info("[CLIENTCOMMANDS] Getting info about NamingServer ...")
        sock = socket(AF_INET, SOCK_STREAM)
        sock.connect((host_name, port))

        message = {"command": "db_snapshot"}
        data = pickle.dumps(message)
        sock.sendall(data)

        received = pickle.loads(sock.recv(block_size))
        print("[CLIENTCOMMANDS] {}".format(received))
        log.info("[CLIENTCOMMANDS] {}".format(received))
        sock.close()
