#!/usr/bin/env python3
from cjnfuncs.core import set_toolname, setuplogging, logging
from cjnfuncs.resourcelock import resource_lock

set_toolname("demo-resourcelock")
setuplogging()
logging.getLogger().setLevel(logging.DEBUG)

LOCK_NAME = 'test_lock'

my_lock = resource_lock(LOCK_NAME)


print ("\n***** Check the initial lock state")
my_lock.is_locked()
my_lock.lock_value()

print ("\n***** Get the lock")
print (f"get_lock:   {my_lock.get_lock(timeout=0.1)} - <True> if lock request is successful")
my_lock.is_locked()
my_lock.lock_value()

print ("\n***** Get the lock a second time")
print (f"get_lock:   {my_lock.get_lock(timeout=0.1)} - Repeated lock requests from same process return <True>")
my_lock.is_locked()
my_lock.lock_value()

print ("\n***** Unget the lock")
print (f"unget_lock: {my_lock.unget_lock()} - <True> if lock is successfully released")
my_lock.is_locked()
my_lock.lock_value()

print ("\n***** Unget the lock a second time")
print (f"unget_lock: {my_lock.unget_lock()} - <False> since the lock is not currently set")
my_lock.is_locked()
my_lock.lock_value()

print ("\n***** Attempt to Unget the lock not owned by current process")
my_lock.get_lock(timeout=0.1)
my_lock.I_have_the_lock = False
my_lock.is_locked()
my_lock.lock_value()
print (f"unget_lock: {my_lock.unget_lock()} - <False> since lock not obtained by current process")
my_lock.is_locked()
my_lock.lock_value()

print ("\n***** Force Unget")
print (f"unget_lock: {my_lock.unget_lock(force=True)} - <True> since lock was set and forced unget")
my_lock.is_locked()
my_lock.lock_value()

print ("\n***** Force Unget when lock not set")
print (f"unget_lock: {my_lock.unget_lock(force=True)} - <False> since lock was not set")
my_lock.is_locked()
my_lock.lock_value()


print ()
print (f"Using the cli, get the lock ('resourcelock {LOCK_NAME} get') and run the test again")