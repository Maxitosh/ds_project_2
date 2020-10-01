import db_worker as db
import logging as log

log.basicConfig(filename="dfs.log", format='%(asctime)s - %(levelname)s - %(message)s', level=log.DEBUG)

storage_servers = ["SS1", "SS2", "SS3"]


class NamingServerCommands:

    def dispatch_command(self, command):
        return getattr(self, 'do_' + command["command"], None)

    @staticmethod
    def do_init():
        print("Initialization called by client")
        log.info("Initialization called by client")

        if db.is_db_exists("DFS"):
            db.drop_db("DFS")
            db.init_db("DFS", ["Files", "Directories"] + storage_servers)
            return {"status": "OK", "size": 1}
        else:
            return {"status": "FAIL", "size": -1}

    @staticmethod
    def do_create_file(args):
        print("Creation of file {}".format(args["file_name"]))
        db.insert_item("DFS", "Files", args)
        return {"status": "OK"}

    @staticmethod
    def do_db_snapshot():
        print("Gathering info about NamingServer")
        log.info("Gathering info about NamingServer")
        return db.get_all_items("DFS")
