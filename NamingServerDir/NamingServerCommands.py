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

    def do_init(self):
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

        NSUtils.insert_dirs_into_db("DFS", ["/usr/src/app/data/"])
        # get list of alive nodes
        alive_nodes = NSUtils.get_alive_ss(storage_servers_db)

        # remove data from SS
        for ss in alive_nodes:
            message = {"command": "init"}
            response = NSUtils.send_message(ss, message)
            log.info("Init response of {}: {}".format(ss, response))
            NSUtils.insert_dirs_into_db(ss, ["/usr/src/app/data/"])
        return {"status": "OK", "size_bits": storage_size}

    def do_create_file(self, args):
        print("Creation of file {}".format(NSUtils.get_full_path(args["file_name"])))
        log.info("Creation of file {}".format(NSUtils.get_full_path(args["file_name"])))

        # check if file exists
        if NSUtils.is_file_exists((NSUtils.get_full_path(args['file_name']))):
            return {"status": "File exists"}

        # update main file system
        NSUtils.insert_file_into_db("DFS", args)
        # update dirs of file system
        NSUtils.insert_dirs_into_db_using_file_name("DFS", args['file_name'])

        # get list of alive nodes
        alive_nodes = NSUtils.get_alive_ss(storage_servers_db)
        # choose alive SS
        picked_ss = random.randint(0, len(alive_nodes) - 1)

        for i in range(len(alive_nodes)):
            # update ss file system
            NSUtils.insert_file_into_db(alive_nodes[i], args)
            # update ss dirs
            NSUtils.insert_dirs_into_db_using_file_name(alive_nodes[i], args['file_name'])

        # get list of ss to get replicas
        ss_replicas_list = NSUtils.get_ss_for_replicas(alive_nodes[picked_ss], alive_nodes)

        message = {"command": "create_file", "file_name": args["file_name"], "replicas": ss_replicas_list}
        NSUtils.send_message(alive_nodes[picked_ss], message)

        return {"status": "OK"}

    def do_read_file(self, args):
        print("Reading of file {}".format(NSUtils.get_full_path(args["file_name"])))
        log.info("Reading of file {}".format(NSUtils.get_full_path(args["file_name"])))

        if not NSUtils.is_file_exists(NSUtils.get_full_path(args['file_name'])):
            return {'status': 'File does not exist'}

        # get list of alive nodes
        alive_nodes = NSUtils.get_alive_ss(storage_servers_db)
        # choose alive SS
        picked_ss = alive_nodes[random.randint(0, len(alive_nodes) - 1)]

        # get file size
        file_size = NSUtils.get_file_size(args['file_name'])

        return {'status': 'OK', 'ss': picked_ss, 'file_size': file_size}

    def do_write_file(self, args):
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
        NSUtils.insert_dirs_into_db_using_file_name("DFS", args['file_name'])

        # update ss file system
        for ss in alive_fit_nodes:
            NSUtils.insert_file_into_db(ss, args)
            # update dirs of file system
            NSUtils.insert_dirs_into_db_using_file_name(ss, args['file_name'])

        # update storages size
        NSUtils.update_storages_size(alive_fit_nodes, args['size'])

        # choose any alive fit ss node
        picked_ss = storage_servers_db[random.randint(0, len(storage_servers_db) - 1)]

        # get list of ss to get replicas
        ss_replicas_list = NSUtils.get_ss_for_replicas(picked_ss, alive_fit_nodes)

        # generate message for client
        message = {"status": "OK", "ss": picked_ss, "replicas": ss_replicas_list}

        return message

    def do_delete_file(self, args):
        print("Delete file {}".format(args['file_name']))
        log.info("Delete file {}".format(args['file_name']))

        # check if file exists
        if not NSUtils.is_file_exists(NSUtils.get_full_path(args['file_name'])):
            return {'status': 'File does not exist'}

        # get file size
        file_size = NSUtils.get_file_size(args['file_name'])

        # delete file from DFS
        NSUtils.delete_entry_from_db('DFS', 'Files', {'file_name': NSUtils.get_full_path(args['file_name'])})

        # get alive nodes
        alive_nodes = NSUtils.get_alive_ss(storage_servers_db)
        for ss in alive_nodes:
            NSUtils.delete_entry_from_db(ss, 'Files', {'file_name': NSUtils.get_full_path(args['file_name'])})

        # update storages size

        print("Deletion file size is {}".format(file_size))
        NSUtils.update_storages_size(alive_nodes, -file_size)
        # send commands to ss
        message = {"command": "delete_file", "file_name": NSUtils.get_full_path(args["file_name"])}
        for ss in alive_nodes:
            NSUtils.send_message(ss, message)

        return {'status': 'OK'}

    def do_info_file(self, args):
        print("Info about file {}".format(args['file_name']))
        log.info("Info about file {}".format(args['file_name']))

        file_data = NSUtils.get_entry_from_db("DFS", "Files", {'file_name': NSUtils.get_full_path(args['file_name'])})
        if file_data == 0: return {'status': 'Failed'}
        alive_nodes = NSUtils.get_alive_ss(storage_servers_db)
        return {'status': 'OK', 'file_name': file_data['file_name'], 'file_size': file_data['size'],
                'nodes': alive_nodes}

    def do_copy_file(self, args):
        print("Copy file {} to {}".format(NSUtils.get_full_path(args['file_name']),
                                          NSUtils.get_full_path(args['directory'])))
        log.info("Copy file {} to {}".format(NSUtils.get_full_path(args['file_name']),
                                             NSUtils.get_full_path(args['directory'])))

        # get clear file name
        file_name_without_dirs = args['file_name'].split('/')[len(args['file_name'].split('/')) - 1]

        # get target file name
        target_file = NSUtils.get_entry_from_db("DFS", "Files",
                                                {'file_name': (NSUtils.get_full_path(
                                                    args['directory']) + file_name_without_dirs)})
        if target_file != 0:
            return {'status': 'File already exists'}

        dir_data = NSUtils.get_entry_from_db("DFS", "Directories",
                                             {'directory_name': NSUtils.get_full_path(args['directory'])})
        if dir_data == 0: return {'status': 'Failed, no directory exists'}

        # get file data
        file_data = NSUtils.get_entry_from_db("DFS", "Files", {'file_name': NSUtils.get_full_path(args['file_name'])})
        if file_data == 0: return {'status': 'File does not exist'}

        # get alive nodes
        alive_nodes = NSUtils.get_alive_ss(storage_servers_db)
        # get alive fit nodes
        alive_fit_nodes = NSUtils.get_fit_nodes(alive_nodes, file_data['size'])

        # check if file does not fit
        if len(alive_fit_nodes) == 0:
            return {'status': 'Not enough space or no alive nodes'}

        # update main file system
        NSUtils.insert_file_into_db("DFS",
                                    {'file_name': (args['directory'] + file_name_without_dirs),
                                     'size': file_data['size']})

        # update ss file system
        for ss in alive_fit_nodes:
            NSUtils.insert_file_into_db(ss, {
                'file_name': (args['directory'] + file_name_without_dirs),
                'size': file_data['size']})

        # update storages size
        NSUtils.update_storages_size(alive_fit_nodes, file_data['size'])

        # send commands to ss
        message = {"command": "copy_file", "file_name": file_data["file_name"],
                   'directory': NSUtils.get_full_path(args["directory"])}
        for ss in alive_nodes:
            NSUtils.send_message(ss, message)

        return {'status': 'OK'}

    def do_move_file(self, args):
        print("Move file {} to {}".format(NSUtils.get_full_path(args['file_name']),
                                          NSUtils.get_full_path(args['directory'])))
        log.info("Move file {} to {}".format(NSUtils.get_full_path(args['file_name']),
                                             NSUtils.get_full_path(args['directory'])))

        # get clear file name
        file_name_without_dirs = args['file_name'].split('/')[len(args['file_name'].split('/')) - 1]

        # get target file name
        target_file = NSUtils.get_entry_from_db("DFS", "Files",
                                                {'file_name': (NSUtils.get_full_path(
                                                    args['directory']) + file_name_without_dirs)})
        if target_file != 0:
            return {'status': 'File already exists'}

        dir_data = NSUtils.get_entry_from_db("DFS", "Directories",
                                             {'directory_name': NSUtils.get_full_path(args['directory'])})
        if dir_data == 0: return {'status': 'Failed, no directory exists'}

        # get file data
        file_data = NSUtils.get_entry_from_db("DFS", "Files", {'file_name': NSUtils.get_full_path(args['file_name'])})
        if file_data == 0: return {'status': 'File does not exist'}

        # get alive nodes
        alive_nodes = NSUtils.get_alive_ss(storage_servers_db)
        # get alive fit nodes
        alive_fit_nodes = NSUtils.get_fit_nodes(alive_nodes, file_data['size'])

        # check if file does not fit
        if len(alive_fit_nodes) == 0:
            return {'status': 'Not enough space or no alive nodes'}

        # update main file system
        NSUtils.insert_file_into_db("DFS",
                                    {'file_name': (args['directory'] + file_name_without_dirs),
                                     'size': file_data['size']})
        NSUtils.delete_entry_from_db('DFS', "Files", {'file_name': NSUtils.get_full_path(args['file_name'])})

        # update ss file system
        for ss in alive_fit_nodes:
            NSUtils.insert_file_into_db(ss, {
                'file_name': (args['directory'] + file_name_without_dirs),
                'size': file_data['size']})
            NSUtils.delete_entry_from_db(ss, "Files", {'file_name': NSUtils.get_full_path(args['file_name'])})

        # send commands to ss
        message = {"command": "move_file", "file_name": file_data["file_name"],
                   'directory': NSUtils.get_full_path(args["directory"])}
        for ss in alive_nodes:
            NSUtils.send_message(ss, message)

        return {'status': 'OK'}

    def do_read_directory(self, args):
        print("Read directory {}".format(args['directory_name']))
        log.info("Read directory {}".format(args['directory_name']))

        # check if directory exists
        dir_data = NSUtils.get_entry_from_db("DFS", "Directories",
                                             {'directory_name': NSUtils.get_full_path(args['directory_name'])})
        if dir_data == 0: return {'status': 'Failed, no directory exists'}

        entries = NSUtils.read_directory(NSUtils.get_full_path(args['directory_name']))

        return {'status': 'OK', 'data': entries}

    def do_db_snapshot(self):
        print("Gathering info about NamingServer")
        log.info("Gathering info about NamingServer")
        return db.get_db_snapshot(naming_server_db + storage_servers_db)

    def do_heart_signal(self, args):
        # TODO check here for SS storages consistency
        # print("Got heartbeat from {}".format(args['ss']))
        # log.info("Got heartbeat from {}".format(args['ss']))
        db.update_ss_life_status(args['ss'])
