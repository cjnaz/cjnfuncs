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
from .core import logging
from .rwt import run_with_timeout


#=====================================================================================
#=====================================================================================
#  C l a s s   m u n g e P a t h
#=====================================================================================
#=====================================================================================

class mungePath():
    def __init__(self, in_path='', base_path='', mkdir=False, set_attributes=False, timeout=1.0, ntries=1):
        """
## Class mungePath (in_path='', base_path='', mkdir=False, set_attributes=False, timeout=1.0, ntries=1) - A clean interface for dealing with filesystem paths

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
- If True then `refresh_stats()` is called, setting `.exists`, `.is_file`, .is_dir` to valid values (or False on timeout).
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

        self.parent =       Path(in_path_pp.parent)
        self.full_path =    Path(in_path_pp)
        self.name =         self.full_path.name
        self.is_absolute =  self.full_path.is_absolute()
        self.is_relative =  not self.is_absolute

        if set_attributes:
            self.refresh_stats(timeout=timeout, ntries=ntries)
        else:
            self.exists = self.is_file = self.is_dir = None


#=====================================================================================
#=====================================================================================
#  r e f r e s h _ s t a t s
#=====================================================================================
#=====================================================================================

    def refresh_stats(self, timeout=1.0, ntries=1):
        """
## refresh_stats (timeout=1.0, ntries=1) - Update the instance .exists, .is_dir, and .is_file booleans attributes

***mungePath() class member function***

The instance attributes `.exists`, `.is_dir`, and `.is_file`) may be set 
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
        """
        self.exists = check_path_exists(self.full_path, timeout=timeout, ntries=ntries)

        try:
            self.is_dir = run_with_timeout (self.full_path.is_dir, rwt_timeout=timeout, rwt_ntries=ntries)
        except Exception as e:
            logging.debug(f"Exception - {type(e).__name__}: {e}")
            self.is_dir = False

        try:
            self.is_file = run_with_timeout (self.full_path.is_file, rwt_timeout=timeout, rwt_ntries=ntries)
        except Exception as e:
            logging.debug(f"Exception - {type(e).__name__}: {e}")
            self.is_file = False

        return self


#=====================================================================================
#=====================================================================================
#  _ _ r e p r _ _
#=====================================================================================
#=====================================================================================

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

def check_path_exists(inpath, timeout=1.0, ntries=1):
    """
## check_path_exists (path, timeout=1.0, ntries=1) - With enforced timeout (no hang)

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
    """

    _path = Path(inpath)

    try:
        return run_with_timeout (_path.exists, rwt_timeout=timeout, rwt_ntries=ntries)
    except Exception as e:
        logging.debug(f"Exception - {type(e).__name__}: {e}")
        return False
