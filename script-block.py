#!/usr/bin/env python

import sys
import threading
import os
import json
import requests
import time

number_threads = 64
smart_contract_alias = 'CENSO__sc02'
node_url = 'https://prod-001-node.cloud.nxtfi.org/v2'
service_url = 'http://localhost:3050'
scans_folders = ['sc01', 'sc02', 'sc03', 'sc04', 'sc05', 'sc06', 'sc07', 'sc08', 'sc09', 'sc10', 'sc11', 'sc12', 'sc13', 'sc14', 'sc15', 'sc16', 'sc17']
#scans_folders = ['sc18', 'sc19', 'sc20', 'sc21', 'sc22', 'sc23', 'sc24', 'sc25', 'sc26', 'sc27', 'sc28', 'sc29', 'sc30', 'sc31', 'sc32', 'sc33', 'sc34']
dest_folder = sys.argv[1]
threadLimiter = threading.BoundedSemaphore(number_threads)

class send_block_thread(threading.Thread):
    def __init__(self, block):
        self.__block = block
        threading.Thread.__init__(self)
    def run (self):
        threadLimiter.acquire()
        try:
            self.send()
        finally:
            threadLimiter.release()
    def send(self):
        block = self.__block
        x3 = requests.post(node_url + '/newBlock', data = block)
        result = json.loads(x3.text)
        print("Block sended: ", block)
        print("Block result: ", result)


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

def send_block(data_field, last_block):
    data_field = "// IMPORT " + smart_contract_alias + "\n\n" + data_field
    block = {
        'prevHash': last_block['head'],
        'height': last_block['height'] + 1,
        'version': 2,
        'data': data_field,
        'timestamp': round(time.time() * 1000),
        'scope': 'CENSO__sc02',
        'by': 'CENSO'
    }
    sign_result = requests.post(service_url + '/sign-block', data = block)
    signature = json.loads(sign_result.text)

    block['signature'] = signature['signature']
    hash_result = requests.post(service_url + '/generate-hash', data = block)
    hash = json.loads(hash_result.text)

    block['by'] = block['by']
    block['hash'] = hash['hash']
    print("Build block: ", block)

    send_block_thread(json.dumps(block, indent=4)).start()

    return {
        'head': block['hash'],
        'height': block['height']
    }

def search_files(path):
    head_result = requests.get(node_url + '/_head/' + smart_contract_alias)
    last_block = json.loads(head_result.text)

    for scan in scans_folders:
        for root, dirs, files in os.walk(path + '/' + scan):
            images_json = []
            for name in files:
                if name.endswith((".hash")):
                    folder = os.listdir(root)
                    if name.split('.')[0] + '.sign' in folder:
                        images_json.append(get_images_json(root + '/' + name, name.split('.')[0], root.split('/')[-3], root.split('/')[-2], root.split('/')[-1]))
            print('data', json.dumps(images_json, indent=4))
            last_block = send_block(json.dumps(images_json, indent=4), last_block)

search_files(dest_folder)