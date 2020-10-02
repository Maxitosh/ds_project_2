import pickle
import random
from socket import *

import db_worker as db
import logging as log

log.basicConfig(filename="dfs.log", format='%(asctime)s - %(levelname)s - %(message)s', level=log.DEBUG)

# TODO move it to some config file
naming_server_db = ["DFS"]
storage_servers_db = ["SS1", "SS2", "SS3"]
storage_size = 800000000  # 100mgbytes
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
        # init dbs for file system
        db.init_db(naming_server_db + storage_servers_db, ["Files", "Directories"])
        db.init_collection("DFS", ["Storages"])

        # init storages size
        for ss in storage_servers_db:
            db.insert_item("DFS", "Storages", {ss: storage_size})

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

        return {"status": "OK", "size_bits": storage_size * len(storage_servers_db)}

    @staticmethod
    def do_create_file(args):
        print("Creation of file {}".format(args["file_name"]))

        # update main file system
        db.insert_item("DFS", "Files", args)

        # TODO check alive SS, for now pick random
        # choose alive SS
        picked_ss = random.randint(0, 2)

        sock = socket(AF_INET, SOCK_STREAM)
        sock.connect((storage_servers_db[picked_ss], 8800))
        message = {"command": "create_file", "file_name": args["file_name"]}
        data = pickle.dumps(message)
        sock.sendall(data)

        return {"status": "OK"}

    @staticmethod
    def do_db_snapshot():
        print("Gathering info about NamingServer")
        log.info("Gathering info about NamingServer")
        return db.get_db_snapshot(naming_server_db + storage_servers_db)
