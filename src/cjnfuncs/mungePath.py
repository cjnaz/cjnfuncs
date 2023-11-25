#!/usr/bin/env python3
"""cjnfuncs.mungePath - Paths made easy and useful.
"""

#==========================================================
#
#  Chris Nelson, 2018-2023
#
#==========================================================

import os.path
from pathlib import Path, PurePath
from concurrent.futures import ThreadPoolExecutor, TimeoutError



# TODO doc
# https://stackoverflow.com/questions/67819869/how-to-efficiently-implement-a-version-of-path-exists-with-a-timeout-on-window
def check_path_exists(path, timeout=1):
    executor = ThreadPoolExecutor(max_workers=1)
    future = executor.submit(path.exists)
    try:
        return future.result(timeout)
    except TimeoutError:
        return False


#=====================================================================================
#=====================================================================================
#  C l a s s   m u n g e P a t h
#=====================================================================================
#=====================================================================================
class mungePath():
    def __init__(self, in_path="", base_path="", mkdir=False):
        """
## Class mungePath (in_path="", base_path="", mkdir=False) - A clean interface for dealing with filesystem paths

`mungePath()` is based on pathlib, producing Path type attributes and status booleans which may be used with all
pathlib.Path methods, such as .open().  `mungePath()` accepts paths in two parts - the tool script specific
portion `in_path` and a `base_path` (prepended if `in_path` is relative), and returns an instance that may 
be cleanly used in the tool script code.
User (~user/) and environment vars ($HOME/) are supported and expanded.


### Parameters
`in_path`
- An absolute or relative path to a file or directory, such as `mydir/myfile.txt`.  

`base_path`
- An absolute or relative path to a file or directory, such as `~/.config/mytool`, prepended to `in_path` if
`in_path` is a relative path.

`mkdir`
- Force-make a full directory path.  `in_path` / `base_path` is understood to be to a directory.


### Returns
- Handle to `mungePath()` instance


### Instance attributes
```
    .full_path      Path        The full expanduser/expandvars path to a file or directory (may not exist)
    .parent         Path        The directory above the .full_path
    .name           str         Just the name.suffix of the .full_path
    .is_absolute    Boolean     True if the .full_path starts from the filesystem root (isn't a relative path) 
    .is_relative    Boolean     Not .is_absolute
    .exists         Boolean     True if the .full_path item (file or dir) actually exists
    .is_file        Boolean     True if the .full_path item exists and is a file
    .is_dir         Boolean     True if the .full_path item exists and is a directory
```

### Member functions
- mungePath.\_\_repr\_\_() - Return a str() listing all stats for the object
- mungePath.refresh_stats() - Update the boolean state attributes for the object. Returns the object
so that it may be used directly/immediately in the code.


### Behaviors and rules
- If `in_path` is a relative path (eg, `mydir/myfile.txt`) portion then the `base_path` is prepended.  
- If both `in_path` and `base_path` are relative then the combined path will also be relative, usually to
the tool script directory (generally not useful).
- If `in_path` is an absolute path (eg, `/tmp/mydir/myfile.txt`) then the `base_path` is ignored.
- `in_path` and `base_path` may be type str(), Path(), or PurePath().
- Symlinks are followed (not resolved).
- User and environment vars are expanded, eg `~/.config` >> `/home/me/.config`, as does `$HOME/.config`.
- The `.parent` is the directory containing (above) the `.full_path`.  If the object `.is_file` then `.parent` is the
directory containing the file.  If the object `.is_dir` then the `.full_path` includes the end-point directory, and 
`.parent` is the directory above the end-point directory.
- When using `mkdir=True` the combined `in_path` / `base_path` is understood to be a directory path (not
to a file), and will be created if it does not already exist. (Uses pathlib.Path.mkdir()).  A FileExistsError 
is raised if you attempt to mkdir on top of an existing file.
- See [GitHub repo](https://github.com/cjnaz/cjnfuncs) /tests/demo-mungePath.py for numerous application examples.


### Example
```
Given:
    tool = set_toolname("mytool")
    myfile = mungePath ("mysubdir/file.txt", tool.data_dir)
    mungePath (myfile.parent, mkdir=True)
    if not myfile.exists:
        with myfile.full_path.open('w') as outfile:
            file_contents = outfile.write("Hello")
        print (myfile)      # NOTE: Prints stats from before the file creation
        myfile.refresh_stats()
        print (myfile)

What gets printed:
    .full_path    :  /home/me/.local/share/mytool/mysubdir/file.txt
    .parent       :  /home/me/.local/share/mytool/mysubdir
    .name         :  file.txt
    .is_absolute  :  True
    .is_relative  :  False
    .exists       :  False
    .is_dir       :  False
    .is_file      :  False

    .full_path    :  /home/me/.local/share/mytool/mysubdir/file.txt
    .parent       :  /home/me/.local/share/mytool/mysubdir
    .name         :  file.txt
    .is_absolute  :  True
    .is_relative  :  False
    .exists       :  True
    .is_dir       :  False
    .is_file      :  True
```
        """
        
        self.in_path = str(in_path)
        self.base_path = str(base_path)

        in_path_pp = PurePath(os.path.expandvars(os.path.expanduser(str(in_path))))

        if not in_path_pp.is_absolute():
            _base_path = str(base_path)
            if _base_path.startswith("."):
                _base_path = Path.cwd() / _base_path
            _base_path = PurePath(os.path.expandvars(os.path.expanduser(str(_base_path))))
            in_path_pp = _base_path / in_path_pp

        if mkdir:
            try:
                Path(in_path_pp).mkdir(parents=True, exist_ok=True)
            except Exception as e:
                raise FileExistsError (e)

        self.parent = Path(in_path_pp.parent)
        self.full_path = Path(in_path_pp)

        self.name = self.full_path.name
        self.exists = check_path_exists(self.full_path)
        self.is_absolute = self.full_path.is_absolute()
        self.is_relative = not self.is_absolute
        try:
            self.is_dir =  self.full_path.is_dir()
            self.is_file = self.full_path.is_file()
        except:
            self.is_dir =  False
            self.is_file = False


    def refresh_stats(self):
        self.exists = check_path_exists(self.full_path)
        self.is_absolute = self.full_path.is_absolute()
        self.is_relative = not self.is_absolute
        # self.is_dir =  self.full_path.is_dir()
        # self.is_file = self.full_path.is_file()
        try:
            self.is_dir =  self.full_path.is_dir()
            self.is_file = self.full_path.is_file()
        except:
            self.is_dir =  False
            self.is_file = False
        return self


    def stats(self):
        return self.__repr__()

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

