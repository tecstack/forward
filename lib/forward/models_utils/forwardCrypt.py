#!/usr/bin/env python
#coding:utf-8

"""
-----Introduction-----
[Core][forward] Class for encryption and decryption.
"""

import binascii,rsa

class CRYPT:
    def __init__(self,publicKeyPath,privateKeyPath):
        self.njInfo = {
            'status':True,
            'errLog':'',
            'content':{}
        }
        try:
            with open(publicKeyPath) as publickfile:
                p = publickfile.read()
                self.pubKey = rsa.PublicKey.load_pkcs1(p)
            with open(privateKeyPath) as privateFile:
                p = privateFile.read()
                self.privKey = rsa.PrivateKey.load_pkcs1(p)
        except Exception,e:
            self.njInfo['status'] = False
            self.njInfo['errLog'] = str(e)
    def encrypt(self,plaintext):
        try:
            ciphertextAscii = rsa.encrypt(plaintext,self.pubKey)
            self.njInfo['content']['plaintext'] = plaintext
            self.njInfo['content']['ciphertext'] = binascii.b2a_hex(ciphertextAscii)
        except Exception as e:
            self.njInfo['status'] = False
            self.njInfo['errLog'] = str(e)
    def decrypt(self,ciphertext):
        try:
            ciphertextAscii = binascii.a2b_hex(ciphertext)
            self.njInfo['content']['ciphertext'] = ciphertext
            self.njInfo['content']['plaintext'] = rsa.decrypt(ciphertextAscii,self.privKey)
        except Exception as e:
            self.njInfo['status'] = False
            self.njInfo['errLog'] = str(e)
