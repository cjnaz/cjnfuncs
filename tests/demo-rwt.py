#!/usr/bin/env python3
"""Demo/test for cjnfuncs.runwithtimeout

Produce / compare to golden results:
    ./demo-run_with_timeout.py --setup-user

    ./demo-run_with_timeout.py | diff demo-run_with_timeout-golden.txt -
        Or use bcompare
        Differences will be timestamps and pids

    ./demo-run_with_timeout.py --cleanup
"""

#==========================================================
#
#  Chris Nelson, 2024-2025
#
#==========================================================

__version__ = "2.0"
TOOLNAME    = "cjnfuncs_rwt"      # rename
# CONFIG_FILE = "demo_config.cfg"     # rename

import argparse
import os.path
import shutil
import sys
import subprocess
import time
import signal
from pathlib import Path

from cjnfuncs.core              import set_toolname, setuplogging, logging, set_logging_level #, restore_logging_level
# from cjnfuncs.deployfiles       import deploy_files
# from cjnfuncs.configman         import config_item
# from cjnfuncs.timevalue         import timevalue, retime
# from cjnfuncs.mungePath         import mungePath
from cjnfuncs.rwt    import run_with_timeout
# import cjnfuncs.core as core

parser = argparse.ArgumentParser(description=__doc__ + __version__, formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-t', '--test', default=0,
                    help="Test number to run (default 0).  0 runs most all tests (not tests with untrapped errors)")

# Include/remove as needed
parser.add_argument('--setup-user', action='store_true',
                    help=f"Install starter files in user space.")
parser.add_argument('--setup-site', action='store_true',
                    help=f"Install starter files in site space.")
parser.add_argument('--cleanup', action='store_true',
                    help="Remove test dirs/files.")

args = parser.parse_args()

set_toolname(TOOLNAME)
# setuplogging()
setuplogging(ConsoleLogFormat="{asctime} {module:>22}.{funcName:20} {levelname:>8}:  {message}")


# --------------------------------------------------------------------
test_dir = f'/tmp/{TOOLNAME}'
if args.setup_user:
    Path(test_dir).mkdir()
    # deploy_files([
    #     { "source": CONFIG_FILE,            "target_dir": "USER_CONFIG_DIR",            "file_stat": 0o644, "dir_stat": 0o770},
    #     { "source": CONFIG_FILE,            "target_dir": "USER_CONFIG_DIR/subdir",     "file_stat": 0o641, "dir_stat": 0o777},
    #     { "source": "testfile.txt",         "target_dir": "$HOME/.config/junk2",        "file_stat": 0o600, "dir_stat": 0o707},
    #     { "source": "testfile.txt",         "target_dir": "USER_CONFIG_DIR/dirxxx"},  # defaults file_stat 0o664, dir_stat 0o775
    #     { "source": "test_dir",             "target_dir": test_dir,       "file_stat": 0o633, "dir_stat": 0o720},
    #     { "source": "test_dir/subdir/x4",   "target_dir": "USER_CONFIG_DIR/mydirs",     "file_stat": 0o612, "dir_stat": 0o711},
    #     # Uncomment these to force error traps
    #     # { "source": "doesnotexist",       "target_dir": "USER_CONFIG_DIR",            "file_stat": 0o633, "dir_stat": 0o770},
    #     { "source": "testfile.txt",       "target_dir": "/no_perm/junkdir",           "file_stat": 0o633, "dir_stat": 0o770},
    #     ] , overwrite=True)
    sys.exit()

