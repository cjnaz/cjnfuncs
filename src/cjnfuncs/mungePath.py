#!/usr/bin/env python3
"""cjnfuncs.mungePath - pathlib Paths made easy and useful
"""

#==========================================================
#
#  Chris Nelson, 2018-2024
#
#==========================================================

import os.path
from pathlib import Path, PurePath
from concurrent.futures import ThreadPoolExecutor #, TimeoutError
from cjnfuncs.core import logging


#=====================================================================================
#=====================================================================================
#  C l a s s   m u n g e P a t h
#=====================================================================================
#=====================================================================================

class mungePath():
    def __init__(self, in_path='', base_path='', mkdir=False):
        """
## Class mungePath (in_path='', base_path='', mkdir=False) - A clean interface for dealing with filesystem paths

`mungePath()` is based on pathlib, producing Path type attributes and status booleans which may be used with all
pathlib.Path methods, such as .open().  `mungePath()` accepts paths in two parts - the tool script specific
portion `in_path` and a `base_path` (prepended if `in_path` is relative), and returns an instance that may 
be cleanly used in the tool script code.
User (`~user/`) and environment vars (`$HOME/`) are supported and expanded.


### Parameters
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
Often in a tool script a user path input is passed to the `in_path` parameter.  Using the `./` prefix, a file in 
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
        """

        in_path = str(in_path)
        base_path = str(base_path)

        if in_path.startswith('./'):
            in_path = Path.cwd() / in_path

        in_path_pp = PurePath(os.path.expandvars(os.path.expanduser(str(in_path))))

        if not in_path_pp.is_absolute():
            _base_path = str(base_path)
            if _base_path.startswith("."):
                _base_path = Path.cwd() / _base_path
            _base_path = PurePath(os.path.expandvars(os.path.expanduser(str(_base_path))))
            in_path_pp = _base_path / in_path_pp

        if mkdir:
            Path(in_path_pp).mkdir(parents=True, exist_ok=True)

        self.parent = Path(in_path_pp.parent)
        self.full_path = Path(in_path_pp)

        self.name = self.full_path.name
        self.refresh_stats()


#=====================================================================================
#=====================================================================================
#  r e f r e s h _ s t a t s
#=====================================================================================
#=====================================================================================

    def refresh_stats(self):
        """
## refresh_stats () - Update the instance booleans

***mungePath() class member function***

The boolean status attributes (.is_absolute, .is_relative, .exists, .is_dir, and .is_file) are set 
at the time the mungePath is created.  These attributes are not updated automatically as changes
happen on the filesystem.  Call refresh_stats() as needed.

### Returns
- The instance handle is returned so that refresh_stats() may be used in-line.
        """
        self.exists = check_path_exists(self.full_path)
        self.is_absolute = self.full_path.is_absolute()
        self.is_relative = not self.is_absolute
        try:
            self.is_dir =  self.full_path.is_dir()
            self.is_file = self.full_path.is_file()
        except:     # Trap if the path does not exist
            self.is_dir =  False
            self.is_file = False
        return self


    def __repr__(self):
        stats = ""
        stats +=  f".full_path    :  {self.full_path}\n"
        stats +=  f".parent       :  {self.parent}\n"
        stats +=  f".name         :  {self.name}\n"
        stats +=  f".is_absolute  :  {self.is_absolute}\n"
        stats +=  f".is_relative  :  {self.is_relative}\n"
        stats +=  f".exists       :  {self.exists}\n"
        stats +=  f".is_dir       :  {self.is_dir}\n"
        stats +=  f".is_file      :  {self.is_file}\n"
        return stats


#=====================================================================================
#=====================================================================================
#  c h e c k _ p a t h _ e x i s t s
#=====================================================================================
#=====================================================================================

def check_path_exists(inpath, timeout=1):
    """
## check_path_exists (path, timeout=1) - With enforced timeout (no hang)

pathlib.Path.exists() tends to hang for an extended period of time.  
check_path_exists() wraps pathlib.Path.exists() with a timeout mechanism.

Implementation stolen from https://stackoverflow.com/questions/67819869/how-to-efficiently-implement-a-version-of-path-exists-with-a-timeout-on-window


### Parameters
`path` (Path or str)
- Path to a file or directory

`timeout` (int or float, default 1 second)
- resolution seconds


### Returns
- True if the path exists
- False if the path does not exist or the timeout is reached
    """

    _path = Path(inpath)
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(_path.exists)
        try:
            return future.result(timeout)
        except Exception as e: #TimeoutError:
            logging.debug(f"Exception - {e}")
            return False
