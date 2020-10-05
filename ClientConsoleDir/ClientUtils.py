import logging as log
import os
import pickle
from socket import *

log.basicConfig(filename="client.log", format='[CU] %(asctime)s - %(levelname)s - %(message)s',
                level=log.DEBUG, force=True)

block_size = 1024


def printProgressBar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█', printEnd="\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=printEnd)
    # Print New Line on Complete
    if iteration == total:
        print()


class ClientUtils:

    def get_filename_and_dfs_filename(self):
        inp = input().split(' ')
        file_name = inp[0]
        dfs_file_name = inp[1]

        return file_name, dfs_file_name

    def get_file_size_in_bits(self, file_name):
        try:
            # return file size in bits
            file_size = os.path.getsize(file_name) * 8
            print("File {} of size {}".format(file_name, file_size))
            return file_size
        except Exception as e:
            print(e)
            log.error(e)

    def send_message(self, host_name, message):
        sock = socket(AF_INET, SOCK_STREAM)
        sock.connect((host_name, 8800))
        data = pickle.dumps(message)
        sock.sendall(data)

        data = b""
        while True:
            packet = sock.recv(block_size)
            if not packet: break
            data += packet
        received = pickle.loads(data)
        sock.close()
        return received

    def send_file(self, host_name, message, file_name):
        sock = socket(AF_INET, SOCK_STREAM)
        sock.connect((host_name, 8800))
        data = pickle.dumps(message)
        sock.sendall(data)

        received = b""
        data = sock.recv(block_size)
        received += data
        while data:
            if len(data) < block_size: break
            data = sock.recv(block_size)
            received += data
        received = pickle.loads(received)

        if not received['command'] == 'ack':
            return

        file = open(file_name, 'rb')  # open file
        total_sent = 0
        file_size = os.path.getsize(file_name)
        printProgressBar(total_sent, file_size, prefix='Progress:', suffix='Complete',
                         length=50)  # init progress bar
        while True:
            bytes = file.read(block_size)  # read block_size at a time
            if not bytes:
                break  # until file totally sent
            sent = sock.send(bytes)

            # update vars for progress bar
            total_sent += sent

            # update progress bar
            printProgressBar(total_sent, file_size, prefix='Progress:', suffix='Complete', length=50)

            # debug
            assert sent == len(bytes)

        sock.close()
        return {'status': 'OK'}

    def read_file(self, host_name, message, local_file_name, file_size):
        sock = socket(AF_INET, SOCK_STREAM)
        sock.connect((host_name, 8800))
        data = pickle.dumps(message)
        sock.sendall(data)

        file = open(local_file_name, 'wb')  # open file
        total_got = 0
        printProgressBar(total_got, file_size, prefix='Progress:', suffix='Complete',
                         length=50)  # init progress bar
        while True:
            data = sock.recv(block_size)
            if not data:
                break  # till closed on server side
            file.write(data)

            # update vars for progress bar
            total_got += len(data)

            # update progress bar
            printProgressBar(total_got, file_size, prefix='Progress:', suffix='Complete', length=50)

        sock.close()
        return {'status': 'OK'}

    def send_delete_dir(self, host_name, message):
        sock = socket(AF_INET, SOCK_STREAM)
        sock.connect((host_name, 8800))
        data = pickle.dumps(message)
        sock.sendall(data)

        data = sock.recv(block_size)
        received = pickle.loads(data)

        if received['status'] == "Confirmation":
            print("Do you want to delete all from directory")
            log.info("Do you want to delete all from directory")
            conf = input()
            data = pickle.dumps({'confirmation': conf})
            sock.sendall(data)

        sock.close()
        return received