# if args.setup_site:
    # deploy_files([
    #     { "source": CONFIG_FILE,            "target_dir": "SITE_CONFIG_DIR",            "file_stat": 0o644, "dir_stat": 0o777},
    #     { "source": "testfile.txt",         "target_dir": "$HOME/.config/junk2",        "file_stat": 0o600, "dir_stat": 0o707},
    #     { "source": "testfile.txt",         "target_dir": "SITE_CONFIG_DIR/dirxxx"},
    #     { "source": "test_dir",             "target_dir": "SITE_DATA_DIR/mydirs",       "file_stat": 0o633, "dir_stat": 0o770},
    #     { "source": "test_dir/subdir/x4",   "target_dir": "SITE_CONFIG_DIR/mydirs",     "file_stat": 0o633, "dir_stat": 0o770},
    #     # Uncomment this to force error traps
    #     # { "source": "doesnotexist", "target_dir": "SITE_CONFIG_DIR",                "file_stat": 0o633, "dir_stat": 0o770},
    #     ] , overwrite=True)
    # sys.exit()

if args.cleanup:
    # if os.path.exists(core.tool.user_config_dir):
    #     print (f"Removing 1  {core.tool.user_config_dir}")
    #     shutil.rmtree(core.tool.user_config_dir)
    # if os.path.exists(core.tool.user_data_dir):
    #     print (f"Removing 2  {core.tool.user_data_dir}")
    #     shutil.rmtree(core.tool.user_data_dir)

    # try:
    #     if os.path.exists(core.tool.site_config_dir):
    #         print (f"Removing 3  {core.tool.site_config_dir}")
    #         shutil.rmtree(core.tool.site_config_dir)
    #     if os.path.exists(core.tool.site_data_dir):
    #         print (f"Removing 4  {core.tool.site_data_dir}")
    #         shutil.rmtree(core.tool.site_data_dir)
    # except:
    #     print ("NOTE:  Run as root/sudo to cleanup site dirs")

    # junk2 = mungePath("$HOME/.config/junk2").full_path
    if os.path.exists(test_dir):
        print (f"Removing 5  {test_dir}")
        shutil.rmtree(test_dir)
    sys.exit()
# --------------------------------------------------------------------

def dotest (testnum, message, func, *args, **kwargs):
    # logging.warning (f"\n==============================================================================================\nTest {testnum} - {message}")
    logging.warning (f"\n\n==============================================================================================\nTest {testnum} - {message}")
    try:
        result = run_with_timeout(func, *args, **kwargs)
        # logging.warning (f"RETURNED:\n{result}\n\n")
        logging.warning (f"RETURNED:\n{result}")
        return result
        # logging.warning (f"RETURNED:\n{run_with_timeout(func, *args, **kwargs)}\n\n")
    except Exception as e:
        # logging.exception (f"EXCEPTION:\n{type(e).__name__}: {e}")          # With call stack
        # logging.error (f"EXCEPTION:\n{type(e).__name__}: {e}\n\n")          # Just the exception 
        logging.error (f"EXCEPTION:\n{type(e).__name__}: {e}")          # Just the exception 
        return e


# --------------------------------------------------------------------
# demo-specific functions and vars

debug_flag = True
set_logging_level(logging.WARNING, save=False)

abc= 42

def test_shell_1(t, tnum, file):
    time.sleep (t)
    logging.warning (f"Hello there {abc} tnum: {tnum}, pid: {os.getpid()}")
    Path(file).touch()

def wont_terminate():
    while 1:
        try:
            time.sleep (0.2)
        except:
            pass

def log_each_level():
    logging.debug ('debug')
    logging.info ('info')
    logging.warning ('warning')

#===============================================================================================


tnum = '1'
if args.test == '0'  or  args.test == tnum:
    dotest (tnum, "test desc - expected result",
            print, "Hello", "there", "again", rwt_timeout=3, sep=" blah ", end=" The end.\n", rwt_debug=debug_flag)

tnum = '2'
if args.test == '0'  or  args.test == tnum:
    dotest(tnum, "Subprocess ping known - Return subprocess pass result",
        subprocess.run, ['ping', 'yahoo.com', '-c', '1'], rwt_timeout=3, timeout=3, capture_output=True, text=True, rwt_debug=debug_flag)

