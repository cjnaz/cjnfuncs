#!/usr/bin/env python3
"""Demo/test for cjnfuncs environment/deployfiles classes/functions

Produce / compare to golden results:
    ./demo-deployfiles.py --setup-user
"""

#==========================================================
#
#  Chris Nelson, 2024
#
#==========================================================

__version__ = "1.3"
TOOLNAME =    "cjnfuncs_testdeployfiles"
CONFIG_FILE = "demo_deployfiles.cfg"

import argparse
import os
import sys
import shutil
from pathlib import Path
from cjnfuncs.core        import set_toolname, setuplogging, logging
from cjnfuncs.deployfiles import deploy_files
from cjnfuncs.mungePath   import mungePath, check_path_exists
import cjnfuncs.core as core


parser = argparse.ArgumentParser(description=__doc__ + __version__, formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('--setup-user', action='store_true',
                    help=f"Install starter files in user space.")
parser.add_argument('--setup-site', action='store_true',
                    help=f"Install starter files in site space.")
parser.add_argument('--cleanup', action='store_true',
                    help="Remove test dirs/files.")
args = parser.parse_args()

set_toolname(TOOLNAME)
setuplogging()
logging.getLogger().setLevel(logging.INFO)


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

print(core.tool)

if not mungePath(CONFIG_FILE, core.tool.user_config_dir).exists  and  not mungePath(CONFIG_FILE, core.tool.site_config_dir).exists:
    print (f"No user or site setup found.  Run with <--setup-user> or <--setup-site> to set up the environment.")
else:
    print ("Inspect the created directories/files for proper content and permissions per the deploy_files call.")


# *****  Test Error Traps
print ("\n\n=====================================================================")
print ("***** Test 1:  User cannot write on site dir")
try:
    deploy_files([
        { "source": CONFIG_FILE,            "target_dir": "SITE_CONFIG_DIR",            "file_stat": 0o644, "dir_stat": 0o777} ])
except Exception:
    logging.exception("deploy_files() failed.")

print ("\n\n=====================================================================")
print ("***** Test 1a: User cannot write on site dir - Quiet exception handling")
try:
    deploy_files([
        { "source": CONFIG_FILE,            "target_dir": "SITE_CONFIG_DIR",            "file_stat": 0o644, "dir_stat": 0o777} ])
except Exception as e:
    logging.warning(f"deploy_files() failed.\n  {e}")

print ("\n\n=====================================================================")
print ("***** Test 2:  Overwrite existing directory")
try:
    deploy_files([
        { "source": "test_dir",             "target_dir": "USER_DATA_DIR/mydirs",       "file_stat": 0o633, "dir_stat": 0o770}, ], overwrite=True)
    deploy_files([
        { "source": "test_dir",             "target_dir": "USER_DATA_DIR/mydirs",       "file_stat": 0o633, "dir_stat": 0o770}, ], overwrite=True)
except Exception:
    logging.exception("deploy_files() failed.")

print ("\n\n=====================================================================")
print ("***** Test 3:  Overwrite existing directory skipped")
try:
    deploy_files([
        { "source": "test_dir",             "target_dir": "USER_DATA_DIR/mydirs",       "file_stat": 0o633, "dir_stat": 0o770}, ])
except Exception:
    logging.exception("deploy_files() failed.")

print ("\n\n=====================================================================")
print ("***** Test 4:  Try copy non-existing source file")
try:
    deploy_files([
        { "source": "no_such_file",         "target_dir": "USER_DATA_DIR",              "file_stat": 0o633, "dir_stat": 0o770}, ])
except Exception:
    logging.exception("deploy_files() failed.")

print ("\n\n=====================================================================")
print ("***** Test 4a: Try copy non-existing source file - Quiet exception handling")
try:
    deploy_files([
        { "source": "no_such_file",         "target_dir": "USER_DATA_DIR",              "file_stat": 0o633, "dir_stat": 0o770}, ])
except Exception as e:
    logging.warning(f"deploy_files() failed.\n  {e}")

print ("\n\n=====================================================================")
print ("***** Test 5:  Try copy non-existing source file with missing_ok")
try:
    deploy_files([
        { "source": "no_such_file",         "target_dir": "USER_DATA_DIR",              "file_stat": 0o633, "dir_stat": 0o770}, ], missing_ok=True)
except Exception:
    logging.exception("deploy_files() failed.")

print ("\n\n=====================================================================")
print ("***** Test 6:  Destination is an existing file")
outfile = Path('/tmp/deployfile_T6')
outfile.write_text('')
try:
    deploy_files([
        { "source": CONFIG_FILE,            "target_dir": "/tmp/deployfile_T6",         "file_stat": 0o633, "dir_stat": 0o770}, ], missing_ok=True)
except Exception:
    logging.exception("deploy_files() failed.")
outfile.unlink()

print ("\n\n=====================================================================")
print ("***** Test 7:  Destination is an existing file, overwrite but no permission")
outfile = mungePath(CONFIG_FILE, '/tmp').full_path
if not check_path_exists(outfile):
    outfile.write_text('')
    os.chmod(str(outfile), 0o000)
try:
    deploy_files([
        { "source": CONFIG_FILE,            "target_dir": "/tmp",         "file_stat": 0o633} ], overwrite=True)
except Exception:
    logging.exception("deploy_files() failed.")
outfile.unlink(missing_ok=True)


