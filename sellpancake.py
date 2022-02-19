from web3 import Web3
import json
import time
import config as bilgiler

import json
import sys, getopt
import os
from time import sleep

# satın alınabilir token listesini getir
listToken = "listtoken.json"
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
  opts, args = getopt.getopt(argv,"ht:a:b:",["ttoken=", "aamount="])
except getopt.GetoptError:
  print("buypancake.py -t <tokenName> -a <amount bnb>")
  sys.exit(2)

for opt, arg in opts:
  if opt == '-h':
      print("buypancake.py -t <tokenName> -a <amount bnb>")
      sys.exit()
  elif opt in ("-t", "--ttoken"):
      tokenArg = arg
  elif opt in ("-a", "--aamount"):
      amountArg = arg


#########################################################

bsc = "https://bsc-dataseed.binance.org/"
web3 = Web3(Web3.HTTPProvider(bsc))

#bsc ile bağlantı
try:
    web3.isConnected()
    ConnectionStatus = web3.isConnected()
    print("bağlantı durumu : ", ConnectionStatus)
except ValueError:
    print("Bağlantı hatası Tekrar deneyiniz")
    print(ValueError)


spend = web3.toChecksumAddress(bilgiler.wbnb)  #wbnb contract

#Get BNB Balance
balance = web3.eth.get_balance(bilgiler.sender_address)
#print("bnb balance : ", balance)
 
humanReadable = web3.fromWei(balance,'ether')
print("bnb balance : ",humanReadable)

#Contract id is the new token we are swaping to
contract_id = web3.toChecksumAddress(d[tokenArg])

#Setup the PancakeSwap contract
contract = web3.eth.contract(address=bilgiler.panRouterContractAddress, abi=bilgiler.panabi)


#Create token Instance for Token
sellTokenContract = web3.eth.contract(contract_id, abi=bilgiler.sellAbi)

#Get Token Balance
balance = sellTokenContract.functions.balanceOf(bilgiler.sender_address).call()
symbol = sellTokenContract.functions.symbol().call()
readable = web3.fromWei(balance,'ether')
print("Token Balance: " + str(readable) + " " + symbol)

#Enter amount of token to sell
tokenValue = web3.toWei(amountArg, 'ether')

#Approve Token before Selling
tokenValue2 = web3.fromWei(tokenValue, 'ether')
start = time.time()
approve = sellTokenContract.functions.approve(bilgiler.panRouterContractAddress, balance).buildTransaction({
            'from': bilgiler.sender_address,
            'gasPrice': web3.toWei('5','gwei'),
            'nonce': web3.eth.get_transaction_count(bilgiler.sender_address),
            })

signed_txn = web3.eth.account.sign_transaction(approve, private_key=bilgiler.private)
tx_token = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
print("Approved: " + web3.toHex(tx_token))

#Wait after approve 10 seconds before sending transaction
time.sleep(10)
print(f"Swapping {tokenValue2} {symbol} for BNB")
#Swaping exact Token for ETH 

pancakeswap2_txn = contract.functions.swapExactTokensForETH(
            tokenValue ,0, 
            [contract_id, spend],
            bilgiler.sender_address,
            (int(time.time()) + 1000000)

            ).buildTransaction({
            'from': bilgiler.sender_address,
            'gasPrice': web3.toWei('5','gwei'),
            'nonce': web3.eth.get_transaction_count(bilgiler.sender_address),
            })
    
signed_txn = web3.eth.account.sign_transaction(pancakeswap2_txn, private_key=bilgiler.private)
tx_token = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
print(f"Sold {symbol}: " + web3.toHex(tx_token))

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

# python sellpancake.py -t alpaca -a 0.01