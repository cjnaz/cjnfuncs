#!/usr/bin/env python3
"""Demo/test for cjnfuncs lock file functions and setuplogging without config file
"""

#==========================================================
#
#  Chris Nelson, 2018-2023
#
#==========================================================

__version__ = "1.0"
TOOLNAME    = "cjnfuncs_testlock"
LOGFILE     = None  #"testlock.log"

import argparse
from cjnfuncs.cjnfuncs import *


tool = set_toolname(TOOLNAME)

parser = argparse.ArgumentParser(description=__doc__ + __version__, formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('--log-file', '-l', default=LOGFILE,
                    help=f"Path to log file (default <{LOGFILE}).")
parser.add_argument('--cleanup', action='store_true',
                    help="Remove test dirs/files.")
args = parser.parse_args()

if args.cleanup:
    if os.path.exists(tool.data_dir):
        print (f"Removing 1  {tool.data_dir}")
        shutil.rmtree(tool.data_dir)
    sys.exit()


# Shows logfile captured in tool class after setuplogging()
setuplogging(args.log_file, call_logfile_wins=True)
print(tool.stats())


print (f"\nUsing default lock file")
stat = requestlock ("try1")
print (f"got back from 1st requestLock.  stat = {stat}")

stat = requestlock ("try2")
print (f"got back from 2nd requestLock.  stat = {stat}")

stat = releaselock ()
print (f"got back from 1st releaseLock.  stat = {stat}")

stat = releaselock ()
print (f"got back from 2nd releaseLock.  stat = {stat}")


print (f"\nUsing absolute lockfile path")
stat = requestlock ("abs path", lockfile= tool.data_dir / "myuserlock")
print (f"got back from abs path requestLock.  stat = {stat}")
stat = requestlock ("abs path", lockfile= tool.data_dir / "myuserlock", timeout="1s")
print (f"got back from second abs path requestLock.  stat = {stat}")

stat = releaselock (lockfile= tool.data_dir / "myuserlock")
print (f"got back from abs path releaseLock.  stat = {stat}")


print (f"\nUsing relative lockfile path")
stat = requestlock ("rel path", "myuserlock")
print (f"got back from rel path requestLock.  stat = {stat}")
stat = requestlock ("rel path", "myuserlock", timeout="0m")
print (f"got back from second rel path requestLock.  stat = {stat}")

stat = releaselock ("myuserlock")
print (f"got back from rel path releaseLock.  stat = {stat}")
