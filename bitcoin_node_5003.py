#Libraries required
import json
import requests
from flask import Flask, jsonify, request
import datetime
from urllib.parse import urlparse
import hashlib
from uuid import uuid4

##########################
## creating the BLOCKCHAIN ###
##########################
class BLOCKCHAIN:
    def __init__(self):
        self.chain = []
        self.transactions = []
        # creating the first and it is called  genesis block
        self.createBlock(proof = 1, previousHashValue = '0')
        self.nodes = set()
        
    def createBlock(self, proof, previousHashValue):
        block = {'index' : len(self.chain) + 1, 
                 'timeStamp' : str(datetime.datetime.now()),
                 'proof' : proof,
                 'previousHashValue' : previousHashValue,
                 'transactions' : self.transactions}
        self.transactions = []
        self.chain.append(block)
        return block
    
    def GetPreviousBlock(self):
        return self.chain[-1]

    #Proof of work function
    def proof_Of_Work(self, previousProof):
        newProof = 1
        checkProof = False
        while checkProof is False:
            hashOperation = hashlib.sha256(str(newProof**2 - previousProof**2).encode()).hexdigest()
            if hashOperation[:4] == '0000':
                checkProof = True
            else:
                newProof += 1
        return newProof
    
    #defining hash function
    def hash(self, block):
        encodedBlock = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(encodedBlock).hexdigest()
    
    #checking if the chain is valid
    def validateChain(self, chain):
        previousBlock = chain[0]
        blockIndex = 1
        while blockIndex < len(chain):
            block = chain[blockIndex]
            if block['previousHashValue'] != self.hash(previousBlock):
                return False
            previousProof = previousBlock['proof']
            proof = block['proof']
            hashOperation = hashlib.sha256(str(proof**2 - previousProof**2).encode()).hexdigest()
            if hashOperation[:4] != '0000':
                return False
            previousBlock = block
            blockIndex += 1
        return True
    
    def addTransaction(self, sender, receiver, amount):
        self.transactions.append({'sender':sender,
                                  'receiver': receiver,
                                  'amount': amount})
        previousBlock = self.GetPreviousBlock()
        return previousBlock['index'] + 1
    
    def addNode(self, address):
        ParsedUrl = urlparse(address)
        self.nodes.add(ParsedUrl.netloc)
        
    def replaceChain(self):
        network = self.nodes
        longestChain= None
        max_length = len(self.chain)
        for node in network:
            response = requests.get(f'http://{node}/getChain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.validateChain(chain):
                    max_length = length
                    longestChain= chain
        if longestChain:
            self.chain = longestChain
            return True
        return False
    
# second step Mining Our BLOCKCHAIN
        
        
#Creating a Web App
app = Flask(__name__)

#Creating an address for the node on Port 5000
node_address = str(uuid4()).replace('-','')
        
#Creating a BLOCKCHAIN
BLOCKCHAIN = BLOCKCHAIN()

#mining a new Block 
@app.route('/mine_block', methods = ['GET'])
def mine_block():
    previousBlock = BLOCKCHAIN.GetPreviousBlock()
    previousProof = previousBlock['proof']
    proof = BLOCKCHAIN.proof_Of_Work(previousProof)
    previousHashValue = BLOCKCHAIN.hash(previousBlock)
    block = BLOCKCHAIN.createBlock(proof, previousHashValue)
    BLOCKCHAIN.addTransaction(sender = node_address, receiver = 'Jayanth', amount = 1)
    response = {
        'message':'Congratulations, you just mined a block!',
        'index': block['index'],
        'timeStamp': block['timeStamp'], 
        'proof': block['proof'],
        'previousHashValue': block['previousHashValue'],
        'transactions' : block['transactions']
    } 
    return jsonify(response), 200

########Getting the full BLOCKCHAIN##################
#####################################################
@app.route('/getChain', methods = ['GET'])
def getChain():
    res = {
        'chain': BLOCKCHAIN.chain,
        'length': len(BLOCKCHAIN.chain)
    }
    return jsonify(res), 200   

#Checking if the BLOCKCHAIN is valid
@app.route('/isValid', methods = ['GET'])
def isValid():
    isValid = BLOCKCHAIN.validateChain(BLOCKCHAIN.chain)
    if isValid:
        res = {
            'message': 'The Block chain has not been tamperd and every thing is valid'
            }
    else:
        res = {'message' : 'Harshith, unAuthorized some body tried to modify the chain'}
    return jsonify(res), 200

#adding a new transaction to a BLOCKCHAIN
@app.route('/addTransaction', methods = ['POST'])
def addTransaction():
    json = request.get_json()
    transactionKeys = ['sender', 'receiver', 'amount']
    if not all (key in json for key in transactionKeys):
        return 'Some elements of the transaction are missing', 400
    index = BLOCKCHAIN.addTransaction(json['sender'], json['receiver'], json['amount'])
    response = {'message': f'This transaction will be added to Block {index}'}
    return jsonify(response), 201

## Decentralising our BLOCKCHAIN######
######################################
    
@app.route('/connectNode', methods = ['POST'])
def connectNode():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return "No Node", 400
    for node in nodes:
        BLOCKCHAIN.addNode(node)
    response = {
        'message' : 'The nodes are connected proceed to transcation. The Bitcoin blockchain now contains the following nodes:',
        'total_nodes' : list(BLOCKCHAIN.nodes)
    }
    return jsonify(response), 201

#checking the consenses Replacing the chain by the longest chain
@app.route('/replaceChain', methods = ['GET'])
def replaceChain():
    checkReplace = BLOCKCHAIN.replaceChain()
    if checkReplace:
        response = {
            'message': 'The node had different length chains, so the node was replaced by the longest one.',
            'new_chain': BLOCKCHAIN.chain
            }
    else:
        response = {
            'message' : 'All good, the chain is the largest one.',
            'actual_chain' : BLOCKCHAIN.chain
        }
    return jsonify(response), 200

#Running the server Local machine
app.run(host = '0.0.0.0', port = 5003)    