tnum = '3'
if args.test == '0'  or  args.test == tnum:
    dotest(tnum, "Subprocess ping unknown - Return subprocess fail result",
        subprocess.run, ['ping', 'dummyunknown.com', '-c', '1'], rwt_timeout=3, timeout=1, capture_output=True, text=True, rwt_debug=debug_flag)

tnum = '4'
if args.test == '0'  or  args.test == tnum:
    dotest(tnum, "Subprocess ping known/unavailable - subprocess timeout < rwt_timeout - Exception subprocess.TimeoutExpired",
        subprocess.run, ['ping', 'testhostx', '-c', '1'], timeout=0.5, capture_output=True, text=True, rwt_timeout=3, rwt_debug=debug_flag)

tnum = '4a'
if args.test == '0'  or  args.test == tnum:
    dotest(tnum, "Subprocess ping known/unavailable - subprocess timeout < rwt_timeout, rwt_ntries=2 - Exception subprocess.TimeoutExpired",
        subprocess.run, ['ping', 'testhostx', '-c', '1'], timeout=0.5, capture_output=True, text=True, rwt_timeout=3, rwt_debug=debug_flag, rwt_ntries=2)

tnum = '5'
if args.test == '0'  or  args.test == tnum:
    dotest(tnum, "Subprocess ping known/unavailable - rwt_timeout < subprocess timeout - Exception TimeoutError",
       subprocess.run, ['ping', 'testhostx', '-c', '1'], timeout=3, capture_output=True, text=True, rwt_timeout=0.5, rwt_debug=debug_flag)

tnum = '5a'
if args.test == '0'  or  args.test == tnum:
    dotest(tnum, "Subprocess ping known/unavailable - rwt_timeout < subprocess timeout, rwt_ntries=2 - Exception TimeoutError",
       subprocess.run, ['ping', 'testhostx', '-c', '1'], timeout=3, capture_output=True, text=True, rwt_timeout=0.5, rwt_debug=debug_flag, rwt_ntries=2)

tnum = '6'
if args.test == '0'  or  args.test == tnum:
    dotest(tnum, "Function took too long, killed - Exception TimeoutError, File 'FileNotTouched' not created", 
       test_shell_1, 2, tnum, f'{test_dir}/FileNotTouched', rwt_timeout=0.5, rwt_debug=debug_flag)

tnum = '7'
if args.test == '0'  or  args.test == tnum:
    dotest(tnum, "Function took too long, not killed - Exception TimeoutError, File 'FileTouched_1' created",
       test_shell_1, 1, tnum, Path(f'{test_dir}/FileTouched_1'), rwt_timeout=0.5, rwt_kill=False, rwt_debug=debug_flag)

tnum = '8'
if args.test == '0'  or  args.test == tnum:
    dotest(tnum, "Sleep took too long, rwt_debug=False - Exception TimeoutError",
       time.sleep, 10, rwt_timeout=1.5)

tnum = '8a'
if args.test == '0'  or  args.test == tnum:
    dotest(tnum, "Sleep took too long - Exception TimeoutError",
       time.sleep, 10, rwt_timeout=0.5, rwt_debug=debug_flag)

tnum = '9'
if args.test == '0'  or  args.test == tnum:
    dotest(tnum, "Invalid rwt_timeout - Exception ValueError, File 'FileTouched_9' not created",
       test_shell_1, 2, tnum, f'{test_dir}/FileTouched_9', rwt_timeout='abc', rwt_kill=False, rwt_debug=debug_flag)

tnum = '9a'
if args.test == '0'  or  args.test == tnum:
    dotest(tnum, "Invalid rwt_ntries - Exception ValueError, File 'FileTouched_9a' not created",
       test_shell_1, 2, tnum, f'{test_dir}/FileTouched_9a', rwt_ntries='abc', rwt_debug=debug_flag)

