import base64
import logging as log
import os
import shutil
from StorageServerUtils import StorageServerUtils

dir = "/usr/src/app/data/"
SSUtils = StorageServerUtils()


class StorageServerCommands:

    def __init__(self):
        host_name = '[' + os.getenv('HOSTNAME').upper() + '] '
        log.basicConfig(force=True, filename="ss.log",
                        format=('%(asctime)s - %(levelname)s - ' + host_name + '%(message)s'),
                        level=log.DEBUG)

    def dispatch_command(self, command):
        return getattr(self, 'do_' + command["command"], None)

    def do_init(self, args):
        print("Initialization called by client")
        log.info("Initialization called by client")
        for root, dirs, files in os.walk('/usr/src/app/data/'):
            for f in files:
                os.unlink(os.path.join(root, f))
            for d in dirs:
                shutil.rmtree(os.path.join(root, d))

        print("Initialization completed, all files removed")
        log.info("Initialization completed, all files removed")
        return {"status": "OK"}

    def do_create_file(self, args):
        print("File creation called by client")
        log.info("File creation called by client")

        # create directories for new file
        directories = SSUtils.extract_dirs_from_filename(args['file_name'])
        for directory in directories:
            SSUtils.mkdir(directory)

        # create empty file
        SSUtils.create_empty_file(args['file_name'])

        # this function will be called on another SS, so it should not replicate anymore
        if len(args['replicas']) != 0:
            # send replicas to other SS
            SSUtils.send_replicas_of_empty_file_to_ss(args['file_name'], args['replicas'])

        print("File {} created".format(args["file_name"]))
        log.info("File {} created".format(args["file_name"]))
        return {"status": "OK", "size": 0}

    def do_read_file(self, args):
        print("File {} reading called by client".format(args['file_name']))
        log.info("File {} reading called by client".format(args['file_name']))

        SSUtils.send_file(args['socket'], dir + args['file_name'])
        return 0

    def do_write_file(self, args):
        print("File writing called by client")
        log.info("File writing called by client")

        # create directories for new file
        directories = SSUtils.extract_dirs_from_filename(args['file_name'])
        for directory in directories:
            SSUtils.mkdir(directory)

        SSUtils.get_file(args['socket'], dir + args['file_name'])

        # this function will be called on another SS, so it should not replicate anymore
        if len(args['replicas']) != 0:
            # send replicas to other SS
            SSUtils.send_file_replicas_to_ss(args['file_name'], args['replicas'])

        print("File {} downloaded".format(args["file_name"]))
        log.info("File {} downloaded".format(args["file_name"]))
        return 0  # {"status": "OK", "size": args['size']}

    def do_delete_file(self, args):
        print("File {} deleting called by client".format(args['file_name']))
        log.info("File {} deleting called by client".format(args['file_name']))

        try:
            SSUtils.delete_file(args['file_name'])
        except Exception as e:
            print(e)
            log.error(e)

        return {'status': 'OK'}

    def do_copy_file(self, args):
        print("File {} copy to {}".format(args['file_name'], args['directory']))
        log.info("File {} copy to {}".format(args['file_name'], args['directory']))

        try:
            SSUtils.copy_file(args['file_name'], args['directory'])
        except Exception as e:
            print(e)
            log.error(e)
        return {'status': 'OK'}