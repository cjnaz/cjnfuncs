#!/usr/bin/env python3
"""Inter-process lock mechanism using posix_ipc

Only works on Linux
"""

#==========================================================
#
#  Chris Nelson, Copyright 2024-2026
#
#==========================================================

import signal
import sys
import posix_ipc
import mmap
import os
import datetime
from .core import logging, set_toolname, setuplogging, set_logging_level

import importlib.metadata
__version__ = importlib.metadata.version(__package__ or __name__)


# Logging events within this module are at the DEBUG level.  With this module's child logger set to
# a minimum of WARNING level by default, then logging from this module is effectively disabled.  To enable
# logging from this module add this within your tool script code:
#       logging.getLogger('cjnfuncs.resourcelock').setLevel(logging.DEBUG)
resourcelock_logger = logging.getLogger('cjnfuncs.resourcelock')

# Logging from the .is_locked method is enabled by:
#       logging.getLogger('cjnfuncs.resourcelock_islocked').setLevel(logging.DEBUG)
resourcelock_logger_islocked = logging.getLogger('cjnfuncs.resourcelock_islocked')


#=====================================================================================
#=====================================================================================
#  r e s o u r c e _ l o c k
#=====================================================================================
#=====================================================================================

class resource_lock():
    """
## Class resource_lock (lockname, shared_mem_size=4096) - Inter-process lock mechanism using posix_ipc

__NOTE:  This module only works on Linux.__

In applications that have independent processes sharing a resource, such as an I2C bus, `resource_lock()`
provides a semaphore communication mechanism between the processes, using the posix-ipc module, 
in order to coordinate access to the shared resource.  By using resource_lock(), ProcessA becomes aware
that the I2C bus is in-use by some other process (ProcessB), and it should wait until that other 
process completes its work, and then acquire the I2C bus lock so that other process(es) are blocked. 

- Resource locks are on the honor system.  Any process can unget a lock, but should not if it didn't get the lock.

- This lock mechanism is just as effective across threads within a process, and between processes.

- As many different/independent locks as needed may be created.

- The first time a lock is created (on the current computer since reboot) the lock info string is set to ''
(accessible via `get_lock_info()`), else it retains the value set by the most recent get_lock() call.

- It is recommended (in order to avoid a minor memory leak) to `close()` the lock in the tool script cleanup code.
Calling `close()` sets the `closed` attribute to True so that any following code within the current tool script
can detect and re-instantiate the lock if needed.

- Semaphores (lock names) and shared memory segments (used for the `lock_info` string) in the posix_ipc module 
must have `/` prefixes.  resource_lock() prepends the `/` if `lockname` doesn't start with a `/`, and hides the `/` prefix.

resource_lock() requires the `posix_ipc` module (installed with cjnfuncs) from PyPI. 
See https://pypi.org/project/posix-ipc/.

NOTE that a crashed process may not have released the lock, resulting in other processes using the lock to hang.
Use the CLI command `resourcelock <lockname> unget` to manually release the lock to un-block other processes.

resource_lock() uses `posix_ipc.Semaphore`, which is a counter mechanism. `get_lock()` 
decrements the counter to 0, indicating a locked state.  `unget_lock()` increments the
counter (non-zero is unlocked). `unget_lock()` wont increment the counter unless the counter is 
currently 0 (indicating locked), so it is ***recommended*** to place (possibly extraneous) `unget_lock()` calls 
in your interrupt-trapped cleanup code so that interrupted code certainly releases the lock.


### Args
`lockname` (str)
- All processes sharing a given resource must use the same lockname.

`shared_mem_size` (int, default 4096)
- The size of the shared memory block associated with `lockname`


### Class attributes
`lockname` (str)
- As specified when the resource_lock was instantiated

`I_have_the_lock` (bool)
- True if the current process has set the lock.  Useful for conditionally ungetting the lock in cleanup code.

`closed` (bool)
- False once instantiated and set True if `close()` is called in script cleanup code, so that the lock can 
checked and re-instantiate if needed.
    """

    def __init__ (self, lockname, shared_mem_size=4096):
        if not lockname.startswith('/'):
            lockname = '/'+lockname         # lockname is required to start with '/'
        self.lockname =         lockname
        self.closed =           False
        self.I_have_the_lock =  False
        self.lock = posix_ipc.Semaphore(self.lockname, flags=posix_ipc.O_CREAT, mode=0o0600, initial_value=1)
        resourcelock_logger.debug (f"<{self.lockname[1:]}> posix_ipc.Semaphore object info: <{self.lock}>")

        preexisting = False
        try:
            memory = posix_ipc.SharedMemory(self.lockname, flags=0)
            preexisting = True
        except posix_ipc.ExistentialError:
            memory = posix_ipc.SharedMemory(self.lockname, flags=posix_ipc.O_CREAT, mode=0o0600, size=shared_mem_size)
        resourcelock_logger.debug (f"<{self.lockname[1:]}> posix_ipc.SharedMemory object info: <{self.lock}>")

        self.mapfile = mmap.mmap(memory.fd, memory.size)
        os.close(memory.fd)
        if not preexisting:
            self.set_lock_info('')


