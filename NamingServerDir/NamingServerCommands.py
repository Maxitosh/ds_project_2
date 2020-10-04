import pickle
import random
from socket import *

import db_worker as db
import logging as log
from NamingServerUtils import NamingServerUtils

log.basicConfig(filename="dfs.log", format='%(asctime)s - %(levelname)s - [NSC] %(message)s', level=log.DEBUG,
                force=True)

# TODO move it to some config file
naming_server_db = ["DFS"]
storage_servers_db = ["SS1", "SS2", "SS3"]
storage_size = 800000000  # 100mgbytes
block_size = 1024

NSUtils = NamingServerUtils()


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
            db.insert_item("DFS", "Storages", {'storage_name': ss, 'storage_size': storage_size})

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

        return {"status": "OK", "size_bits": storage_size}

    @staticmethod
    def do_create_file(args):
        print("Creation of file {}".format(NSUtils.get_full_path(args["file_name"])))
        log.info("Creation of file {}".format(NSUtils.get_full_path(args["file_name"])))

        # check if file exists
        if NSUtils.is_file_exists((NSUtils.get_full_path(args['file_name']))):
            return {"status": "File exists"}

        # update main file system
        NSUtils.insert_file_into_db("DFS", args)
        # update dirs of file system
        NSUtils.insert_dirs_into_db("DFS", args['file_name'])

        # TODO check alive SS, for now pick random
        # choose alive SS
        picked_ss = random.randint(0, len(storage_servers_db) - 1)

        # TODO check if SS is alive to write its DB
        for i in range(len(storage_servers_db)):
            # update ss file system
            NSUtils.insert_file_into_db(storage_servers_db[i], args)
            # update ss dirs
            NSUtils.insert_dirs_into_db(storage_servers_db[i], args['file_name'])

        # get list of ss to get replicas
        ss_replicas_list = NSUtils.get_ss_for_replicas(storage_servers_db[picked_ss], storage_servers_db)

        message = {"command": "create_file", "file_name": args["file_name"], "replicas": ss_replicas_list}
        NSUtils.send_message_to_ss(storage_servers_db[picked_ss], message)

        return {"status": "OK"}

    @staticmethod
    def do_write_file(args):
        print("Write file {}".format(NSUtils.get_full_path(args["file_name"])))
        log.info("Write file {}".format(NSUtils.get_full_path(args["file_name"])))

        # check if file exists
        # TODO save copy of file
        if NSUtils.is_file_exists(NSUtils.get_full_path(args['file_name'])):
            return {'status': 'File exists'}

        # get alive nodes
        alive_nodes = NSUtils.get_alive_ss(storage_servers_db)

        # get alive fit nodes
        alive_fit_nodes = NSUtils.get_fit_nodes(alive_nodes, args['size'])

        # check if file does not fit
        if len(alive_fit_nodes) == 0:
            return {'status': 'NotEnoughSpace'}

        # update main file system
        NSUtils.insert_file_into_db("DFS", args)
        # update dirs of file system
        NSUtils.insert_dirs_into_db("DFS", args['file_name'])

        # update ss file system
        for ss in alive_fit_nodes:
            NSUtils.insert_file_into_db(ss, args)
            # update dirs of file system
            NSUtils.insert_dirs_into_db(ss, args['file_name'])

        # update storages size
        NSUtils.update_storages_size(alive_fit_nodes, args['size'])

        # choose any alive fit ss node
        picked_ss = storage_servers_db[random.randint(0, len(storage_servers_db) - 1)]

        # get list of ss to get replicas
        ss_replicas_list = NSUtils.get_ss_for_replicas(picked_ss, alive_fit_nodes)

        # generate message for client
        message = {"status": "OK", "ss": picked_ss, "replicas": ss_replicas_list}

        return message


    @staticmethod
    def do_db_snapshot():
        print("Gathering info about NamingServer")
        log.info("Gathering info about NamingServer")
        return db.get_db_snapshot(naming_server_db + storage_servers_db)

    @staticmethod
    def do_heart_signal(args):
        # print("Got heartbeat from {}".format(args['ss']))
        # log.info("Got heartbeat from {}".format(args['ss']))
        db.update_ss_life_status(args['ss'])
