import logging as log
import os

log.basicConfig(filename="client.log", format='[CU] %(asctime)s - %(levelname)s - %(message)s',
                level=log.DEBUG, force=True)


class ClientUtils:

    def get_filename_and_dfs_filename(self):
        print("Enter local file name and name of file to write in DFS: ")
        inp = input().split(' ')
        file_name = inp[0]
        dfs_file_name = inp[1]

        return file_name, dfs_file_name

    def get_file_size_in_bits(self, file_name):
        try:
            # return file size in bits
            file_size = os.path.getsize(file_name) * 8
            print("File {} of size {}".format(file_name, file_size))
            return file_size
        except Exception as e:
            print(e)
            log.error(e)
