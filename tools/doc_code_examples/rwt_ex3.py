#!/usr/bin/env python3
# ***** rwt_ex3.py *****

import time
import os
import signal

from cjnfuncs.core      import set_toolname, logging
from cjnfuncs.rwt       import run_with_timeout

set_toolname('rwt_ex3')


def wont_terminate():
    # This function is hard to kill.  SIGTERM doesn't break the loop.
    while 1:
        try:
            time.sleep (0.2)
        except:
            pass


try:
    run_with_timeout(wont_terminate, rwt_timeout=0.5, rwt_kill=False, rwt_ntries=3)
except Exception as e:
    logging.error (f"EXCEPTION received:  {type(e).__name__}: {e}")

    # Kill the orphaned processes
    orphaned_pids = str(e).split('orphaned pids: ')[1].split(' ')
    for pid in orphaned_pids:
        os.kill(int(pid), signal.SIGKILL)
