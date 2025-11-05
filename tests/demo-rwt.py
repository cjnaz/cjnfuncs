#!/usr/bin/env python3
"""Demo/test for cjnfuncs.rwt run_with_timeout()

Produce / compare to golden results:
    ./demo-rwt.py -t 0 | diff demo-rwt-golden.txt -
        Differences will be pids and function addresses

    ./demo-rwt.py --cleanup
"""

#==========================================================
#
#  Chris Nelson, 2024-2025
#
#==========================================================

__version__ =   '3.1'
TOOLNAME =      'demo_rwt'          # rename

import argparse
import tempfile
import shutil
import sys
import os
import re
import subprocess
import time
import signal
from pathlib import Path

from cjnfuncs.core      import set_toolname, setuplogging, logging, set_logging_level
from cjnfuncs.rwt       import run_with_timeout

set_toolname(TOOLNAME)
setuplogging(ConsoleLogFormat="{module:>22}.{funcName:20} {levelname:>8}:  {message}")      # No timestamps for cleaner compares
test_dir = Path(tempfile.gettempdir()) / TOOLNAME
test_dir.mkdir(exist_ok=True)

parser = argparse.ArgumentParser(description=__doc__ + __version__, formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-t', '--test', default='0',
                    help="Test number to run (default 0).  0 runs all tests")
parser.add_argument('--cleanup', action='store_true',
                    help="Remove test dirs/files.")

args = parser.parse_args()




if args.cleanup:
    try:
        print (f"Removing   {test_dir}")
        shutil.rmtree(test_dir)
    except:
        pass
    sys.exit(0)


# --------------------------------------------------------------------

def dotest (desc, expect, func, *args, **kwargs):
    logging.warning (f"\n\n==============================================================================================\n" +
                     f"Test {tnum} - {desc}\n" +
                     f"  EXPECT: {expect}")
    try:
        result = run_with_timeout(func, *args, **kwargs)
        logging.warning (f"  RETURNED:\n{result}")
        return result
    except Exception as e:
        logging.error (f"\n  RAISED:     {type(e).__name__}: {e}")
        # logging.exception (f"\n  RAISED:     {type(e).__name__}: {e}")
        return e

tnum_parse = re.compile(r"([\d]+)([\w]*)")
def check_tnum(tnum_in, include0='0'):
    global tnum
    tnum = tnum_in
    if args.test == include0  or  args.test == tnum_in:  return True
    try:
        if int(args.test) == int(tnum_parse.match(tnum_in).group(1)):  return True
    except:  pass
    return False


# --------------------------------------------------------------------
# Setups, functions, and vars

abc= 42

def test_shell_1(t, tnum, file):    # Used in tests 6a, 6b (placeholder in test 9 series)
    time.sleep (t)
    logging.info (f"Hello there {abc}.  Log from unkilled Test {tnum}, pid: {os.getpid()}")
    Path(file).touch()


def wont_terminate():               # Used in tests 14 series
    while 1:
        try:
            time.sleep (0.2)
        except:
            pass


def log_each_level():               # Used in test 17 series
    logging.debug ('debug')
    logging.info ('info')
    logging.warning ('warning')


def kill_pids (runner_pids):        # String of pids, eg, '2267117 2267141 2267160 2267186'
    for runner_pid in runner_pids.split(' '):
        try:
            if sys.platform.startswith("win"):
                subprocess.run(["taskkill", "/PID", runner_pid, "/F"])
            else:
                os.kill(int(runner_pid), signal.SIGKILL)
            logging.warning(f"Killed pid <{runner_pid}>")
        
        except Exception as e:
            logging.warning(f"Failed to kill pid <{runner_pid}>")


def hack():                         # Development / debug use
    global abc1
    abc1 += 1
    print ("in hack", abc1)

#===============================================================================================

