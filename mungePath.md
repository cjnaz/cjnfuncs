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

if __name__ == '__main__':                                          # **** NOTE 8   
    tool = set_toolname("mungePath_ex1")
                                                                    # **** NOTE 1
    my_mp = mungePath ("mysubdir/file.txt", core.tool.data_dir, set_attributes=True)
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

4. A mungePath instance holds a set of status booleans (attributes, not methods) that are 
handy for coding.

5. `.full_path` and `.parent` are pathlib.Path types, so all of the Path methods may be used.

6. If the mungePath `.exists`, `.is_dir` and `.is_file` instance booleans are stale, a call to `.refresh_stats()` is needed.

7. `.refresh_stats()` returns the instance handle, so it may be called in-line with boolean checks, etc.

8. Using `set_attributes=True` on Windows slows down execution dramatically due to three underlying `run_with_timeout()` calls, which invoke multiprocess spawns on Windows.  See note 1 for alternatives.  On Linux this code runs quickly.
<br>

## check_path_exists() eliminates hangs

Executing `pathlib.Path(/network_path_not_currently_available/myfile).exists()` may result in a many second hang.  `check_path_exists()` is a simple function that wraps `Path.exists()` with timeout enforcement using `run_with_timeout()`.  Note that it can take a couple seconds to run `check_path_exists()` on Windows (fast on Linux), but it wont hang.


<a id="links"></a>
         
<br>

---

# Links to classes, methods, and functions

