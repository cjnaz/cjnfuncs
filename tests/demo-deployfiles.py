#!/usr/bin/env python3
"""Demo/test for cjnfuncs.deployfiles

Produce / compare to golden results on Linux:

  As user on Linux:
    ./demo-deployfiles.py | diff demo-deployfiles-golden-user-linux.txt -
        No differences expected on Linux

  As root Linux:
    ./demo-deployfiles.py --setup-site-mode
    ./demo-deployfiles.py | diff demo-deployfiles-golden-site-linux.txt -
    ./demo-deployfiles.py --remove-site-mode


Produce / compare to golden results on Windows:

  As user on Windows:
    ./demo-deployfiles.py > tempfile.txt    Then check diff to demo-deployfiles-golden-user-windows.txt

  As privileged user Windows:
    demo-deployfiles.py --setup-site-mode
    demo-deployfiles.py > tempfile.txt      Then check diff to demo-deployfiles-golden-site-windows.txt
    demo-deployfiles.py --remove-site-mode

Linux and Windows test 6 will show significant difference due to .config_dir, .data_dir, and .state_dir
all mapping to the same directory on Windows user mode:
    C:\\Users\\stuff\\AppData\\Local\\cjnfuncs_testdeployfiles
Similar for site mode.
"""

#==========================================================
#
#  Chris Nelson, 2024-2025
#
#==========================================================

__version__ =   '3.1'
TOOLNAME =      'cjnfuncs_testdeployfiles'
CONFIG_FILE =   "demo_deployfiles.cfg"

import argparse
import tempfile
import os
import stat
import shutil
import sys
from pathlib import Path

from cjnfuncs.core              import set_toolname, setuplogging, logging, set_logging_level
from cjnfuncs.deployfiles       import deploy_files
import cjnfuncs.core as core

set_toolname(TOOLNAME)
setuplogging(ConsoleLogFormat="{module:>22}.{funcName:20} {levelname:>8}:  {message}")

testpath = Path(tempfile.gettempdir()) / TOOLNAME
testpath.mkdir(exist_ok=True)