#=====================================================================================
#=====================================================================================
#  g e t _ l o c k
#=====================================================================================
#=====================================================================================

    def get_lock(self, timeout=1.0, same_process_ok=False, lock_info=''):
        """
## get_lock (timeout=1.0, same_process_ok=False, lock_info='') - Request the resource lock

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
- The current datetime is prepended to lock_info.
- A useful lock_info string format might be `<module_name>.<function_name> <get_lock_call_instance_number>`, eg, 
`tempmon.measure_loop #3`.
- This string remains in place after an unget() call for lock history purposes while debugging.

### Returns
- True:  Lock successfully acquired, timeout time not exceeded
- False: Lock request failed, timed out
        """
        if same_process_ok  and  self.I_have_the_lock == True:
            resourcelock_logger.debug (f"<{self.lockname[1:]}> lock already acquired   - Prior grant     <{self.get_lock_info()}>")
            return True

        try:
            self.lock.acquire(timeout)
            lock_text = f"{datetime.datetime.now()} - {lock_info}"
            self.set_lock_info(lock_text)
            self.I_have_the_lock = True
            resourcelock_logger.debug (f"<{self.lockname[1:]}> lock request successful - Granted         <{lock_text}>")
            return True
        except posix_ipc.BusyError:
            resourcelock_logger.debug (f"<{self.lockname[1:]}> lock request timed out  - Current owner   <{self.get_lock_info()}>")
            return False


#=====================================================================================
#=====================================================================================
#  u n g e t _ l o c k
#=====================================================================================
#=====================================================================================

    def unget_lock(self, force=False, where_called=''):
        """
## unget_lock (force=False, where_called='') - Release the resource lock

***resource_lock() class member function***

If the lock was acquired by the current process then release the lock.
- If the lock is not currently set then the `unget_lock()` call is discarded, leaving the lock
in the same unset state.
- If the lock is currently set but _not_ acquired by this process then don't release the lock,
unless `force=True`.  _Lock unget request ignored_ calls are logged at the info level.

### Arg
`force` (bool, default False)
- Release the lock regardless of whether or not this process acquired it.
- Useful for forced cleanup, for example, by the CLI interface.
- Dangerous if another process had acquired the lock.  Be careful.

`where_called` (str, default '')
- Debugging aid string for indicating what code released the lock.  Logged at the debug level.
Not stored nor available to a later call.

### Returns
- True:  Lock successfully released
- False: Lock not currently set (redundant unget_lock() call), or lock was not acquired by the current process
        """
        if self.lock.value == 0:
            if self.I_have_the_lock:
                self.lock.release()
                self.I_have_the_lock = False
                resourcelock_logger.debug (f"<{self.lockname[1:]}> lock released  <{where_called}>")
                return True
            else:
                if force:
                    self.lock.release()
                    resourcelock_logger.debug (f"<{self.lockname[1:]}> lock force released  <{where_called}>")
                    return True
                else:
                    resourcelock_logger.info (f"<{self.lockname[1:]}> lock unget request ignored - lock not owned by current process  <{where_called}>")
                    return False
        else:
            resourcelock_logger.debug (f"<{self.lockname[1:]}> Extraneous lock unget request ignored  <{where_called}>")
            return False


