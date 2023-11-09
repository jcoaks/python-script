#!/usr/bin/env python

import sys

from Crypto.Hash import SHA512
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from base64 import urlsafe_b64encode

hash = sys.argv[1]
key_file = sys.argv[2]

with open(key_file) as infile:
    privateKeyPEM = infile.read()
privateKey = RSA.importKey(privateKeyPEM)

def sign(str_hash):
    hash_object = SHA512.new(str_hash.encode("utf8"))
    signer = PKCS1_v1_5.new(privateKey)
    signature_binary = signer.sign(hash_object)
    signature_bytes = urlsafe_b64encode(signature_binary)
    signature_str = signature_bytes.decode("utf-8")

    print("Firma (Copia y pega esta firma en el navegador en el campo 'Firma generada')")
    print(signature_str)

sign(hash)