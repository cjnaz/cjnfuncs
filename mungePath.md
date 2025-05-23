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


$ ./mungePath_ex1.py 
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
1. The `my_mP` mungePath instance gets created. 
2. Printing the instance shows all its stats.  `my_mP.exists` indicates whether the file exists _at the time the instance was created_.
3. The `my_mP.parent` directory is created, if it doesn't yet exist.
4. A mungePath instance holds a set of status booleans (attributes, not methods) that are handy for coding.
5. `.full_path` and `.parent` are pathlib.Path types, so all of the Path methods may be used.
6. If the mungePath instance booleans may be stale, a call to `.refresh_stats()` is needed.
7. `.refresh_stats()` returns the instance handle, so it may be called in-line with boolean checks, etc.

## check_path_exists() eliminates hangs

Executing `pathlib.Path(/network_path_not_currently_available/myfile).exists()` may result in a many second hang.  `check_path_exists()` is a simple function that wraps Path.exists() with timeout enforcement.  This function is used within the mungePath class, and is exposed for use by script code.


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

# Class mungePath (in_path='', base_path='', mkdir=False) - A clean interface for dealing with filesystem paths

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

set_attributes (bool, default True)
- If True, these attributes are set: `.exists`, .is_file`, .is_dir`.
- If False, those attributes are set to `None`.
- These attributes are always set: `.full_path`, `.parent`, `.name`, `.is_absolute`, and `.is_relative`.
- When accessing a remote file system and there are access issues (eg, the remote host is down) then setting `.exists`, `.is_file`, 
and `.is_dir` can incur 1 second timeout delays each.  If these attributes are not needed by the user script then
setting set_attributes = False can lead to faster and more stable code. Alternately, any pathlib method or attribute may be 
directly accessed, or accessed using `run_with_timeout()`, eg `my_mungepath_inst.full_path.exists()`.

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
`.exists`        | Boolean  |   True if the .full_path item (file or dir) actually exists
`.is_file`       | Boolean  |   True if the .full_path item exists and is a file
`.is_dir`        | Boolean  |   True if the .full_path item exists and is a directory


### Behaviors and rules
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
- User and environment vars are expanded, eg `~/.config` >> `/home/me/.config`, as does `$HOME/.config`.
- The `.parent` is the directory containing (above) the `.full_path`.  If the object `.is_file` then `.parent` is the
directory containing the file.  If the object `.is_dir` then the `.full_path` includes the end-point directory, and 
`.parent` is the directory above the end-point directory.
- When using `mkdir=True` the combined `base_path` / `in_path` is understood to be a directory path (not
to a file), and will be created if it does not already exist. (Uses `pathlib.Path.mkdir()`).  A FileExistsError 
is raised if you attempt to mkdir on top of an existing file.
- See [GitHub repo](https://github.com/cjnaz/cjnfuncs) tests/demo-mungePath.py for numerous application examples.
        
<br/>

<a id="refresh_stats"></a>

---

# refresh_stats () - Update the instance booleans

***mungePath() class member function***

The boolean status attributes (`.exists`, `.is_dir`, and `.is_file`) are set 
at the time the mungePath instance is created (when `set_attributes=True` (the default)). 
These attributes are not updated automatically as changes happen on the filesystem. 
Call `refresh_stats()` as needed, or directly access the pathlib methods (or access through
`run_with_timeout()`), eg `my_mungepath_inst.full_path.exists()`.

NOTE:  `refresh_stats()` utilizes `run_with_timeout()` with `rwt_timeout=1`.  This can result in 
up to a 3 second _hang_ if there are access issues.

### Returns
- The instance handle is returned so that refresh_stats() may be used in-line.
        
<br/>

<a id="check_path_exists"></a>

---

# check_path_exists (path, timeout=1) - With enforced timeout (no hang)

pathlib.Path.exists() tends to hang for an extended period of time when there are network access issues.
check_path_exists() wraps `pathlib.Path.exists()` with a timeout mechanism.


### Args
`path` (Path or str)
- Path to a file or directory

`timeout` (int or float, default 1 second)
- resolution seconds


### Returns
- True if the path exists
- False if the path does not exist or the timeout is reached
    