#=====================================================================================
#=====================================================================================
#  i s _ l o c k e d
#=====================================================================================
#=====================================================================================

    def is_locked(self):
        """
## is_locked () - Returns the current state of the lock

***resource_lock() class member function***

Note that `is_locked()` uses a separate child logger - `'cjnfuncs.resourcelock_islocked'` - so that `is_locked()` may be 
checked in a loop without flooding the log.  `is_locked()` calls are logged at the debug level.

### Returns
- True if currently locked, else False
        """
        locked = True  if self.lock.value == 0  else False
        resourcelock_logger_islocked.debug (f"<{self.lockname[1:]}> is currently locked?  <{locked}>  Prior info  <{self.get_lock_info()}>")
        return locked


#=====================================================================================
#=====================================================================================
#  l o c k _ v a l u e
#=====================================================================================
#=====================================================================================

    def lock_value(self):
        """
## lock_value () - Returns the lock semaphore count

***resource_lock() class member function***

### Returns
- Current value of the semaphore count - should be 0 (locked) or 1 (unlocked)
        """
        _value = self.lock.value
        resourcelock_logger.debug (f"<{self.lockname[1:]}> semaphore = {_value}")
        return _value


#=====================================================================================
#=====================================================================================
#  s e t _ l o c k _ i n f o
#=====================================================================================
#=====================================================================================

    def set_lock_info(self, desc):
        """
## set_lock_info (desc) - Set the shared memory block to `desc`

***resource_lock() class member function***

### Args

desc (str)
- String content written to the shared memory block
- Max size is as defined at lock instantiation via `shared_mem_size`, default 4k bytes


### Returns
- None


### Behaviors and rules
- `get_lock()` writes info for who requested the lock and when to shared memory.
- The shared memory block is allocated when the lock is instantiated, and may be written and read
independent of `get_lock()` and `unget_lock()`, thus used as a shared memory string block.
- Data stored in the shared memory block is stored as bytes.  `set_lock_info()` encodes `desc` as bytes, and 
`get_lock_info()` decodes the shared memory bytes to str.
- In shared memory the bytes list is terminated by a null character (0x00).
        """
        self.mapfile.seek(0)
        desc += '\0'
        self.mapfile.write(desc.encode())
       

#=====================================================================================
#=====================================================================================
#  g e t _ l o c k _ i n f o
#=====================================================================================
#=====================================================================================

    def get_lock_info(self):
        """
## get_lock_info () - Returns the `desc` string from previous `set_lock_info` call

***resource_lock() class member function***

### Returns
- `set_lock_info(desc)` string
        """
        self.mapfile.seek(0)
        s = []
        c = self.mapfile.read_byte()
        while c != 0:    # NULL_CHAR
            s.append(c)
            c = self.mapfile.read_byte()

        s = ''.join([chr(c) for c in s])

        return s


#=====================================================================================
#=====================================================================================
#  c l o s e
#=====================================================================================
#=====================================================================================

    def close(self):
        """
## close () - Release this process' access to the semaphore and the memory-mapped shared memory segment

***resource_lock() class member function***

### Returns
- None
        """
        self.lock.close()
        self.mapfile.close()
        self.closed = True
        resourcelock_logger.debug (f"<{self.lockname[1:]}> semaphore closed")



