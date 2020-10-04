import json
import pickle
from socket import *
from bson.json_util import loads
import logging as log
from ClientUtils import CLientUtils

log.basicConfig(filename="client.log", format='[CCM] %(asctime)s - %(levelname)s - %(message)s',
                level=log.DEBUG, force=True)

host_name = "namingserver"
port = 8800
block_size = 1024

CUtils = CLientUtils()

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
        filename = input()
        sock = socket(AF_INET, SOCK_STREAM)
        sock.connect((host_name, port))

        message = {"command": "create_file", "file_name": filename, "size": 0}
        data = pickle.dumps(message)
        sock.sendall(data)

        data = b""
        while True:
            packet = sock.recv(block_size)
            if not packet: break
            data += packet
        received = pickle.loads(data)
        print("{}".format(received))
        log.info("{}".format(received))
        sock.close()

    @staticmethod
    def write_file():
        # get input from user
        file_name, dfs_file_name = CUtils.get_filename_and_dfs_filename()

        # get size of file
        file_size = CUtils.get_file_size_in_bits(file_name)



    @staticmethod
    def get_naming_server_db_snapshot():
        print("Getting info about NamingServer ...")
        log.info("Getting info about NamingServer ...")
        sock = socket(AF_INET, SOCK_STREAM)
        sock.connect((host_name, port))

        message = {"command": "db_snapshot"}
        data = pickle.dumps(message)
        sock.sendall(data)

        data = b""
        while True:
            packet = sock.recv(block_size)
            if not packet: break
            data += packet
        received = pickle.loads(data)
        print("{}".format(received))
        log.info("{}".format(received))
        sock.close()
