import logging as log
import os
import shutil

host_name = os.getenv('HOSTNAME').upper()
log.basicConfig(filename="ss.log", format='[%s] ' % host_name + '%(asctime)s - %(levelname)s - %(message)s',
                level=log.DEBUG)


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
        return 0#{"status": "OK", "size": 1}