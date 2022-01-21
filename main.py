import time

import json
from web3 import Web3
from web3.middleware import geth_poa_middleware
from web3_input_decoder import decode_function
import urllib.request

# вот тут укажи каку-ю нить нормальную ноду
NODE_URI = "https://bsc-dataseed.binance.org/"

STRIKEX_PAIR_ADDRESS = "0X472E71C0E729CBE32B883502F833E6E8F2CD78D2"
PANCAKE_SWAP_ADDRESS = "0X10ED43C718714EB63D5AA57B78B54704E256024E"

STRIKEX_TOKEN_ADDRESS = "0xd6fdde76b8c1c45b33790cc8751d5b88984c44ec"
SWAP_SIG = "0x791ac947"

WATCHING_CONTRACTS = [
    STRIKEX_PAIR_ADDRESS,
    PANCAKE_SWAP_ADDRESS
]

f = urllib.request.urlopen("https://api.bscscan.com/api?module=contract&action=getabi&address=0x472e71c0e729cBe32B883502F833e6e8F2Cd78d2")

STRIPE_PAIR_ABI = json.loads(json.load(f)["result"])

time.sleep(6)

f = urllib.request.urlopen("https://api.bscscan.com/api?module=contract&action=getabi&address=0x10ED43C718714eb63d5aA57B78B54704E256024E")

PANCAKE_SWAP_ABI = json.loads(json.load(f)["result"])

w3 = Web3(Web3.HTTPProvider(NODE_URI))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

if __name__ == '__main__':
    while 1:
        block = w3.eth.get_block('latest', full_transactions=True)
        # для проверки. В этом блоке есть свап 60 STRIKEX на WBNB
        # block = w3.eth.get_block(14390273, full_transactions=True)

        for block_transaction in block.transactions:
            if block_transaction["to"].upper() in WATCHING_CONTRACTS:
                if block_transaction["to"].upper() == PANCAKE_SWAP_ADDRESS:
                    if SWAP_SIG[2:] in block_transaction.input:
                        decode_input = decode_function(PANCAKE_SWAP_ABI, block_transaction["input"])
                        swap_tokens_addresses = decode_input[2][2]
                        if STRIKEX_TOKEN_ADDRESS in swap_tokens_addresses:
                            print(f"STRIKEX swap detect!: {swap_tokens_addresses}")
                            print(f"tx hash: {block_transaction.hash.hex()}")
                            if STRIKEX_TOKEN_ADDRESS == swap_tokens_addresses[0]:
                                strikex_amount = decode_input[0][2] * 1e-18
                                print(f"swap {strikex_amount} STRIKEX -> {swap_tokens_addresses[1]}")
                            if STRIKEX_TOKEN_ADDRESS == swap_tokens_addresses[1]:
                                strikex_amount = decode_input[1][2] * 1e-18
                                print(f"swap {swap_tokens_addresses[0]} -> {strikex_amount} STRIKEX")

                        pass

        time.sleep(1.5)
