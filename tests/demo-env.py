#!/usr/bin/env python3
"""Demo/test for cjnfuncs environment classes/functions
"""

#==========================================================
#
#  Chris Nelson, 2023
#
#==========================================================

__version__ = "1.1"
TOOLNAME =    "cjnfuncs_testenv"
CONFIG_FILE = "demo_env.cfg"

import argparse
import os
import sys
import shutil
# from cjnfuncs.cjnfuncs import *
from cjnfuncs.core     import set_toolname #, setuplogging, logging, ConfigError
import cjnfuncs.core as core
# set_toolname(TOOLNAME)
from cjnfuncs.deployfiles import deploy_files
from cjnfuncs.mungePath import mungePath


parser = argparse.ArgumentParser(description=__doc__ + __version__, formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('--setup-user', action='store_true',
                    help=f"Install starter files in user space.")
parser.add_argument('--setup-site', action='store_true',
                    help=f"Install starter files in site space.")
parser.add_argument('--cleanup', action='store_true',
                    help="Remove test dirs/files.")
args = parser.parse_args()

# tool = set_toolname(TOOLNAME)
set_toolname(TOOLNAME)
# print(tool)


if args.setup_user:
    deploy_files([
        { "source": CONFIG_FILE,            "target_dir": "USER_CONFIG_DIR",            "file_stat": 0o644, "dir_stat": 0o770},
        { "source": CONFIG_FILE,            "target_dir": "USER_CONFIG_DIR/subdir",     "file_stat": 0o641, "dir_stat": 0o777},
        { "source": "testfile.txt",         "target_dir": "$HOME/.config/junk2",        "file_stat": 0o600, "dir_stat": 0o707},
        { "source": "testfile.txt",         "target_dir": "USER_CONFIG_DIR/dirxxx"},  # defaults file_stat 0o664, dir_stat 0o775
        { "source": "test_dir",             "target_dir": "USER_DATA_DIR/mydirs",       "file_stat": 0o633, "dir_stat": 0o720},
        { "source": "test_dir/subdir/x4",   "target_dir": "USER_CONFIG_DIR/mydirs",     "file_stat": 0o612, "dir_stat": 0o711},
        # Uncomment these to force error traps
        # { "source": "doesnotexist",       "target_dir": "USER_CONFIG_DIR",            "file_stat": 0o633, "dir_stat": 0o770},
        # { "source": "testfile.txt",       "target_dir": "/no_perm/junkdir",           "file_stat": 0o633, "dir_stat": 0o770},
        ] , overwrite=True)

if args.setup_site:
    deploy_files([
        { "source": CONFIG_FILE,            "target_dir": "SITE_CONFIG_DIR",            "file_stat": 0o644, "dir_stat": 0o777},
        { "source": "testfile.txt",         "target_dir": "$HOME/.config/junk2",        "file_stat": 0o600, "dir_stat": 0o707},
        { "source": "testfile.txt",         "target_dir": "SITE_CONFIG_DIR/dirxxx"},
        { "source": "test_dir",             "target_dir": "SITE_DATA_DIR/mydirs",       "file_stat": 0o633, "dir_stat": 0o770},
        { "source": "test_dir/subdir/x4",   "target_dir": "SITE_CONFIG_DIR/mydirs",     "file_stat": 0o633, "dir_stat": 0o770},
        # Uncomment this to force error traps
        # { "source": "doesnotexist", "target_dir": "SITE_CONFIG_DIR",                "file_stat": 0o633, "dir_stat": 0o770},
        ] , overwrite=True)

if args.cleanup:
    if os.path.exists(core.tool.user_config_dir):
        print (f"Removing 1  {core.tool.user_config_dir}")
        shutil.rmtree(core.tool.user_config_dir)
    if os.path.exists(core.tool.user_data_dir):
        print (f"Removing 2  {core.tool.user_data_dir}")
        shutil.rmtree(core.tool.user_data_dir)

    try:
        if os.path.exists(core.tool.site_config_dir):
            print (f"Removing 3  {core.tool.site_config_dir}")
            shutil.rmtree(core.tool.site_config_dir)
        if os.path.exists(core.tool.site_data_dir):
            print (f"Removing 4  {core.tool.site_data_dir}")
            shutil.rmtree(core.tool.site_data_dir)
    except:
        print ("NOTE:  Run as root/sudo to cleanup site dirs")

    junk2 = mungePath("$HOME/.config/junk2").full_path
    if os.path.exists(junk2):
        print (f"Removing 5  {junk2}")
        shutil.rmtree(junk2)
    sys.exit()

# tool = set_toolname(TOOLNAME)
print(core.tool)


if not mungePath(CONFIG_FILE, core.tool.user_config_dir).exists  and  not mungePath(CONFIG_FILE, core.tool.site_config_dir).exists:
    print (f"No user or site setup found.  Run with <--setup-user> or <--setup-site> to set up the environment.")
else:
    print ("Inspect the created directories/files for proper content and permissions per the deploy_files call.")
