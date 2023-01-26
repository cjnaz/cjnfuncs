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
tool.dump()

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


print ("\nShows logfile captured in tool class after setuplogging")
setuplogging(loglevel=10, logfile=args.log_file)
tool.dump()


print ()
stat = requestlock ("try1")
print (f"got back from 1st requestLock.  stat = {stat}")

print ()
stat = requestlock ("try2")
print (f"got back from 2nd requestLock.  stat = {stat}")

print ()
stat = releaselock ()
print (f"got back from 1st releaseLock.  stat = {stat}")

print ()
stat = releaselock ()
print (f"got back from 2nd releaseLock.  stat = {stat}")