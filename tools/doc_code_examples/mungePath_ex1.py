#!/usr/bin/env python3
# ***** mungePath_ex1.py *****

from cjnfuncs.core      import set_toolname
from cjnfuncs.mungePath import mungePath
import cjnfuncs.core as core

tool = set_toolname("mungePath_ex1")
my_mP = mungePath ("mysubdir/file.txt", core.tool.data_dir)        # **** NOTE 1
print (my_mP)                                                      # **** NOTE 2

mungePath (my_mP.parent, mkdir=True)                               # **** NOTE 3

if not my_mP.exists:                                               # **** NOTE 4
    print (f"Making the file <{my_mP.name}>")
    with my_mP.full_path.open('w') as outfile:                     # **** NOTE 5
        outfile.write("Hello")
    my_mP.refresh_stats()                                          # **** NOTE 6
    print (my_mP)
else:
    print ("File content: ", my_mP.full_path.read_text())          # **** NOTE 5
    print ("Removing the file")
    my_mP.full_path.unlink()                                       # **** NOTE 5
    print (my_mP.refresh_stats())                                  # **** NOTE 7
