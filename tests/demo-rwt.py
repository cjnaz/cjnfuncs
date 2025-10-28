#!/usr/bin/env python3
"""Demo/test for cjnfuncs.rwt run_with_timeout()

Produce / compare to golden results:
    ./demo-rwt.py -t 0 | diff demo-rwt-golden.txt -
        Differences will be timestamps, pids, function addresses, and yahoo.com IP address

    ./demo-rwt.py --cleanup
"""

#==========================================================
#
#  Chris Nelson, 2024-2025
#
#==========================================================

__version__ =   '2.0'
TOOLNAME =      'demo_rwt'          # rename
test_dir =      f'/tmp/{TOOLNAME}'

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

from cjnfuncs.core              import set_toolname, setuplogging, logging, set_logging_level #, restore_logging_level
# from cjnfuncs.deployfiles       import deploy_files
# from cjnfuncs.configman         import config_item
# from cjnfuncs.timevalue         import timevalue, retime
# from cjnfuncs.mungePath         import mungePath
from cjnfuncs.rwt    import run_with_timeout
# import cjnfuncs.core as core

set_toolname(TOOLNAME)
# setuplogging()
setuplogging(ConsoleLogFormat="{asctime} {module:>22}.{funcName:20} {levelname:>8}:  {message}")

parser = argparse.ArgumentParser(description=__doc__ + __version__, formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-t', '--test', default='0',
                    help="Test number to run (default 0).  0 runs all tests")
                    # help="Test number to run (default 0).  0 runs most all tests (not tests with untrapped errors)")

# Include/remove as needed
# parser.add_argument('--setup-user', action='store_true',
#                     help=f"Install starter files in user space.")
# parser.add_argument('--setup-site', action='store_true',
#                     help=f"Install starter files in site space.")
parser.add_argument('--cleanup', action='store_true',
                    help="Remove test dirs/files.")

args = parser.parse_args()



# THIS DEMO TEST FILE IS A TEMPLATE FOR OTHER TESTS, THUS LOTS OF EXTRANEOUS STUFF IS RETAINED.
# --------------------------------------------------------------------
# if args.setup_user:
#     Path(test_dir).mkdir()
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
    # sys.exit()

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

    try:
        print (f"Removing 5  {test_dir}")
        shutil.rmtree(test_dir)
    except:
        pass
    sys.exit()


Path(test_dir).mkdir(exist_ok=True)

# --------------------------------------------------------------------

def dotest (desc, expect, func, *args, **kwargs):
    logging.warning (f"\n\n==============================================================================================\n" +
                     f"Test {tnum} - {desc}\n" +
                     f"  EXPECT: {expect}")
                    #  f"Test {tnum} - {desc}\n" +
                    #  f"  GIVEN:      {args}, {kwargs}\n"
                    #  f"  EXPECT:     {expect}")
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

# test_dir =      f'/tmp/{TOOLNAME}'
# tempfile.gettempdir()
test_dir = Path(tempfile.gettempdir()) / TOOLNAME
test_dir.mkdir(exist_ok=True)

set_logging_level(logging.WARNING, save=False)
abc= 42

def test_shell_1(t, tnum, file):
    time.sleep (t)
    logging.info (f"Hello there {abc}.  Log from unkilled Test {tnum}, pid: {os.getpid()}")
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


# abc1 = 5
def hack():
    global abc1
    abc1 += 1
    print ("in hack", abc1)

#===============================================================================================

