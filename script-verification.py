#!/usr/bin/env python

import sys
import hashlib

from Crypto.Hash import SHA512
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Util.asn1 import DerSequence
from binascii import a2b_base64
from base64 import urlsafe_b64decode

hash_file = sys.argv[1]
signature_file = sys.argv[2]

cer_file = "KEYS/clavePribHomologacion.cer"
# key_file = "KEYS/clavePribHomologacion.key"
# csr_file = "KEYS/clavePribHomologacion.csr"
# pfx_file = "KEYS/clavePribHomologacion.pfx"

def get_hash_from_file(hash_file):
    with open(hash_file) as f:
        data = f.readlines()
    hash = data[0]
    print("Hash: " + hash)
    return hash

def get_signature_from_file(sign_file):
    with open(sign_file) as f:
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

hash = get_hash_from_file(hash_file)
signature = get_signature_from_file(signature_file)
verified = verify_data(hash, signature)
print("Verificación %s con PKCS1_v1_5"
       % ("exitosa" if verified else "No exitosa"))