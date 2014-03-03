import os, sys #used to extract path to project lib
import json
import datetime as dt
from urllib2 import Request, urlopen, URLError

lib_path = os.path.abspath('.')
if sys.path.count(lib_path) == 0 : sys.path.append(lib_path) #Add lib to path if not already added
from lib.marketquery.core import getBitcoinPrice

_address_query_cache = {}
_block_query_cache = {}
CACHE_LIFE_IN_SECONDS = 300
_get_address_info_cache_misses = 0
_get_block_info_cache_misses = 0

def SATOSHIS_IN_A_BITCOIN():
    return 100000000

def getAddressInfo(*addresses):
    '''Returns a dictionary object from the json response set by blockchain.info: 
    address = bitcoin address
    final_balance = closing balance in satoshis
    hash160 = hash160 of address
    total_received = total satoshis received
    total_sent = total satoshis send
    txs = a dictionary of transactions with keys 1 onwards
    n_tx = number of transactions
    
    '''  

    global _get_address_info_cache_misses 
    global _get_address_info_misses
    btc_info_addr_json_list = []
    for addr in addresses:

        # First check if we are in the cache, if so we grab from cache and continue to next interation
        if addr in _address_query_cache:
            if _address_query_cache[addr][0] < dt.datetime.utcnow() + dt.timedelta(seconds = CACHE_LIFE_IN_SECONDS):
                btc_info_addr_json_list.append(_address_query_cache[addr][1])
                continue

        _get_address_info_cache_misses  +=1
        
        # If we didn't find in cache then we look it up
        balanceurl = 'http://blockchain.info/address/{0}?format=json'
        formatted = balanceurl.format(addr)
        request = Request(formatted)
        try:
            response = urlopen(request)
            jsonread = response.read()
        except URLError as e:
            #TODO:Need to cusomise this error
            print('Could not retrive the address balance, received the following error: {}', e)
    
        # Let's extract and cleanup the response
        btc_info_addr_json =  json.loads(jsonread)
        doFixTransactionResultValue(btc_info_addr_json)
        _address_query_cache[addr] = (dt.datetime.utcnow(),btc_info_addr_json) #save a tuple with the time
        btc_info_addr_json_list.append(btc_info_addr_json)

    return btc_info_addr_json_list


def getBlockInfo(*heights):
    '''Returns a dictionary object from the json response set by blockchain.info: 
    address = bitcoin address
    final_balance = closing balance in satoshis
    hash160 = hash160 of address
    total_received = total satoshis received
    total_sent = total satoshis send
    txs = a dictionary of transactions with keys 1 onwards
    n_tx = number of transactions
    
    '''  

    global _block_query_cache
    global _get_block_info_cache_misses
    btc_info_block_json_list = []
    for height in heights:

        # First check if we are in the cache, if so we grab from cache and continue to next interation
        if height in _block_query_cache:
            btc_info_block_json_list.append(_block_query_cache[height][1])
            continue

        _get_block_info_cache_misses +=1

        # If we didn't find in cache then we look it up
        blockurl = 'https://blockchain.info/block-height/{0}?format=json'
        formatted = blockurl.format(height)
        request = Request(formatted)
        try:
            response = urlopen(request)
            jsonread = response.read()
        except URLError as e:
            #TODO:Need to cusomise this error
            print('Could not retrive the address balance, received the following error: {}', e)
        
        # Let's extract and cleanup the response
        btc_info_block_json =  json.loads(jsonread)
        _block_query_cache[height] = (dt.datetime.utcnow(),btc_info_block_json) #save a tuple with the time
        btc_info_block_json_list.append(btc_info_block_json)

    return btc_info_block_json_list

