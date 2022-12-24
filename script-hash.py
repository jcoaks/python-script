#!/usr/bin/env python

import sys
import hashlib
import threading
import os

number_threads = 12
replace_files = False
orig_folder = sys.argv[1]
dest_folder = sys.argv[2]

threadLimiter = threading.BoundedSemaphore(number_threads)

BUF_SIZE = 65536  # lets read stuff in 64kb chunks!

#sha256 = hashlib.sha256()
sha512 = hashlib.sha512()

class hash_thread(threading.Thread):
    def __init__(self, file):
        self.__file = file
        threading.Thread.__init__(self)
    def run (self):
        threadLimiter.acquire()
        try:
            self.hash()
        finally:
            threadLimiter.release()

    def hash(self):
        file = self.__file
        print(file)
        with open(orig_folder + file, 'rb') as f:
            while True:
                data = f.read(BUF_SIZE)
                if not data:
                    break
                sha512.update(data)
            with open(dest_folder + file.split('.')[0] + '.hash', 'w') as f2:
                f2.write(sha512.hexdigest())
            print("Hash creado: ", file)
            print("Sha512: {0}".format(sha512.hexdigest()))


def search_files(path):
    for root, dirs, files in os.walk(path):
        if root != path and not os.path.exists(dest_folder + root.split(orig_folder)[1]):
            os.makedirs(dest_folder + root.split(orig_folder)[1])
        for name in files:
            if name.endswith((".tic")):
                folder = os.listdir(dest_folder + root.split(orig_folder)[1])
                if name.split('.')[0] + '.hash' not in folder or replace_files:
                    hash_thread(root.split(orig_folder)[1] + '\\' + name).start()

search_files(orig_folder)
