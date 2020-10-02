import socket
from threading import Thread
from time import sleep

import pickle
from NamingServerCommands import NamingServerCommands
import logging as log

log.basicConfig(filename="dfs.log", format='[NS] %(asctime)s - %(levelname)s - %(message)s', level=log.DEBUG)

block_size = 1024
NSCommands = NamingServerCommands()
clients = []


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
            data = pickle.loads(self.sock.recv(block_size))

            # divide command and args
            command = {"command": data["command"]}
            args = {}
            for key, value in data.items():
                if key != "command":
                    args[key] = value

            if data:
                return_data = NSCommands.dispatch_command(command)(args) if len(
                    args.items()) > 0 else NSCommands.dispatch_command(command)()
                if return_data != 0:
                    self.sock.sendall(pickle.dumps(return_data))
                    self._close()
                    return
            else:
                self._close()
                # finish the thread
                return


def main():
    print("NamingServer starting...")
    log.info("NamingServer starting...")
    next_user = 1
    # # AF_INET – IPv4, SOCK_STREAM – TCP
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # # listen to all interfaces at 8800 port
    sock.bind(('', 8800))
    sock.listen()
    print("NamingServer waiting for connections...")
    log.info("NamingServer waiting for connections...")
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
