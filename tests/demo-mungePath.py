#!/usr/bin/env python3
"""Demo/test for mungePath
"""
#==========================================================
#
#  Chris Nelson, 2023
#
#   NOTE:  This demo file leaves a remnant dir: /tmp/mungepath
#    
#==========================================================

__version__ = "1.1"

import shutil
import os
from cjnfuncs.cjnfuncs import *

def touch (file_path):
    file_path.open('w').close()

def remove_file (file_path):
    os.remove(file_path)

def remove_tree (path):
    shutil.rmtree(path)


def wrapper (in_path="", base_path="", mkdir=False, note=None):
    """
    Operates exactly the same as mungePath, with the additional note field and results stats.
    """
    print()
    if note:
        print ("NOTE: ", note)
    print (f"Given:\n in_path   :  <{in_path}>\n base_path :  <{base_path}>\n mkdir     :  <{mkdir}>")
    xx = mungePath(in_path=in_path, base_path=base_path, mkdir=mkdir)
    print(xx)
    return xx

print ("\n\n***** File paths relative to a base path")
wrapper ("xyz/file.txt", ".",       note="01 - Path specified relative to the calling script directory - Returns absolute results")
wrapper ("", "",                    note="02 - Returns relative '.' (current directory)")
wrapper ("file.txt",                note="03 - No base_path - returns relative to script dir - same dir")
wrapper ("xyz/file.txt",            note="04 - No base_path - returns relative to script dir - below")
wrapper ("../file.txt",             note="05 - No base_path - returns relative to script dir - above")
wrapper ("", ".",                   note="06 - Returns absolute full path to calling script dir")
wrapper ("", "~",                   note="07 - User expanded")
wrapper ("xyz/file.txt", "$HOME",   note="08 - Env vars expanded")
wrapper ("~/xyz/file.txt", ".",     note="09 - User expanded, An absolute in_path overrides the base_path (base_path not used)")

print ("\n\n***** Using the base_path")
if wrapper ("", "/tmp/mungePath",   note="10 - Check existence of the work space tree").exists:
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



print ("\n\n***** README.md mungePath example")
tool = set_toolname("mytool")
myfile = mungePath ("mysubdir/file.txt", tool.data_dir)
mungePath (myfile.parent, mkdir=True)
if not myfile.exists:
    with myfile.full_path.open('w') as outfile:
        file_contents = outfile.write("Hello")
    print (myfile)      # NOTE: Prints stats from before the file creation
    myfile.refresh_stats()
    print (myfile)

remove_tree(tool.data_dir)