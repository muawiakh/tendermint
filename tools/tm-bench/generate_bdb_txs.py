# Place holder until BigchainDB go driver is in good shape.
from bigchaindb import BigchainDB
from bigchaindb.models import Transaction
from bigchaindb.common.crypto import generate_key_pair
import datetime
import json
import base64
import sys
import os



def help():
    help_string = """
    Used to generate BigchainDB transactions.
    Disclaimer: Only a placeholder file using python bigchaindb driver
    until bigchaindb go driver is ready.
    Usage:
    python generate_bdb_txs.py <base_directory_to_store_txs> <num_files> <num_txs_per_file> <JSON format>
    """
    print(help_string)
    sys.exit(1)

if len(sys.argv) <= 1 or len(sys.argv) < 4:
    help()

base_dir = str(sys.argv[1])
try:
    num_files = int(sys.argv[2])
    num_txs = int(sys.argv[3])
except ValueError:
    raise Exception("Num of files and num of txs must be an integer")
try:
    if sys.argv[4].lower() == "json":
        b64_encoded = False
    else:
        b64_encoded = True
except IndexError:
    b64_encoded = True

for i in range(num_files):
    if os.path.isdir(base_dir):
        with open(base_dir + '/txns_' + str(i), 'w') as tx_file:
            for i in range(0, num_txs):
                alice = generate_key_pair()
                bicycle = {'data': {'timestamp': str(datetime.datetime.now()),},}
                tx = Transaction.create([alice.public_key],
                                        [([alice.public_key], 1)],
                                        asset=bicycle).sign([alice.private_key])
                if b64_encoded:
                    tx = base64.b64encode(json.dumps(tx.to_dict()).encode('utf8')).decode('utf8')
                else:
                    tx = json.dumps(tx.to_dict())
                print(i)
                tx_file.write(tx)
                tx_file.write('\n')
    else:
        raise NotADirectoryError(f"Base directory: '{base_dir}' does not exist.")
