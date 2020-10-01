import db_worker as db


class NamingServerCommands:

    def dispatch_command(self, command):
        return getattr(self, 'do_' + command["command"], None)

    @staticmethod
    def do_init(args):
        print("Initialization called by client. Args: ", args)
        if not db.is_db_exists("DFS"):
            db.create_db("DFS")
            db.print_dbs()
        else:
            print("Database exists")
            db.print_dbs()
        return {"status": "OK", "size": 1}

    @staticmethod
    def do_create_file(args):
        print("Creation of file {}".format(args["file_name"]))
        db.insert_item("DFS", "Files", args)
        return {"status": "OK"}

    @staticmethod
    def do_info():
        print("Gathering info about NamingServer")
        return db.get_all_items("DFS")