#=====================================================================================
#=====================================================================================
#  c l i
#=====================================================================================
#=====================================================================================

def int_handler(sig, frame):
    resourcelock_logger.warning(f"Signal {sig} received")
    sys.exit(0)

signal.signal(signal.SIGINT,  int_handler)      # Ctrl-C
signal.signal(signal.SIGTERM, int_handler)      # kill


def cli():
    """**** Inter-process lock mechanism using posix_ipc ****

Commands:
    get:    Get/set the lock named LockName.  '-a' specifies a automatic timed unget (only applied if the get was successful).
    unget:  Force-release LockName.
    state:  Print the current state of LockName.
    trace:  Continuously print the state of LockName.  '-u' specifies update interval.  Ctrl-C to exit.
"""
    import argparse
    from time import sleep

    TOOLNAME =          'resourcelock'

    set_toolname (TOOLNAME)
    setuplogging()

    GET_TIMEOUT =       0.5
    TRACE_INTERVAL =    0.5
    

    parser = argparse.ArgumentParser(description=cli.__doc__ + __version__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('LockName',
                        help="Name of the system-wide lock to access")
    parser.add_argument('Command', choices=['get', 'unget', 'state', 'trace'],
                        help="Command choices")
    parser.add_argument('-t', '--get-timeout', type=float, default=GET_TIMEOUT,
                        help=f"Timeout value for a get call (default {GET_TIMEOUT} sec, -1 for no timeout)")
    parser.add_argument('-m', '--message', default='cli',
                        help=f"Lock get/unget debug message text (default 'cli')")
    parser.add_argument('-a', '--auto-unget', type=float,
                        help="After a successful get, unget the lock in (float) sec")
    parser.add_argument('-u', '--update', type=float, default=TRACE_INTERVAL,
                        help=f"Trace update interval (default {TRACE_INTERVAL} sec)")
    parser.add_argument('-v', '--verbose', action='count', default=0,
                        help="Print status and activity messages (-vv for debug level logging)")
    parser.add_argument('-V', '--version', action='version', version=f"{TOOLNAME} {__version__}",
                        help="Print version number and exit")
    args = parser.parse_args()


    ll = [logging.WARNING, logging.INFO, logging.DEBUG][args.verbose]
    set_logging_level (ll, logger_name='cjnfuncs.resourcelock')
    set_logging_level (ll, logger_name='cjnfuncs.resourcelock_islocked')

    lock = resource_lock(args.LockName)

    if args.Command == "get":
        _timeout = args.get_timeout
        if _timeout == -1:
            _timeout = None
        get_result = lock.get_lock(timeout=_timeout, lock_info=args.message)
        print (f"<{args.LockName}> get_lock called - Returned <{get_result}>, Currently locked: <{lock.is_locked()}>, Lock info: <{lock.get_lock_info()}>")
        if get_result and args.auto_unget:
            print (f"Release lock after <{args.auto_unget}> sec delay")
            sleep(args.auto_unget)
            unget_result = lock.unget_lock(where_called=f'{args.message} - auto unget')
            print (f"<{args.LockName}> unget_lock called - Returned <{unget_result}>, Currently locked: <{lock.is_locked()}>, Lock info: <{lock.get_lock_info()}>")

    elif args.Command == "unget":
        unget_result = lock.unget_lock(force=True, where_called=args.message)
        print (f"<{args.LockName}> unget_lock called - Returned <{unget_result}>, Currently locked: <{lock.is_locked()}>, Lock info: <{lock.get_lock_info()}>")

    elif args.Command == "state":
        print (f"<{args.LockName}> Currently locked: <{lock.is_locked()}>, Lock info: <{lock.get_lock_info()}>")

    elif args.Command == "trace":
        while True:
            print (f"<{args.LockName} Currently locked: <{lock.is_locked()}>, Lock info: <{lock.get_lock_info()}>")
            sleep (args.update)
