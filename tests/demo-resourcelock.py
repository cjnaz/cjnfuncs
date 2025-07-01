#!/usr/bin/env python3
"""Demo/test for cjnfuncs resourcelock functions

Produce / compare to golden results:
    ./demo-resourcelock.py | diff demo-resourcelock-initial-unlocked-golden.txt -
        Test comments are for this case
        Timestamps will be different
        Test 1 Prior info (who locked) may be different

    resourcelock test_lock get
    ./demo-resourcelock.py | diff demo-resourcelock-initial-locked-golden.txt -
        Timestamps will be different
"""

#==========================================================
#
#  Chris Nelson, 2024
#
#==========================================================

__version__ = "1.3"

from cjnfuncs.core import set_toolname, setuplogging, logging
from cjnfuncs.resourcelock import resource_lock

set_toolname("demo-resourcelock")
# setuplogging()
logging.getLogger().setLevel(logging.DEBUG)

LOCK_NAME = 'test_lock'

print ("\n***** 0 - Lock instantiation")
my_lock = resource_lock(LOCK_NAME)

print ("\n***** 1 - Check the initial lock state")
print (f"is_lock returned    <{my_lock.is_locked()}> - Expecting <False> for initial unlocked test case, and <True> for initial locked test case")
my_lock.lock_value()

print ("\n***** 2 - Get the lock")
print (f"get_lock returned   <{my_lock.get_lock(timeout=0.1, lock_info='Lock in test #2')}> - Expecting <True> if lock request is successful")
my_lock.is_locked()
my_lock.lock_value()

print ("\n***** 3 - Get the lock a second time, same_process_ok=False")
print (f"get_lock returned   <{my_lock.get_lock(timeout=0.1, lock_info='Lock try in test #3')}> - Expecting <False> Repeated lock request fails")
my_lock.is_locked()
my_lock.lock_value()

print ("\n***** 4 - Get the lock a third time, same_process_ok=True")
print (f"get_lock returned   <{my_lock.get_lock(timeout=0.1, same_process_ok=True, lock_info='Lock try in test #4')}> - Expecting <True> Repeated lock request passes with switch")
my_lock.is_locked()
my_lock.lock_value()

print ("\n***** 5 - Unget the lock")
print (f"unget_lock returned <{my_lock.unget_lock(where_called='In test #5')}> - Expecting <True> if lock is successfully released")
my_lock.is_locked()
my_lock.lock_value()

print ("\n***** 6 - Unget the lock a second time")
print (f"unget_lock returned <{my_lock.unget_lock(where_called='In test #6')}> - Expecting <False> since the lock is not currently set")
my_lock.is_locked()
my_lock.lock_value()

print ("\n***** 7 - Attempt to Unget the lock not owned by current process")
my_lock.get_lock(timeout=0.1, lock_info='Lock in test #7')
my_lock.I_have_the_lock = False
my_lock.is_locked()
my_lock.lock_value()
print (f"unget_lock returned <{my_lock.unget_lock(where_called='In test #7')}> - Expecting <False> since lock not obtained by current process")
my_lock.is_locked()
my_lock.lock_value()

print ("\n***** 8 - Force Unget")
print (f"unget_lock returned <{my_lock.unget_lock(force=True, where_called='In test #8')}> - Expecting <True> since lock was set and forced unget")
my_lock.is_locked()
my_lock.lock_value()

print ("\n***** 9 - Force Unget when lock not set")
print (f"unget_lock returned <{my_lock.unget_lock(force=True, where_called='In test #9')}> - Expecting <False> since lock was not set")
my_lock.is_locked()
my_lock.lock_value()

my_lock.close()

print ()
print (f"Using the cli, get the lock ('resourcelock {LOCK_NAME} get') and run the test again")