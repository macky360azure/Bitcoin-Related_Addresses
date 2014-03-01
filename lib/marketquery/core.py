import exceptions
import csv
import datetime as dt
from urllib2 import Request, urlopen, URLError
import json

#Global variables
_bitcoin_prices = dict()
_bitcoin_prices_last = '1980-01-01' 
_built = False
_dateformat = '%Y-%m-%d'

def getBitcoinPrice(date):
        '''
        Retrieves the bitcoin price in USD. Date needs to be specified as yyyy-mm-dd
        If the price is not found one of the following errors is returned:
        DateNotFoundError
        '''
        #check if we have built the lookup dictionary yet, if not, we do so now
        if not _built : RefreshBitcoinPrices()

        #grab the price
        try:
            return float(_bitcoin_prices[date])
        except:
            return float(_bitcoin_prices[_bitcoin_prices_last])
            #TODO - This is just temporary

def RefreshBitcoinPrices():
    '''Causes the bitcoin price dictionary to be rebuilt

    ''' 
    global _bitcoin_prices, _bitcoin_prices_last, _built
   
    
    url='http://api.coindesk.com/v1/bpi/historical/close.json?start=2010-07-18&end={0}'
    formatted = url.format((dt.datetime.now() + dt.timedelta(days=1)).strftime(_dateformat)) #we advance a day to ensure all captured
    request = Request(formatted)
    try:
       response = urlopen(request)
       jsonread = response.read()
    except URLError as e:
        #TODO:Need to cusomise this error
        print('Could not retrive the pricelist, received the following error: {}', e)
    #OK we have a response, lets return the balance 
    object =  json.loads(jsonread)
    _bitcoin_prices = object['bpi']
    for key in _bitcoin_prices:
        try: 
            d = dt.datetime.strptime(key,_dateformat)
            if d>dt.datetime.strptime(_bitcoin_prices_last,_dateformat): 
                _bitcoin_prices_last = key 
        except: 
            _bitcoin_prices.pop(key)#kill any non date rows
    _built = True
    
def run_tests():
    '''Runs some tests on the module

    '''
    
    #verify some known prices
    price = getBitcoinPrice('2010-10-15')
    assert price == '0.1050'
    print('All checks passed')

if __name__ == '__main__':
    run_tests()






    