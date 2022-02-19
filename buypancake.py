from web3 import Web3

import config as bilgiler
import time
from time import sleep

import json
import sys, getopt
import os

# satın alınabilir token listesini getir
listToken = "listtoken.json"
tokenamountArg = 1000000000
amountArg = 0
tokenArg = "alpaca"
try:
    with open(listToken) as f:
        d = json.load(f)
except ValueError:
    print("token lstesi dosyası açılamadı")
    print(ValueError)

#komut satırından bilgi alma
argv = sys.argv[1:]
try:
  opts, args = getopt.getopt(argv,"ht:a:b:",["ttoken=", "aamount=", "aamounttoken="])
except getopt.GetoptError:
  print("buypancake.py -t <tokenName> -a <amount bnb> -b <amount token>")
  sys.exit(2)

for opt, arg in opts:
  if opt == '-h':
      print("buypancake.py -t <tokenName> -a <amount bnb> -b <amount token>")
      sys.exit()
  elif opt in ("-t", "--ttoken"):
      tokenArg = arg
  elif opt in ("-a", "--aamount"):
      amountArg = arg
  elif opt in ("-b", "--aamounttoken"):
      tokenamountArg = arg

#########################################################
bsc = "https://bsc-dataseed.binance.org/"
web3 = Web3(Web3.HTTPProvider(bsc))
try:
    web3.isConnected()
    ConnectionStatus = web3.isConnected()
    print("bağlantı durumu : ", ConnectionStatus)
except ValueError:
    print("Bağlantı hatası Tekrar deneyiniz")
    print(ValueError)

balance = web3.eth.get_balance(bilgiler.sender_address)
#print(balance)

humanReadable = web3.fromWei(balance,'ether')
print("bnb balance durumu : ", humanReadable)
print(d[tokenArg])

print(amountArg)
print(tokenamountArg)

#Contract Address of Token we want to buy
tokenToBuy = web3.toChecksumAddress(d[tokenArg])
spend = web3.toChecksumAddress(bilgiler.wbnb)  #wbnb contract

print("token buy : ", tokenToBuy)
print("spend     : ", spend)


#Setup the PancakeSwap contract
contract = web3.eth.contract(address=bilgiler.panRouterContractAddress, abi=bilgiler.panabi)

nonce = web3.eth.get_transaction_count(bilgiler.sender_address)

start = time.time()

pancakeswap2_txn = contract.functions.swapExactETHForTokens(
    tokenamountArg, # minimum alınacak miktar
    [spend,tokenToBuy],
    bilgiler.sender_address,
    (int(time.time()) + 10000)
    ).buildTransaction({
        'from': bilgiler.sender_address,
        'value': web3.toWei(amountArg,'ether'),#harcanacak bnb miktarı
        'gas': 250000,
        'gasPrice': web3.toWei('5','gwei'),
        'nonce': nonce,
    }
)

signed_txn = web3.eth.account.sign_transaction(pancakeswap2_txn, private_key=bilgiler.private)
tx_token = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
print("transaction code : ",web3.toHex(tx_token))


# transaction kontrol
sleep(10)
transactionStatus = False
transactionStatusTryCount = 0
while transactionStatus == False:
    son_durum = web3.eth.getTransactionReceipt(web3.toHex(tx_token))
    if son_durum["status"] == 0:
        print(" Transaction beklemede")
    else:
        print("transaction başarılı")
        transactionStatus = True
    if transactionStatusTryCount == 10:
        transactionStatus = True
        print("transaction problemi bulunmaktadır. manuel kontrol ediniz.")
    transactionStatusTryCount += 1

# python buypancake.py -t alpaca -a 0.01