parser = argparse.ArgumentParser(description=__doc__ + __version__, formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('--setup-site-mode', action='store_true',
                    help=f"Configure for site-mode by creating a tool site-mode directory.  Run tests as root.")
parser.add_argument('--remove-site-mode', action='store_true',
                    help=f"Remove for site-mode directories.  Tests then run on user-mode directories.")
parser.add_argument('-t', '--test', default='0',
                    help="Test number to run (default 0).  0 runs all tests")

args = parser.parse_args()


# --------------------------------------------------------------------

def dotest (testnum, desc, expect, *args, **kwargs):
    logging.warning (f"\n\n==============================================================================================\n" +
                     f"Test {testnum} - {desc}\n" +
                     f"  GIVEN:      {args}, {kwargs}\n"
                     f"  EXPECT:     {expect}")
    try:
        result = deploy_files(*args, **kwargs)
        logging.warning (f"\n  RETURNED:   {result}")
        return result
    except Exception as e:
        logging.error (f"\n  RAISED:     {type(e).__name__}: {e}")
        # logging.exception (f"\n  RAISED:     {type(e).__name__}: {e}")
        return e


# --------------------------------------------------------------------
# Setups, support functions, and vars

set_logging_level(logging.INFO, save=False)

if sys.platform.startswith("win"):
    config_junk2 = Path(os.path.expandvars('%HOMEDRIVE%%HOMEPATH%/.config/junk2'))
else:
    config_junk2 = Path(os.path.expandvars('$HOME/.config/junk2'))


def rmtree(root):
    try:
        if os.path.exists(root):
            shutil.rmtree(root)
    except:
        pass


if args.setup_site_mode:                        # Must be run as root
    Path(core.tool.site_config_dir).mkdir(exist_ok=True)
    logging.info (f"Site mode enabled.  Created:  {core.tool.site_config_dir}")
    sys.exit()

if args.remove_site_mode:                       # Must be run as root
    rmtree(core.tool.site_config_dir)
    rmtree(core.tool.site_data_dir)
    rmtree(config_junk2)
    logging.info (f"Site mode disabled.  Removed:\n  {core.tool.site_config_dir}\n  {core.tool.site_data_dir}\n  {config_junk2}")
    sys.exit()


def dump_tree(start_path="."):
    """
    Return a string of the directory tree with permissions (symbolic + octal) and size.
    """
    lines = []

    def _walk(dir_path, prefix=""):
        try:
            entries = sorted(os.scandir(dir_path), key=lambda e: (not e.is_dir(), e.name.lower()))
        except PermissionError:
            lines.append(f"{prefix}[Permission Denied]")
            return

        if not entries:
            return

        max_name_len = max(len(entry.name) for entry in entries)

        for i, entry in enumerate(entries):
            is_last = (i == len(entries) - 1)
            # connector = "└── " if is_last else "├── "     # Avoid utf-8 conflict
            connector = "`-- " if is_last else "|-- "
            next_prefix = prefix + ("    " if is_last else "|   ")

            try:
                st = entry.stat(follow_symlinks=False)
                perm_symbolic = stat.filemode(st.st_mode)
                perm_octal = oct(st.st_mode & 0o777)
                size = st.st_size
            except Exception:
                perm_symbolic = "??????????"
                perm_octal = "???"
                size = 0

            pad_len = 30 - len(prefix + connector + entry.name)     # weak.  fails on deeper paths
            padded_name = entry.name + ' '*pad_len
            lines.append(f"{prefix}{connector}{padded_name}[{perm_symbolic}] {perm_octal:<5} {size:>7} bytes")

            if entry.is_dir(follow_symlinks=False):
                _walk(entry.path, next_prefix)

    lines.append(f"Contents of {os.path.abspath(start_path)}")
    _walk(start_path)
    return "\n".join(lines)

logging.info (core.tool)


#===============================================================================================

# *****  Deploy a directory test cases
tnum = '1'
if args.test == '0'  or  args.test in '1 2 3':      # tnum 1 sets base env for tnums 2 & 3
    rmtree(core.tool.user_data_dir)
    dotest(tnum, "Deploy directory tree", "None (success)", [
        { "source": "test_dir",             "target_dir": "DATA_DIR/",       "file_stat": 0o601, "dir_stat": 0o701},
        ])
    logging.info(f"\n------------------------------------\n{dump_tree(core.tool.data_dir)}")

tnum = '2'
if args.test == '0'  or  args.test == tnum:
    Path(core.tool.data_dir / 'test_dir/x2').unlink()
    rmtree(core.tool.data_dir / 'test_dir/subdir')
    dotest(tnum, "Deploy directory tree, overwrite=False", "None (success) with <Copytree skipped.>", [
        { "source": "test_dir",             "target_dir": "DATA_DIR/",       "file_stat": 0o602, "dir_stat": 0o702},
        ])
    logging.info(f"\n------------------------------------\n{dump_tree(core.tool.data_dir)}")

tnum = '3'
if args.test == '0'  or  args.test == tnum:
    Path(core.tool.data_dir / 'test_dir/x2').unlink()
    rmtree(core.tool.data_dir / 'test_dir/subdir')
    # rmtree (Path(core.tool.data_dir / 'test_dir/subdir/emptydir'))
    dotest(tnum, "Deploy directory tree, overwrite=True", "None (success)", [
        { "source": "test_dir",             "target_dir": "DATA_DIR/",       "file_stat": 0o603, "dir_stat": 0o703},
        ], overwrite=True)
    logging.info(f"\n------------------------------------\n{dump_tree(core.tool.data_dir)}")

if args.test == '0'  or  args.test in '1 2 3':      # Cleanup for tests 1, 2, 3
    rmtree(core.tool.data_dir)


# **** Missing source file handling
tnum = '4a'
if args.test == '0'  or  args.test == tnum:
    dotest(tnum, "Try copy non-existing source file", "FileNotFoundError: Can't deploy <no_such_file>.  Item not found.", [
        { "source": "testfile.txt",         "target_dir": "DATA_DIR/xyz",          "file_stat": 0o601, "dir_stat": 0o701},
        { "source": "no_such_file",         "target_dir": "DATA_DIR",              "file_stat": 0o602, "dir_stat": 0o702},
        { "source": "testfile.txt",         "target_dir": "DATA_DIR",              "file_stat": 0o603, "dir_stat": 0o703},
        ])
    logging.info(f"\n------------------------------------\n{dump_tree(core.tool.data_dir)}")
    rmtree(core.tool.data_dir)

tnum = '4b'
if args.test == '0'  or  args.test == tnum:
    dotest(tnum, "Try copy non-existing source file", "None (success) with Can't deploy <no_such_file>.  Item not found and missing_ok=True.  Skipping.", [
        { "source": "testfile.txt",         "target_dir": "DATA_DIR/xyz",          "file_stat": 0o601, "dir_stat": 0o701},
        { "source": "no_such_file",         "target_dir": "DATA_DIR",              "file_stat": 0o602, "dir_stat": 0o702},
        { "source": "testfile.txt",         "target_dir": "DATA_DIR",              "file_stat": 0o603, "dir_stat": 0o703},
        ], missing_ok=True)
    logging.info(f"\n------------------------------------\n{dump_tree(core.tool.data_dir)}")
    rmtree(core.tool.data_dir)


# **** target_dir errors
tnum = '5a'
if args.test == '0'  or  args.test == tnum:
    (testpath / 'IsAFile').touch()
    dotest(tnum, "target_dir exists as a file", "NotADirectoryError: [Errno 20] Not a directory: '/tmp/cjnfuncs_testdeployfiles/IsAFile/testfile.txt'", [
        { "source": "testfile.txt",         "target_dir": testpath,                 "file_stat": 0o601, "dir_stat": 0o701},
        { "source": "testfile.txt",         "target_dir": testpath,                 "file_stat": 0o602, "dir_stat": 0o702},
        { "source": "testfile.txt",         "target_dir": testpath / 'IsAFile',     "file_stat": 0o603, "dir_stat": 0o703},
        ])
    logging.info(f"\n------------------------------------\n{dump_tree(testpath)}")
    rmtree(testpath)

tnum = '5b'
if args.test == '0'  or  args.test == tnum:
    dotest(tnum, "Destination is an existing file with overwrite but no permission", "PermissionError: [Errno 13] Permission denied: '/tmp/cjnfuncs_testdeployfiles/testfile.txt'", [
        { "source": "testfile.txt",         "target_dir": testpath,                 "file_stat": 0o000, "dir_stat": 0o701},
        { "source": "testfile.txt",         "target_dir": testpath,                 "file_stat": 0o602, "dir_stat": 0o702},
        ], overwrite=True)
    logging.info(f"\n------------------------------------\n{dump_tree(testpath)}")
    rmtree(testpath)


# **** Full deploy demo
tnum = '6'
if args.test == '0'  or  args.test == tnum:

    dotest(tnum, "Deploy to various directories", "None (success)", [
        { "source": CONFIG_FILE,            "target_dir": "CONFIG_DIR",             "file_stat": 0o601, "dir_stat": 0o701},
        { "source": CONFIG_FILE,            "target_dir": "CONFIG_DIR/subdir",      "file_stat": 0o602, "dir_stat": 0o702},
        { "source": "testfile.txt",         "target_dir": config_junk2,             "file_stat": 0o603, "dir_stat": 0o703},
        { "source": "testfile.txt",         "target_dir": "CONFIG_DIR/dirxxx"},         # use default file_stat, dir_stat
        { "source": "test_dir",             "target_dir": "DATA_DIR/mydirs",        "file_stat": 0o604, "dir_stat": 0o704},
        { "source": "test_dir",             "target_dir": "DATA_DIR/mydirs/defaults"},  # use default file_stat, dir_stat
        { "source": "test_dir/subdir/x4",   "target_dir": "CONFIG_DIR/mydirs",      "file_stat": 0o605, "dir_stat": 0o705},
        ])

    logging.info(f"\n------------------------------------\n{dump_tree(core.tool.config_dir)}")
    logging.info(f"\n------------------------------------\n{dump_tree(config_junk2)}")
    logging.info(f"\n------------------------------------\n{dump_tree(core.tool.data_dir)}")

    rmtree(core.tool.config_dir)
    rmtree(config_junk2)
    rmtree(core.tool.data_dir)


# **** Deploy subdirs
tnum = '7a'
if args.test == '0'  or  args.test == tnum:
    dotest(tnum, "Deploy empty directory", "None (success)", [
        { "source": "emptydir2",            "target_dir": "CONFIG_DIR",                 "file_stat": 0o601, "dir_stat": 0o701},
        ])
    logging.info(f"\n------------------------------------\n{dump_tree(core.tool.config_dir)}")
    rmtree(core.tool.config_dir)

tnum = '7b'
if args.test == '0'  or  args.test == tnum:
    dotest(tnum, "Deploy subdirectory to top level", "None (success)", [
        { "source": "test_dir/subdir",      "target_dir": "CONFIG_DIR",                 "file_stat": 0o602, "dir_stat": 0o702},
        ])
    logging.info(f"\n------------------------------------\n{dump_tree(core.tool.config_dir)}")
    rmtree(core.tool.config_dir)

tnum = '7c'
if args.test == '0'  or  args.test == tnum:
    dotest(tnum, "Deploy subdirectory to subdirectory", "None (success)", [
        { "source": "test_dir/subdir",      "target_dir": "CONFIG_DIR/mydir",           "file_stat": 0o603, "dir_stat": 0o703},
        ])
    logging.info(f"\n------------------------------------\n{dump_tree(core.tool.config_dir)}")
    rmtree(core.tool.config_dir)

tnum = '8a'
if args.test == '0'  or  args.test == tnum:
    dotest(tnum, "Demo dir_stat rules - overwrite=False", "None (success)", [
        { "source": "test_dir/subdir",      "target_dir": 'CONFIG_DIR/dir1/dir2',       "file_stat": 0o601, "dir_stat": 0o701},
        { "source": "x0",                   "target_dir": 'CONFIG_DIR/dir1/dir2/subdir',"file_stat": 0o602, "dir_stat": 0o702},
        { "source": "x0",                   "target_dir": 'CONFIG_DIR/dir1',            "file_stat": 0o603, "dir_stat": 0o703},
        { "source": "test_dir/emptydir",    "target_dir": "CONFIG_DIR/dir1",            "file_stat": 0o604, "dir_stat": 0o704},
        ])
    logging.info(f"\n------------------------------------\n{dump_tree(core.tool.config_dir)}")
    rmtree(core.tool.config_dir)

tnum = '8b'
if args.test == '0'  or  args.test == tnum:
    dotest(tnum, "Demo dir_stat rules - overwrite=True", "None (success)", [
        { "source": "test_dir/subdir",      "target_dir": 'CONFIG_DIR/dir1/dir2',       "file_stat": 0o601, "dir_stat": 0o701},
        { "source": "x0",                   "target_dir": 'CONFIG_DIR/dir1/dir2/subdir',"file_stat": 0o602, "dir_stat": 0o702},
        { "source": "x0",                   "target_dir": 'CONFIG_DIR/dir1',            "file_stat": 0o603, "dir_stat": 0o703},
        { "source": "test_dir/emptydir",    "target_dir": "CONFIG_DIR/dir1",            "file_stat": 0o604, "dir_stat": 0o704},
        ], overwrite=True)
    logging.info(f"\n------------------------------------\n{dump_tree(core.tool.config_dir)}")
    rmtree(core.tool.config_dir)


# Retain site mode across runs if previously set
if core.tool.env_defined == 'site':
    Path(core.tool.site_config_dir).mkdir(exist_ok=True)



if args.test == '50':   # Development

    rmtree(core.tool.config_dir)
    dotest(tnum, "How dir_stat is applied, modified", "None (success)", [
        { "source": "test_dir/subdir/",      "target_dir": 'USER_CONFIG_DIR/..',       "file_stat": 0o611, "dir_stat": 0o711},
        { "source": "x0",      "target_dir": 'USER_CONFIG_DIR',       "file_stat": 0o613, "dir_stat": 0o713},
        # { "source": "test_dir/subdir",      "target_dir": 'USER_CONFIG_DIR/dir1/',       "file_stat": 0o612, "dir_stat": 0o712},

        # { "source": "test_dir/x1", "target_dir": 'USER_CONFIG_DIR/dir1/dir2',  "file_stat": 0o612, "dir_stat": 0o712},
        # { "source": "x0",          "target_dir": 'USER_CONFIG_DIR/dir1',       "file_stat": 0o614, "dir_stat": 0o714},
        # {"source": "test_dir/x1",  "target_dir": "USER_CONFIG_DIR/subdir"},
        # {"source": "test_dir/emptydir",  "target_dir": "USER_CONFIG_DIR/dir1",  "file_stat": 0o615, "dir_stat": 0o715},
        # { "source": "test_dir/subdir",      "target_dir": testpath,                 "file_stat": 0o612, "dir_stat": 0o712},
        ], overwrite=True)
    logging.info(f"\n------------------------------------\n{dump_tree(core.tool.config_dir)}")
    # rmtree(testpath)
