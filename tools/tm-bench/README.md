# tm-bench

Tendermint and BigchainDB benchmarking tool:

- https://github.com/muawiakh/tendermint/tree/tm-bench-bdb

For example, the following:

    tm-bench -ws -T 10 -r 1000 localhost:26657

will output something like:

    Stats          Avg       StdDev     Max      Total     
    Txs/sec        818       532        1549     9000      
    Blocks/sec     0.818     0.386      1        9


## Quick Start

### Tendermint Stand alone

[Install Tendermint](https://github.com/tendermint/tendermint#install)
This currently is setup to work on tendermint's develop branch. Please ensure
you are on that. (If not, update `tendermint` and `tmlibs` in gopkg.toml to use
  the master branch.)

then run:

    tendermint init
    tendermint node --proxy_app=kvstore

    tm-bench -ws localhost:26657

with the last command being in a seperate window.

### Tendermint + BigchainDB

[Install BigchainDB](https://docs.bigchaindb.com/projects/contributing/en/latest/dev-setup-coding-and-contribution-process/run-node-with-docker-compose.html)

The above mentioned guide will deploy a BigchainDB + Tendermint + MongoDB local setup with Docker containers.

You can benchmark BigchainDB + Tendermint using two strategies:

- Send BigchainDB compatible transactions(base64 encoded string) to Tendermint Websocket
  - Generate BigchainDB Transactions
    - *NOTE*: We need this step until we have a working BigchainDB go driver in place
```bash
$ cd tendermint/tools/tm-bench
$ python generate_bdb_txs
    Used to generate BigchainDB transactions.
Disclaimer: Only a placeholder file using python bigchaindb driver
until bigchaindb go driver is ready.
Usage:
python generate_bdb_txs.py <base_directory_to_store_txs> <num_files> <num_txs_per_file> <JSON format>
$ python3 generate_bdb_txs.py bdb_txs 10 1000
....
....
# generate 1000 BigchainDB b64encoded transactions in 20 files. 
# We generate the transactions in different files because we can have multiple
# connections while running the tm-bench tool and each connection has its own
# transaction file 
```
  - Run `tm-bench`
```bash
$ tm-bench -ws -bdbTx localhost:26657 -bdb-txs-base-dir bdb_txs
```
- Send BigchainDB(JSON) transactions to BigchainDB HTTP Interface
  - Generate BigchainDB Transactions
    - *NOTE*: We need this step until we have a working BigchainDB go driver in place
```bash
$ cd tendermint/tools/tm-bench
$ python generate_bdb_txs
    Used to generate BigchainDB transactions.
Disclaimer: Only a placeholder file using python bigchaindb driver
until bigchaindb go driver is ready.
Usage:
python generate_bdb_txs.py <base_directory_to_store_txs> <num_files> <num_txs_per_file> <bool>
$ python3 generate_bdb_txs.py bdb_txs 10 1000 json
....
....
# generate 1000 BigchainDB JSON based transactions in 20 files. 
# We generate the transactions in different files because we can have multiple
# connections while running the tm-bench tool and each connection has its own
# transaction file 
```
  - Run `tm-bench`
```bash
$ tm-bench -bdb-http localhost:26657 -bdb-txs-base-dir bdb_txs
```


#### Usage

Tendermint and BigchainDB benchmarking tool.

``` bash
Usage:
	tm-bench [-c 1] [-T 10] [-r 1000] [-s 250] [-ws] [-bdb-http] [-bdb-tx] [endpoints] [-output-format <plain|json> [-broadcast-tx-method <async|sync|commit>]]

Examples:
	tm-bench -ws localhost:26657
Flags:
  -T int
    	Exit after the specified amount of time in seconds (default 10)
  -bdb-http
    	Send transacations to BigchainDB HTTP API
  -bdb-txs-base-dir string
    	Base directory to access the BigchainDB transactions (default "bdb_txs")
  -bdbTx
    	Send BigchainDB transaction to Tendermint websocket
  -broadcast-tx-method string
    	Broadcast method: async (no guarantees; fastest), sync (ensures tx is checked) or commit (ensures tx is checked and committed; slowest) (default "async")
  -c int
    	Connections to keep open per endpoint (default 1)
  -output-format string
    	Output format: plain or json (default "plain")
  -r int
    	Txs per second to send in a connection (default 1000)
  -s int
    	The size of a transaction in bytes. (default 250)
  -v	Verbose output
  -ws
    	Send transactions to Tendermint websocket
```

## How stats are collected

These stats are derived by having each connection send transactions at the
specified rate (or as close as it can get) for the specified time.
After the specified time, it iterates over all of the blocks that were created
in that time.
The average and stddev per second are computed based off of that, by
grouping the data by second.

To send transactions at the specified rate in each connection, we loop
through the number of transactions.
If its too slow, the loop stops at one second.
If its too fast, we wait until the one second mark ends.
The transactions per second stat is computed based off of what ends up in the
block.

Note that there will be edge effects on the number of transactions in the first
and last blocks.
This is because transactions may start sending midway through when tendermint
starts building the next block, so it only has half as much time to gather txs
that tm-bench sends.
Similarly the end of the duration will likely end mid-way through tendermint
trying to build the next block.

Each of the connections is handled via two separate goroutines. 
