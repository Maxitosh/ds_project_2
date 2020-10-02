import os
import socket
import subprocess
from threading import Thread
from time import sleep
import platform

from StorageServerCommands import StorageServerCommands
import pickle
import logging as log

log.basicConfig(filename="ss.log", format='%(asctime)s - %(levelname)s - %(message)s', level=log.DEBUG)

host_name = ""
block_size = 1024
clients = []
SSCommands = StorageServerCommands()


class Server(Thread):

    def __init__(self, name: str, sock: socket.socket):
        super().__init__(daemon=True)
        self.sock = sock
        self.name = name

    # clean up
    def _close(self):
        self.sock.close()
        print("[%s] " % host_name + self.name + ' disconnected')
        log.info("[%s] " % host_name + self.name + ' disconnected')

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

            return_data = SSCommands.dispatch_command(command)(args) if len(
                args.items()) > 0 else SSCommands.dispatch_command(command)()
            if return_data != 0:
                self.sock.sendall(pickle.dumps(return_data))
            self._close()
            return



def main():
    global host_name
    host_name = os.getenv('HOSTNAME').upper()
    print("[%s] starting..." % host_name)
    log.info("[%s] starting..." % host_name)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    next_user = 1
    sock.bind(('', 8800))
    sock.listen()
    print("[%s] waiting for connections..." % host_name)
    log.info("[%s] waiting for connections..." % host_name)
    while True:
        # blocking call, waiting for new client to connect
        con, addr = sock.accept()
        clients.append(con)
        name = 'user#' + str(next_user)
        next_user += 1
        print("[%s]" % host_name + str(addr) + ' connected as ' + name)
        log.info("[%s]" % host_name + str(addr) + ' connected as ' + name)

        # start new thread to deal with client
        Server(name, con).start()


if __name__ == "__main__":
    main()
