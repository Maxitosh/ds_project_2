import socket
from time import sleep

from Server import Server

clients = []
block_size = 1024


def main():
    next_user = 1
    # # AF_INET – IPv4, SOCK_STREAM – TCP
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # # listen to all interfaces at 8800 port
    sock.bind(('', 8800))
    sock.listen()
    while True:
        # blocking call, waiting for new client to connect
        con, addr = sock.accept()
        clients.append(con)
        name = 'user#' + str(next_user)
        next_user += 1
        print(str(addr) + ' connected as ' + name)
        # start new thread to deal with client
        Server(name, con).start()




if __name__ == "__main__":
    main()