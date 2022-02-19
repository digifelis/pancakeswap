import json
import config as bilgiler
from web3 import Web3
import sys, getopt
import os

# metamasktan belirtilen cüzdana token yollar
def gonder(status, hedef_adres, miktar, contract_address):
    if status == "real":
        bsc = "https://bsc-dataseed.binance.org/"
    if status == "test":
        bsc = "https://data-seed-prebsc-1-s1.binance.org:8545/"
    web3 = Web3(Web3.HTTPProvider(bsc))
    if web3.isConnected() == False:
        return {"success":0, "data":"connection failed"}
    else:
        main_address= bilgiler.sender_address
        to_address = hedef_adres
        abi = bilgiler.sellAbi
        contract = web3.eth.contract(address=contract_address, abi=abi)
        balanceOf = contract.functions.balanceOf(main_address).call()
        send =  web3.toWei(miktar, 'ether')
        if balanceOf > send:
            nonce = web3.eth.getTransactionCount(main_address)
            chk_to = web3.toChecksumAddress(to_address)
            token_tx = contract.functions.transfer(chk_to, send).buildTransaction({
                'chainId':97, 'gas': 200000,'gasPrice': web3.toWei('20','gwei'), 'nonce':nonce
            })
            sign_txn = web3.eth.account.signTransaction(token_tx, private_key=bilgiler.private)
            trx_hash = web3.eth.sendRawTransaction(sign_txn.rawTransaction)
            print(f"Transaction has been sent to {trx_hash.hex()}")
            return {"trx_hash":trx_hash.hex(), "success":1, "data":"successfully sent transaction"}
        else:
            return {"success":0, "data": "transaction failed"}



# satın alınabilir token listesini getir
listToken = "listtoken.json"
tokennameArg = "mns"
targetAddressArg = ""
amountArg = 0

try:
    with open(listToken) as f:
        d = json.load(f)
except ValueError:
    print("token lstesi dosyası açılamadı")
    print(ValueError)

#komut satırından bilgi alma
argv = sys.argv[1:]
try:
  opts, args = getopt.getopt(argv,"ht:a:b:",["targetAddress=", "amount=", "tokenname="])
except getopt.GetoptError:
  print("sendtoken.py -t <targetAddress> -a <amount token> -b <token name>")
  sys.exit(2)

for opt, arg in opts:
  if opt == '-h':
      print("sendtoken.py -t <targetAddress> -a <amount token> -b <token name>")
      sys.exit()
  elif opt in ("-t", "--targetAddress"):
      targetAddressArg = arg
  elif opt in ("-a", "--amount"):
      amountArg = arg
  elif opt in ("-b", "--tokenname"):
      tokennameArg = arg

# python sendtoken.py -t 0xf0b2db51A24431a70Ae67c8c512Cc8F02BFc7e84 -a 100 -b mns
gonder("test", targetAddressArg, amountArg, d[tokennameArg])