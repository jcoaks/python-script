#!/usr/bin/env python

import sys
import threading
import os

from Crypto.Hash import SHA256, SHA512
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Util.asn1 import DerSequence
from binascii import a2b_base64
from base64 import urlsafe_b64decode, urlsafe_b64encode
from Crypto.Util.number import bytes_to_long, long_to_bytes

number_threads = 12
replace_files = False
dest_folder = sys.argv[1]
key_file = sys.argv[2]
threadLimiter = threading.Semaphore(number_threads)

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
        signature_binary = signer.sign(hash_object)
        signature_bytes = urlsafe_b64encode(signature_binary)
        signature_str = signature_bytes.decode("utf-8")

        with open(file.split('.')[0] + '.sign', 'w') as file_sign:
            file_sign.write(signature_str)

        print(signature_str)
        print("Archivo firmado: ", file)

        ##result = verify_data(data, signature_str)
        ##print("Archivo verificado: ", result, file)

def maybe_pad(s):
    return (s + '=' * (4 - len(s) % 4))

def get_publickey_from_cert(filename):
    cert_in_pem_format = open(filename).read()
    lines = cert_in_pem_format.replace(" ", "").split()
    der = a2b_base64(''.join(lines[1:-1]))

    cert = DerSequence()
    cert.decode(der)

    tbsCertificate = DerSequence()
    tbsCertificate.decode(cert[0])
    subjectPublicKeyInfo = tbsCertificate[6]

    publicKey = RSA.importKey(subjectPublicKeyInfo)
    return publicKey.publickey()

def verify_data(data, signature):
    hash_object = SHA512.new(data.encode("utf8"))
    signature_binary = urlsafe_b64decode(signature.encode("utf-8"))
    publicKey = get_publickey_from_cert('KEYS/clavePribHomologacion.cer')
    verifier = PKCS1_v1_5.new(publicKey)
    verified = verifier.verify(hash_object, signature_binary)
    #print("Verificación %s con PKCS1_v1_5"
    #        % ("exitosa" if verified else "No exitosa"))
    return verified

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
