# resourcelock - Inter-process resource lock and shared memory mechanism

Skip to [API documentation](#links)

The resourcelock module provides a highly reliable mechanism to lock out other processes
while owning/controlling a shared resource.  It uses the posix-ipc module from PyPI, and ONLY WORKS ON LINUX.

The resource_lock class keeps track of whether the current code/process has acquired the lock, and appropriately handles releasing the lock, on request.

Any number of named locks may be created to handle whatever lockout scenarios your application may require.  resourcelock may also be used as a
semaphore mechanism between scripts or other applications, or by using the cli to control code execution within a script.

resourcelock may also be used to allocate shared memory blocks for passing string data between processes.

Semaphores and shared memory blocks live at `/dev/shm`.


## Example

Wrap lock-protected resource accesses with `get_lock()` and `unget_lock()` calls

```
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
```

And running this code:
```
$ ./resourcelock_ex.py 
   resourcelock.get_lock             -    DEBUG:  <test_lock> lock request successful - Granted         <2025-11-06 10:38:11.545309 - resourcelock_ex.module #1>
resourcelock_ex.<module>             -  WARNING:  I have the <test_lock> lock
   resourcelock.unget_lock           -    DEBUG:  <test_lock> lock released  <at end of code>
resourcelock_ex.<module>             -  WARNING:  Lock <test_lock> released
   resourcelock.close                -    DEBUG:  <test_lock> semaphore closed


$ # Get the lock using the CLI tool
$ resourcelock test_lock get
   resourcelock.get_lock             -    DEBUG:  <test_lock> lock request successful - Granted         <2025-11-06 10:39:00.512996 - cli>


$ ./resourcelock_ex.py 
   resourcelock.get_lock             -    DEBUG:  <test_lock> lock request timed out  - Current owner   <2025-11-06 10:39:00.512996 - cli>
resourcelock_ex.<module>             -  WARNING:  Lock <test_lock> request timeout
   resourcelock.close                -    DEBUG:  <test_lock> semaphore closed


$ # Unget the lock to allow the code to run again
$ resourcelock test_lock unget
   resourcelock.unget_lock           -    DEBUG:  <test_lock> lock force released  <cli>


$ ./resourcelock_ex.py 
   resourcelock.get_lock             -    DEBUG:  <test_lock> lock request successful - Granted         <2025-11-06 10:43:02.482497 - resourcelock_ex.module #1>
resourcelock_ex.<module>             -  WARNING:  I have the <test_lock> lock
   resourcelock.unget_lock           -    DEBUG:  <test_lock> lock released  <at end of code>
resourcelock_ex.<module>             -  WARNING:  Lock <test_lock> released
   resourcelock.close                -    DEBUG:  <test_lock> semaphore closed
```


<br>

## The demo-resourcelock.py test module shows all of the usage scenarios:

```
#!/usr/bin/env python3
"""Demo/test for cjnfuncs resourcelock functions

Produce / compare to golden results:
    sudo rm /dev/shm/demo-resourcelock-shm; sudo rm /dev/shm/test_lock
    ./demo-resourcelock.py > testrun.txt
    Compare to:     demo-resourcelock-initial-unlocked-golden.txt
        Test comments are for this case
        Timestamps will be different

    resourcelock test_lock get
    ./demo-resourcelock.py > testrun.txt
    Compare to:     demo-resourcelock-initial-locked-golden.txt
        Timestamps will be different
"""

#==========================================================
#
#  Chris Nelson, 2024-2026
#
#==========================================================

__version__ = "3.2"     # Added test 10

from cjnfuncs.core import set_toolname, logging
from cjnfuncs.resourcelock import resource_lock

set_toolname("demo-resourcelock")
logging.getLogger('cjnfuncs.resourcelock').setLevel(logging.DEBUG)
logging.getLogger('cjnfuncs.resourcelock_islocked').setLevel(logging.DEBUG)
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


print ("\n***** 10 - set_lock_info/get_lock_info")
my_shm = resource_lock('demo-resourcelock-shm')
print (f"demo-resourcelock-shm on init:    <{my_shm.get_lock_info()}>")

my_shm.set_lock_info("""Hello, my name is Scarecrow.
I could while away the hours, conferrin' with the flowers...
    If I only had a brain.
""")
print (f"demo-resourcelock-shm after set:  <{my_shm.get_lock_info()}>")

my_shm.close()


print ()
print (f"Using the cli, get the lock ('resourcelock {LOCK_NAME} get') and run the test again")
```

And the output results:

```
$ ./demo-resourcelock.py

***** 0 - Lock instantiation
   resourcelock.__init__             -    DEBUG:  <test_lock> posix_ipc.Semaphore object info: </test_lock>
   resourcelock.__init__             -    DEBUG:  <test_lock> posix_ipc.SharedMemory object info: </test_lock>

***** 1 - Check the initial lock state
   resourcelock.is_locked            -    DEBUG:  <test_lock> is currently locked?  <False>  Prior info  <>
is_lock returned    <False> - Expecting <False> for initial unlocked test case, and <True> for initial locked test case
   resourcelock.lock_value           -    DEBUG:  <test_lock> semaphore = 1

***** 2 - Get the lock
   resourcelock.get_lock             -    DEBUG:  <test_lock> lock request successful - Granted         <2026-05-04 09:14:00.512516 - Lock in test #2>
get_lock returned   <True> - Expecting <True> if lock request is successful
   resourcelock.is_locked            -    DEBUG:  <test_lock> is currently locked?  <True>  Prior info  <2026-05-04 09:14:00.512516 - Lock in test #2>
   resourcelock.lock_value           -    DEBUG:  <test_lock> semaphore = 0

***** 3 - Get the lock a second time, same_process_ok=False
   resourcelock.get_lock             -    DEBUG:  <test_lock> lock request timed out  - Current owner   <2026-05-04 09:14:00.512516 - Lock in test #2>
get_lock returned   <False> - Expecting <False> Repeated lock request fails
   resourcelock.is_locked            -    DEBUG:  <test_lock> is currently locked?  <True>  Prior info  <2026-05-04 09:14:00.512516 - Lock in test #2>
   resourcelock.lock_value           -    DEBUG:  <test_lock> semaphore = 0

***** 4 - Get the lock a third time, same_process_ok=True
   resourcelock.get_lock             -    DEBUG:  <test_lock> lock already acquired   - Prior grant     <2026-05-04 09:14:00.512516 - Lock in test #2>
get_lock returned   <True> - Expecting <True> Repeated lock request passes with switch
   resourcelock.is_locked            -    DEBUG:  <test_lock> is currently locked?  <True>  Prior info  <2026-05-04 09:14:00.512516 - Lock in test #2>
   resourcelock.lock_value           -    DEBUG:  <test_lock> semaphore = 0

***** 5 - Unget the lock
   resourcelock.unget_lock           -    DEBUG:  <test_lock> lock released  <In test #5>
unget_lock returned <True> - Expecting <True> if lock is successfully released
   resourcelock.is_locked            -    DEBUG:  <test_lock> is currently locked?  <False>  Prior info  <2026-05-04 09:14:00.512516 - Lock in test #2>
   resourcelock.lock_value           -    DEBUG:  <test_lock> semaphore = 1

***** 6 - Unget the lock a second time
   resourcelock.unget_lock           -    DEBUG:  <test_lock> Extraneous lock unget request ignored  <In test #6>
unget_lock returned <False> - Expecting <False> since the lock is not currently set
   resourcelock.is_locked            -    DEBUG:  <test_lock> is currently locked?  <False>  Prior info  <2026-05-04 09:14:00.512516 - Lock in test #2>
   resourcelock.lock_value           -    DEBUG:  <test_lock> semaphore = 1

***** 7 - Attempt to Unget the lock not owned by current process
   resourcelock.get_lock             -    DEBUG:  <test_lock> lock request successful - Granted         <2026-05-04 09:14:00.614527 - Lock in test #7>
   resourcelock.is_locked            -    DEBUG:  <test_lock> is currently locked?  <True>  Prior info  <2026-05-04 09:14:00.614527 - Lock in test #7>
   resourcelock.lock_value           -    DEBUG:  <test_lock> semaphore = 0
   resourcelock.unget_lock           -    DEBUG:  <test_lock> lock unget request ignored - lock not owned by current process  <In test #7>
unget_lock returned <False> - Expecting <False> since lock not obtained by current process
   resourcelock.is_locked            -    DEBUG:  <test_lock> is currently locked?  <True>  Prior info  <2026-05-04 09:14:00.614527 - Lock in test #7>
   resourcelock.lock_value           -    DEBUG:  <test_lock> semaphore = 0

***** 8 - Force Unget
   resourcelock.unget_lock           -    DEBUG:  <test_lock> lock force released  <In test #8>
unget_lock returned <True> - Expecting <True> since lock was set and forced unget
   resourcelock.is_locked            -    DEBUG:  <test_lock> is currently locked?  <False>  Prior info  <2026-05-04 09:14:00.614527 - Lock in test #7>
   resourcelock.lock_value           -    DEBUG:  <test_lock> semaphore = 1

***** 9 - Force Unget when lock not set
   resourcelock.unget_lock           -    DEBUG:  <test_lock> Extraneous lock unget request ignored  <In test #9>
unget_lock returned <False> - Expecting <False> since lock was not set
   resourcelock.is_locked            -    DEBUG:  <test_lock> is currently locked?  <False>  Prior info  <2026-05-04 09:14:00.614527 - Lock in test #7>
   resourcelock.lock_value           -    DEBUG:  <test_lock> semaphore = 1
   resourcelock.close                -    DEBUG:  <test_lock> semaphore closed

***** 10 - set_lock_info/get_lock_info
   resourcelock.__init__             -    DEBUG:  <demo-resourcelock-shm> posix_ipc.Semaphore object info: </demo-resourcelock-shm>
   resourcelock.__init__             -    DEBUG:  <demo-resourcelock-shm> posix_ipc.SharedMemory object info: </demo-resourcelock-shm>
demo-resourcelock-shm on init:    <>
demo-resourcelock-shm after set:  <Hello, my name is Scarecrow.
I could while away the hours, conferrin' with the flowers...
    If I only had a brain.
>
   resourcelock.close                -    DEBUG:  <demo-resourcelock-shm> semaphore closed

Using the cli, get the lock ('resourcelock test_lock get') and run the test again
```

<br>

## String block shared across processes

Associated with an instantiated lock is also a shared memory block.  When `get_lock()` is called the `lock_info` string is stored
in this associated shared memory block.  

Alternately, this shared memory block may be used as a general purpose shared memory block for sharing string data across processes.  You may wish to use another lock to signal across processes that there is new data in the shared memory block.

### Example string passing between processes (also see above test case 10):

```
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
```

```
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

Only works on Linux
3.2
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

<br>

## Controlling logging from within resourcelock code

Logging within the resourcelock module uses the `cjnfuncs.resourcelock` and `cjnfuncs.resourcelock_islocked` named/child loggers.  By default these loggers are set to the `logging.WARNING` level, 
meaning that no logging messages are produced from within the resourcelock code.  For validation and debug purposes, logging from within resourcelock code (other than from is_locked())
can be enabled by setting this module's logging level as follows from within the tool script code:

        logging.getLogger('cjnfuncs.resourcelock').setLevel(logging.DEBUG)

        # Or alternately, use the core module set_logging_level() function:
        set_logging_level (logging.DEBUG, 'cjnfuncs.resourcelock')

The `.is_locked()` method uses the separate `cjnfuncs.resourcelock_islocked` named/child logger so that .is_locked() may be used in a loop without flooding the log.  To enable debug logging from is_locked():

        logging.getLogger('cjnfuncs.resourcelock_islocked').setLevel(logging.DEBUG)

        # Or alternately, use the core module set_logging_level() function:
        set_logging_level (logging.DEBUG, 'cjnfuncs.resourcelock_islocked')

