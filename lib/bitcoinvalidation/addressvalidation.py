'''Module that can be used to verify the validity of a bitcoin public address
http://rosettacode.org/wiki/Bitcoin/address_validation
'''
from hashlib import sha256
 
digits58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
 
def to_bytes(n, length, endianess='big'):
    h = '%x' % n
    s = ('0'*(len(h) % 2) + h).zfill(length*2).decode('hex')
    return s if endianess == 'big' else s[::-1]

def decode_base58(bc, length):
    n = 0
    for char in bc:
        n = n * 58 + digits58.index(char)
    #return n.to_bytes(length, 'big')  PYTHON 3+
    return to_bytes(n,length, 'big') 

def check_bitcoin_address(bc):
    '''Checks if the provided bitcoin address is valid'''
    try:
        bcbytes = decode_base58(bc, 25)
    except: # This is not a Base58 string
        return False
    return bcbytes[-4:] == sha256(sha256(bcbytes[:-4]).digest()).digest()[:4]
 
if __name__ == '__main__':
    bc = '1AGNa15ZQXAZUgFiqJ2i7Z2DPU2J6hW62i'
    assert check_bitcoin_address(bc)
    assert not check_bitcoin_address( bc.replace('N', 'P', 1) )
    assert check_bitcoin_address('1111111111111111111114oLvT2')
    assert check_bitcoin_address("17NdbrSGoUotzeGCcMMCqnFkEvLymoou9j")