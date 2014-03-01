Bitcoin Related Addresses Finder
================================

Introduction
------------
The Related Address Finder identifies and reports on any related Bitcoin addresses. This may be useful when attempting to identify muliple addresses controlled by the same owner.

Usage
-----
```
RELATEDADDRESSES.PY [-r][-t][-s] Address1 Address2 ...

  -r Recursively scan for related addresses
  -s Suppress addresses with a zero balance
  -t Scans using the test addresses 19hJLtfs5pqv2S4kRySMcnxnCzkNf7rhGS

eg. RELATEDADDRESSES.PY -r -s 19hJLtfs5pqv2S4kRySMcnxnCzkNf7rhGS
```
Prerequisites
-------------
This code has only been tested on Python 2.7 and may not work on other versions

Related Accounts Identification
-------------------------------
The following addresses will be identified as being related to the address being examined:
* **Fellow Inputs** All input addresses where the address being examined is also an input for that transaction AND there are two or less outputs. The second condition has been included to ignore potential 'coinjoin' transactions.
* **Change Addresses** The smallest output address where the address being examined is the input to a transaction AND there are exactly two output addresses AND the smallest address is smaller than the smallest input address.
