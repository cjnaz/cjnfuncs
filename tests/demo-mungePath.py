#!/usr/bin/env python3

#==========================================================
#
#  Chris Nelson, 2018-2023
#
#  2.0  220109  Restructured as a formal package
#
# Changes pending
#   
#==========================================================

from cjnfuncs.cjnfuncs import *
import shutil
import os

# import pathlib, __main__

def touch (file_path):
    file_path.open('w').close()
    # io.open(file_path, 'w').close()

def remove_file (file_path):
    os.remove(file_path)

def remove_tree (path):
    shutil.rmtree(path)


def wrapper (in_path="", base_path="", mkdir=False, note=None):
    """
    Operates exactly the same as mungePath, with the additional note field and results dump.
    """
    print()
    if note:
        print ("NOTE: ", note)
    print (f"Given:\n in_path   :  <{in_path}>\n base_path :  <{base_path}>\n mkdir     :  <{mkdir}>")
    xx = mungePath(in_path=in_path, base_path=base_path, mkdir=mkdir)
    print (f"{'full_path'}    :  {xx.full_path}")
    print (f"{'parent'}       :  {xx.parent}")
    print (f"{'dir'}          :  {xx.dir}")
    print (f"{'name'}         :  {xx.name}")
    print (f"{'is_absolute'}  :  {xx.is_absolute}")
    print (f"{'is_relative'}  :  {xx.is_relative}")
    print (f"{'exists'}       :  {xx.exists}")
    print (f"{'is_dir'}       :  {xx.is_dir}")
    print (f"{'is_file'}      :  {xx.is_file}")
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
os.symlink(xx.full_path, xx.dir / "subdir" / "symlink.txt")
os.symlink(xx.dir, xx.dir / "symlinkdir")
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

