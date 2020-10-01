import json
from socket import *

host_name = "namingserver"
port = 8800

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

        message = {"command": "init"}
        data = json.dumps(message)
        sock.sendall(bytes(data,encoding="utf-8"))
        sock.close()

    def create_file(self):
        print("Enter file name: ")
