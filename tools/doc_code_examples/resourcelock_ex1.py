#!/usr/bin/env python3
# ***** resourcelock_ex1.py *****

from cjnfuncs.core import set_toolname, setuplogging, logging
from cjnfuncs.resourcelock import resource_lock

set_toolname("resourcelock_ex1")
setuplogging()

LOCK_NAME = 'test_lock'
my_lock = resource_lock(LOCK_NAME)


# Attempt to get the lock
if not my_lock.get_lock(1):   # 1 sec timeout
    logging.warning(f"Lock <{LOCK_NAME}> request timeout")
else:
    logging.warning(f"I have the <{LOCK_NAME}> lock")
    # do interesting stuff with known/secure access to the resource

    # Release the lock so that other processes & threads can use the resource
    my_lock.unget_lock()
    logging.warning(f"Lock <{LOCK_NAME}> released")