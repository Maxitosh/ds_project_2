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
        elif command == "Naming Server info":
            self.get_naming_server_info()

    @staticmethod
    def initialize_dfs():
        print("Starting initialization of DFS")
        log.info("Starting initialization of DFS")
        sock = socket(AF_INET, SOCK_STREAM)
        sock.connect((host_name, port))

        message = {"command": "init", "arg1": 123}
        data = pickle.dumps(message)
        sock.sendall(data)

        received = pickle.loads(sock.recv(block_size))
        print(received)
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
        print("[CLIENTCOMMANDS] ", received)
        log.info("[CLIENTCOMMANDS] ", received)
        sock.close()

    @staticmethod
    def get_naming_server_info():
        print("[CLIENTCOMMANDS] Getting info about NamingServer ...")
        log.info("[CLIENTCOMMANDS] Getting info about NamingServer ...")
        sock = socket(AF_INET, SOCK_STREAM)
        sock.connect((host_name, port))

        message = {"command": "info"}
        data = pickle.dumps(message)
        sock.sendall(data)

        received = pickle.loads(sock.recv(block_size))
        print("[CLIENTCOMMANDS] ", received)
        log.info("[CLIENTCOMMANDS] ", received)
        sock.close()
