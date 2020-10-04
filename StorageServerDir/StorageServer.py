import os
import socket
import subprocess
from threading import Thread
from time import sleep
import platform

from StorageServerCommands import StorageServerCommands
from StorageServerUtils import StorageServerUtils
import pickle
import logging as log

host_name = '[' + os.getenv('HOSTNAME').upper() + '] '
log.basicConfig(force=True, filename="ss.log",
                format=('%(asctime)s - %(levelname)s - ' + host_name + '%(message)s'),
                level=log.DEBUG)

block_size = 1024
clients = []
SSCommands = StorageServerCommands()
SSUtils = StorageServerUtils()


class Server(Thread):

    def __init__(self, name: str, sock: socket.socket):
        super().__init__(daemon=True)
        self.sock = sock
        self.name = name

    # clean up
    def _close(self):
        self.sock.close()
        print(self.name + ' disconnected')
        log.info(self.name + ' disconnected')

    def run(self):
        while True:
            # try to read 1024 bytes from user
            # this is blocking call, thread will be paused here
            received = b""
            data = self.sock.recv(block_size)
            received += data
            while data:
                if len(data) < block_size: break
                data = self.sock.recv(block_size)
                received += data
            data = pickle.loads(received)

            # divide command and args
            command = {"command": data["command"]}
            args = {}
            for key, value in data.items():
                if key != "command":
                    args[key] = value

            return_data = SSCommands.dispatch_command(command)(args) if len(
                args.items()) > 0 else SSCommands.dispatch_command(command)()
            if return_data != 0:
                self.sock.sendall(pickle.dumps(return_data))
            self._close()
            return


def main():
    print("starting...")
    log.info("starting...")
    SSUtils.init_heart_beat_system("namingserver")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    next_user = 1
    sock.bind(('', 8800))
    sock.listen()
    print("waiting for connections...")
    log.info("waiting for connections...")
    while True:
        # blocking call, waiting for new client to connect
        con, addr = sock.accept()
        clients.append(con)
        name = 'connection#' + str(next_user)
        next_user += 1
        print(str(addr) + ' connected as ' + name)
        log.info(str(addr) + ' connected as ' + name)

        # start new thread to deal with client
        Server(name, con).start()


if __name__ == "__main__":
    main()
