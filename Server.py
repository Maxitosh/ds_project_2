import os
import socket
from threading import Thread

clients = []
block_size = 1024


class NamingServer(Thread):
    file = None

    def __init__(self, name: str, sock: socket.socket):
        super().__init__(daemon=True)
        self.sock = sock
        self.name = name

    # clean up
    def _close(self):
        clients.remove(self.sock)
        self.sock.close()
        print(self.name + ' disconnected')

    def run(self):
        while True:
            # try to read 1024 bytes from user
            # this is blocking call, thread will be paused here
            data = self.sock.recv(block_size)
            if data:
                print(data)
            else:
                self.file.close()
                self._close()
                # finish the thread
                return
