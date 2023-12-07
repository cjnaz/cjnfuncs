#!/usr/bin/env python3
# ***** timevalue_ex1.py *****

import time
from cjnfuncs.timevalue import timevalue, retime

xx = timevalue('0.5m')
print (xx)
print (f"Sleep <{xx.seconds}> seconds")
time.sleep(xx.seconds)

print()
yy = timevalue("1w")
print (f"{yy.orig_val} = {yy.seconds} seconds = {retime(yy.seconds, 'h')} hours")