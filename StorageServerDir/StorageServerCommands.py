import logging as log
import os
import shutil

host_name = os.getenv('HOSTNAME').upper()
log.basicConfig(filename="ss.log", format='[%s] ' % host_name + '%(asctime)s - %(levelname)s - %(message)s',
                level=log.DEBUG)

dir = "/usr/src/app/data/"


class StorageServerCommands:

    def dispatch_command(self, command):
        return getattr(self, 'do_' + command["command"], None)

    @staticmethod
    def do_init():
        print("Initialization called by client")
        log.info("Initialization called by client")
        for root, dirs, files in os.walk('/usr/src/app/data/'):
            for f in files:
                os.unlink(os.path.join(root, f))
            for d in dirs:
                shutil.rmtree(os.path.join(root, d))

        print("Initialization completed, all files removed")
        log.info("Initialization completed, all files removed")
        return 0  # {"status": "OK", "size": 1}

    @staticmethod
    def do_create_file(args):
        print("File creation called by client")
        log.info("File creation called by client")

        directories_to_create = ""
        for directory in args["file_name"].split('/')[0:len(args["file_name"].split('/'))-1]:
            directories_to_create += directory + "/"
            os.system("mkdir {}".format(dir+directories_to_create))


        os.system("touch {}".format(dir + args["file_name"]))

        print("File {} created".format(args["file_name"]))
        log.info("File {} created".format(args["file_name"]))
        return 0  # {"status": "OK", "size": 1}
