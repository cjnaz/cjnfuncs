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

<a id="links"></a>
         
<br>

---

# Links to classes, methods, and functions

- [resource_lock](#resource_lock)
- [get_lock](#get_lock)
- [unget_lock](#unget_lock)
- [is_locked](#is_locked)
- [lock_value](#lock_value)



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
- There is no need to dispose of a lock. While posix-ipc.Semaphore has an unlink() method, resource_lock does
not call it. Lock flags are persistent until the system is rebooted.
- Lock names in the posix_ipc module have `/` prefixes.  resource_lock() prepends the `/` if `lockname`
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

### Parameters
`lockname`
- All processes sharing the given resource must use the same lockname.
    
<br/>

<a id="get_lock"></a>

---

# get_lock (timeout=1) - Request the resource lock

***resource_lock() class member function***

Attempt to acquire/get the lock while waiting up to `timeout` time.  

If the lock was previously acquired by this script (process) then get_lock() immediately returns True.
This allows the script code to not have to track state to decide if the lock has
previously been acquired before calling get_lock() again, leading to cleaner code.

### Parameters
`timeout` (default 1 second)
- The max time, in seconds, to wait to acquire the lock
- None is no timeout - wait forever (Hang forever.  Unwise.)

### Returns
- True:  Lock successfully acquired, timeout time not exceeded
- False: Lock request failed, timed out
        
<br/>

<a id="unget_lock"></a>

---

# unget_lock (force=False) - Release the resource lock

***resource_lock() class member function***

If the lock was acquired by the current process then release the lock.
- If the lock is not currently set then the `unget_lock()` call is discarded, leaving the lock
in the same unset state.
- If the lock is currently set but _not_ acquired by this process then don't release the lock,
unless `force=True`.

### Parameter
`force` (default False)
- Release the lock regardless of whether or not this process acquired it.
- Useful for forced cleanup, for example, by the CLI interface.
- Dangerous if another process had acquired the lock.  Be careful.

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
        