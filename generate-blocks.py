#!/usr/bin/env python

import sys
import threading
import os
import json
import requests
import time
import hashlib
from Crypto.PublicKey import RSA
from Crypto.Signature import pss
from Crypto.Hash import SHA256
import binascii

number_threads = 64
by = 'CENSO'
scope = 'CENSO__SC'
smart_contract_alias = 'CENSO__SC'
node_url = 'https://prod-001-node.cloud.nxtfi.org/v2'
#node_url = 'http://localhost:5300/development/v2'
service_url = 'http://localhost:3050'
scans_folders = ['sc01', 'sc02', 'sc03', 'sc04', 'sc05', 'sc06', 'sc07', 'sc08', 'sc09', 'sc10', 'sc11', 'sc12', 'sc13', 'sc14', 'sc15', 'sc16', 'sc17']
#scans_folders = ['sc18', 'sc19', 'sc20', 'sc21', 'sc22', 'sc23', 'sc24', 'sc25', 'sc26', 'sc27', 'sc28', 'sc29', 'sc30', 'sc31', 'sc32', 'sc33', 'sc34']
dest_folder = sys.argv[1]
threadLimiter = threading.BoundedSemaphore(number_threads)

class send_block_thread(threading.Thread):
    def __init__(self, block, hash):
        self.__block = block
        self.__hash = hash
        threading.Thread.__init__(self)
    def run (self):
        threadLimiter.acquire()
        try:
            self.send()
        finally:
            threadLimiter.release()
    def send(self):
        block = self.__block
        hash = self.__hash
        #x3 = requests.post(node_url + '/newBlock', data = block)
        #result = json.loads(x3.text)
        f = open("_block/" + hash + ".json", "x")
        f.write(block)
        f.close()
        print("Block writed")


def get_images_json(file, filename, scanner, pallet, box):
    with open(file) as f1:
        data1 = f1.readlines()
    filehash = data1[0]

    with open(file.split('.')[0] + '.sign') as f2:
        data2 = f2.readlines()
    filesignature = data2[0]

    data = {}
    data['filename'] = filename
    data['scanner'] = scanner
    data['pallet'] = pallet
    data['box'] = box
    data['hash'] = filehash
    data['signature'] = filesignature

    return data

def load_key(private_key_path):
    key_file = open(private_key_path, 'r').read()
    private = RSA.import_key(key_file)
    return private
private_key = load_key("CENSO.key")

def send_block(data_field, last_block, counter):
    data_field = "// IMPORT " + smart_contract_alias + "\n\n" + data_field
    block = {
        'prevHash': last_block['head'],
        'height': last_block['height'] + 1,
        'version': 2,
        'data': data_field,
        'timestamp': round(time.time() * 1000),
        'scope': scope,
        'by': by
    }

    # sign_result = requests.post(service_url + '/sign-block', data = block)
    # signature = json.loads(sign_result.text)
    # signature0 = signature['signature']

    # hash_result = requests.post(service_url + '/generate-hash', data = block)
    # hash = json.loads(hash_result.text)
    # hash0 = hash['hash']

    msg = json.dumps(block).encode('utf-8')
    hashs = SHA256.new(msg)
    signer = pss.new(private_key)
    signature = signer.sign(hashs)
    block['signature'] = binascii.hexlify(signature).decode()

    block['hash'] = hashlib.sha256(json.dumps(block).encode('utf-8')).hexdigest()

    # print("signature0", signature0)
    # print("signature", block['signature'])
    # print("hash0", hash0)
    # print("hash", block['hash'])

    send_block_thread(json.dumps(block, indent=4), block['hash']).start()

    return {
        'head': block['hash'],
        'height': block['height']
    }

def search_files(path):
    head_result = requests.get(node_url + '/_head/' + smart_contract_alias)
    last_block = json.loads(head_result.text)

    #print("Last block: ", last_block)
    counter = 0
    for scan in scans_folders:
        for root, dirs, files in os.walk(path + '\\' + scan):
            images_json = []
            for name in files:
                if name.endswith((".hash")):
                    folder = os.listdir(root)
                    if name.split('.')[0] + '.sign' in folder:
                        counter += 1
                        images_json.append(get_images_json(root + '/' + name, name.split('.')[0], root.split('\\')[-3], root.split('\\')[-2], root.split('\\')[-1]))
                        if counter == 50:
                            #print('data', json.dumps(images_json, indent=4))
                            last_block = send_block(json.dumps(images_json, indent=4), last_block, counter)
                            images_json = []
                            counter = 0
            if counter > 0:
                #print('data', json.dumps(images_json, indent=4))
                last_block = send_block(json.dumps(images_json, indent=4), last_block, counter)
                images_json = []
                counter = 0

search_files(dest_folder)