- [mungepath](#mungepath)
- [refresh_stats](#refresh_stats)
- [check_path_exists](#check_path_exists)



<br/>

<a id="mungepath"></a>

---

# Class mungePath (in_path='', base_path='', mkdir=False, set_attributes=False, timeout=1.0, ntries=1) - A clean interface for dealing with filesystem paths

`mungePath()` is based on pathlib, producing Path type attributes and status booleans which may be used with all
pathlib.Path methods, such as .open().  `mungePath()` accepts paths in two parts - the tool script specific
portion `in_path` and a `base_path` (prepended if `in_path` is relative), and returns an instance that may 
be cleanly used in the tool script code.
User (`~user/`) and environment vars (`$HOME/`) are supported and expanded.


### Args
`in_path` (Path or str, default '')
- An absolute or relative path to a file or directory, such as `mydir/myfile.txt`
- If `in_path` is an absolute path then the `base_path` is disregarded.
- If `in_path` starts with `./` then the absolute path to the current working directory (cwd) is prepended 
to `in_path`, and the `base_path` is disregarded.  See Special handling note, below.

`base_path` (Path or str, default '')
- An absolute or relative path to a directory, such as `~/.config/mytool`
- `base_path` is prepended to `in_path` if `in_path` is a relative path
- `base_path = ''` (the default) results in a relative path based on the shell current working directory (cwd)
- `base_path = '.'` results in an absolute path based on the shell cwd
- `base_path = core.tool.main_dir` results in an absolute path based on the tool script directory

`mkdir` (bool, default False)
- Force-make a full directory path.  `base_path` / `in_path` is understood to be to a directory.

`set_attributes` (bool, default False) - _See the first note in Behaviors and rules, below_
- If True then `refresh_stats()` is called, setting `.exists`, `.is_file`, `.is_dir` to valid values (or False on timeout).
- If False then those attributes are set to `None`, indicating not initialized.
- These other attributes are always set: `.full_path`, `.parent`, `.name`, `.is_absolute`, and `.is_relative`, as the do not depend on file system access.

`timeout` (int or float, default 1.0 second)
- If `set_attributes=True` then `refresh_stats()` is called using this timeout value for each of the three `run_with_timeout()` calls.

`ntries` (int, default 1)
If `set_attributes=True` then `refresh_stats()` is called using this ntries value for each of the three `run_with_timeout()` calls.


### Returns
- Handle to `mungePath()` instance


### Instance attributes

Attribute | Type | Description
-- | -- | --
`.full_path`     | Path     |   The full expanduser/expandvars path to a file or directory (may not exist)
`.parent`        | Path     |   The directory above the .full_path
`.name`          | str      |   Just the name.suffix of the .full_path
`.is_absolute`   | Boolean  |   True if the .full_path starts from the filesystem root (isn't a relative path) 
`.is_relative`   | Boolean  |   Not .is_absolute
`.exists`        | Boolean  |   True if the .full_path item (file or dir) actually exists **
`.is_file`       | Boolean  |   True if the .full_path item exists and is a file **
`.is_dir`        | Boolean  |   True if the .full_path item exists and is a directory **

** These attributes are set to None, by default.  See the `set_attributes` arg, above, and the first note in Behaviors and rules, below.


### Behaviors and rules
- NOTE: `set_attributes` was added in cjnfuncs version 3.0 and defaults to False, effectively disabling the setting of
`.exists`, `.is_file` and `.is_dir` attributes. When pointing to a remote filesystem that is flaky, evaluating these attributes
can lead to long hang times. If `set_attributes=True` then `refresh_stats()` is called which attempts to populates `.exists`, `.is_file`, 
and `.is_dir` attributes with real values.  On timeout each attribute is set to False.  refresh_stats() uses run_with_timeout() with The default timeout of 1 second is used.
, or will time out with approximately a total 3 second delay.  If these attributes are not needed
for a given mungePath instance then don't set `set_attributes=True`.  The recommended alternatives are to call `check_path_exists()` 
(which uses `run_with_timeout()` with `rwt_ntries=1` and `rwt_timeout=1.0`), or to implement `run_with_timeout()` calls in your code. 

- If `in_path` is a relative path (eg, `mydir/myfile.txt`) portion then the `base_path` is prepended.  
- If both `in_path` and `base_path` are relative then the combined path will also be relative, usually to
the shell cwd.
- If `in_path` is an absolute path (eg, `/tmp/mydir/myfile.txt`) then the `base_path` is disregarded.
- **Special handling for `in_path` starting with `./`:**  Normally, paths starting with `.` are relative paths.
mungePath interprets `in_path` starting with `./` as an absolute path reference to the shell current working 
directory (cwd).
Often in a tool script a user path input is passed to the `in_path` arg.  Using the `./` prefix, a file in 
the shell cwd may be
referenced, eg `./myfile`.  _Covering the cases, assuming the shell cwd is `/home/me`:_

    in_path | base_path | .full_path resolves to
    -- | -- | --
    myfile          | /tmp  | /tmp/myfile
    ./myfile        | /tmp  | /home/me/myfile
    ../myfile       | /tmp  | /tmp/../myfile
    ./../myfile     | /tmp  | /home/me/../myfile
    xyz/myfile      | /tmp  | /tmp/xyz/myfile
    ./xyz/myfile    | /tmp  | /home/me/xyz/myfile

- `in_path` and `base_path` may be type str(), Path(), or PurePath().
- Symlinks are followed (not resolved).
- User and environment vars are expanded, eg `~/.config` >> `/home/me/.config` (`C:\\Users\\me` on Windows), as does `$HOME/.config`. 
Environment var `$HOME` on Linux is equivalent to `%HOMEDRIVE%%HOMEPATH%` on Windows.  mungePath does not
make the substitution since `$HOME` is just one of many possible environment vars.
- The `.parent` is the directory containing (above) the `.full_path`.  If the object `.is_file` then `.parent` is the
directory containing the file.  If the object `.is_dir` then the `.full_path` includes the end-point directory, and 
`.parent` is the directory above the end-point directory.
- When using `mkdir=True` the combined `base_path` / `in_path` is understood to be a directory path (not
to a file), and that directory if possible. (Uses `pathlib.Path.mkdir()`).  A FileExistsError 
is raised if you attempt to mkdir on top of an existing file.
- See [GitHub repo](https://github.com/cjnaz/cjnfuncs) tests/demo-mungePath.py for numerous application examples.
        
<br/>

<a id="refresh_stats"></a>

---

# refresh_stats (timeout=1.0, ntries=1) - Update the instance .exists, .is_dir, and .is_file booleans attributes

***mungePath() class member function***

The instance attributes `.exists`, `.is_dir`, and `.is_file` may be set 
at the time the mungePath instance is created by setting `set_attributes=True` (the default is False). 
These attributes are not updated automatically as changes happen on the filesystem. 
Call `refresh_stats()` as needed, or directly access the pathlib methods (or access through
`run_with_timeout()`), eg `my_mungepath_inst.full_path.exists()`.  Also see `check_path_exists()`.

NOTE:  `refresh_stats()` utilizes `run_with_timeout()` for each of the three attribute settings.
refresh_stat's default timeout=1 second and ntries=1 can result in up to a 3 second _hang_ if there 
are access issues.


### Args
`timeout` (int or float, default 1.0 second)
- The timeout value passed to each call to `run_with_timeout()`

`ntries` (int, default 1)
- Number of tries value passed to each call to `run_with_timeout()`


### Returns
- The instance handle is returned so that refresh_stats() may be used in-line.
- Sets each attribute to valid True/False value if possible, else sets the attribute to False on timeout error.
- Sets each attribute to False on any exception.
        
<br/>

<a id="check_path_exists"></a>

---

# check_path_exists (inpath, timeout=1.0, ntries=1) - With enforced timeout (no hang)

pathlib.Path.exists() tends to hang for an extended time when there are network access issues.
check_path_exists() wraps `pathlib.Path.exists()` with a call to run_with_timeout().


### Args
`inpath` (Path or str)
- Path to a file or directory

`timeout` (int or float, default 1.0 second)
- timeout value used in `run_with_timeout()` call

`ntries` (int, default 1)
- Number of tries value passed to `run_with_timeout()`


### Returns
- True if the path exists
- False if the path does not exist or the timeout is reached (or any other exception)
    