import os
import socket
from threading import Thread

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
            data = self.sock.recv(block_size).decode("utf-8")
            if data:
                NSCommands.dispatch_command(data)
            else:
                self._close()
                # finish the thread
                return
