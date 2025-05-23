#!/usr/bin/env python3
"""Demo/test for mungePath

Produce / compare to golden results:
    ./demo-mungePath.py | diff demo-mungePath-golden.txt -
"""
#==========================================================
#
#  Chris Nelson, 2024
#
#   NOTE:  This demo file leaves a remnant dir: /tmp/mungepath
#    
#==========================================================

__version__ = "1.3"

import shutil
import os
from pathlib import Path, PurePath

from cjnfuncs.core      import set_toolname, set_logging_level, setuplogging
from cjnfuncs.mungePath import mungePath
import cjnfuncs.core as core

set_toolname("mytool")
setuplogging(ConsoleLogFormat="{asctime} {module:>22}.{funcName:20} {levelname:>8}:  {message}")

def touch (file_path):
    file_path.open('w').close()

def remove_file (file_path):
    os.remove(file_path)

def remove_tree (path):
    shutil.rmtree(path)


def wrapper (in_path="", base_path="", mkdir=False, note=None, set_attributes=True):
    """
    Operates exactly the same as mungePath, with the additional note field and results stats.
    """
    print()
    if note:
        print ("NOTE: ", note)
    print (f"Given:\n in_path   :  <{in_path}>\n base_path :  <{base_path}>\n mkdir     :  <{mkdir}>")
    xx = mungePath(in_path=in_path, base_path=base_path, mkdir=mkdir, set_attributes=set_attributes)
    print(xx)
    return xx

set_logging_level(10)

print ("\n\n***** File paths relative to a base path")
wrapper ("xyz/file.txt", ".",                               note="01 - Returns absolute path to shell cwd")
wrapper ("", "",                                            note="02 - No base_path - Returns relative path from shell cwd")
wrapper ("file.txt",                                        note="03 - No base_path - Returns relative path from shell cwd - same dir")
wrapper ("xyz/file.txt",                                    note="04 - No base_path - Returns relative path from shell cwd - below")
wrapper ("../file.txt",                                     note="05 - No base_path - Returns relative path from shell cwd - above")
wrapper ("newdir", mkdir=True,                              note="05a- No base_path - Make dir at shell cwd, returns relative path")
wrapper ("", ".",                                           note="06 - Returns absolute full path to shell cwd")
wrapper ("", "~",                                           note="07 - User expanded")
wrapper ("xyz/file.txt", "$HOME",                           note="08 - Env vars expanded")
wrapper ("~/xyz/file.txt", ".",                             note="09 - User expanded, Absolute in_path overrides the base_path (base_path not used)")

print ("\n\n***** Using the base_path")
if wrapper ("", "/tmp/mungePath",                           note="10 - Check existence of the work space tree").exists:
    print ("Exists, removed.")
    remove_tree ("/tmp/mungePath")
else:
    print ("Does not exist")
testpath = wrapper ("", "/tmp/mungePath", mkdir=True,
                                                            note="11 - Make a work space, then create /tmp/mungePath/file.txt").full_path
touch (mungePath("file.txt", testpath).full_path)

wrapper ("", testpath,                                      note="12 - /tmp/mungePath exists")
wrapper ("file.txt", testpath,                              note="13 - file.txt exists")
wrapper ("../mungePath/file.txt", testpath,                 note="14 - file.txt exists")
wrapper ("subdir/../file.txt", testpath,                    note="15 - file.txt does NOT exist since referenced thru non-existent subdir")
wrapper ("subdir/", testpath, mkdir=True,                   note="16 - Make subdir (trailing '/' doesn't matter)")
xx = wrapper ("subdir/../file.txt", testpath,               note="17 - Now file.txt exists - referenced thru subdir")
wrapper ("../file.txt", testpath / "subdir",                note="18 - Referenced thru different base_path")

print ("\n\n***** str, Path, and PurePath arguments types accepted")
wrapper ("file.txt", "/tmp/mungePath",                      note="19 - Accepts str types")
wrapper (Path("file.txt"), Path("/tmp/mungePath"),          note="20 - Accepts Path types")
wrapper (PurePath("file.txt"), PurePath("/tmp/mungePath"),  note="21 - Accepts PurePath types")

print ("\n\n***** symlinks followed (not resolved)")
os.symlink(xx.full_path, xx.parent / "subdir" / "symlink.txt")
os.symlink(xx.parent, xx.parent / "symlinkdir")
# NOTE on Win10 symlinks do not appear to be valid - Properties Shortcut of symlinkdir = C:\tmp\mungePath\temp\mungePath)
# however these tests seem to be retuning expected results.

wrapper ("subdir/symlink.txt", testpath,                    note="22 - symlink file honored (symlink created earlier)")
remove_file(xx.full_path)
wrapper ("subdir/symlink.txt", testpath,                    note="23 - symlink target file was removed")
wrapper ("symlinkdir", testpath,                            note="24 - symlink dir honored (symlink created earlier)")

print ("\n\n***** mkdir=True makes the full path.  Don't inadvertently include a file part.")
wrapper ("subdir/testxxxx.txt", testpath, mkdir=True,       note="25 - Happy to make a dir with a file-like name")

touch(testpath / "dummyfile.txt")
try:
    wrapper ("dummyfile.txt", testpath, mkdir=True, 
                                                            note="26 - Exception raised due to trying to make a directory on top of an existing file")
except Exception as e:
    print (f"Exception: {e}")

print ("\n\n***** Referencing the tool script dir")
wrapper ("xyz/file.txt", core.tool.main_dir,                note="27 - Returns absolute path to script dir")

print ("\n\n***** Referencing file in shell cwd, overriding base_path")
wrapper ("./file.txt", '/tmp',                              note="28 - Returns absolute path to <cwd>/file")
wrapper ("./../file.txt", '/tmp',                           note="29 - Returns absolute path to <cwd>/../file")
wrapper ("./xyz/file.txt", '/tmp',                          note="30 - Returns absolute path to <cwd>/xyz/file")

wrapper ("./xyz/wxy", '/tmp',   mkdir=True,                 note="31 - mkdir <cwd>/xyz/wxy")

wrapper ('nosuchfile', './',                                note="32 - abs path - attributes not set", set_attributes=False)
wrapper ('nosuchfile', '',                                  note="33 - rel path - attributes not set", set_attributes=False)
