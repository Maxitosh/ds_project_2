import json
import pickle
from socket import *

host_name = "namingserver"
port = 8800
block_size = 1024

class ClientCommands:

    def dispatch_command(self, command):
        if command == "Initialize":
            self.initialize_dfs()
        elif command == "Create file":
            self.create_file()

    def initialize_dfs(self):
        print("Starting initialization of DFS")
        sock = socket(AF_INET, SOCK_STREAM)
        sock.connect((host_name, port))

        message = {"command": "init", "arg1": 123}
        data = pickle.dumps(message)
        sock.sendall(data)

        received = pickle.loads(sock.recv(block_size))
        print(received)
        sock.close()

    def create_file(self):
        print("Enter file name: ")
