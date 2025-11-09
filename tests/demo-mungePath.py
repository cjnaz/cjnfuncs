#!/usr/bin/env python3
"""Demo/test for mungePath

Produce / compare to golden results:
    ./demo-mungePath.py | diff demo-mungePath-golden-linux.txt -
  or
    demo-mungePath.py > tempfile.txt (On Windows, and then compare)

        No differences expected

    ./demo-mungePath.py --cleanup

Note:  This test takes about 1s to run on Linux, but > 1m on Windows due to many spawned processes.
"""
#==========================================================
#
#  Chris Nelson, 2025
#
#==========================================================

__version__ = "2.0"

import shutil
import argparse
import os
import sys
import re
import logging
import tempfile
from pathlib import Path, PurePath

from cjnfuncs.core      import set_toolname, set_logging_level, setuplogging
from cjnfuncs.mungePath import mungePath
import cjnfuncs.core as core

TOOLNAME = "demo-mungePath"

set_toolname(TOOLNAME)
test_dir = Path(tempfile.gettempdir()) / TOOLNAME
test_dir.mkdir(exist_ok=True)
setuplogging(ConsoleLogFormat="{module:>22}.{funcName:20} {levelname:>8}:  {message}")

parser = argparse.ArgumentParser(description=__doc__ + __version__, formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-t', '--test', default='0',
                    help="Test number to run (default 0).  0 runs all tests")
parser.add_argument('--cleanup', action='store_true',
                    help="Remove test dirs/files.")

args = parser.parse_args()

if args.cleanup:
    try:
        newdir = mungePath('newdir', '.').full_path
        print (f"Removing   {newdir}")
        shutil.rmtree(newdir)
    except:
        pass

    try:
        xyzdir = mungePath('xyz', '.').full_path
        print (f"Removing   {xyzdir}")
        shutil.rmtree(xyzdir)
    except:
        pass

    try:
        print (f"Removing   {test_dir}")
        shutil.rmtree(test_dir)
    except:
        pass
    sys.exit(0)


# --------------------------------------------------------------------

def dotest (desc, expect, *args, **kwargs):
    logging.warning (f"\n\n==============================================================================================\n" +
                     f"Test {tnum} - {desc}\n" +
                     f"  GIVEN:      {args}, {kwargs}\n" +
                     f"  EXPECT:     {expect}")
    try:
        result = mungePath(*args, timeout=2.0, **kwargs)    # timeout set to 2s for Windows stability
        print (result)
        return result
    except Exception as e:
        logging.error (f"\n  RAISED:     {type(e).__name__}: {e}")
        # logging.exception (f"\n  RAISED:     {type(e).__name__}: {e}")        # for debug
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

def touch (file_path):
    file_path.open('w').close()

def remove_file (file_path):
    os.remove(file_path)

def remove_tree (path):
    shutil.rmtree(path)


# --------------------------------------------------------------------

