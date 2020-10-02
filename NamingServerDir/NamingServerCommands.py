import pickle
from socket import *

import db_worker as db
import logging as log

log.basicConfig(filename="dfs.log", format='%(asctime)s - %(levelname)s - %(message)s', level=log.DEBUG)

naming_server_db = ["DFS"]
storage_servers_db = ["SS1", "SS2", "SS3"]
block_size = 1024


class NamingServerCommands:

    def dispatch_command(self, command):
        return getattr(self, 'do_' + command["command"], None)

    @staticmethod
    def do_init():
        print("Initialization called by client")
        log.info("Initialization called by client")

        # remove info from db
        for db_name in (naming_server_db + storage_servers_db):
            db.drop_db(db_name)
        db.init_db(naming_server_db + storage_servers_db, ["Files", "Directories"])

        # remove data from SS
        for ss in storage_servers_db:
            sock = socket(AF_INET, SOCK_STREAM)
            sock.connect((ss, 8800))
            message = {"command": "init"}
            data = pickle.dumps(message)
            sock.sendall(data)

            # received = pickle.loads(sock.recv(block_size))
            # print("[CLIENTCOMMANDS] {}".format(received))
            # log.info("[CLIENTCOMMANDS] {}".format(received))
            sock.close()

        return {"status": "OK", "size": 1}

    @staticmethod
    def do_create_file(args):
        print("Creation of file {}".format(args["file_name"]))
        db.insert_item("DFS", "Files", args)
        return {"status": "OK"}

    @staticmethod
    def do_db_snapshot():
        print("Gathering info about NamingServer")
        log.info("Gathering info about NamingServer")
        return db.get_db_snapshot(naming_server_db + storage_servers_db)
