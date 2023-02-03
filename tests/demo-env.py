#!/usr/bin/env python3
"""Demo/test for cjnfuncs environment classes/functions
"""

#==========================================================
#
#  Chris Nelson, 2018-2023
#
#==========================================================

__version__ = "1.0"
TOOLNAME =    "cjnfuncs_testenv"
CONFIG_FILE = "demo_env.cfg"

import argparse
from cjnfuncs.cjnfuncs import *


parser = argparse.ArgumentParser(description=__doc__ + __version__, formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('--config-file', '-c', type=str, default=CONFIG_FILE,
                    help=f"Path to the config file (Default <{CONFIG_FILE})> in user/site config directory.")
parser.add_argument('--setup-user', action='store_true',
                    help=f"Install starter files in user space.")
parser.add_argument('--setup-site', action='store_true',
                    help=f"Install starter files in site space.")
parser.add_argument('--cleanup', action='store_true',
                    help="Remove test dirs/files.")
args = parser.parse_args()

tool = set_toolname(TOOLNAME)
print(tool.stats())


if args.setup_user:
    deploy_files([
        { "source": CONFIG_FILE,            "target_dir": "USER_CONFIG_DIR",            "file_stat": 0o644, "dir_stat": 0o770},
        { "source": CONFIG_FILE,            "target_dir": "USER_CONFIG_DIR/subdir",     "file_stat": 0o641, "dir_stat": 0o777},
        { "source": "testfile.txt",         "target_dir": "$HOME/.config/junk2",        "file_stat": 0o600, "dir_stat": 0o707},
        { "source": "testfile.txt",         "target_dir": "USER_CONFIG_DIR"},       # defaults to file_stat 0o764
        { "source": "test_dir",             "target_dir": "USER_DATA_DIR/mydirs",       "file_stat": 0o633, "dir_stat": 0o720},
        { "source": "test_dir/subdir/x4",   "target_dir": "USER_CONFIG_DIR/mydirs",     "file_stat": 0o612, "dir_stat": 0o711},
        # Uncomment these to force error traps
        # { "source": "doesnotexist",       "target_dir": "USER_CONFIG_DIR",            "file_stat": 0o633, "dir_stat": 0o770},
        # { "source": "testfile.txt",       "target_dir": "/no_perm/junkdir",           "file_stat": 0o633, "dir_stat": 0o770},
        ] , overwrite=True)
    print ("Inspect these created directories/files for proper content and permissions per the deploy_files call.")
    sys.exit()

if args.setup_site:
    deploy_files([
        { "source": CONFIG_FILE, "target_dir": "SITE_CONFIG_DIR",                   "file_stat": 0o644, "dir_stat": 0o777},
        { "source": "testfile.txt", "target_dir": "$HOME/.config/junk2",            "file_stat": 0o600, "dir_stat": 0o707},
        { "source": "testfile.txt", "target_dir": "SITE_CONFIG_DIR"},
        { "source": "test_dir", "target_dir": "SITE_DATA_DIR/mydirs",               "file_stat": 0o633, "dir_stat": 0o770},
        { "source": "test_dir/subdir/x4", "target_dir": "SITE_CONFIG_DIR/mydirs",   "file_stat": 0o633, "dir_stat": 0o770},
        # Uncomment this to force error traps
        # { "source": "doesnotexist", "target_dir": "SITE_CONFIG_DIR",                "file_stat": 0o633, "dir_stat": 0o770},
        ] , overwrite=True)
    print ("Inspect these created directories/files for proper content and permissions per the deploy_files call.")
    sys.exit()

if args.cleanup:
    if os.path.exists(tool.user_config_dir):
        print (f"Removing 1  {tool.user_config_dir}")
        shutil.rmtree(tool.user_config_dir)
    if os.path.exists(tool.user_data_dir):
        print (f"Removing 2  {tool.user_data_dir}")
        shutil.rmtree(tool.user_data_dir)

    if os.path.exists(tool.site_config_dir):
        print (f"Removing 3  {tool.site_config_dir}")
        shutil.rmtree(tool.site_config_dir)
    if os.path.exists(tool.site_data_dir):
        print (f"Removing 4  {tool.site_data_dir}")
        shutil.rmtree(tool.site_data_dir)

    junk2 = mungePath("$HOME/.config/junk2").full_path
    if os.path.exists(junk2):
        print (f"Removing 5  {junk2}")
        shutil.rmtree(junk2)
    sys.exit()


if not mungePath(CONFIG_FILE, tool.config_dir).exists:
    print (f"No user or site setup found.  Run with <--setup-user> or <--setup-site> to set up the environment.")
    sys.exit()

print ("Inspect the created directories/files for proper content and permissions per the deploy_files call.")
