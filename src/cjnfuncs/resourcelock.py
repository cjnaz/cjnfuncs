#!/usr/bin/env python3
"""Inter-process lock mechanism using posix_ipc
"""

#==========================================================
#
#  Chris Nelson, Copyright 2024
#
#==========================================================

import signal
import sys
import posix_ipc
from .core import logging

try:
    import importlib.metadata
    __version__ = importlib.metadata.version(__package__ or __name__)
except:
    try:
        import importlib_metadata
        __version__ = importlib_metadata.version(__package__ or __name__)
    except:
        __version__ = "1.0 X"


#=====================================================================================
#=====================================================================================
#  r e s o u r c e _ l o c k
#=====================================================================================
#=====================================================================================

class resource_lock():
    """
## Class resource_lock (lockname) - Inter-process lock mechanism using posix_ipc

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
`lockname` (str)
- All processes sharing a given resource must use the same lockname.
    """

    def __init__ (self, lockname):
        if not lockname.startswith('/'):
            lockname = '/'+lockname         # lockname is required to start with '/'
        self.lockname = lockname
        self.I_have_the_lock = False
        self.lock = posix_ipc.Semaphore(self.lockname, flags=posix_ipc.O_CREAT, mode=0o0600, initial_value=1)


#=====================================================================================
#=====================================================================================
#  g e t _ l o c k
#=====================================================================================
#=====================================================================================

    def get_lock(self, timeout=1, same_process_ok=False, where=''):
        """
## get_lock (timeout=1, same_process_ok=False) - Request the resource lock

***resource_lock() class member function***

Attempt to acquire/get the lock while waiting up to `timeout` time.  

By default, get_lock() waits for the lock if it is currently set, whether the lock was set by this
or another script/job/process.

By setting `same_process_ok=True`, then if the lock was previously acquired by this same script/process
then get_lock() immediately returns True.  This allows the script code to not have to track state to 
decide if the lock has previously been acquired before calling get_lock() again, leading to cleaner code.

### Parameters
`timeout` (int or float, default 1 second)
- The max time, in seconds, to wait to acquire the lock
- None is no timeout - wait forever (Hang forever.  Unwise.)

`same_process_ok` (bool, default False)
- If True, then if the current process currently has the lock then get_lock() immediately returns True.
- If False, then if the lock is currently set by the same process or another process then get_lock() blocks
with timeout.

`where` (str, default ' ')
- Comment string in the debug log

### Returns
- True:  Lock successfully acquired, timeout time not exceeded
- False: Lock request failed, timed out
        """
        if same_process_ok  and  self.I_have_the_lock == True:
            return True

        try:
            self.lock.acquire(timeout)
            self.I_have_the_lock = True
            logging.debug (f"<{self.lockname[1:]}> lock request successful <{where}> (Semaphore = {self.lock.value})")
            return True
        except posix_ipc.BusyError:
            logging.debug (f"<{self.lockname[1:]}> lock request timed out <{where}>  (Semaphore = {self.lock.value})")
            return False


#=====================================================================================
#=====================================================================================
#  u n g e t _ l o c k
#=====================================================================================
#=====================================================================================

    def unget_lock(self, force=False, where=''):
        """
## unget_lock (force=False) - Release the resource lock

***resource_lock() class member function***

If the lock was acquired by the current process then release the lock.
- If the lock is not currently set then the `unget_lock()` call is discarded, leaving the lock
in the same unset state.
- If the lock is currently set but _not_ acquired by this process then don't release the lock,
unless `force=True`.

### Parameter
`force` (bool, default False)
- Release the lock regardless of whether or not this process acquired it.
- Useful for forced cleanup, for example, by the CLI interface.
- Dangerous if another process had acquired the lock.  Be careful.

`where` (str, default ' ')
- Comment string in the debug log

### Returns
- True:  Lock successfully released
- False: Lock not currently set (redundant unget_lock() call), or lock was not acquired by the current process
        """
        if self.lock.value == 0:
            if self.I_have_the_lock:
                self.lock.release()
                self.I_have_the_lock = False
                logging.debug (f"<{self.lockname[1:]}> lock released <{where}> (Semaphore = {self.lock.value})")
                return True
            else:
                if force:
                    self.lock.release()
                    logging.debug (f"<{self.lockname[1:]}> lock force released <{where}> (Semaphore = {self.lock.value})")
                    return True
                else:
                    logging.debug (f"<{self.lockname[1:]}> lock unget request ignored - lock not owned by current process <{where}> (Semaphore = {self.lock.value})")
                    return False
        else:
            logging.debug (f"<{self.lockname[1:]}> Extraneous lock unget request ignored <{where}> (Semaphore = {self.lock.value})")
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

### Returns
- True if currently locked, else False
        """
        locked = True if self.lock.value == 0 else False
        logging.debug (f"<{self.lockname[1:]}> is currently locked? {locked}")
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
        logging.debug (f"<{self.lockname[1:]}> semaphore = {_value}")
        return _value


#=====================================================================================
#=====================================================================================
#  c l i
#=====================================================================================
#=====================================================================================

def int_handler(sig, frame):
    logging.warning(f"Signal {sig} received")
    sys.exit(0)

signal.signal(signal.SIGINT,  int_handler)      # Ctrl-C
signal.signal(signal.SIGTERM, int_handler)      # kill


def cli():
    docplus = """
    Commands:
        get:    Get/set the lock named LockName.  '-a' specifies a automatic timed unget (only applied if the get was successful).
        unget:  Force-release LockName.
        state:  Print the current state of LockName.
        trace:  Continuously print the state of LockName.  '-u' specifies update interval.  Ctrl-C to exit.
    """
    import argparse
    from time import sleep

    GET_TIMEOUT = 0.5
    TRACE_INTERVAL = 0.5
    

    parser = argparse.ArgumentParser(description=__doc__ + __version__+docplus, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('LockName',
                        help="Name of the system-wide lock to access")
    parser.add_argument('Cmd', choices=['get', 'unget', 'state', 'trace'],
                        help="Command choices")
    parser.add_argument('-t', '--get-timeout', type=float, default=GET_TIMEOUT,
                        help=f"Timeout value for a get call (default {GET_TIMEOUT} sec, -1 for no timeout)")
    parser.add_argument('-a', '--auto-unget', type=float,
                        help="After a successful get, unget the lock in (float) sec")
    parser.add_argument('-u', '--update', type=float, default=TRACE_INTERVAL,
                        help=f"Trace update interval (default {TRACE_INTERVAL} sec)")
    args = parser.parse_args()

    lock = resource_lock(args.LockName)

    logging.getLogger().setLevel(logging.DEBUG)

    if args.Cmd == "get":
        _timeout = args.get_timeout
        if _timeout == -1:
            _timeout = None
        get_status = lock.get_lock(timeout=_timeout)
        if get_status and args.auto_unget:
                print (f"Release lock after <{args.auto_unget}> sec delay")
                sleep(args.auto_unget)
                lock.unget_lock()

    elif args.Cmd == "unget":
        lock.unget_lock(force=True)

    elif args.Cmd == "state":
        lock.is_locked()

    elif args.Cmd == "trace":
        while True:
            lock.is_locked()
            sleep (args.update)

    else:
        print ("How did we get here?")
