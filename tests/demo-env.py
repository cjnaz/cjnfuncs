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

tool = set_toolname(TOOLNAME)
tool.dump()


if args.config_file == "newuserconfig":
    deploy_files([
        { "source": CONFIG_FILE, "target_dir": "USER_CONFIG_DIR",                   "file_stat": 0o644, "dir_stat": 0o770},
        { "source": CONFIG_FILE, "target_dir": "USER_CONFIG_DIR/subdir",            "file_stat": 0o644, "dir_stat": 0o777},
        { "source": "testfile.txt", "target_dir": "$HOME/.config/junk2",            "file_stat": 0o600, "dir_stat": 0o707},
        { "source": "testfile.txt", "target_dir": "USER_CONFIG_DIR"},
        { "source": "test_dir", "target_dir": "USER_DATA_DIR/mydirs",               "file_stat": 0o633, "dir_stat": 0o770},
        { "source": "test_dir/subdir/x4", "target_dir": "USER_CONFIG_DIR/mydirs",   "file_stat": 0o633, "dir_stat": 0o770},
        # { "source": "doesnotexist", "target_dir": "USER_CONFIG_DIR",                "file_stat": 0o633, "dir_stat": 0o770},
        # { "source": "testfile.txt", "target_dir": "/no_perm/junkdir",               "file_stat": 0o633, "dir_stat": 0o770},
        ] , overwrite=True)
    sys.exit()

if args.config_file == "newsiteconfig":
    deploy_files([
        { "source": CONFIG_FILE, "target_dir": "SITE_CONFIG_DIR",                   "file_stat": 0o644, "dir_stat": 0o777},
        { "source": "testfile.txt", "target_dir": "$HOME/.config/junk2",            "file_stat": 0o600, "dir_stat": 0o707},
        { "source": "testfile.txt", "target_dir": "SITE_CONFIG_DIR"},
        { "source": "test_dir", "target_dir": "SITE_DATA_DIR/mydirs",               "file_stat": 0o633, "dir_stat": 0o770},
        { "source": "test_dir/subdir/x4", "target_dir": "SITE_CONFIG_DIR/mydirs",   "file_stat": 0o633, "dir_stat": 0o770},
        # { "source": "doesnotexist", "target_dir": "SITE_CONFIG_DIR",                "file_stat": 0o633, "dir_stat": 0o770},
        # { "source": "testfile.txt", "target_dir": "/no_perm/junkdir",               "file_stat": 0o633, "dir_stat": 0o770},
        ] , overwrite=True)


if args.config_file == "cleanup":
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


if tool.env_defined == False:
    print ("No user or site setup found.  Run with <--config-file = newuserconfig (or newsiteconfig)> to set up the environment.")
    sys.exit()
