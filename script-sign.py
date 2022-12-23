#!/usr/bin/env python

import sys
import threading
import os

from Crypto.Hash import SHA256, SHA512
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

number_threads = 12
replace_files = False
dest_folder = sys.argv[1]
key_file = sys.argv[2]
threadLimiter = threading.BoundedSemaphore(number_threads)

# cer_file = "KEYS/clavePribHomologacion.cer"
# key_file = "KEYS/clavePribHomologacion.key"
# csr_file = "KEYS/clavePribHomologacion.csr"
# pfx_file = "KEYS/clavePribHomologacion.pfx"

with open(key_file) as infile:
    privateKeyPEM = infile.read()
privateKey = RSA.importKey(privateKeyPEM)

class sign_thread(threading.Thread):
    def __init__(self, file):
        self.__file = file
        threading.Thread.__init__(self)
    def run (self):
        threadLimiter.acquire()
        try:
            self.sign()
        finally:
            threadLimiter.release()

    def sign(self):
        file = self.__file

        with open(file) as f:
            data = f.readlines()
        print(data[0])

        data = data[0]
        
        # hash_of_data = SHA256.new(b'hola').hexdigest()
        # signature = privateKey.sign(hash_of_data, Crypto.Signature.pkcs1_15)

        hash_object = SHA512.new(data.encode("utf8"))
        signer = PKCS1_v1_5.new(privateKey)
        signature = signer.sign(hash_object)

        print(signature)

        with open(file.split('.')[0] + '.sign', 'wb') as binary_file:
            binary_file.write(signature)

        print("Archivo firmado: ", file)

def search_files(path):
    print(path)
    for root, dirs, files in os.walk(path):
        for name in files:
            if name.endswith((".hash")):
                print(name)
                folder = os.listdir(root)
                if name.split('.')[0] + '.sign' not in folder or replace_files:
                    sign_thread(root + '\\' + name).start()

search_files(dest_folder)
