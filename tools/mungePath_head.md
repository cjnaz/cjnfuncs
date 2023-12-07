# mungePath - A clean interface for dealing with filesystem paths

Skip to [API documentation](#links)

The mungePath() class adds value in these important ways:
- Hides the distinction between pathlib's purePath and Path classes. mungePath provides interfaces to script code that just work.
- Allows platform base paths and script-specific files and directories to be entered separately, and then appropriately merges them.  The split-handling greatly cleans up script code.
- Absolute and relative paths are supported, along with expansion of user (~user/) and environment vars ($HOME/).


## Example
Given:
```
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
```

What gets printed:
```
$ ./mungePath_ex1.py 
.full_path    :  /home/cjn/.local/share/mungePath_ex1/mysubdir/file.txt
.parent       :  /home/cjn/.local/share/mungePath_ex1/mysubdir
.name         :  file.txt
.is_absolute  :  True
.is_relative  :  False
.exists       :  False
.is_dir       :  False
.is_file      :  False

Making the file <file.txt>
.full_path    :  /home/cjn/.local/share/mungePath_ex1/mysubdir/file.txt
.parent       :  /home/cjn/.local/share/mungePath_ex1/mysubdir
.name         :  file.txt
.is_absolute  :  True
.is_relative  :  False
.exists       :  True
.is_dir       :  False
.is_file      :  True


$ ./mungePath_ex1.py 
.full_path    :  /home/cjn/.local/share/mungePath_ex1/mysubdir/file.txt
.parent       :  /home/cjn/.local/share/mungePath_ex1/mysubdir
.name         :  file.txt
.is_absolute  :  True
.is_relative  :  False
.exists       :  True
.is_dir       :  False
.is_file      :  True

File content:  Hello
Removing the file
.full_path    :  /home/cjn/.local/share/mungePath_ex1/mysubdir/file.txt
.parent       :  /home/cjn/.local/share/mungePath_ex1/mysubdir
.name         :  file.txt
.is_absolute  :  True
.is_relative  :  False
.exists       :  False
.is_dir       :  False
.is_file      :  False

```

Notables:
1. The `myfile` mungePath instance gets created. 
2. Printing the instance shows all its stats.  `myfile.exists` indicates whether the file exists _at the time the instance was created_.
3. The `myfile.parent` directory is created, if it doesn't yet exist.
4. A mungePath instance holds a set of status booleans (not methods) that are handy for coding.
5. `.full_path` and `.parent` are pathlib.Path types, so all of the Path methods may be used.
6. If the mungePath instance booleans may be stale, a call to `.refresh_stats()` is needed.
7. `.refresh_stats()` returns the instance handle, so it may be called in-line with boolean checks, etc.

## check_path_exists() eliminates hangs

Executing pathlib.Path(/path/not/currently/available/myfile) may result in a many second hang.  `check_path_exists()` is a simple function that wraps Path.exists() with timeout enforcement.  This function is used within the mungePath class, and is exposed for use by script code.
