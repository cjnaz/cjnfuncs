#!/usr/bin/env python3
# ***** rwt_ex1.py *****

import time
from cjnfuncs.rwt import run_with_timeout

if __name__ == '__main__':
    # Case 1
    print ("0.5 sec delay")
    run_with_timeout (time.sleep, 0.5, rwt_timeout=1)

    # Case 2
    print ("0.5 sec delay, killed after 0.2 sec")
    run_with_timeout (time.sleep, 0.5, rwt_timeout=0.2)
