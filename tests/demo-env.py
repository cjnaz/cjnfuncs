#!/usr/bin/env python3
"""Demo/test for cjnfuncs environment classes/functions
"""

#==========================================================
#
#  Chris Nelson, 2018-2023
#
#  2.0  220109  Restructured as a formal package
#
# Changes pending
#   
#==========================================================

__version__ = "1.0"
CONFIG_FILE = "demo_env.cfg"

import argparse
from cjnfuncs.cjnfuncs import *

# import pathlib, __main__

# def touch (file_path):
#     file_path.open('w').close()
#     # io.open(file_path, 'w').close()

# def remove_file (file_path):
#     os.remove(file_path)

# def remove_tree (path):
#     shutil.rmtree(path)

parser = argparse.ArgumentParser(description=__doc__ + __version__, formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('--config-file', '-c', type=str, default=CONFIG_FILE,
                    help=f"Path to the config file (Default <{CONFIG_FILE})> in user/site config directory.")

args = parser.parse_args()

toolname = set_toolname("envtest")
toolname.dump()

if toolname.env_defined == False:
    print ("No user or site setup found.  Run with <--config-file = newuserconfig (or newsiteconfig)> to set up the environment.")


if args.config_file == "newuserconfig":
    deploy_files([
        { "source": CONFIG_FILE, "target_dir": "USER_CONFIG_DIR",                   "file_stat": 0o644, "dir_stat": 0o777},
        { "source": "creds_test", "target_dir": "$HOME/.config/junk2",              "file_stat": 0o600, "dir_stat": 0o707},
        { "source": "creds_test", "target_dir": "USER_CONFIG_DIR"},
        { "source": "test_dir", "target_dir": "USER_DATA_DIR/mydirs",               "file_stat": 0o633, "dir_stat": 0o770},
        { "source": "test_dir/subdir/x4", "target_dir": "USER_CONFIG_DIR/mydirs",   "file_stat": 0o633, "dir_stat": 0o770},
        # { "source": "doesnotexist", "target_dir": "USER_CONFIG_DIR",              "file_stat": 0o633, "dir_stat": 0o770},
        # { "source": "creds_test", "target_dir": "/no_perm/junkdir",               "file_stat": 0o633, "dir_stat": 0o770},
        ] , overwrite=True)
    sys.exit()

if args.config_file == "newsiteconfig":
    deploy_files([
        { "source": CONFIG_FILE, "target_dir": "SITE_CONFIG_DIR", "stat": 0o644 },
        { "source": "creds_test", "target_dir": "$HOME/.config", "stat": 0o600 },
        ])# , overwrite=True)
    sys.exit()
