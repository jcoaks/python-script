#!/usr/bin/env python

import sys
import hashlib

from Crypto.Hash import SHA512
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Util.asn1 import DerSequence
from binascii import a2b_base64
from base64 import urlsafe_b64decode

tic_file = sys.argv[1]
signature_file = sys.argv[2]

cer_file = "KEYS/clavePribHomologacion.cer"
# key_file = "KEYS/clavePribHomologacion.key"
# csr_file = "KEYS/clavePribHomologacion.csr"
# pfx_file = "KEYS/clavePribHomologacion.pfx"

def open_tic_file(file):
    BUF_SIZE = 65536
    sha512 = hashlib.sha512()
    with open(file, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            sha512.update(data)
        print("Sha512: {0}".format(sha512.hexdigest()))
        return sha512.hexdigest()

def get_signature_file(file):
    with open(file) as f:
        data = f.readlines()
    signature = data[0]
    print("Signature: " + signature)
    return signature

def verify_data(data, signature):
    hash_object = SHA512.new(data.encode("utf8"))
    signature_binary = urlsafe_b64decode(signature.encode("utf-8"))
    publicKey = get_publickey_from_cert(cer_file)
    verifier = PKCS1_v1_5.new(publicKey)
    verified = verifier.verify(hash_object, signature_binary)
    return verified

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

hash = open_tic_file(tic_file)
signature = get_signature_file(signature_file)
verified = verify_data(hash, signature)
print("Verificación %s con PKCS1_v1_5"
       % ("exitosa" if verified else "No exitosa"))