tnum = '10'
if args.test == '0'  or  args.test == tnum:
    dotest(tnum, "Invalid rwt_kill - Exception ValueError, File 'FileTouched_10' not created",
       test_shell_1, 2, tnum, f'{test_dir}/FileTouched_10', rwt_kill='abc', rwt_debug=debug_flag)

tnum = '11'
if args.test == '0'  or  args.test == tnum:
    nosuchfile = Path(f'{test_dir}//nosuchfile')
    dotest(tnum, "Delete non-existing file - Exception FileNotFoundError from function runtime",
       nosuchfile.unlink, rwt_debug=debug_flag)

tnum = '12'
if args.test == '0'  or  args.test == tnum:
    t12a = Path(f'{test_dir}/t12a')
    t12a.touch()
    t12b = Path(f'{test_dir}/t12b')
    dotest(tnum, "shutil.copy, rwt_debug True - passes",
        shutil.copy, t12a, t12b, rwt_timeout=1, rwt_debug=debug_flag)

tnum = '13'
if args.test == '0'  or  args.test == tnum:
    t13a = Path(f'{test_dir}/t13a')
    t13a.touch()
    t13b = Path(f'{test_dir}/t13b')
    dotest(tnum, "shutil.copy, rwt_debug False - passes",
       shutil.copy, t13a, t13b, rwt_timeout=1)

tnum = '14'
if args.test == '0'  or  args.test == tnum:
    dotest(tnum, "Function wont_terminate, requiring os.kill, rwt_ntries=1 - Exception TimeoutError",
       wont_terminate, rwt_timeout=0.5, rwt_debug=debug_flag, rwt_ntries=1) #, rwt_kill=False)

tnum = '15'
if args.test == '0'  or  args.test == tnum:
    xx = dotest(tnum, "Function wont_terminate, not killed, rwt_ntries=1 - Exception TimeoutError",
       wont_terminate, rwt_timeout=0.5, rwt_debug=debug_flag, rwt_ntries=1, rwt_kill=False)
    runner_pid = int(str(xx).split('pid ')[1][:-1])
    os.kill(runner_pid, signal.SIGKILL)

tnum = '16'
if args.test == '0'  or  args.test == tnum:
    nosuchfile = Path(f'{test_dir}//nosuchfile')
    dotest(tnum, "Delete non-existing file, rwt_tries=2 - Debug logging for both tries",
       nosuchfile.unlink, rwt_ntries=2, rwt_debug=debug_flag)
    logging.debug ("This wont be logged")
    logging.warning ("This will be logged")

tnum = '17a'
if args.test == '0'  or  args.test == tnum:
    set_logging_level(logging.WARNING, save=False)
    dotest(tnum, "Initial logging level WARNING, rwt_debug=True - log_each_test logs WARNING",
       log_each_level, rwt_debug=True)
    logging.warning (f"Post test logging level:  {logging.getLogger().level}")

tnum = '17b'
if args.test == '0'  or  args.test == tnum:
    set_logging_level(logging.INFO, save=False)
    dotest(tnum, "Initial logging level INFO, rwt_debug=True - log_each_test logs WARNING, INFO",
       log_each_level, rwt_debug=True)
    logging.warning (f"Post test logging level:  {logging.getLogger().level}")

tnum = '17c'
if args.test == '0'  or  args.test == tnum:
    set_logging_level(logging.DEBUG, save=False)
    dotest(tnum, "Initial logging level DEBUG, rwt_debug=True - log_each_test logs WARNING, INFO, DEBUG",
       log_each_level, rwt_debug=True)
    logging.warning (f"Post test logging level:  {logging.getLogger().level}")

tnum = '17d'
if args.test == '0'  or  args.test == tnum:
    set_logging_level(logging.DEBUG, save=False)
    dotest(tnum, "Initial logging level DEBUG, rwt_debug=False - log_each_test logs WARNING, INFO, DEBUG",
       log_each_level, rwt_debug=False)
    logging.warning (f"Post test logging level:  {logging.getLogger().level}")

