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

<a id="links"></a>
         
<br>

---

# Links to classes, methods, and functions

- [resource_lock](#resource_lock)
- [get_lock](#get_lock)
- [unget_lock](#unget_lock)
- [is_locked](#is_locked)
- [lock_value](#lock_value)
- [close](#close)
- [get_lock_info](#get_lock_info)



<br/>

<a id="resource_lock"></a>

---

# Class resource_lock (lockname) - Inter-process lock mechanism using posix_ipc

In applications that have independent processes sharing a resource, such as an I2C bus, `resource_lock()`
provides a semaphore communication mechanism between the processes, using the posix-ipc module, 
in order to coordinate access to the shared resource.  By using resource_lock(), ProcessA becomes aware
that the I2C bus is in-use by some other process (ProcessB), and it should wait until that other 
process completes its work, and then acquire the I2C bus lock so that other process(es) are blocked. 
- Resource locks are on the honor system.  Any process can unget a lock, but should not if it didn't get the lock.
- This lock mechanism is just as effective across threads within a process.
- As many different/independent locks as needed may be created.
- The first time a lock is created (on the current computer since reboot) the lock info string (accessible via `get_lock_info()`)
is set to '', else it retains the value set by the most recent get_lock() call.
- It is recommended (in order to avoid a minor memory leak) to `close()` the lock in the tool script cleanup code.
Calling `close()` sets the `closed` attribute to True so that any following code can detect and re-instantiate the 
lock if needed.
- Semaphores (lock names) and shared memory segments (used for the `lock_info` string) in the posix_ipc module 
must have `/` prefixes.  resource_lock() prepends the `/` if `lockname`
doesn't start with a `/`, and hides the `/` prefix.

resource_lock() requires the `posix_ipc` module (installed with cjnfuncs) from PyPI. 
See https://pypi.org/project/posix-ipc/.

NOTE that a crashed process may not have released the lock, resulting in other processes using the lock to hang.
Use the CLI command `resourcelock <lockname> unget` to manually release the lock to un-block other processes.

resource_lock() uses `posix_ipc.Semaphore`, which is a counter mechanism. `get_lock()` 
decrements the counter to 0, indicating a locked state.  `unget_lock()` increments the
counter (non-zero is unlocked). `unget_lock()` wont increment the counter unless the counter is 
currently 0 (indicating locked), so it is ***recommended*** to have (possibly extraneous) `unget_lock()` calls, 
such as in your interrupt-trapped cleanup code.


### Args
`lockname` (str)
- All processes sharing a given resource must use the same lockname.

### Class attributes
`lockname` (str)
- As specified when the resource_lock was instantiated

`I_have_the_lock` (bool)
- True if the current process has set the lock.  Useful for conditionally ungetting the lock in cleanup code.

`closed` (bool)
- False once instantiated and set True if `close()` is called in script cleanup code, so that the lock can 
checked and re-instantiate if needed.
    
<br/>

<a id="get_lock"></a>

---

# get_lock (timeout=1.0, same_process_ok=False, lock_info='') - Request the resource lock

***resource_lock() class member function***

Attempt to acquire/get the lock while waiting up to `timeout` time.  

By default, get_lock() waits for the lock if it is currently set, whether the lock was set by this
or another script/job/process.

By setting `same_process_ok=True`, then if the lock was previously acquired by this same script/process
then get_lock() immediately returns True.  This allows the script code to not have to track state to 
decide if the lock has previously been acquired before calling get_lock() again, leading to cleaner code.

### Args
`timeout` (int or float, or None, default 1.0 second)
- The max time, in seconds, to wait to acquire the lock
- None is no timeout - wait forever (Hang forever.  Unwise.)

`same_process_ok` (bool, default False)
- If True, then if the current process currently has the lock then get_lock() immediately returns True.
- If False, then if the lock is currently set by the same process or another process then get_lock() blocks
with timeout.

`lock_info` (str, default '')
- Optional debugging info string for indicating when and by whom the lock was set.  Logged at the debug level.
- The datetime is prepended to lock_info.
- A useful lock_info string format might be `<module_name>.<function_name> <get_lock_call_instance_number>`, eg, 
`tempmon.measure_loop #3`.
- This string remains in place after an unget() call (`is_locked() == False`) for lock history purposes while debugging.

### Returns
- True:  Lock successfully acquired, timeout time not exceeded
- False: Lock request failed, timed out
        
<br/>

<a id="unget_lock"></a>

---

# unget_lock (force=False, where_called='') - Release the resource lock

***resource_lock() class member function***

If the lock was acquired by the current process then release the lock.
- If the lock is not currently set then the `unget_lock()` call is discarded, leaving the lock
in the same unset state.
- If the lock is currently set but _not_ acquired by this process then don't release the lock,
unless `force=True`.

### Arg
`force` (bool, default False)
- Release the lock regardless of whether or not this process acquired it.
- Useful for forced cleanup, for example, by the CLI interface.
- Dangerous if another process had acquired the lock.  Be careful.

`where_called` (str, default '')
- Debugging aid string for indicating what code released the lock.  Logged at the debug level.

### Returns
- True:  Lock successfully released
- False: Lock not currently set (redundant unget_lock() call), or lock was not acquired by the current process
        
<br/>

<a id="is_locked"></a>

---

# is_locked () - Returns the current state of the lock

***resource_lock() class member function***

### Returns
- True if currently locked, else False
        
<br/>

<a id="lock_value"></a>

---

# lock_value () - Returns the lock semaphore count

***resource_lock() class member function***

### Returns
- Current value of the semaphore count - should be 0 (locked) or 1 (unlocked)
        
<br/>

<a id="close"></a>

---

# close () - Release this process' access to the semaphore and the memory-mapped shared memory segment

***resource_lock() class member function***

### Returns
- None
        
<br/>

<a id="get_lock_info"></a>

---

# get_lock_info () - Returns the lock_info string from previous get_lock call

***resource_lock() class member function***

### Returns
- lock_info string
        