def doFixTransactionResultValue(addressobject):
    '''For some reason, the result value returned by BlockChainInfo appears to be offset by one transaction. Such
        that the Result for tx[0] is displayed presented under tx[1]. Tx[0] has a result of 0 and tx[last] proper result is lost
        This function aims to recalculate the tx 'result' so that it can be relied on
    '''

    # We do through transaction by transaction and subtract inputs from the address and add any outputs made to the address
    for tx in addressobject['txs']:
        result = 0
        for input in tx['inputs']:
            if 'prev_out' in input: # Newly created blocks donot have an prev_out        
                if 'addr' in input['prev_out']: # sometimes not have an addr. This appears to be related to non-standard transactions: https://bitcointalk.org/index.php?topic=130392.0
                    if (input['prev_out']['addr'] == addressobject['address']) :
                        result = result - input['prev_out']['value']
        for output in tx['out']:
            if 'addr' in output: # Sometimes outputs have a corrupt address 
                if (output['addr'] == addressobject['address']) :
                    result = result + output['value']
        tx['my_result']=result # Lets save it as a new dictionary entry, we could overight 'result' but lets keep it seperate for clarity

        # It has been observed that not all tx's have a time associated with them, in this case we refer to the block_height
        if 'time' in tx:
            dateYmd = dt.datetime.fromtimestamp(int(tx['time'])).strftime('%Y-%m-%d')
        else:
            block = getBlockInfo(tx['block_height'])[0]['blocks'][0]
            tx['time'] = block['time']
            dateYmd = dt.datetime.fromtimestamp(int(tx['time'])).strftime('%Y-%m-%d')

        tx['my_dateYmd'] = dateYmd
        rate =   getBitcoinPrice(dateYmd)
        tx['my_est_USD_rate']=rate  #lets save the USD value at the time of the transaction
        tx['my_est_USD_result']=result * rate / SATOSHIS_IN_A_BITCOIN()  #lets save the USD value at the time of the transaction


def getRelatedAddresses(recursive = False, related_addr_dic = None,  *addresses):
    '''Returns a dictionary of related addresses (key=address, relationidentified= address, relationtype=[Change,Fellow]). 
    Related addresses are defined as address that
    have been used in conjunction with the provided address on the input side of a transaction. The 
    logic is that they same person must control all the input private keys. 
    
    '''

    # This function relies on the fact that optional mutable objects persist accross calls
    if(related_addr_dic == None):
        related_addr_dic = {} 


    for addr in addresses:
        if(not related_addr_dic.has_key(addr)):
            related_addr_dic[addr] = {'relation':'none','relationtype':'root','txhash':'none'} # Add this address
        info = getAddressInfo(addr)[0]
        for tx in info['txs']:

            # 1st check if we have only 1 or 2 outputs. Any more and this may be a coinjoin transaction
            if len(tx['out']) == 0 or len(tx['out']) >2:    
                break           
            # 2nd scan To see if this address is one of the inputs
            bool_addr_is_an_input = False
            for input in tx['inputs']:
                if 'prev_out' in input:        
                    if(addr == input['prev_out']['addr']):
                        bool_addr_is_an_input  = True
                        break
            # 3rd, if this address is an input for the tx, then fellow input addresses are related
            if(bool_addr_is_an_input):
                smallest_input = 9999 * SATOSHIS_IN_A_BITCOIN()
                newly_identified_related_addresses = []
                for input in tx['inputs']:
                    if 'prev_out' in input:        
                        input_addr = input['prev_out']['addr']
                        if(smallest_input> int(input['prev_out']['value'])):
                           smallest_input = int(input['prev_out']['value']) 
                        # only scan if this address hasnt already been scanned
                        if not related_addr_dic.has_key(input_addr):
                            newly_identified_related_addresses.append(input_addr)
                            if recursive:
                                related_addr_dic[input_addr] = {'relation':addr,'relationtype':'fellow','txhash':tx['hash']} # Add this address
                                #getRelatedAddresses(True, related_addr_dic, input_addr)
                            else:
                                related_addr_dic[input_addr] = {'relation':addr,'relationtype':'fellow','txhash':tx['hash']} # Add this address
                # 4th, if we are scanning for change addresses any address smaller than the biggest input (must have multiple inputs)
                for output in tx['out']:
                    if len(tx['inputs'])>1:       
                        if(int(output['value'])<smallest_input):
                            output_addr = output['addr']
                            # only scan if this address hasnt already been scanned
                            if not related_addr_dic.has_key(output_addr):
                                newly_identified_related_addresses.append(output_addr)
                                if recursive:
                                    related_addr_dic[output_addr] = {'relation':addr,'relationtype':'change','txhash':tx['hash']} # Add this address
                                    #getRelatedAddresses(True, related_addr_dic, output_addr)
                                else:
                                    related_addr_dic[output_addr] = {'relation':addr,'relationtype':'change','txhash':tx['hash']} # Add this address
                # 5th, recurse if required
                if recursive:
                    for addr in newly_identified_related_addresses:
                          getRelatedAddresses(True, related_addr_dic, addr)
                          
    return related_addr_dic


def run_tests():
  pass
  
if __name__ == '__main__':
    run_tests()

