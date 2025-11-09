#!/usr/bin/env python3
# ***** resourcelock_ex.py *****

from cjnfuncs.core import set_toolname, logging
from cjnfuncs.resourcelock import resource_lock

set_toolname("resourcelock_ex")
logging.getLogger('cjnfuncs.resourcelock').setLevel(logging.DEBUG)


LOCK_NAME = 'test_lock'
my_lock = resource_lock(LOCK_NAME)


# Attempt to get the lock
if not my_lock.get_lock(1, lock_info='resourcelock_ex.module #1'):   # 1 sec timeout
    logging.warning(f"Lock <{LOCK_NAME}> request timeout")
else:
    logging.warning(f"I have the <{LOCK_NAME}> lock")
    # do interesting stuff with known/secure access to the resource

    # Release the lock so that other processes & threads can use the resource
    my_lock.unget_lock(where_called='at end of code')
    logging.warning(f"Lock <{LOCK_NAME}> released")

my_lock.close()