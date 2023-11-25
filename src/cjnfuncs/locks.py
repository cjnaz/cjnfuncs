#!/usr/bin/env python3
"""cjnfuncs - Manage process blocking via file locks
"""

#==========================================================
#
#  Chris Nelson, 2018-2023
#
#==========================================================

import time
import tempfile

from .core      import logging
from .mungePath import mungePath
from .timevalue import timevalue
import cjnfuncs.core as core

# Configs / Constants

# Project globals


#=====================================================================================
#=====================================================================================
#  r e q u e s t l o c k
#=====================================================================================
#=====================================================================================
def requestlock(caller, lockfile=None, timeout=5):
    """
## requestlock (caller, lockfile, timeout=5) - Lock file request

For tool scripts that may take a long time to run and are run by CRON, the possibility exists that 
a job is still running when CRON wants to run it again, which may create a real mess.
This lock file mechanism is used in https://github.com/cjnaz/rclonesync-V2, as an example.

`requestlock()` places a file to indicate that the current process is busy.
Other processes then attempt to `requestlock()` the same `lockfile` before doing an operation
that would conflict with the process that set the lock.

The `lockfile` is written with `caller` information that indicates which tool script set the lock, and when.
Multiple lock files may be used simultaneously by specifying unique `lockfile` names.


### Parameters
`caller`
- Info written to the lock file and displayed in any error messages

`lockfile` (default /tmp/\<toolname>_LOCK)
- Lock file name, relative to the system tempfile.gettempdir(), or absolute path

`timeout` (default 5s)
- Time in seconds to wait for the lockfile to be removed by another process before returning with a `-1` result.
  `timeout` may be an int, float or timevalue string (eg, '5s').


### Returns
- `0` on successfully creating the `lockfile`
- `-1` if failed to create the `lockfile` (either file already exists or no write access).
  A WARNING level message is also logged.
    """

    if lockfile == None:
        lockfile = core.tool.toolname + "_LOCK"
    lock_file = mungePath(lockfile, tempfile.gettempdir())

    fail_time = time.time() + timevalue(timeout).seconds
    while True:
        if not lock_file.exists:
            try:
                mungePath(lock_file.parent, mkdir=True)     # Ensure directory path exists
                with lock_file.full_path.open('w') as ofile:
                    ofile.write(f"Locked by <{caller}> at {time.asctime(time.localtime())}.")
                    logging.debug (f"<{lock_file.full_path}> locked by <{caller}> at {time.asctime(time.localtime())}.")
                return 0
            except Exception as e:
                logging.warning(f"Unable to create lock file <{lock_file.full_path}>\n  {e}")
                return -1
        else:
            if time.time() > fail_time:
                break
        time.sleep(0.1)

    try:
        with lock_file.full_path.open() as ifile:
            lockedBy = ifile.read()
        logging.warning (f"Timed out waiting for lock file <{lock_file.full_path}> to be cleared.  {lockedBy}")
    except Exception as e:
        logging.warning (f"Timed out and unable to read existing lock file <{lock_file.full_path}>\n  {e}.")
    return -1


#=====================================================================================
#=====================================================================================
#  r e l e a s e l o c k
#=====================================================================================
#=====================================================================================
def releaselock(lockfile=None):
    """
## releaselock (lockfile) - Release a lock file

Any code can release a lock, even if that code didn't request the lock.
Generally, only the requester should issue the releaselock.
A common use is with a tool script that runs periodically by CRON, but may take a long time to complete.  Using 
file locks ensures that the tool script does not run if the prior run has not completed.


### Parameters
`lockfile` (default /tmp/\<toolname>_LOCK)
- Lock file name, relative to the system tempfile.gettempdir(), or absolute path


### Returns
- `0` on successfully `lockfile` release (lock file deleted)
- `-1` if failed to delete the `lockfile`, or the `lockfile` does not exist.  A WARNING level message is also logged.
    """

    if lockfile == None:
        lockfile = core.tool.toolname + "_LOCK"
    lock_file = mungePath(lockfile, tempfile.gettempdir())
    if lock_file.exists:
        try:
            lock_file.full_path.unlink()
        except Exception as e:
            logging.warning (f"Unable to remove lock file <{lock_file.full_path}>\n  {e}.")
            return -1
        logging.debug(f"Lock file removed: <{lock_file.full_path}>")
        return 0
    else:
        logging.warning(f"Attempted to remove lock file <{lock_file.full_path}> but the file does not exist.")
        return -1

