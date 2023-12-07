# resourcelock - Inter-process resource lock mechanism

Skip to [API documentation](#links)

The resourcelock module provides a highly reliable mechanism to lock out other processes
while sharing a common resource.  It uses the posix-ipc module from PiPY.

The resource_lock class keeps track of whether the current code/process has acquired the lock, and appropriately handles releasing the lock, on request.

Any number of named locks may be created to handle whatever lockout scenarios your application may require.

## Example

Wrap lock-protected resource accesses with `get_lock()` and `unget_lock()` calls

```
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
```

And running this code:
```
$ ./resourcelock_ex1.py 
resourcelock_ex1.<module>             -  WARNING:  I have the <test_lock> lock
resourcelock_ex1.<module>             -  WARNING:  Lock <test_lock> released

$ # Set the lock using the CLI tool
$ resourcelock test_lock get
DEBUG:root:<test_lock> lock request successful (Semaphore = 0)

$ ./resourcelock_ex1.py 
resourcelock_ex1.<module>             -  WARNING:  Lock <test_lock> request timeout

```

## The demo-resourcelock.py test module shows all of the usage scenarios:

```
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
print (f"Using the cli, get the lock ('resourcelock {LOCK_NAME} get') and run the test again")```
```
And the output results:
```
$ ./demo-resourcelock.py

***** Check the initial lock state
   resourcelock.is_locked            -    DEBUG:  <test_lock> is currently locked? False
   resourcelock.lock_value           -    DEBUG:  <test_lock> semaphore = 1

***** Get the lock
   resourcelock.get_lock             -    DEBUG:  <test_lock> lock request successful (Semaphore = 0)
get_lock:   True - <True> if lock request is successful
   resourcelock.is_locked            -    DEBUG:  <test_lock> is currently locked? True
   resourcelock.lock_value           -    DEBUG:  <test_lock> semaphore = 0

***** Get the lock a second time
get_lock:   True - Repeated lock requests from same process return <True>
   resourcelock.is_locked            -    DEBUG:  <test_lock> is currently locked? True
   resourcelock.lock_value           -    DEBUG:  <test_lock> semaphore = 0

***** Unget the lock
   resourcelock.unget_lock           -    DEBUG:  <test_lock> lock released (Semaphore = 1)
unget_lock: True - <True> if lock is successfully released
   resourcelock.is_locked            -    DEBUG:  <test_lock> is currently locked? False
   resourcelock.lock_value           -    DEBUG:  <test_lock> semaphore = 1

***** Unget the lock a second time
   resourcelock.unget_lock           -    DEBUG:  <test_lock> Extraneous lock unget request ignored (Semaphore = 1)
unget_lock: False - <False> since the lock is not currently set
   resourcelock.is_locked            -    DEBUG:  <test_lock> is currently locked? False
   resourcelock.lock_value           -    DEBUG:  <test_lock> semaphore = 1

***** Attempt to Unget the lock not owned by current process
   resourcelock.get_lock             -    DEBUG:  <test_lock> lock request successful (Semaphore = 0)
   resourcelock.is_locked            -    DEBUG:  <test_lock> is currently locked? True
   resourcelock.lock_value           -    DEBUG:  <test_lock> semaphore = 0
   resourcelock.unget_lock           -    DEBUG:  <test_lock> lock unget request ignored - lock not owned by current process (Semaphore = 0)
unget_lock: False - <False> since lock not obtained by current process
   resourcelock.is_locked            -    DEBUG:  <test_lock> is currently locked? True
   resourcelock.lock_value           -    DEBUG:  <test_lock> semaphore = 0

***** Force Unget
   resourcelock.unget_lock           -    DEBUG:  <test_lock> lock force released (Semaphore = 1)
unget_lock: True - <True> since lock was set and forced unget
   resourcelock.is_locked            -    DEBUG:  <test_lock> is currently locked? False
   resourcelock.lock_value           -    DEBUG:  <test_lock> semaphore = 1

***** Force Unget when lock not set
   resourcelock.unget_lock           -    DEBUG:  <test_lock> Extraneous lock unget request ignored (Semaphore = 1)
unget_lock: False - <False> since lock was not set
   resourcelock.is_locked            -    DEBUG:  <test_lock> is currently locked? False
   resourcelock.lock_value           -    DEBUG:  <test_lock> semaphore = 1

Using the cli, get the lock ('resourcelock test_lock get') and run the test again
```

## CLI tool

resourcelock provides a CLI interface for interacting with locks.
- A lock may be acquired and released - `get`, `unget`
- A lock may be queried and traced - `state`, `trace`
- For testing purposes the `get` operation can be automatically `unget`'ed after `--auto-unget` seconds to test
your tool script's handling of get_lock timeouts.

```
$ resourcelock -h
usage: resourcelock [-h] [-t GET_TIMEOUT] [-a AUTO_UNGET] [-u UPDATE] LockName {get,unget,state,trace}

Inter-process lock mechanism using posix_ipc
2.1b8
    Commands:
        get:    Get/set the lock named LockName.  '-a' specifies a automatic timed unget (only applied if the get was successful).
        unget:  Force-release LockName.
        state:  Print the current state of LockName.
        trace:  Continuously print the state of LockName.  '-u' specifies update interval.  Ctrl-C to exit.
    

positional arguments:
  LockName              Name of the system-wide lock to access
  {get,unget,state,trace}
                        Command choices

options:
  -h, --help            show this help message and exit
  -t GET_TIMEOUT, --get-timeout GET_TIMEOUT
                        Timeout value for a get call (default 0.5 sec, -1 for no timeout)
  -a AUTO_UNGET, --auto-unget AUTO_UNGET
                        After a successful get, unget the lock in (float) sec
  -u UPDATE, --update UPDATE
                        Trace update interval (default 0.5 sec)
```