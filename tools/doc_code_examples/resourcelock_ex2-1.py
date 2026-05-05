#!/usr/bin/env python3
# ***** resourcelock_ex2-1.py *****

from cjnfuncs.resourcelock import resource_lock

shared_mem_block = resource_lock('shared_mem')
new_data_signal =  resource_lock('new_data_signal')

my_str = """To be, or not to be...
    Wherever you go, there you are.
        Inconceivable!"""

shared_mem_block.set_lock_info(my_str)
new_data_signal.get_lock()

shared_mem_block.close()
new_data_signal.close()