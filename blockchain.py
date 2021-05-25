# -*- coding: utf-8 -*-
"""
Create a blockchain 

"""
import datetime
import hashlib
import json
from flask import Flask, jsonify

# Building blockchain
class Blockchain:
    
    def __init__(self):
        self.chain = []
        self.create_block(proof = 1, previous_hash = '0')
        
    def create_block(self, proof, previous_hash):
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash}
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
  # Mining block chain  
 # create a web app

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

# creating block chain

blockchain =  Blockchain()
            
# Mining the block
@app.route("/mine_block", methods = ["GET"])
def mine_block():
    previous_block = blockchain.get_previous_block()
    prev_proof = previous_block['proof']
    proof = blockchain.proof_of_work(prev_proof)
    previous_hash = blockchain.hash(previous_block)
    block = blockchain.create_block(proof, previous_hash)
    response = {'message': 'created',
                'index': block['index'],
                 'timestamp': block['timestamp'],
                 'proof': block['proof'],
                 'previous_hash': block['previous_hash']}
    
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
    
    response ={"length": len(blockchain.chain),
               "is_valid": valid}
    
    return jsonify(response), 200

# Decentralizing blockchains
# run web app
app.run(host='0.0.0.0', port=5000)
            
