# python-script

## Install requirements

`pip install -r requirements.txt`

## Use hash script

### Parameters
- origin folder
- destination folder

`python script-hash.py "C:\\folder_ori" "C:\\folder_dest"`

## Use sign script

### Parameters
- origin folder
- private key

`python script-sign.py "C:\\folder_ori" "C:\\KEYS\\clavePribHomologacion.key"`

## Use verification script

### Parameters
- hash file
- signature file

`python script-verification.py "C:\\hash_file.hash" "C:\\sign_file.sign"`
