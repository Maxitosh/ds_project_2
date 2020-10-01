
import db_worker as db

class NamingServerCommands:

    def dispatch_command(self, command):
        return getattr(self, 'do_' + command["command"].upper(), None)

    def do_INIT(self, args):
        print("Initialization called by client. Args: ", args)
        if not db.is_db_exists("DFS"):
            db.create_db("DFS")
            db.print_dbs()
        else:
            print("Database exists")
            db.print_dbs()
        return {"status": "OK", "size": 1}
