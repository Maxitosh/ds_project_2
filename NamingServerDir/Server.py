import os
import socket
from threading import Thread
import pickle
from NamingServerCommands import NamingServerCommands

block_size = 1024

NSCommands = NamingServerCommands()


class Server(Thread):

    def __init__(self, name: str, sock: socket.socket):
        super().__init__(daemon=True)
        self.sock = sock
        self.name = name

    # clean up
    def _close(self):
        self.sock.close()
        print(self.name + ' disconnected')

    def run(self):
        while True:
            # try to read 1024 bytes from user
            # this is blocking call, thread will be paused here
            data = pickle.loads(self.sock.recv(block_size))

            # divide command and args
            command = {"command": data["command"]}
            args = {}
            for key, value in data.items():
                if key != "command":
                    args[key] = value

            if data:
                return_data = NSCommands.dispatch_command(command)(args)
                if return_data != 0:
                    self.sock.sendall(pickle.dumps(return_data))
                    self._close()
                    return
            else:
                self._close()
                # finish the thread
                return
