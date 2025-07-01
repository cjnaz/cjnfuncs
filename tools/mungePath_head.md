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
```

What gets printed:
```
$ ./mungePath_ex1.py        # First run
.full_path    :  /home/me/.local/share/mungePath_ex1/mysubdir/file.txt
.parent       :  /home/me/.local/share/mungePath_ex1/mysubdir
.name         :  file.txt
.is_absolute  :  True
.is_relative  :  False
.exists       :  False
.is_dir       :  False
.is_file      :  False

Making the file <file.txt>
.full_path    :  /home/me/.local/share/mungePath_ex1/mysubdir/file.txt
.parent       :  /home/me/.local/share/mungePath_ex1/mysubdir
.name         :  file.txt
.is_absolute  :  True
.is_relative  :  False
.exists       :  True
.is_dir       :  False
.is_file      :  True


$ ./mungePath_ex1.py        # Second run
.full_path    :  /home/me/.local/share/mungePath_ex1/mysubdir/file.txt
.parent       :  /home/me/.local/share/mungePath_ex1/mysubdir
.name         :  file.txt
.is_absolute  :  True
.is_relative  :  False
.exists       :  True
.is_dir       :  False
.is_file      :  True

File content:  Hello
Removing the file
.full_path    :  /home/me/.local/share/mungePath_ex1/mysubdir/file.txt
.parent       :  /home/me/.local/share/mungePath_ex1/mysubdir
.name         :  file.txt
.is_absolute  :  True
.is_relative  :  False
.exists       :  False
.is_dir       :  False
.is_file      :  False

```

Notables:
1. The `my_mp` mungePath instance gets created. **NOTE:** Starting with cjnfuncs 3.0 the `.exists`, `.is_dir` and `.is_file` attributes are only set if `set_attributes=True` is included, else these attributes are set to `None`.  ***Alternatives:***
   - _Recommended:_ Call `check_path_exists(my_mp.full_path)`, which supports enforced timeout and retries, and returns `True` or `False`.
   - Call `my_mp.refresh_stats()` before accessing `my_mp.exists`, but `refresh_status()` updates all three attributes, with possible 3x timeouts, while the code only needs `.exists`.
   - Access the pathlib method directly: `my_mp.full_path.exists()`, but this can hang.
2. Printing the instance shows all its stats.  `my_mp.exists` indicates whether the file exists _at the time the instance was created_.
3. The `my_mp.parent` directory is created, if it doesn't yet exist.
4. A mungePath instance holds a set of status booleans (attributes, not methods) that are handy for coding.
5. `.full_path` and `.parent` are pathlib.Path types, so all of the Path methods may be used.
6. If the mungePath `.exists`, `.is_dir` and `.is_file` instance booleans are stale, a call to `.refresh_stats()` is needed.
7. `.refresh_stats()` returns the instance handle, so it may be called in-line with boolean checks, etc.

<br>

## check_path_exists() eliminates hangs

Executing `pathlib.Path(/network_path_not_currently_available/myfile).exists()` may result in a many second hang.  `check_path_exists()` is a simple function that wraps `Path.exists()` with timeout enforcement using `run_with_timeout()`.  
