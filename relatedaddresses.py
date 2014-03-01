#!/usr/bin/env python
import sys, os
from lib.blockchainquery import core as bq
from lib.bitcoinvalidation import addressvalidation as bv

EXAMPLE_ADDRESS = '19hJLtfs5pqv2S4kRySMcnxnCzkNf7rhGS' #clark moody public donation address

def generate_related_report(recursive,suppresszero, *addresses):
    '''Uses various techniques to identify addresses related and generates a report

    '''

    os.system('cls' if os.name == 'nt' else 'clear')
    if recursive:
        print("Recursively identifying addresses related to:")
    else:
        print("Identifying addresses related to:")
    print("-"*60) 
    for count, addr in enumerate(addresses):
        print ('{:>3}. {:<39}'.format(count+1,addr))
    print("-"*60) 
    print('')
    print("Please wait...") 

    related_addr = bq.getRelatedAddresses(recursive, None, *addresses)
    running_balance = 0
  
    #Generate text report
    os.system('cls' if os.name == 'nt' else 'clear')
    NonZeroAccount = 0
    if(suppresszero):
        print("Non Zero Related Accounts") 
    else:
        print("Related Accounts") 
    print("-"*60) 
    for count, addr in enumerate(related_addr):
        balance = float(bq.getAddressInfo(addr)[0]['final_balance']) / bq.SATOSHIS_IN_A_BITCOIN()
        running_balance += balance 
        if(balance > 0 or not suppresszero):
            print ('{:>3}. {:<39}{:>16f}'.format(NonZeroAccount+1 if suppresszero else count+1,addr,balance))
            NonZeroAccount +=1
    if NonZeroAccount ==0:
        print("All related accounts have a zero balance")
    print("-"*60) 
    print("Total BTC {:>50f}".format(running_balance)) 


def run_test(recursive,suppresszero):
    '''Runs some tests on the module

    '''
    generate_related_report(recursive,suppresszero,EXAMPLE_ADDRESS)


def show_help():
    '''Prints the commandline help'''
    filename = os.path.basename(__file__)
    print('Reports the balances of any related bitcoin addresses.')
    print('')
    print('{} [-r][-t][-s] Address1 Address2 ...'.format(filename.upper()))
    print('')
    print('  -r Recursively scan for related addresses')
    print('  -s Suppress addresses with a zero balance')
    print('  -t Scans using the test addresses {0}'.format(EXAMPLE_ADDRESS))
    print('')
    print('eg. {0} -r -s {1}'.format(filename.upper(),EXAMPLE_ADDRESS))
    print('')
    
      
if __name__ == '__main__':
    
    showhelp = False
    recurse = False
    usetestaddress = False
    suppresszero = False
    addresses = []
    unknownflags = []
    if len(sys.argv) ==1: showhelp = True 
    else:
        for flag in sys.argv[1:]:
            if flag == '-?': showhelp = True
            elif flag == '-t': usetestaddress = True
            elif flag == '-r': recurse = True
            elif flag == '-s': suppresszero = True
            elif bv.check_bitcoin_address(flag):
                addresses.append(flag)
            else:
                unknownflags.append(flag)   
    
    
    if len(unknownflags)>0:
        for flag in unknownflags:
            print("This argument is not understood: {0}".format(flag))
        print('')
        show_help()
    elif showhelp:
        show_help()
    elif usetestaddress:
        run_test(recurse,suppresszero)
    else :
        generate_related_report(recurse, suppresszero, *addresses)

