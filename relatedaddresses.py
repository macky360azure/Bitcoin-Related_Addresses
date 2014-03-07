#!/usr/bin/env python
import sys, os
from lib.blockchainquery import core as bq
from lib.bitcoinvalidation import addressvalidation as bv

EXAMPLE_ADDRESS = '18WaqDnNRbXpbfgGAv5bC7spb366c4CCfX'

def generate_related_report(recursive, indent, suppresszero, includechangeinputs, maxresult, *addresses):
    '''Uses various techniques to identify addresses related and generates a report

    '''

    os.system('cls' if os.name == 'nt' else 'clear')
    if recursive:
        print("Recursively identifying addresses related to:")
    else:
        print("Identifying addresses related to:")
    print("-"*70) 
    for count, addr in enumerate(addresses):
        print ('{:>3}. {:<39}'.format(count+1,addr))
    print("-"*70) 
    print('')
    print("Please wait...") 

    related_addr_dict = bq.getRelatedAddresses(recursive, includechangeinputs, maxresult, None, *addresses)
    running_balance = 0
  
    #Generate text report
    os.system('cls' if os.name == 'nt' else 'clear')
    NonZeroAccount = 0
    if(suppresszero):
        print("Non Zero Related Accounts") 
    else:
        print("Related Accounts") 
    print("-"*70)
    resultsshown = print_audit_report_body(related_addr_dict,indent,suppresszero)
    if(len(related_addr_dict) == maxresult):
        print('     ...Maximum Limit Reached...')
    if(resultsshown <len(related_addr_dict)):
        print('     ...{:d} Zero Balance Results Suppressed...'.format(maxresult - resultsshown))
    print("-"*70)
    
    # Running balance
    for addr in related_addr_dict:
        running_balance = running_balance + float(bq.getAddressInfo(addr)[0]['final_balance']) / bq.SATOSHIS_IN_A_BITCOIN()
    print("Total BTC {:>60f}".format(running_balance)) 



def print_audit_report_body(related_addr_dict, indent,suppresszero, parent_addr = None, depth=0, line_num = 0):
    '''Outputs the audit report body. The function returns the number of lines printed'''    
    if(parent_addr == None):
         for outer_addr, outer_value in related_addr_dict.iteritems():
            if outer_value['relationtype'] == 'root':
                ref = outer_value['txhash']
                balance = float(bq.getAddressInfo(outer_addr)[0]['final_balance']) / bq.SATOSHIS_IN_A_BITCOIN()
                line_num +=1
                print ('{:>3}. {:<49}{:>16f}'.format(line_num, outer_addr,balance))
                
                # Now we print any address related to the root
                line_num = print_audit_report_body(related_addr_dict, indent, suppresszero, outer_addr, depth+1, line_num)
    else:
        # Now we print any address related to the parent 
        for addr, value in related_addr_dict.iteritems():
            if(value['relation']==parent_addr):
                balance = float(bq.getAddressInfo(addr)[0]['final_balance']) / bq.SATOSHIS_IN_A_BITCOIN()
                MAX_DEPTH = 17
                if(indent):
                    if(depth<MAX_DEPTH):
                        indents = ' ' * (depth-1) + ('=' if value['relationtype'] == 'fellow' else '>' if value['relationtype']=='change' else '?')
                    else:
                        prefix = ' d+' + str(depth-MAX_DEPTH+1)
                        indents =  prefix + ' ' * (MAX_DEPTH-len(prefix)-2) + ('=' if value['relationtype'] == 'fellow' else '>' if value['relationtype']=='change' else '?')
                else:
                    indents=''
                if not suppresszero or balance>0:
                    if(not suppresszero or balance>0):
                        line_num += 1
                        print ('{:>3}. {:<49}{:>16f}'.format(line_num ,indents + addr,balance))
                line_num = print_audit_report_body(related_addr_dict, indent, suppresszero, addr, depth+1, line_num)
    return line_num

def show_help():
    '''Prints the commandline help'''
    filename = os.path.basename(__file__)
    print('Reports the balances of any related bitcoin addresses.')
    print('')
    print('{} [-r][-s][-d][-t][-m] Address1 Address2 ...'.format(filename.upper()))
    print('')
    print('  -r Recursively scan for related addresses')
    print('  -s Suppress addresses with a zero balance')
    print('  -i Indent to show relationships; useful when doing a recursive scan')
    print('  -t Test addresses {0} used for scan'.format(EXAMPLE_ADDRESS))
    print('  -e Calls made to external servers are reported')
    print('  -c Includes inputs that appear to be using a related addresses to store change')
    print('  -m Max results, enter as -m300 to limit results to 300. [Default:50]')
    print('')
    print('eg. {0} -r -s {1}'.format(filename.upper(),EXAMPLE_ADDRESS))
    print('')
    
      
if __name__ == '__main__':
    
    showhelp = False
    recurse = False
    usetestaddress = False
    suppresszero = False
    indent = False
    reportcalls = False
    includechangeinputs = False
    addresses = []
    unknownflags = []
    maxresults = 50
    if len(sys.argv) ==1: showhelp = True 
    else:
        for flag in sys.argv[1:]:
            if flag == '-?': showhelp = True
            elif flag == '-t': usetestaddress = True
            elif flag == '-r': recurse = True
            elif flag == '-s': suppresszero = True
            elif flag == '-i': indent = True
            elif flag == '-e': reportcalls = True
            elif flag == '-c': includechangeinputs = True
            elif flag.startswith('-m'): 
                try:
                    maxresults = int(flag[2:])
                except:
                    showhelp = True
                if maxresults < 1:
                    showhelp = True
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
        generate_related_report(recurse, indent, suppresszero, includechangeinputs, maxresults, EXAMPLE_ADDRESS)
    else :
        generate_related_report(recurse, indent, suppresszero, includechangeinputs, maxresults, *addresses)
    
    if indent:
        print('')
        print('Address Prefix Key')
        print('------------------')
        print('None: Root address, this is one of the keys you searched for')
        print('=   : Fellow input address of its parent')
        print('>   : Used as a change address by its parent')
        if includechangeinputs:
            print('?   : Used its parent as a change address. {May be unreliable}')

        
        
    if reportcalls:
        print('')
        print('Call report')
        print('-----------')
        print('')
        print('Calls to blockchain.info requesting information on addresses: ' + str(bq._get_address_info_cache_misses))
        print('Calls to blockchain.info requesting information on blocks: ' + str(bq._get_block_info_cache_misses))