if __name__ == '__main__':
    set_logging_level(10)
    logging.getLogger('rwt').setLevel(logging.WARNING)

    #-------------------------------------------------------------------------
    print ("\n\n***** File paths relative to a base path")

    if check_tnum('1'):
        dotest ("'.' base_path", "Returns absolute path from shell cwd",
                "xyz/file.txt", ".",                        set_attributes=True)

    if check_tnum('2'):
        dotest ("'' base_path", "Returns relative path from shell cwd",
                "", "",                                     set_attributes=True)

    if check_tnum('3'):
        dotest ("No base_path", "Returns relative path from shell cwd - file in same dir",
                "file.txt",                                 set_attributes=True)

    if check_tnum('4'):
        dotest ("No base_path", "Returns relative path from shell cwd - file in dir below",
                "xyz/file.txt",                             set_attributes=True)

    if check_tnum('5'):
        dotest ("No base_path", "Returns relative path from shell cwd - file in dir above",
                "../file.txt",                              set_attributes=True)

    if check_tnum('5a'):
        dotest ("No base_path, mkdir at shell cdw", "Returns relative path to 'newdir' from shell cwd",
                "newdir",                                   set_attributes=True, mkdir=True)

    if check_tnum('6'):
        dotest ("'.' base_path", "Returns absolute full path to shell cwd",
                "", ".",                                    set_attributes=True)

    if check_tnum('7'):
        dotest ("Expand user", "Returns absolute full path to user home dir",
                "", "~",                                    set_attributes=True)

    if sys.platform.startswith("win"):
        if check_tnum('8a'):
            dotest ("Expand environment var", "Returns absolute full path to user home dir",
                    "", "%HOMEDRIVE%%HOMEPATH%",            set_attributes=True)
    else:       # Linux
        if check_tnum('8b'):
            dotest ("Expand environment var", "Returns absolute full path to user home dir",
                    "", "$HOME",                            set_attributes=True)

    if check_tnum('9'):
        dotest ("Expand user in in_path", "Absolute in_path overrides the base_path (base_path not used)",
                "~/xyz/file.txt", ".",                      set_attributes=True)


    #-------------------------------------------------------------------------
    print ("\n\n***** Using the base_path")

    if mungePath("", test_dir).full_path.exists():
        print (f"<{test_dir}> exists, removed.")
        remove_tree (test_dir)

    if check_tnum('11a'):
        dotest (f"Make work space", f"Dir <{test_dir}> created",
                "", test_dir,                               set_attributes=True, mkdir=True)
        touch (mungePath("file.txt", test_dir).full_path)
    else:
        mungePath(test_dir, mkdir=True)                     # Make env for later tests is test 11a is not run
        touch (mungePath("file.txt", test_dir).full_path)

    if check_tnum('11b'):
        dotest (f"Check status of <{test_dir}/file.txt>", f"File exists, absolute path",
                "file.txt", test_dir,                       set_attributes=True)

    if check_tnum('14'):
        dotest (f"Path up then down", f"File exists, absolute path",
                f"../{TOOLNAME}/file.txt", test_dir,        set_attributes=True)

    if check_tnum('15'):
        dotest (f"file.txt referenced thru non-existent subdir", f"Linux: file.txt does NOT exist since referenced thru non-existent subdir.  Exists on Windows.",
                "subdir/../file.txt", test_dir,             set_attributes=True)

    if check_tnum('16'):
        dotest (f"Make subdir (trailing '/' doesn't matter)", f"subdir exists",
                "subdir/", test_dir,                        set_attributes=True, mkdir=True)
    else:
        mungePath("subdir/", test_dir, mkdir=True)      # Make env for later tests if test 16 is not run

    if check_tnum('17'):
        dotest (f"Now file.txt exists - referenced thru subdir", f"file.txt exists, absolute path",
                "subdir/../file.txt", test_dir,             set_attributes=True)

    if check_tnum('18'):
        dotest (f"file.txt referenced thru different base_path", f"file.txt exists, absolute path",
                "../file.txt", test_dir / "subdir",         set_attributes=True)


    #-------------------------------------------------------------------------
    print ("\n\n***** str, Path, and PurePath arguments types accepted")

    if check_tnum('19'):
        dotest (f"Accepts str types", f"file.txt exists, absolute path",
                "file.txt", str(test_dir),                  set_attributes=True)

    if check_tnum('20'):
        dotest (f"Accepts Path types", f"file.txt exists, absolute path",
                Path("file.txt"), test_dir,                 set_attributes=True)

    if check_tnum('21'):
        dotest (f"Accepts PurePath types", f"file.txt exists, absolute path",
                PurePath("file.txt"), PurePath(test_dir),   set_attributes=True)


    #-------------------------------------------------------------------------
    # symlinks not supported on Windows
    if sys.platform.startswith("linux"):
        print ("\n\n***** symlinks followed (not resolved)")
        xx = mungePath("file.txt", test_dir)
        xx.full_path.touch()
        os.symlink(xx.full_path, xx.parent / "subdir" / "symlink.txt")
        os.symlink(xx.parent, xx.parent / "symlinkdir")

        if check_tnum('22'):
            dotest (f"symlink file honored", f"file.txt exists, absolute path",
                    "subdir/symlink.txt", test_dir,         set_attributes=True)

        remove_file(xx.full_path)
        if check_tnum('23'):
            dotest (f"symlink target file was removed", f"file.txt does not exist, absolute path",
                    "subdir/symlink.txt", test_dir,         set_attributes=True)

        if check_tnum('24'):
            dotest (f"symlink dir honored", f"symlink dir exists, absolute path",
                    "symlinkdir", test_dir,                 set_attributes=True)


    #-------------------------------------------------------------------------
    print ("\n\n***** mkdir=True makes the full path.  Don't inadvertently include a file part.")

    if check_tnum('25'):
        dotest (f"Happy to make a dir with a file-like name", f"dir named testxxxx.txt exists, absolute path",
                "subdir/testxxxx.txt", test_dir,            set_attributes=True, mkdir=True)


    touch(test_dir / "dummyfile.txt")
    if check_tnum('26'):
        dotest (f"Exception raised due to trying to make a directory on top of an existing file", f"Raise FileExistsError",
                "dummyfile.txt", test_dir,                  set_attributes=True, mkdir=True)


    #-------------------------------------------------------------------------
    print ("\n\n***** Referencing the tool script dir")

    if check_tnum('27'):
        dotest (f"Returns absolute path to script dir", f"Absolute path to script dir, xyz/file.txt does not exist",
                "xyz/file.txt", core.tool.main_dir,         set_attributes=True)


    #-------------------------------------------------------------------------
    print ("\n\n***** Referencing file in shell cwd, overriding base_path")

    if check_tnum('28'):
        dotest (f"Absolute in_path overrides base_path", f"Absolute path to <cwd>/file.txt (does not exist)",
                "./file.txt", test_dir,                     set_attributes=True)

    if check_tnum('29'):
        dotest (f"Absolute in_path overrides base_path", f"Absolute path to <cwd>/../file.txt (does not exist)",
                "./../file.txt", test_dir,                  set_attributes=True)

    if check_tnum('30'):
        dotest (f"Absolute in_path overrides base_path", f"Absolute path to <cwd>/xyz/file.txt (does not exist)",
                "./xyz/file.txt", test_dir,                 set_attributes=True)

    if check_tnum('31'):
        dotest (f"mkdir <cwd>/xyz/wxy", f"Absolute path to dir <cwd>/xyz/wxy (exists)",
                "./xyz/wxy", test_dir,                      set_attributes=True, mkdir=True)


    #-------------------------------------------------------------------------
    print ("\n\n***** Attributes not set")

    if check_tnum('32'):
        dotest (f"Abs path - attributes not set", f"Absolute path to dir <cwd>/nosuchfile, attributes = None",
                'nosuchfile', './')

    if check_tnum('33'):
        dotest (f"Rel path - attributes not set", f"Relative path to dir <cwd>/nosuchfile, attributes = None",
                'nosuchfile', '')