# freeze_support()
if __name__ == "__main__":
    if check_tnum('1'):
    # tnum = '1'
    # if args.test == '0'  or  args.test == tnum:
        dotest ("Built-in print", "Pass, return None",
                print, "Hello", "there", "again", rwt_timeout=3, sep=" blah ", end=" The end.\n", rwt_debug=True)

    if check_tnum('2'):
        dotest("Subprocess ping known", "Return subprocess pass result",
               subprocess.run, ['ping', 'yahoo.com', '-c', '1'], rwt_timeout=3, timeout=3, capture_output=True, text=True, rwt_debug=True)

    if check_tnum('3'):
        dotest("Subprocess ping unknown", "Return subprocess fail result",
               subprocess.run, ['ping', 'dummyunknown.com', '-c', '1'], rwt_timeout=3, timeout=1, capture_output=True, text=True, rwt_debug=True)


    # Test 4 series - Check subprocess calls with subprocess timeout arg < and > rwt_timeout
    if check_tnum('4a'):
        dotest("Subprocess ping known/unavailable. subprocess timeout < rwt_timeout", "Exception subprocess.TimeoutExpired",
               subprocess.run, ['ping', 'testhostx', '-c', '1'], timeout=0.5, capture_output=True, text=True, rwt_timeout=3, rwt_debug=True)

    if check_tnum('4b'):
        dotest("Subprocess ping known/unavailable, subprocess timeout < rwt_timeout, rwt_ntries=2", "Exception subprocess.TimeoutExpired",
               subprocess.run, ['ping', 'testhostx', '-c', '1'], timeout=0.5, capture_output=True, text=True, rwt_timeout=3, rwt_debug=True, rwt_ntries=2)

    if check_tnum('4c'):
        dotest("Subprocess ping known/unavailable, rwt_timeout < subprocess timeout", "Exception TimeoutError",
               subprocess.run, ['ping', 'testhostx', '-c', '1'], timeout=3, capture_output=True, text=True, rwt_timeout=0.5, rwt_debug=True)

    if check_tnum('4d'):
        dotest("Subprocess ping known/unavailable, rwt_timeout < subprocess timeout, rwt_ntries=2", "Exception TimeoutError",
               subprocess.run, ['ping', 'testhostx', '-c', '1'], timeout=3, capture_output=True, text=True, rwt_timeout=0.5, rwt_debug=True, rwt_ntries=2)

    if check_tnum('4e'):
        dotest("Subprocess ping known/unavailable, No subprocess timeout", "Exception TimeoutError",
               subprocess.run, ['ping', 'testhostx', '-c', '1'], capture_output=True, text=True, rwt_timeout=0.5, rwt_debug=True)

    if check_tnum('4f'):
        dotest("Subprocess ping known/unavailable, No subprocess timeout, rwt_ntries=2", "Exception TimeoutError",
               subprocess.run, ['ping', 'testhostx', '-c', '1'], capture_output=True, text=True, rwt_timeout=0.5, rwt_ntries=2, rwt_debug=True)


    # Test 6 series - Exercise rwt_kill=False
    if check_tnum('6a'):
        dotest("Function took too long, killed", "Exception TimeoutError, File 'FileNotTouched' not created", 
               test_shell_1, 2, tnum, f'{test_dir}/FileNotTouched', rwt_timeout=0.5, rwt_debug=True)

    if check_tnum('6b'):
        set_logging_level(logging.INFO, save=False)
        dotest("INFO external log level, Function took too long, not killed", "Exception TimeoutError, File 'FileTouched_1' created, message logged during Test 6c",
               test_shell_1, 1, tnum, Path(f'{test_dir}/FileTouched_1'), rwt_timeout=0.5, rwt_kill=False, rwt_debug=True)

    if check_tnum('6c'):
        set_logging_level(logging.WARNING, save=False)
        dotest("WARNING external log level, Sleep took too long, rwt_debug=False", "Exception TimeoutError, Test 6b INFO log",
               time.sleep, 10, rwt_timeout=1.5)

    if check_tnum('6d'):
        dotest("Sleep took too long", "Exception TimeoutError",
               time.sleep, 10, rwt_timeout=0.5, rwt_debug=True)


    # Test 9 series - Check rwt kwargs check logic
    if check_tnum('9a'):
        dotest("Invalid rwt_timeout", "Exception ValueError",
               test_shell_1, 2, tnum, f'{test_dir}/FileTouched_9a', rwt_timeout='abc', rwt_debug=True)

    if check_tnum('9b'):
        dotest("Invalid rwt_ntries", "Exception ValueError",
               test_shell_1, 2, tnum, f'{test_dir}/FileTouched_9b', rwt_ntries='abc', rwt_debug=True)

    if check_tnum('9c'):
        dotest("Invalid rwt_kill", "Exception ValueError",
               test_shell_1, 2, tnum, f'{test_dir}/FileTouched_9c', rwt_kill='abc', rwt_debug=True)

    if check_tnum('9d'):
        dotest("Invalid rwt_debug", "Exception ValueError",
               test_shell_1, 2, tnum, f'{test_dir}/FileTouched_9d', rwt_debug='abc')

    if check_tnum('11'):
        nosuchfile = Path(f'{test_dir}//nosuchfile')
        dotest("Delete non-existing file", "Exception FileNotFoundError from function runtime",
               nosuchfile.unlink, rwt_debug=True)

    if check_tnum('12'):
        t12a = test_dir / 't12a'
        t12a.touch()
        t12b = test_dir / 't12b'
        # t12a = Path(f'{test_dir}/t12a')
        # t12a.touch()
        # t12b = Path(f'{test_dir}/t12b')
        dotest("shutil.copy, rwt_debug True", "Pass",
               shutil.copy, t12a, t12b, rwt_timeout=1, rwt_debug=True)

    if check_tnum('13'):
        t13a = Path(f'{test_dir}/t13a')
        t13a.touch()
        t13b = Path(f'{test_dir}/t13b')
        dotest("shutil.copy, rwt_debug False", "Pass",
               shutil.copy, t13a, t13b, rwt_timeout=1)


    # Test 14 series - Process wont exit, kill scenarios
    if check_tnum('14a'):
        dotest("Function wont_terminate, requiring os.kill, rwt_ntries=1", "Exception TimeoutError",
               wont_terminate, rwt_timeout=0.5, rwt_debug=True, rwt_ntries=1)

    if check_tnum('14b'):
        xx = dotest("Function wont_terminate, not killed, rwt_ntries=1", "Exception TimeoutError, pid listed",
               wont_terminate, rwt_timeout=0.5, rwt_debug=True, rwt_ntries=1, rwt_kill=False)
        runner_pids = str(xx).split('orphaned pids: ')[1].split(' ')
        for runner_pid in runner_pids:
            # os.kill(int(runner_pid), signal.SIGKILL)
            if sys.platform.startswith("win"):
                subprocess.run(["taskkill", "/PID", runner_pid, "/F"])
            else:
                os.kill(int(runner_pid), signal.SIGKILL)
    

    if check_tnum('14c'):
        xx = dotest("Function wont_terminate, not killed, rwt_ntries=4", "Exception TimeoutError, pids listed",
               wont_terminate, rwt_timeout=0.5, rwt_debug=True, rwt_ntries=4, rwt_kill=False)
        runner_pids = str(xx).split('orphaned pids: ')[1].split(' ')
        # for runner_pid in runner_pids:
        #     os.kill(int(runner_pid), signal.SIGKILL)
        for runner_pid in runner_pids:
            if sys.platform.startswith("win"):
                subprocess.run(["taskkill", "/PID", runner_pid, "/F"])
            else:
                os.kill(int(runner_pid), signal.SIGKILL)


    # Test 16 series - Check logging level handling with exception raised by function
    if check_tnum('16a'):
        set_logging_level(logging.WARNING, save=False)
        nosuchfile = Path(f'{test_dir}//nosuchfile')
        dotest("WARNING external log level, rwt_ntries=1, rwt_debug=True", "Exception FileNotFoundError, Post test logging level:  30",
               nosuchfile.unlink, rwt_ntries=1, rwt_debug=True)
        logging.warning (f"Post test logging level:  {logging.getLogger().level}")

    if check_tnum('16b'):
        set_logging_level(logging.INFO, save=False)
        nosuchfile = Path(f'{test_dir}//nosuchfile')
        dotest("INFO external log level, rwt_ntries=1, rwt_debug=True", "Exception FileNotFoundError, Post test logging level:  20",
               nosuchfile.unlink, rwt_ntries=1, rwt_debug=True)
        logging.warning (f"Post test logging level:  {logging.getLogger().level}")

    if check_tnum('16c'):
        set_logging_level(logging.DEBUG, save=False)
        nosuchfile = Path(f'{test_dir}//nosuchfile')
        dotest("DEBUG external log level, rwt_ntries=1, rwt_debug=True", "Exception FileNotFoundError, Post test logging level:  10",
               nosuchfile.unlink, rwt_ntries=1, rwt_debug=True)
        logging.warning (f"Post test logging level:  {logging.getLogger().level}")

    if check_tnum('16d'):
        set_logging_level(logging.DEBUG, save=False)
        nosuchfile = Path(f'{test_dir}//nosuchfile')
        dotest("DEBUG external log level, rwt_ntries=1, rwt_debug=False", "Exception FileNotFoundError, Post test logging level:  10",
               nosuchfile.unlink, rwt_ntries=1, rwt_debug=False)
        logging.warning (f"Post test logging level:  {logging.getLogger().level}")

    if check_tnum('16e'):
        set_logging_level(logging.WARNING, save=False)
        nosuchfile = Path(f'{test_dir}//nosuchfile')
        dotest("WARNING external log level, rwt_ntries=2, rwt_debug=True", "Exception FileNotFoundError, Post test logging level:  30",
               nosuchfile.unlink, rwt_ntries=2, rwt_debug=True)
        logging.warning (f"Post test logging level:  {logging.getLogger().level}")

    if check_tnum('16f'):
        set_logging_level(logging.INFO, save=False)
        nosuchfile = Path(f'{test_dir}//nosuchfile')
        dotest("INFO external log level, rwt_ntries=2, rwt_debug=True", "Exception FileNotFoundError, Post test logging level:  20",
               nosuchfile.unlink, rwt_ntries=2, rwt_debug=True)
        logging.warning (f"Post test logging level:  {logging.getLogger().level}")

    if check_tnum('16g'):
        set_logging_level(logging.DEBUG, save=False)
        nosuchfile = Path(f'{test_dir}//nosuchfile')
        dotest("DEBUG external log level, rwt_ntries=2, rwt_debug=True", "Exception FileNotFoundError, Post test logging level:  10",
               nosuchfile.unlink, rwt_ntries=2, rwt_debug=True)
        logging.warning (f"Post test logging level:  {logging.getLogger().level}")

    if check_tnum('16h'):
        set_logging_level(logging.DEBUG, save=False)
        nosuchfile = Path(f'{test_dir}//nosuchfile')
        dotest("DEBUG external log level, rwt_ntries=2, rwt_debug=False", "Exception FileNotFoundError, Post test logging level:  10",
               nosuchfile.unlink, rwt_ntries=2, rwt_debug=False)
        logging.warning (f"Post test logging level:  {logging.getLogger().level}")



    # Test 17 series - Check logging level handling with normal exit by function
    if check_tnum('17a'):
        set_logging_level(logging.WARNING, save=False)
        dotest("WARNING external log level, rwt_ntries=1, rwt_debug=True", "log_each_level logs WARNING, Post test logging level:  30",
               log_each_level, rwt_ntries=1, rwt_debug=True)
        logging.warning (f"Post test logging level:  {logging.getLogger().level}")

    if check_tnum('17b'):
        set_logging_level(logging.INFO, save=False)
        dotest("INFO external log level, rwt_ntries=1, rwt_debug=True", "log_each_level logs WARNING, INFO, Post test logging level:  20",
               log_each_level, rwt_ntries=1, rwt_debug=True)
        logging.warning (f"Post test logging level:  {logging.getLogger().level}")

    if check_tnum('17c'):
        set_logging_level(logging.DEBUG, save=False)
        dotest("DEBUG external log level, rwt_ntries=1, rwt_debug=True", "log_each_level logs WARNING, INFO, DEBUG, Post test logging level:  10",
               log_each_level, rwt_ntries=1, rwt_debug=True)
        logging.warning (f"Post test logging level:  {logging.getLogger().level}")

    if check_tnum('17d'):
        set_logging_level(logging.DEBUG, save=False)
        dotest("DEBUG external log level, rwt_ntries=1, rwt_debug=False", "log_each_level logs WARNING, INFO, DEBUG, Post test logging level:  10",
               log_each_level, rwt_ntries=1, rwt_debug=False)
        logging.warning (f"Post test logging level:  {logging.getLogger().level}")

    if check_tnum('17e'):
        set_logging_level(logging.WARNING, save=False)
        dotest("WARNING external log level, rwt_ntries=2, rwt_debug=True", "log_each_level logs WARNING, Post test logging level:  30",
               log_each_level, rwt_ntries=2, rwt_debug=True)
        logging.warning (f"Post test logging level:  {logging.getLogger().level}")

    if check_tnum('17f'):
        set_logging_level(logging.INFO, save=False)
        dotest("INFO external log level, rwt_ntries=2, rwt_debug=True", "log_each_level logs WARNING, INFO, Post test logging level:  20",
               log_each_level, rwt_ntries=2, rwt_debug=True)
        logging.warning (f"Post test logging level:  {logging.getLogger().level}")

    if check_tnum('17g'):
        set_logging_level(logging.DEBUG, save=False)
        dotest("DEBUG external log level, rwt_ntries=2, rwt_debug=True", "log_each_level logs WARNING, INFO, DEBUG, Post test logging level:  10",
               log_each_level, rwt_ntries=2, rwt_debug=True)
        logging.warning (f"Post test logging level:  {logging.getLogger().level}")

    if check_tnum('17h'):
        set_logging_level(logging.DEBUG, save=False)
        dotest("DEBUG external log level, rwt_ntries=2, rwt_debug=False", "log_each_level logs WARNING, INFO, DEBUG, Post test logging level:  10",
               log_each_level, rwt_ntries=2, rwt_debug=False)
        logging.warning (f"Post test logging level:  {logging.getLogger().level}")



    # Debug / development

# Defined above at top level:
# abc1 = 5
# def hack():
#     global abc1
#     abc1 += 1
#     print ("in hack", abc1)

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

        # set_logging_level(logging.DEBUG, save=False)
        # dotest("DEBUG external log level, rwt_ntries=2, rwt_debug=False", "log_each_level logs WARNING, INFO, DEBUG, Post test logging level:  10",
        # log_each_level, rwt_ntries=2, rwt_debug=False)
        # logging.warning (f"Post test logging level:  {logging.getLogger().level}")

