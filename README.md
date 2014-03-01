Bitcoin Related Addresses Finder
================================

Introduction
------------
The Related Address Finder identifies and reports on any related Bitcoin addresses. This may be useful when attempting to identify muliple addresses controlled by the same owner.

Usage Instructions
------------------
```
RELATEDADDRESSES.PY [-r][-t][-s] Address1 Address2 ...

  -r Recursively scan for related addresses
  -s Suppress addresses with a zero balance
  -t Scans using the test addresses 19hJLtfs5pqv2S4kRySMcnxnCzkNf7rhGS

eg. RELATEDADDRESSES.PY -r -s 19hJLtfs5pqv2S4kRySMcnxnCzkNf7rhGS
```
Example Output
--------------
```
Non Zero Related Accounts
------------------------------------------------------------
  1. 1NCRDwLJWYF6oAi37L53pGHkBz2Bgx3w4C             0.257813
  2. 19hJLtfs5pqv2S4kRySMcnxnCzkNf7rhGS             0.291575
  3. 15qfwdA11R1KhWv6ceZr2iquHDc2V2H1W1             3.000000
  4. 17fhKuTtN3a9yr8X86obh391rJaqJ1BjCj             0.040000
  5. 18WaqDnNRbXpbfgGAv5bC7spb366c4CCfX             0.013000
------------------------------------------------------------
Total BTC                                           3.602388
```
Prerequisites
-------------
This code has only been tested on Python 2.7 and may not work on other versions

Limitations
-----------
* Only limited testing has been done
* Relies on JSON responses from Blockchain.info that can sometimes be slow. Queries are not yet done asynchronously 
* Graceful error handling not yet implemented
* No upper limit on related addresses has been implemented yet. i.e. If there are 100 million related addresses, it will run until it runs out of memory


Related Accounts Identification
-------------------------------
The following addresses will be identified as being related to the address being examined:
* **Fellow Inputs** All input addresses where the address being examined is also an input for that transaction AND there are two or less outputs. The second condition has been included to ignore potential 'coinjoin' transactions.
* **Change Addresses** The smallest output address where the address being examined is the input to a transaction AND there are exactly two output addresses AND the smallest address is smaller than the smallest input address.
 

