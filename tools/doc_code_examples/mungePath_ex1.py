#!/usr/bin/env python3
# ***** mungePath_ex1.py *****

from cjnfuncs.core      import set_toolname
from cjnfuncs.mungePath import mungePath
import cjnfuncs.core as core

tool = set_toolname("mungePath_ex1")

my_mp = mungePath ("mysubdir/file.txt", core.tool.data_dir, set_attributes=True)    # **** NOTE 1
print (my_mp)                                                   # **** NOTE 2

mungePath (my_mp.parent, mkdir=True)                            # **** NOTE 3

if not my_mp.exists:                                            # **** NOTE 4, NOTE 1
    print (f"Making the file <{my_mp.name}>")
    with my_mp.full_path.open('w') as outfile:                  # **** NOTE 5
        outfile.write("Hello")
    my_mp.refresh_stats()                                       # **** NOTE 6
    print (my_mp)
else:
    print ("File content: ", my_mp.full_path.read_text())       # **** NOTE 5
    print ("Removing the file")
    my_mp.full_path.unlink()                                    # **** NOTE 5
    print (my_mp.refresh_stats())                               # **** NOTE 7
