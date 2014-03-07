Bitcoin Related Addresses Finder
================================

Introduction
------------
The Related Address Finder identifies and reports on any related Bitcoin addresses. This may be useful when attempting to identify muliple addresses controlled by the same owner. This program leverages blockchain.info's api to obtain details on the transactions associated with the addresses being analysed.

Usage Instructions
------------------
```
RELATEDADDRESSES.PY [-r][-s][-d][-t][-m][-p] Address1 Address2 ...

  -r Recursively scan for related addresses
  -s Suppress addresses with a zero balance
  -i Indent to show relationships; useful when doing a recursive scan
  -t Test addresses 18WaqDnNRbXpbfgGAv5bC7spb366c4CCfX used for scan
  -e Calls made to external servers are reported
  -c Includes inputs that appear to be using a related addr to store change
  -m Max results, enter as -m300 to limit results to 300 [Default:50]
  -p Use parallel queries to Blockchain.info to increase speed. [Experimental]

eg. RELATEDADDRESSES.PY -r -s 18WaqDnNRbXpbfgGAv5bC7spb366c4CCfX
```
Example Output 1
----------------
RELATEDADDRESSES.PY -r -s 18WaqDnNRbXpbfgGAv5bC7spb366c4CCfX
```
Non Zero Related Accounts
----------------------------------------------------------------------
  1. 18WaqDnNRbXpbfgGAv5bC7spb366c4CCfX                       0.013000
  2. 1NCRDwLJWYF6oAi37L53pGHkBz2Bgx3w4C                       0.257813
  3. 19hJLtfs5pqv2S4kRySMcnxnCzkNf7rhGS                       0.291575
  4. 15qfwdA11R1KhWv6ceZr2iquHDc2V2H1W1                       3.000000
  5. 17fhKuTtN3a9yr8X86obh391rJaqJ1BjCj                       0.040000
----------------------------------------------------------------------
Total BTC                                                     3.602388
```
Example Output 2 
----------------
RELATEDADDRESSES.PY -r -i 18WaqDnNRbXpbfgGAv5bC7spb366c4CCfX
```
Related Accounts
----------------------------------------------------------------------
  1. 18WaqDnNRbXpbfgGAv5bC7spb366c4CCfX                       0.013000
  2. -1BSWtALfbYFAmwYZysWrV9BMhZJJr2q3ti                      0.000000
  3.  -176zUhfs4pgdcrhmzuxxancNoHvNZP1jEk                     0.000000
  4.  -1uAe9JW5EvSsf6JNWtoxyvnDpVtqpy1wa                      0.000000
  5. -15NjXdHEMhBN61qcu1H7zULbNYH6KiLfcm                      0.000000
  6. -1BVLbn7fZbQuNczNu7Mykw22EoFYx4DCf4                      0.000000
  7. -188RWdfjEXPFKATgRAeMScoMRZWYAjJVFK                      0.000000
  8. -16RvWgMGmu9pAPuMmXeFxNAR6DnxT2HR5q                      0.000000
  9. -1NCRDwLJWYF6oAi37L53pGHkBz2Bgx3w4C                      0.257813
 10. -19hJLtfs5pqv2S4kRySMcnxnCzkNf7rhGS                      0.291575
 11.  -1GUzB4zaNjLSzH3jPCGGUS8ZnmKtWG1mkd                     0.000000

 ....etc....
 
----------------------------------------------------------------------
Total BTC                                                     3.602388
```

Prerequisites
-------------
This code has only been tested on Python 2.7 and may not work on other versions

Limitations
-----------
* Only limited testing has been done
* Relies on JSON responses from Blockchain.info that can sometimes be slow. Queries are not yet done asynchronously 
* Graceful error handling not yet implemented

Related Accounts Identification
-------------------------------
The following addresses will be identified as being related to the address being examined:
* **Fellow Inputs** All input addresses where the address being examined is also an input for that transaction AND there are two or less outputs. The second condition has been included to ignore potential 'coinjoin' transactions.
* **Change Addresses** The smallest output address where the address being examined is the input to a transaction AND there are exactly two output addresses AND the smallest address is smaller than the smallest input address.
 

