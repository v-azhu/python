#encryption.py
###############################################################
# name     : encryption
# author   : zhuys
# created  : 2016-07-05
# purpose  : encrypt/decrypt password
# copyright: copyright(c) zhuyunsheng awen.zhu@hotmail.com 2016
###############################################################
import argparse
from os import environ
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto import Random
import base64,struct
import version
__all__=['encrypt','decrypt']
class encryption:  
    def __init__(self,key=None):
        h = SHA256.new()
        h.update(base64.b64encode(key))
        self.key=h.digest() 
    def parseArgs(self):
        try:
            _parser=argparse.ArgumentParser(description="encrypt / decrypt the password related for password safe")
            _parser.add_argument("-e","--encrypt",type=str,default=None,help="The option for encrypts a password or string, exclusive with option --decrypt")
            _parser.add_argument("-d","--decrypt",type=str,default=None,help="The option for decrypts a password or string, exclusive with option --encrypt")
            _parser.add_argument("-k","--key",type=str,required=True,help="priv key for encryption/decreyption, this is an force option")
            _parser.add_argument("-v","--version",action='version',version='%(prog)s '+version.version+' Built by zhuys, Copyright(c) 2016-2050 received.',help="version info")
            _pars = _parser.parse_args()
            k = _pars.key
            h = SHA256.new()            
            h.update(base64.b64encode(k))
            self.key=h.digest()
            if _pars.encrypt is None and _pars.decrypt is None:
                return _parser.parse_args(['--help'])
            if _pars.encrypt is not None and _pars.decrypt is not None:
                return _parser.parse_args(['--help'])
            if _pars.encrypt:
                print self.encrypt(_pars.encrypt)
            elif _pars.decrypt:
                print self.decrypt(_pars.decrypt)
        except Exception as e:
            _parser.parse_args(['--help'])
            raise e
    def encrypt(self,data):
        salt=Random.new().read(AES.block_size)
        padding = Random.new().read(AES.block_size)
        cipher = AES.new(self.key,AES.MODE_CBC,salt)
        header = struct.pack('<Q',len(data)) + salt
        trim = AES.block_size - (len(data) % AES.block_size)
        encryptedData = cipher.encrypt(data + padding[:trim]) if trim != AES.block_size else cipher.encrypt(data)
        return base64.b64encode(header + encryptedData)
    def decrypt(self,data):
        encryptedData = base64.b64decode(data)
        a = struct.calcsize('Q')
        b = a + AES.block_size
        dataLen = struct.unpack('<Q',encryptedData[:a])[0]
        salt = encryptedData[a:b]
        cipher = AES.new(self.key,AES.MODE_CBC,salt)
        return cipher.decrypt(encryptedData[b:])[:dataLen]
if __name__ == "__main__":
    #e = encryption('Priv@key1')
    e = encryption(environ['pmonkey'])
    e.parseArgs()
    #print e.encrypt('DB_qwerty_155')
    #print e.encrypt('Cool_pass8')