if __name__ == "__main__":
    set_logging_level(logging.DEBUG, 'cjnfuncs.rwt')

    #-------------------------------------------------------------------------
    # Test 1 series - Check function run pass/fail/exception cases
    if check_tnum('1a'):
        dotest ("Built-in print, all rwt defaults", "Success, return None",
                print, "Hello", "there", "again", sep=" blah ", end=" The end.\n"
                )

    if check_tnum('1b'):
        dotest ("time.sleep less than rwt_timeout", "Success, return None",
                time.sleep, 0.5,
                rwt_timeout = 2)

    if check_tnum('1c'):
        dotest ("time.sleep greater than rwt_timeout", "Raise TimeoutError (killed)",
                time.sleep, 0.5,
                rwt_timeout = 0.4)

    if check_tnum('1d'):
        dotest ("time.sleep greater than rwt_timeout, rwt_ntries=2", "Raise TimeoutError (killed)",
                time.sleep, 0.5,
                rwt_timeout = 0.4, rwt_ntries=2)


    #-------------------------------------------------------------------------
    # Test 6 series - Exercise rwt_kill=False
    if check_tnum('6a'):
        dotest("Function took too long, killed", "Raise TimeoutError, File 'FileNotTouched' not created", 
               test_shell_1, 2, tnum, f'{test_dir}/FileNotTouched', rwt_timeout=0.5)

    if check_tnum('6b'):
        set_logging_level(logging.INFO)
        dotest("INFO root log level, Function took too long, not killed", "Raise TimeoutError, File 'FileTouched_1' created, message logged during Test 6c",
               test_shell_1, 1, tnum, Path(f'{test_dir}/FileTouched_1'), rwt_timeout=0.5, rwt_kill=False)

    if check_tnum('6c'):
        set_logging_level(logging.WARNING, 'cjnfuncs.rwt')
        set_logging_level(logging.WARNING)
        dotest("WARNING root log level, Sleep took too long, No rwt logging", "Raise TimeoutError, Test 6b INFO log",
               time.sleep, 10, rwt_timeout=1.5)
        set_logging_level(logging.DEBUG, 'cjnfuncs.rwt')

    if check_tnum('6d'):
        dotest("Sleep took too long", "Raise TimeoutError",
               time.sleep, 10, rwt_timeout=0.5)


    #-------------------------------------------------------------------------
    # Test 9 series - Check rwt kwargs check logic
    if check_tnum('9a'):
        dotest("Invalid rwt_timeout", "Raise ValueError",
               test_shell_1, 2, tnum, f'{test_dir}/FileTouched_9a', rwt_timeout='abc')

    if check_tnum('9b'):
        dotest("Invalid rwt_ntries", "Raise ValueError",
               test_shell_1, 2, tnum, f'{test_dir}/FileTouched_9b', rwt_ntries='abc')

    if check_tnum('9c'):
        dotest("Invalid rwt_kill", "Raise ValueError",
               test_shell_1, 2, tnum, f'{test_dir}/FileTouched_9c', rwt_kill='abc')


    #-------------------------------------------------------------------------
    if check_tnum('11'):
        nosuchfile = Path(f'{test_dir}//nosuchfile')
        dotest("Delete non-existing file", "Raise FileNotFoundError from function runtime",
               nosuchfile.unlink)

    if check_tnum('12'):
        t12a = test_dir / 't12a'
        t12a.touch()
        t12b = test_dir / 't12b'
        dotest("shutil.copy, rwt_debug True", "Pass",
               shutil.copy, t12a, t12b, rwt_timeout=1)

    if check_tnum('13'):
        set_logging_level(logging.WARNING, 'cjnfuncs.rwt')
        t13a = Path(f'{test_dir}/t13a')
        t13a.touch()
        t13b = Path(f'{test_dir}/t13b')
        dotest("shutil.copy, rwt_debug False", "Pass",
               shutil.copy, t13a, t13b, rwt_timeout=1)
        set_logging_level(logging.DEBUG, 'cjnfuncs.rwt')


    #-------------------------------------------------------------------------
    # Test 14 series - Process wont exit, kill scenarios
    if check_tnum('14a'):
        dotest("Function wont_terminate, requires SIGKILL on Linux, rwt_ntries=1", "Raises TimeoutError",
               wont_terminate, rwt_timeout=0.5, rwt_ntries=1)

    if check_tnum('14b'):
        xx = dotest("Function wont_terminate, not killed, rwt_ntries=1", "Raise TimeoutError, pid listed",
               wont_terminate, rwt_timeout=0.5, rwt_ntries=1, rwt_kill=False)
        kill_pids(str(xx).split('orphaned pids: ')[1])
    
    if check_tnum('14c'):
        xx = dotest("Function wont_terminate, not killed, rwt_ntries=4", "Raise TimeoutError, pids listed",
               wont_terminate, rwt_timeout=0.5, rwt_ntries=4, rwt_kill=False)
        kill_pids(str(xx).split('orphaned pids: ')[1])


    #-------------------------------------------------------------------------
    # Test 16 series - Check logging level handling with exception raised by function
    if check_tnum('16a'):
        set_logging_level(logging.WARNING)
        nosuchfile = Path(f'{test_dir}//nosuchfile')
        dotest("WARNING root log level, rwt_ntries=1", "Exception FileNotFoundError, Post test logging level:  30",
               nosuchfile.unlink, rwt_ntries=1, rwt_timeout=2)
        logging.warning (f"Post test logging level:  {logging.getLogger().level}")

    if check_tnum('16b'):
        set_logging_level(logging.INFO)
        nosuchfile = Path(f'{test_dir}//nosuchfile')
        dotest("INFO root log level, rwt_ntries=1", "Raise FileNotFoundError, Post test logging level:  20",
               nosuchfile.unlink, rwt_ntries=1, rwt_timeout=2)
        logging.warning (f"Post test logging level:  {logging.getLogger().level}")

    if check_tnum('16c'):
        set_logging_level(logging.DEBUG)
        nosuchfile = Path(f'{test_dir}//nosuchfile')
        dotest("DEBUG root log level, rwt_ntries=1", "Raise FileNotFoundError, Post test logging level:  10",
               nosuchfile.unlink, rwt_ntries=1, rwt_timeout=2)
        logging.warning (f"Post test logging level:  {logging.getLogger().level}")

    if check_tnum('16d'):
        set_logging_level(logging.WARNING, 'cjnfuncs.rwt')
        set_logging_level(logging.DEBUG)
        nosuchfile = Path(f'{test_dir}//nosuchfile')
        dotest("DEBUG root log level, rwt_ntries=1, No rwt logging", "Raise FileNotFoundError, Post test logging level:  10",
               nosuchfile.unlink, rwt_ntries=1, rwt_timeout=2)
        logging.warning (f"Post test logging level:  {logging.getLogger().level}")
        set_logging_level(logging.DEBUG, 'cjnfuncs.rwt')

    if check_tnum('16e'):
        set_logging_level(logging.WARNING)
        nosuchfile = Path(f'{test_dir}//nosuchfile')
        dotest("WARNING root log level, rwt_ntries=2", "Raise FileNotFoundError, Post test logging level:  30",
               nosuchfile.unlink, rwt_ntries=2, rwt_timeout=2)
        logging.warning (f"Post test logging level:  {logging.getLogger().level}")

    if check_tnum('16f'):
        set_logging_level(logging.INFO)
        nosuchfile = Path(f'{test_dir}//nosuchfile')
        dotest("INFO root log level, rwt_ntries=2", "Raise FileNotFoundError, Post test logging level:  20",
               nosuchfile.unlink, rwt_ntries=2, rwt_timeout=2)
        logging.warning (f"Post test logging level:  {logging.getLogger().level}")

    if check_tnum('16g'):
        set_logging_level(logging.DEBUG)
        nosuchfile = Path(f'{test_dir}//nosuchfile')
        dotest("DEBUG root log level, rwt_ntries=2", "Raise FileNotFoundError, Post test logging level:  10",
               nosuchfile.unlink, rwt_ntries=2, rwt_timeout=2)
        logging.warning (f"Post test logging level:  {logging.getLogger().level}")

    if check_tnum('16h'):
        set_logging_level(logging.WARNING, 'cjnfuncs.rwt')
        set_logging_level(logging.DEBUG)
        nosuchfile = Path(f'{test_dir}//nosuchfile')
        dotest("DEBUG root log level, rwt_ntries=2, No rwt logging", "Raise FileNotFoundError, Post test logging level:  10",
               nosuchfile.unlink, rwt_ntries=2, rwt_timeout=2)
        logging.warning (f"Post test logging level:  {logging.getLogger().level}")
        set_logging_level(logging.DEBUG, 'cjnfuncs.rwt')


    #-------------------------------------------------------------------------
    # Test 17 series - Check logging level handling with normal exit by function
    if check_tnum('17a'):
        set_logging_level(logging.WARNING)
        dotest("WARNING root log level, rwt_ntries=1", "log_each_level logs WARNING, Post test logging level:  30",
               log_each_level, rwt_ntries=1)
        logging.warning (f"Post test logging level:  {logging.getLogger().level}")

    if check_tnum('17b'):
        set_logging_level(logging.INFO)
        dotest("INFO root log level, rwt_ntries=1", "log_each_level logs WARNING, INFO, Post test logging level:  20",
               log_each_level, rwt_ntries=1)
        logging.warning (f"Post test logging level:  {logging.getLogger().level}")

    if check_tnum('17c'):
        set_logging_level(logging.DEBUG)
        dotest("DEBUG root log level, rwt_ntries=1", "log_each_level logs WARNING, INFO, DEBUG, Post test logging level:  10",
               log_each_level, rwt_ntries=1)
        logging.warning (f"Post test logging level:  {logging.getLogger().level}")

    if check_tnum('17d'):
        set_logging_level(logging.WARNING, 'cjnfuncs.rwt')
        set_logging_level(logging.DEBUG)
        dotest("DEBUG root log level, rwt_ntries=1, No rwt logging", "log_each_level logs WARNING, INFO, DEBUG, Post test logging level:  10",
               log_each_level, rwt_ntries=1)
        logging.warning (f"Post test logging level:  {logging.getLogger().level}")
        set_logging_level(logging.DEBUG, 'cjnfuncs.rwt')

    if check_tnum('17e'):
        set_logging_level(logging.WARNING)
        dotest("WARNING root log level, rwt_ntries=2", "log_each_level logs WARNING, Post test logging level:  30",
               log_each_level, rwt_ntries=2)
        logging.warning (f"Post test logging level:  {logging.getLogger().level}")

    if check_tnum('17f'):
        set_logging_level(logging.INFO)
        dotest("INFO root log level, rwt_ntries=2", "log_each_level logs WARNING, INFO, Post test logging level:  20",
               log_each_level, rwt_ntries=2)
        logging.warning (f"Post test logging level:  {logging.getLogger().level}")

    if check_tnum('17g'):
        set_logging_level(logging.DEBUG)
        dotest("DEBUG root log level, rwt_ntries=2", "log_each_level logs WARNING, INFO, DEBUG, Post test logging level:  10",
               log_each_level, rwt_ntries=2)
        logging.warning (f"Post test logging level:  {logging.getLogger().level}")

    if check_tnum('17h'):
        set_logging_level(logging.WARNING, 'cjnfuncs.rwt')
        set_logging_level(logging.DEBUG)
        dotest("DEBUG root log level, rwt_ntries=2, No rwt logging", "log_each_level logs WARNING, INFO, DEBUG, Post test logging level:  10",
               log_each_level, rwt_ntries=2)
        logging.warning (f"Post test logging level:  {logging.getLogger().level}")
        set_logging_level(logging.DEBUG, 'cjnfuncs.rwt')



    # Debug / development


    if args.test == '50':
        
        abc1 = 0
        for _ in range(2):  # On linux and windows this prints 0 1 1 2
            print ("in main", abc1)
            hack()

        abc1 = 10
        print ()
        try:
            for _ in range(2):  # On linux this prints 10 11 10 11.  On Windows this prints 10 6 10 6 
                    # On Windows, due to multiprocess spawn, nothing within the application code is accessible to the spawned process.
                    # On Windows, with the above 'abc1 = 5' commented out this code errors in hack() on the 'abc1 += 1' with NameError: name 'abc1' is not defined
                print ("in main", abc1)
                run_with_timeout(hack)
        except Exception as e:
            logging.exception (f"{type(e).__name__}: {e}")
        exit()      


    if args.test == '51':
        dotest ("Built-in print", "Pass, return None",
                print, "Hello", "there", "again", rwt_timeout=1, sep=" blah ", end=" The end.\n")

    if args.test == '52':
        dotest ("Built-in print", "Pass, return None",
                print, "Hello", "there", "again", rwt_timeout=1, sep=" blah ", end=" The end.\n")

    if args.test == '53':
                run_with_timeout(print, "Hello", "there", "again", sep=" blah ", end=" The end.\n", flush=True,
                                 rwt_timeout=3)

    if args.test == '54':
                run_with_timeout(time.sleep, 0.01,
                                 rwt_timeout=3)

    time.sleep(0.2)     # TODO debug

