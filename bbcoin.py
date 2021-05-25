# -*- coding: utf-8 -*-
"""
Create crypto coin(bbcoin)
"""
import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse

# Building blockchain
class Blockchain:
    
    def __init__(self):
        self.chain = []
        self.transactions = []
        self.create_block(proof = 1, previous_hash = '0')
        self.nodes = set()
        
    def create_block(self, proof, previous_hash):
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash,
                 'transactions': self.transactions}
        self.transactions = []
        self.chain.append(block)
        return block
    
    def get_previous_block(self):
        return self.chain[-1]
    
    def proof_of_work(self, previous_proof):
        
        new_proof = 1
        check_proof = False
        
        while check_proof == False:
            hash_op = hashlib.sha256(str(new_proof ** 2 - previous_proof ** 2).encode()).hexdigest()
            if hash_op[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
                
        return new_proof
    
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    def is_chain_valid(self, chain):
        prev_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            curr_block = chain[block_index]
            
            if curr_block['previous_hash'] != self.hash(prev_block):
                return False
            
            prev_proof = prev_block['proof']
            proof = curr_block['proof']
            
            hash_op = hashlib.sha256(str(proof ** 2 - prev_proof ** 2).encode()).hexdigest()
            if hash_op[:4] != '0000':
                return False
            
            prev_block = curr_block
            block_index += 1
            
        return True
    
    def add_transactions(self, sender, receiver, amount):
        self.transactions.append({'sender' : sender,
                                  'receiver' : receiver,
                                  'amount' : amount})
        prev_block = self.get_previous_block()
        
        return prev_block['index'] + 1
    
    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
        
    def replace_chain(self):
        long_chain = None
        max_length = len(self.chain)
        for node in self.nodes:
            response = requests.get(f'http://{node}/chain')
            if response.status_code == 200:
                length = response.json()[1]
                chain = response.json()[0]
            
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    long_chain = chain
                    
        if long_chain:
            self.chain = long_chain
            return True
        
        return False
        
 # Mining the block chain 
 # create a web app

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

# creating node address
node_address = str(uuid4()).replace('-', '')

# creating block chain
blockchain =  Blockchain()
            
# Mining the block
@app.route("/mine_block", methods = ["GET"])
def mine_block():
    previous_block = blockchain.get_previous_block()
    prev_proof = previous_block['proof']
    proof = blockchain.proof_of_work(prev_proof)
    previous_hash = blockchain.hash(previous_block)
    blockchain.add_transactions(sender = node_address, receiver = 'John Doe', amount = 1)
    block = blockchain.create_block(proof, previous_hash)
    response = {'message': 'created',
                'index': block['index'],
                 'timestamp': block['timestamp'],
                 'proof': block['proof'],
                 'previous_hash': block['previous_hash'],
                 'transactions': block['transactions']}
    
    return jsonify(response), 200
            
# return the blockchain
@app.route("/chain", methods = ["GET"])
def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    
    return jsonify(response), 200

# Check if the block chain is valid
@app.route("/is_valid", methods= ["GET"])
def is_valid():
    valid = blockchain.is_chain_valid(blockchain.chain)
    
    if valid:
        response ={'message': 'The blockchain is valid'}
    else:
        response ={'message': 'The blockchain is invalid'}
    
    return jsonify(response), 200

@app.route("/add_transaction", methods= ["POST"])
def add_transaction():
    json = request.get_json()
    transaction_keys = ['sender', 'receiver', 'amount']
    if not all (keys in json for keys in transaction_keys):
        return 'The request is incomplete', 400
    index = blockchain.add_transactions(json['sender'], json['receiver'], json['amount'])
    
    response ={"message": f'The trancaction will be added to {index} in the block'}
    
    return jsonify(response), 201

# Decentralizing blockchains

@app.route("/connect_node", methods= ["POST"])
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')
    
    if nodes is None:
        return 'The nodes cannot be empty', 400
   
    for node in nodes:
        blockchain.add_node(node)
    
    response ={'message': 'All nodes are connected',
               'list': list(blockchain.nodes)}
    
    return jsonify(response), 201

@app.route("/replace_chain", methods= ["GET"])
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    
    if is_chain_replaced:
        response = {'message': 'The blockchain is replaced with longest chain'}
    else:
        response = {'message': 'The blockchain is replaced with longest chain'}
    
    return jsonify(response), 200

# Replacing the chain by longest chain if needed.

# run web app
app.run(host='0.0.0.0', port=5000)
