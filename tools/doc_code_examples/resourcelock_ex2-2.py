#!/usr/bin/env python3
# ***** resourcelock_ex2-2.py *****

import time
from cjnfuncs.resourcelock import resource_lock

shared_mem_block = resource_lock('shared_mem')
new_data_signal =  resource_lock('new_data_signal')

while 1:
    if new_data_signal.is_locked():
        print (f"New string data received:\n\n<{shared_mem_block.get_lock_info()}>")
        # force=True required since this process did not set the lock
        new_data_signal.unget_lock(force=True)
        break
    time.sleep (0.1)

shared_mem_block.close()
new_data_signal.close()