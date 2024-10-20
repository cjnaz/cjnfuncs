# resourcelock - Inter-process resource lock mechanism

Skip to [API documentation](#links)

The resourcelock module provides a highly reliable mechanism to lock out other processes
while sharing a common resource.  It uses the posix-ipc module from PiPY.

The resource_lock class keeps track of whether the current code/process has acquired the lock, and appropriately handles releasing the lock, on request.

Any number of named locks may be created to handle whatever lockout scenarios your application may require.  resourcelock may also be used as
semaphore mechanism between scripts, or by using the cli to control code execution in a script.

## Example

Wrap lock-protected resource accesses with `get_lock()` and `unget_lock()` calls

```
#!/usr/bin/env python3
# ***** resourcelock_ex.py *****

from cjnfuncs.core import set_toolname, setuplogging, logging
from cjnfuncs.resourcelock import resource_lock

set_toolname("resourcelock_ex")
setuplogging()
logging.getLogger().setLevel(logging.DEBUG)


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
```

And running this code:
```
$ ./resourcelock_ex.py 
   resourcelock.is_locked            -    DEBUG:  <test_lock> is currently locked?  <False>  Prior info  <2024-10-20 15:47:28.415898 - cli>
   resourcelock.get_lock             -    DEBUG:  <test_lock> lock request successful - Granted         <2024-10-20 16:00:51.864484 - resourcelock_ex.module #1>
resourcelock_ex.<module>             -  WARNING:  I have the <test_lock> lock
   resourcelock.unget_lock           -    DEBUG:  <test_lock> lock released  <at end of code>
resourcelock_ex.<module>             -  WARNING:  Lock <test_lock> released
   resourcelock.close                -    DEBUG:  <test_lock> semaphore closed


$ # Get the lock using the CLI tool
$ resourcelock test_lock get
DEBUG:root:<test_lock> lock request successful - Granted         <2024-10-20 16:01:39.571127 - cli>


$ ./resourcelock_ex.py 
   resourcelock.is_locked            -    DEBUG:  <test_lock> is currently locked?  <True>  Prior info  <2024-10-20 16:01:39.571127 - cli>
   resourcelock.get_lock             -    DEBUG:  <test_lock> lock request timed out  - Current owner   <2024-10-20 16:01:39.571127 - cli>
resourcelock_ex.<module>             -  WARNING:  Lock <test_lock> request timeout
   resourcelock.close                -    DEBUG:  <test_lock> semaphore closed


$ # Unget the lock to allow the code to run again
$ resourcelock test_lock unget
DEBUG:root:<test_lock> lock force released  <cli>
```
Note that the first logged instance of is_locked comes from instantiating the lock (`my_lock = resource_lock(LOCK_NAME`).

<br>

## The demo-resourcelock.py test module shows all of the usage scenarios:

```
#!/usr/bin/env python3
"""Demo/test for cjnfuncs resourcelock functions

Produce / compare to golden results:
    ./demo-resourcelock.py | diff demo-resourcelock-initial-unlocked-golden.txt -
        (Test comments are for this case)

    resourcelock test_lock get
    ./demo-resourcelock.py | diff demo-resourcelock-initial-locked-golden.txt -
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
setuplogging()
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
```
And the output results:
```
$ ./demo-resourcelock.py

***** 0 - Lock instantiation
   resourcelock.is_locked            -    DEBUG:  <test_lock> is currently locked?  <False>  Prior info  <2024-10-20 16:22:06.213743 - cli>

***** 1 - Check the initial lock state
   resourcelock.is_locked            -    DEBUG:  <test_lock> is currently locked?  <False>  Prior info  <>
is_lock returned    <False> - Expecting <False> for initial unlocked test case, and <True> for initial locked test case
   resourcelock.lock_value           -    DEBUG:  <test_lock> semaphore = 1

***** 2 - Get the lock
   resourcelock.get_lock             -    DEBUG:  <test_lock> lock request successful - Granted         <2024-10-20 16:23:54.833327 - Lock in test #2>
get_lock returned   <True> - Expecting <True> if lock request is successful
   resourcelock.is_locked            -    DEBUG:  <test_lock> is currently locked?  <True>  Prior info  <2024-10-20 16:23:54.833327 - Lock in test #2>
   resourcelock.lock_value           -    DEBUG:  <test_lock> semaphore = 0

***** 3 - Get the lock a second time, same_process_ok=False
   resourcelock.get_lock             -    DEBUG:  <test_lock> lock request timed out  - Current owner   <2024-10-20 16:23:54.833327 - Lock in test #2>
get_lock returned   <False> - Expecting <False> Repeated lock request fails
   resourcelock.is_locked            -    DEBUG:  <test_lock> is currently locked?  <True>  Prior info  <2024-10-20 16:23:54.833327 - Lock in test #2>
   resourcelock.lock_value           -    DEBUG:  <test_lock> semaphore = 0

***** 4 - Get the lock a third time, same_process_ok=True
   resourcelock.get_lock             -    DEBUG:  <test_lock> lock already acquired   - Prior grant     <2024-10-20 16:23:54.833327 - Lock in test #2>
get_lock returned   <True> - Expecting <True> Repeated lock request passes with switch
   resourcelock.is_locked            -    DEBUG:  <test_lock> is currently locked?  <True>  Prior info  <2024-10-20 16:23:54.833327 - Lock in test #2>
   resourcelock.lock_value           -    DEBUG:  <test_lock> semaphore = 0

***** 5 - Unget the lock
   resourcelock.unget_lock           -    DEBUG:  <test_lock> lock released  <In test #5>
unget_lock returned <True> - Expecting <True> if lock is successfully released
   resourcelock.is_locked            -    DEBUG:  <test_lock> is currently locked?  <False>  Prior info  <2024-10-20 16:23:54.833327 - Lock in test #2>
   resourcelock.lock_value           -    DEBUG:  <test_lock> semaphore = 1

***** 6 - Unget the lock a second time
   resourcelock.unget_lock           -    DEBUG:  <test_lock> Extraneous lock unget request ignored  <In test #6>
unget_lock returned <False> - Expecting <False> since the lock is not currently set
   resourcelock.is_locked            -    DEBUG:  <test_lock> is currently locked?  <False>  Prior info  <2024-10-20 16:23:54.833327 - Lock in test #2>
   resourcelock.lock_value           -    DEBUG:  <test_lock> semaphore = 1

***** 7 - Attempt to Unget the lock not owned by current process
   resourcelock.get_lock             -    DEBUG:  <test_lock> lock request successful - Granted         <2024-10-20 16:23:54.934063 - Lock in test #7>
   resourcelock.is_locked            -    DEBUG:  <test_lock> is currently locked?  <True>  Prior info  <2024-10-20 16:23:54.934063 - Lock in test #7>
   resourcelock.lock_value           -    DEBUG:  <test_lock> semaphore = 0
   resourcelock.unget_lock           -    DEBUG:  <test_lock> lock unget request ignored - lock not owned by current process  <In test #7>
unget_lock returned <False> - Expecting <False> since lock not obtained by current process
   resourcelock.is_locked            -    DEBUG:  <test_lock> is currently locked?  <True>  Prior info  <2024-10-20 16:23:54.934063 - Lock in test #7>
   resourcelock.lock_value           -    DEBUG:  <test_lock> semaphore = 0

***** 8 - Force Unget
   resourcelock.unget_lock           -    DEBUG:  <test_lock> lock force released  <In test #8>
unget_lock returned <True> - Expecting <True> since lock was set and forced unget
   resourcelock.is_locked            -    DEBUG:  <test_lock> is currently locked?  <False>  Prior info  <2024-10-20 16:23:54.934063 - Lock in test #7>
   resourcelock.lock_value           -    DEBUG:  <test_lock> semaphore = 1

***** 9 - Force Unget when lock not set
   resourcelock.unget_lock           -    DEBUG:  <test_lock> Extraneous lock unget request ignored  <In test #9>
unget_lock returned <False> - Expecting <False> since lock was not set
   resourcelock.is_locked            -    DEBUG:  <test_lock> is currently locked?  <False>  Prior info  <2024-10-20 16:23:54.934063 - Lock in test #7>
   resourcelock.lock_value           -    DEBUG:  <test_lock> semaphore = 1
   resourcelock.close                -    DEBUG:  <test_lock> semaphore closed

Using the cli, get the lock ('resourcelock test_lock get') and run the test again
```

<br>

## CLI tool

resourcelock provides a CLI interface for interacting with locks.
- A lock may be acquired and released - `get`, `unget`
- A lock may be queried and traced - `state`, `trace`
- For testing purposes the `get` operation can be automatically `unget`'ed after `--auto-unget` seconds to test
your tool script's handling of get_lock timeouts.

```
$ resourcelock -h
usage: resourcelock [-h] [-t GET_TIMEOUT] [-m MESSAGE] [-a AUTO_UNGET] [-u UPDATE] LockName {get,unget,state,trace}

Inter-process lock mechanism using posix_ipc
2.4
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
  -m MESSAGE, --message MESSAGE
                        Lock get/unget debug message text (default 'cli')
  -a AUTO_UNGET, --auto-unget AUTO_UNGET
                        After a successful get, unget the lock in (float) sec
  -u UPDATE, --update UPDATE
                        Trace update interval (default 0.5 sec)

```