import json
import urllib2
import cPickle as pickle
import sys

clusterAddresses = []
addressesToProcess = [sys.argv[1]]

txIds = {}

while len(addressesToProcess) > 0:
    currentAdr = addressesToProcess[0]
    offset = 0
    while True:
        link = "https://blockchain.info/rawaddr/" + currentAdr + "?offset=" + str(offset)
        print link
        data = json.loads(urllib2.urlopen(link).read())
        if len(data["txs"]) == 0:
            break
        offset = offset + 50
        
        for tx in data["txs"]:
            addressIsInput = False
            for input in tx["inputs"]:
                if input["prev_out"]["addr"] == currentAdr:
                    addressIsInput = True
            if addressIsInput:
                for input in tx["inputs"]:
                    newAdr = input["prev_out"]["addr"]
                    if newAdr not in clusterAddresses:
                        print len(clusterAddresses), len(addressesToProcess)
                        clusterAddresses.append(newAdr)
                        addressesToProcess.append(newAdr)
                    if newAdr in txIds:
                        if tx["hash"] not in txIds[newAdr]:
                            txIds[newAdr].append(tx["hash"])
                    else:
                        txIds[newAdr] = [ tx["hash"] ]
        if len(data["txs"]) < 50:
            break
    addressesToProcess.pop(0)

with open("clusterAddresses.txt", "wb") as file:
    pickle.dump(clusterAddresses, file)

with open("txIds.txt", "wb") as file:
    pickle.dump(txIds, file)
