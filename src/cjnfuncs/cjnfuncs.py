#!/usr/bin/env python3
"""cjnfuncs - A collection of support functions for writing clean and effective tool scripts
"""

#==========================================================
#
#  Chris Nelson, 2018-2023
#
# 2.0.2 230729 - Added modify_configfile.
#   Documentation touch for logging formats in config file. 
#   Improved snd_notif failure logging.
# 2.0.1 230222 - deploy_files() fix for files from package
# 2.0   230208 - Refactored and converted to installed package.  Renamed funcs3 to cjnfuncs.
# ...
# 0.1   180520 - New
#
# #==========================================================

import sys
import time
import os.path
import smtplib
from email.mime.text import MIMEText
import logging
import tempfile
import inspect
import platform
import re
import ast
from pathlib import Path, PurePath
import shutil
import __main__
import appdirs
# if sys.version_info < (3, 9):
#     from importlib_resources import files as ir_files
# else:
      # Errors on Py3.9:  TypeError: <module ...> is not a package.  The module __spec__.submodule_search_locations is None
#     from importlib.resources import files as ir_files
from importlib_resources import files as ir_files


# Configs / Constants
# FILE_LOGGING_FORMAT    = '{asctime}/{module}/{funcName}/{levelname}:  {message}'    # Classic format
FILE_LOGGING_FORMAT    = '{asctime} {module:>15}.{funcName:20} {levelname:>8}:  {message}'
CONSOLE_LOGGING_FORMAT = '{module:>15}.{funcName:20} - {levelname:>8}:  {message}'
# CONSOLE_LOGGING_FORMAT = '{pathname:>15}.{funcName:20} - {levelname:>8}:  {message}'

DEFAULT_LOGGING_LEVEL  = logging.WARNING
MAIN_MODULE_STEM       = Path(__main__.__file__).stem
# print ("__main__.__spec__:", __main__.__spec__)

# Project globals
cfg = {}


# Get the main / calling module info.  Made available by set_toolname.main_module
stack = inspect.stack()
calling_module = ""
for item in stack:  # Look for the import cjnaz.cjnfuncs line
    code_context = item[4]
    if code_context is not None:
        # if "cjnaz.cjnfuncs" in code_context[0]:
        if "cjnfuncs" in code_context[0]:
            calling_module = inspect.getmodule(item[0])
            break
# print ("calling_module:", calling_module)
# print (calling_module.__package__)
# # print (calling_module.__path__)
# print ("calling_module.__spec__", calling_module.__spec__) #.submodule_search_locations)


#=====================================================================================
#=====================================================================================
#  M o d u l e   e x c e p t i o n s
#=====================================================================================
#=====================================================================================
class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class ConfigError(Error):
    """Exceptions raised for config file function errors.
    Attributes:
        message -- error message including item in error
    Format:
        ConfigError:  <function> - <message>.
    """
    def __init__(self, message):
        self.message = message

class SndEmailError(Error):
    """Exceptions raised for snd_email and snd_notif errors.
    Attributes:
        message -- error message including item in error
    Format:
        SndEmailError:  <function> - <message>.
    """
    def __init__(self, message):
        self.message = message


#=====================================================================================
#=====================================================================================
#  s e t u p l o g g i n g
#=====================================================================================
#=====================================================================================
def setuplogging(call_logfile=None, call_logfile_wins=False, config_logfile=None):
    """
## setuplogging (call_logfile=None, call_logfile_wins=False, config_logfile=None) - Set up the root logger

Logging may be directed to the console (stdout), or to a file.  Each time setuplogging()
is called the current/active log file (or console) may be reassigned.

setuplogging() works standalone or in conjunction with loadconfig().
If a loaded config file has a `LogFile` parameter then loadconfig() passes it thru
`config_logfile`.  loadconfig() also passes along any `call_logfile` and `call_logfile_wins`
that were passed to loadconfig() from the tool script.  This mechanism allows the tool script
to override any config `LogFile`, such as for directing output to the console for a tool script's 
interactive use, eg:
    `setuplogging (call_logfile=None, call_logfile_wins=True, config_logfile='some_logfile.txt')`

    
### Parameters
`call_logfile`
- Potential log file passed from the tool script.  Selected by `call_logfile_wins = True`.
call_logfile may be an absolute path or relative to the tool.log_dir_base directory.  
`None` specifies the console.

`call_logfile_wins`
- If True, the `call_logfile` is selected.  If False, the `config_logfile` is selected.

`config_logfile`
- Potential log file passed from loadconfig() if there is a `LogFile` param in the 
loaded config.  Selected by `call_logfile_wins = False`.
config_logfile may be absolute path or relative to the tool.log_dir_base directory.  
`None` specifies the console.


### cfg dictionary params
`ConsoleLogFormat` (optional)
- Overrides the default console logging format: `{module:>15}.{funcName:20} - {levelname:>8}:  {message}`.

`FileLogFormat` (optional)
- Overrides the default file logging format: `{asctime} {module:>15}.{funcName:20} {levelname:>8}:  {message}`.

Also see `LogFile` and `LogLevel` info in loadconfig() documentation, below.


### Returns
- NoneType
    """

    _lfp = "__console__"
    if call_logfile_wins == False  and  config_logfile:
        _lfp = mungePath(config_logfile, tool.log_dir_base)

    if call_logfile_wins == True   and  call_logfile:
        _lfp = mungePath(call_logfile, tool.log_dir_base)

    logger = logging.getLogger()
    logger.handlers.clear()

    if _lfp == "__console__":
        log_format = logging.Formatter(getcfg("ConsoleLogFormat", CONSOLE_LOGGING_FORMAT), style='{')
        handler = logging.StreamHandler(sys.stdout)                             
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(log_format)
        logger.addHandler(handler)

        tool.log_dir = None
        tool.log_file = None
        tool.log_full_path = "__console__"

    else:
        mungePath(_lfp.parent, mkdir=True)  # Force make the target dir
        log_format = logging.Formatter(getcfg("FileLogFormat", FILE_LOGGING_FORMAT), style='{')
        handler = logging.FileHandler(_lfp.full_path, "a") #, sys.stdout)                             
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(log_format)
        logger.addHandler(handler)
    
        tool.log_dir = _lfp.parent
        tool.log_file = _lfp.name
        tool.log_full_path = _lfp.full_path


#=====================================================================================
#=====================================================================================
#  C l a s s   s e t _ t o o l n a m e
#=====================================================================================
#=====================================================================================
class set_toolname():
    """
## Class set_toolname (toolname) - Set target directories for config and data storage

set_toolname() centralizes and establishes a set of base directory path variables for use in
the tool script.  It looks for existing directories, based on the specified toolname, in
the site-wide (system-wide) and then user-specific locations.  Specifically, site-wide 
config and/or data directories are looked for at (eg) `/etc/xdg/cjnfuncs_testenv` and/or 
`/usr/share/cjnfuncs_testenv`.  If site-wide directories are not 
found then user-specific is assumed.  No directories are created.


### Parameter
`toolname`
- Name of the tool, type str()


### Returns
- Handle to the `set_toolname()` instance


### Member function
`stats()`
- Returns a str() listing of the available attributes of the instance


### Behaviors, rules, and _variances from the XDG spec and/or the appdirs package_
- set_toolname() uses the 
[appdirs package](https://pypi.org/project/appdirs/), which is a close implementation of the
[XDG basedir specification](https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html).

- The `user` and `site`-prefixed attributes are as defined by the XDG spec and/or the appdirs package.  The 
non-such-prefixed attributes are resolved based on the existing user or site environment, and are the attributes
that generally should be used within tool scripts.

- For a `user` setup, the `.log_dir_base` is initially set to the `.user_data_dir` (variance from XDG spec).
If a config file is subsequently
loaded then the `.log_dir_base` is changed to the `.user_config_dir`.  (Not changed for a `site` setup.)
Thus, for a `user` setup, logging is done to the default configuration directory.  This is a 
style variance, and can be reset in the tool script by reassigning: `tool.log_dir_base = tool.user_log_dir` (or any
other directory) before calling loadconfig() or setuplogging().
(The XDG spec says logging goes to the `.user_state_dir`, while appdirs sets it to the `.user_cache_dir/log`.)

- The `.log_dir`, `.log_file`, and `.log_full_path` attributes are set by calls to setuplogging() or loadconfig(),
and are initially set to `None` by set_toolname().

- For a `site` setup, the `.site_data_dir` is set to `/usr/share/toolname`.  The XDG spec states that 
the `.cache_dir` and `.state_dir` should be in the root user tree; however, set_toolname() sets these two 
also to the `.site_data_dir`.


### Examples
Given:
```
tool = set_toolname("cjnfuncs_testenv")
print (tool.stats())
```

Example stats() for a user-specific setup:
```
    Stats for set_toolname <wanstatus>:
    .toolname         :  wanstatus
    .main_module      :  <module 'wanstatus.wanstatus' from '/<path-to-venv>/lib/python3.9/site-packages/wanstatus/wanstatus.py'>
    .user_config_dir  :  /home/me/.config/wanstatus
    .user_data_dir    :  /home/me/.local/share/wanstatus
    .user_state_dir   :  /home/me/.local/state/wanstatus
    .user_cache_dir   :  /home/me/.cache/wanstatus
    .user_log_dir     :  /home/me/.cache/wanstatus/log
    .site_config_dir  :  /etc/xdg/wanstatus
    .site_data_dir    :  /usr/share/wanstatus
    Based on found user or site dirs:
    .env_defined      :  user
    .config_dir       :  /home/me/.config/wanstatus
    .data_dir         :  /home/me/.local/share/wanstatus
    .state_dir        :  /home/me/.local/state/wanstatus
    .cache_dir        :  /home/me/.cache/wanstatus
    .log_dir_base     :  /home/me/.local/share/wanstatus
    .log_dir          :  None
    .log_file         :  None
    .log_full_path    :  None
```
    
Example stats() for a site setup (.site_config_dir and/or .site_data_dir exist):
```
    Stats for set_toolname <wanstatus>:
    .toolname         :  wanstatus
    .main_module      :  <module 'wanstatus.wanstatus' from '/<path-to-venv>/lib/python3.9/site-packages/wanstatus/wanstatus.py'>
    .user_config_dir  :  /root/.config/wanstatus
    .user_data_dir    :  /root/.local/share/wanstatus
    .user_state_dir   :  /root/.local/state/wanstatus
    .user_cache_dir   :  /root/.cache/wanstatus
    .user_log_dir     :  /root/.cache/wanstatus/log
    .site_config_dir  :  /etc/xdg/wanstatus
    .site_data_dir    :  /usr/share/wanstatus
    Based on found user or site dirs:
    .env_defined      :  site
    .config_dir       :  /etc/xdg/wanstatus
    .data_dir         :  /usr/share/wanstatus
    .state_dir        :  /usr/share/wanstatus
    .cache_dir        :  /usr/share/wanstatus
    .log_dir_base     :  /usr/share/wanstatus
    .log_dir          :  None
    .log_file         :  None
    .log_full_path    :  None
```
    """
    def __init__(self, toolname):
        global tool             # handle used elsewhere in this module
        tool = self
        self.toolname  = toolname
        self.main_module        = calling_module
        self.user_config_dir    = Path(appdirs.user_config_dir(toolname, appauthor=False))  # appauthor=False to avoid double toolname on Windows
        self.user_data_dir      = Path(appdirs.user_data_dir  (toolname, appauthor=False))
        self.user_state_dir     = Path(appdirs.user_state_dir (toolname, appauthor=False))
        self.user_cache_dir     = Path(appdirs.user_cache_dir (toolname, appauthor=False))
        self.user_log_dir       = Path(appdirs.user_log_dir   (toolname, appauthor=False))
        self.site_config_dir    = Path(appdirs.site_config_dir(toolname, appauthor=False))
        if platform.system() == "Windows":
            self.site_data_dir  = Path(appdirs.site_data_dir  (toolname, appauthor=False))
        else:   # Linux, ...
            self.site_data_dir  = Path("/usr/share") / toolname

        if self.site_config_dir.exists()  or  self.site_data_dir.exists():
            self.env_defined= "site"
            self.config_dir     = self.site_config_dir
            self.data_dir       = self.site_data_dir
            self.state_dir      = self.site_data_dir
            self.cache_dir      = self.site_data_dir
            self.log_dir_base   = self.site_data_dir
        else:
            self.env_defined= "user"
            self.config_dir     = self.user_config_dir
            self.data_dir       = self.user_data_dir
            self.state_dir      = self.user_state_dir
            self.cache_dir      = self.user_cache_dir
            self.log_dir_base   = self.user_data_dir

        self.log_file = self.log_dir = self.log_full_path = None

        # print (self.stats())


    def stats(self):
        stats = ""
        stats +=  f"\nStats for set_toolname <{self.toolname}>:\n"
        stats +=  f".toolname         :  {self.toolname}\n"
        stats +=  f".main_module      :  {self.main_module}\n"
        stats +=  f".user_config_dir  :  {self.user_config_dir}\n"
        stats +=  f".user_data_dir    :  {self.user_data_dir}\n"
        stats +=  f".user_state_dir   :  {self.user_state_dir}\n"
        stats +=  f".user_cache_dir   :  {self.user_cache_dir}\n"
        stats +=  f".user_log_dir     :  {self.user_log_dir}\n"
        stats +=  f".site_config_dir  :  {self.site_config_dir}\n"
        stats +=  f".site_data_dir    :  {self.site_data_dir}\n"

        stats +=  f"Based on found user or site dirs:\n"
        stats +=  f".env_defined      :  {self.env_defined}\n"
        stats +=  f".config_dir       :  {self.config_dir}\n"
        stats +=  f".data_dir         :  {self.data_dir}\n"
        stats +=  f".state_dir        :  {self.state_dir}\n"
        stats +=  f".cache_dir        :  {self.cache_dir}\n"
        stats +=  f".log_dir_base     :  {self.log_dir_base}\n"
        stats +=  f".log_dir          :  {self.log_dir}\n"
        stats +=  f".log_file         :  {self.log_file}\n"
        stats +=  f".log_full_path    :  {self.log_full_path}\n"
        return stats


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
- mungePath.stats() - Return a str() listing all stats for the object
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
    xx = mungePath ("mysubdir/file.txt", tool.data_dir)
    mungePath (xx.parent, mkdir=True)
    if not xx.exists:
        with xx.full_path.open('w') as outfile:
            file_contents = outfile.write("Hello")
    print (xx.refresh_stats().stats())      # Refresh needed else prints stats from when xx was created (before file.txt was created)

What gets printed:
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

        PP_in_path = PurePath(os.path.expandvars(os.path.expanduser(str(in_path))))

        if not PP_in_path.is_absolute():
            _base_path = str(base_path)
            if _base_path.startswith("."):
                _base_path = Path.cwd() / _base_path
            _base_path = PurePath(os.path.expandvars(os.path.expanduser(str(_base_path))))
            PP_in_path = _base_path / PP_in_path

        if mkdir:
            try:
                Path(PP_in_path).mkdir(parents=True, exist_ok=True)
            except Exception as e:
                raise FileExistsError (e)

        self.parent = Path(PP_in_path.parent)
        self.full_path = Path(PP_in_path)

        self.name = self.full_path.name
        self.exists =  self.full_path.exists()
        self.is_absolute = self.full_path.is_absolute()
        self.is_relative = not self.is_absolute
        self.is_dir =  self.full_path.is_dir()
        self.is_file = self.full_path.is_file()


    def refresh_stats(self):
        self.exists =  self.full_path.exists()
        self.is_absolute = self.full_path.is_absolute()
        self.is_relative = not self.is_absolute
        self.is_dir =  self.full_path.is_dir()
        self.is_file = self.full_path.is_file()
        return self


    def stats(self):
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
#  d e p l o y _ f i l e s
#=====================================================================================
#=====================================================================================
def deploy_files(files_list, overwrite=False, missing_ok=False):
    """
## deploy_files (files_list, overwrite=False, missing_ok=False) - Install initial tool script files in user or site space

`deploy_files()` is used to install initial setup files (and directory trees) from the module to the user 
or site config and data directories. Suggested usage is with the CLI `--setup-user` or `--setup-site` switches.
Distribution files and directory trees are hosted in `<module_root>/deployment_files/`.

`deploy_files()` accepts a list of dictionaries to be pushed to user or site space. 
If deployment fails then execution aborts.  This functions is intended for interactive use.


### Parameters
`files_list`
- A list of dictionaries, each specifying a `source` file or directory tree to be copied to a `target_dir`.
  - `source` - Either an individual file or directory tree within and relative to `<module_root>/deployment_files/`.
    No wildcard support.
  - `target_dir` - A directory target for the pushed `source`.  It is expanded for user and environment vars, 
    and supports these substitutions (per set_toolname()):
    - USER_CONFIG_DIR, USER_DATA_DIR, USER_STATE_DIR, USER_CACHE_DIR
    - SITE_CONFIG_DIR, SITE_DATA_DIR
    - Also absolute paths
  - `file_stat` - Permissions set on each created file (default 0o664)
  - `dir_stat` - Permissions set on each created directory (if not already existing, default 0o775)

`overwrite`
- If overwrite=False (default) then only missing files will be copied.  If overwrite=True then all files will be overwritten 
if they exist - data may be lost!

`missing_ok`
- If missing_ok=True then a missing source file or directory is tolerated (non-fatal).  This feature is used for testing.


### Returns
- NoneType


### Example
```
    deploy_files( [
        { "source": "creds_test", "target_dir": "USER_CONFIG_DIR/example", "file_stat": 0o600, "dir_stat": 0o707},
        { "source": "test_dir",   "target_dir": "USER_DATA_DIR",           "file_stat": 0o633, "dir_stat": 0o770},
        ...
        ], overwrite=True )
```

The first line will push the `<module_root>/deployment_files/creds_test` file to `~/.config/mytool/example/creds_test`.
The toolname `mytool` was set by a prior call to `set_toolname("mytool")`, in this example.
The directories `~/.config/mytool/` and `~/.config/mytool/example` will have permissions 0o707 and files will have
permission 0o600.
Directory and file owner:group settings will be user:user, or root:root if called under sudo.

The second line pushes a directory (with possible subdirectories) to `~/.local/share/mytool/`.
The target_dir may specify a subdirectory, such as `"target_dir": "USER_DATA_DIR/mydirs"`.
Any _new directories_ in the  `target_dir` path will be created with the `dir_stat` permissions,
and files will be created with the `file_stat` permissions.
    """

    global tool

    mapping = [
        ["USER_CONFIG_DIR", tool.user_config_dir],
        ["USER_DATA_DIR",   tool.user_data_dir],
        ["USER_STATE_DIR",  tool.user_state_dir],
        ["USER_CACHE_DIR",  tool.user_cache_dir],
        ["SITE_CONFIG_DIR", tool.site_config_dir],
        ["SITE_DATA_DIR",   tool.site_data_dir],
        ]

    def resolve_target(_targ, mkdir=False):
        """Do any CONFIG/DATA replacements.  Return a fully resolved mungePath.
        """
        base_path = ""
        for remap in mapping:
            if remap[0] in _targ:
                _targ = _targ.replace(remap[0], "")
                if len(_targ) > 0:
                    _targ = _targ[1:]   # TODO This is weak.  Drops leading '/' after remap removed.
                base_path = remap[1]
                break
        try:
            xx = mungePath(_targ, base_path, mkdir=mkdir)
            return xx
        except Exception as e:
            print (f"Can't make target directory.  Aborting.\n  {e}")
            sys.exit(1)
    
    def copytree(src, dst, file_stat=None, dir_stat=None):
        """ Adapted from link, plus permissions settings feature.  No needed support for symlinks and ignore.
        https://stackoverflow.com/questions/1868714/how-do-i-copy-an-entire-directory-of-files-into-an-existing-directory-using-pyth
        """
        for item in os.listdir(src):
            s = os.path.join(src, item)
            d = os.path.join(dst, item)
            if os.path.isdir(s):
                if not os.path.exists(d):
                    os.makedirs(d)
                    if dir_stat:
                        os.chmod(d, dir_stat)
                copytree(s, d, file_stat=file_stat, dir_stat=dir_stat)
            else:
                shutil.copy2(s, d)
                if file_stat:
                    os.chmod(d, file_stat)

    if calling_module.__name__ == "__main__":   # Caller is a tool script file, not an installed module
        my_resources = mungePath(__main__.__file__).parent / "deployment_files"
        # print (f"Script case:  <{my_resources}>")
    else:                                       # Caller is an installed module
        my_resources = ir_files(calling_module).joinpath("deployment_files")
        # print (f"Module case:  <{my_resources}>")

    for item in files_list:
        source = my_resources.joinpath(item["source"])
        if source.is_file():
            target_dir = resolve_target(item["target_dir"], mkdir=True)
            if "dir_stat" in item:
                os.chmod(target_dir.full_path, item["dir_stat"])

            if not target_dir.is_dir:
                print (f"Can't deploy {source.name}.  Cannot access target_dir <{target_dir.parent}>.  Aborting.")
                sys.exit(1)

            outfile = target_dir.full_path / PurePath(item["source"]).name
            if not outfile.exists()  or  overwrite:
                try:
                    with outfile.open('w') as ofile:
                        ofile.write(source.read_text())
                    if "file_stat" in item:
                        os.chmod(outfile, item["file_stat"])
                except Exception as e:
                    print (f"File copy of <{item['source']}> to <{target_dir.full_path}> failed.  Aborting.\n  {e}")
                    sys.exit(1)
                print (f"Deployed  {item['source']:20} to  {target_dir.full_path}")
            else:
                print (f"File <{item['source']}> already exists at <{target_dir.full_path}>.  Skipped.")

        elif source.is_dir():
                # ONLY WORKS if the source dir is on the file system (eg, not in a package .zip)
                if not resolve_target(item["target_dir"]).exists  or  overwrite:
                    target_dir = resolve_target(item["target_dir"], mkdir=True)
                    try:
                        if "dir_stat" in item:
                            os.chmod(target_dir.full_path, item["dir_stat"])
                        copytree(source, target_dir.full_path, file_stat=item.get("file_stat", None), dir_stat=item.get("dir_stat", None))
                    except Exception as e:
                        print (f"Failed copying tree <{source.name}> to <{target_dir.full_path}>.  target_dir can't already exist.  Aborting.\n  {e}")
                        sys.exit(1)
                    print (f"Deployed  {source.name:20} to  {target_dir.full_path}")
                else:
                    print (f"Directory <{target_dir.full_path}> already exists.  Copytree skipped.")
        elif missing_ok:
            print (f"Can't deploy {source.name}.  Item not found.  Skipping.")
        else:
            print (f"Can't deploy {source.name}.  Item not found.  Aborting.")
            sys.exit(1)
        

#=====================================================================================
#=====================================================================================
#  C l a s s   c o n f i g _ i t e m
#=====================================================================================
#=====================================================================================
initial_logging_setup = False   # Global since more than one config can be loaded
CFGLINE = re.compile(r"([^\s=:]+)[\s=:]+(.+)")                   # used in load_config()
CFGLINE2 = re.compile(r"(\s*)([^\s=:]+)([\s=:]+)([^#]+)(.*)")    # used in modify_configfile()


class config_item():
    """
## Class config_item (config_file, remap_logdirbase=True) - Create a configuration instance for use with loadconfig()

Several attributes are kept for use by the tool script, including the name, path, and the timestamp
of the config file (timestamp once loaded).  

The config file may be loaded and reloaded with successive calls to loadconfig().


### Parameters
`config_file`
- Path to the configuration file, relative to the `tool.config_dir` directory, or an absolute path.

`remap_logdirbase` (default True)
- If `remap_logdirbase=True` and the tool script is running in user mode (not site mode) 
then the `tool.log_dir_base` will be remapped to `tool.user_config_dir`.


### Returns
- Handle to the `config_item()` instance
- Raises a `ConfigError` if the specified config file is not found


### Member functions
- config_item.stats() - Return a str() listing all stats for the instance, plus the `tool.log_dir_base` value.
- config_item.load_config() - Load the config file to the `cfg` dictionary.  See below.
- modify_configfile() - Modify, add, remove params from the config file.


### Behaviors and rules
- More than one `config_item()` may be created and loaded.  This allows for configuration data to be partitioned 
as desired.  All configs are loaded to the `cfg` dictionary.  Also see the loadconfig `import` feature.
- Initially in _user_ mode, after the `set_toolname()` call, `tool.log_dir_base` 
(the log directory) is set to the `tool.user_data_dir`.
Once `config_item()` is called the `tool.log_dir_base` is _remapped_ to 
`tool.user_config_dir`.  This is the author's style preference (centralize user files, and 
reduce spreading files around the file system).
To disable this remap, in the `config_item()` call set `remap_logdirbase=False`.
This remapping is not done in site mode.
- A different log base directory may be set by user code by setting `tool.log_dir_base` to a different path after 
the `set_toolname()` call and before the `loadconfig()` call, for example `tool.log_dir_base = "/var/log"` may 
be desireable in site mode.


### Example
```
Given
    tool = set_toolname("testcfg")
    print (f"tool.log_dir_base : {tool.log_dir_base}")
    config = config_item("demo_config.cfg", remap_logdirbase=True)
    print (config.stats())
    config.loadconfig()
    print (config.stats())

Output
    tool.log_dir_base : /home/me/.local/share/testcfg

    Stats for config file <demo_config.cfg>:
    .config_file        :  demo_config.cfg
    .config_dir         :  /home/me/.config/testcfg
    .config_full_path   :  /home/me/.config/testcfg/demo_config.cfg
    .config_timestamp   :  0
    tool.log_dir_base   :  /home/me/.config/testcfg

    Stats for config file <demo_config.cfg>:
    .config_file        :  demo_config.cfg
    .config_dir         :  /home/me/.config/testcfg
    .config_full_path   :  /home/me/.config/testcfg/demo_config.cfg
    .config_timestamp   :  1675529660.7154639
    tool.log_dir_base   :  /home/me/.config/testcfg
```
    """
    def __init__(self, config_file, remap_logdirbase=True):
        global tool

        config = mungePath(config_file, tool.config_dir)
        if config.is_file:
            self.config_file        = config.name
            self.config_dir         = config.parent
            self.config_full_path   = config.full_path
            self.config_timestamp   = 0
            self.config_content     = ""    # Used by modify_configfile()
            if remap_logdirbase  and  tool.log_dir_base == tool.user_data_dir:
                tool.log_dir_base = tool.user_config_dir
        else:
            _msg = f"Config file <{config_file}> not found."
            raise ConfigError (_msg)


    def stats(self):
        stats = ""
        stats += f"\nStats for config file <{self.config_file}>:\n"
        stats += f".config_file        :  {self.config_file}\n"
        stats += f".config_dir         :  {self.config_dir}\n"
        stats += f".config_full_path   :  {self.config_full_path}\n"
        stats += f".config_timestamp   :  {self.config_timestamp}\n"
        stats += f"tool.log_dir_base   :  {tool.log_dir_base}\n"
        # stats += f"tool.log_full_path  :  {tool.log_full_path}\n"
        return stats


#=====================================================================================
#=====================================================================================
#  l o a d c o n f i g
#=====================================================================================
#=====================================================================================
    def loadconfig(self,
            ldcfg_ll            = DEFAULT_LOGGING_LEVEL,
            call_logfile        = None,
            call_logfile_wins   = False,
            flush_on_reload     = False,
            force_flush_reload  = False,
            isimport            = False,
            tolerate_missing    = False):
        """
## loadconfig () (config_item class member function) - Load a configuration file into the cfg dictionary
```
loadconfig(
    ldcfg_ll            = DEFAULT_LOGGING_LEVEL,
    call_logfile        = None,
    call_logfile_wins   = False,
    flush_on_reload     = False,
    force_flush_reload  = False,
    isimport            = False,
    tolerate_missing    = False)        
```
loadconfig() is a member function of the `config_item()` class.  Create a `config_item()` instance
and then invoke `loadconfig()` on that instance. Config file parameters are loaded to the `cfg` 
dictionary, and can be accessed directly or via `getcfg()`.

`loadconfig()` initializes the root logger for logging either to 1) the `LogFile` specified in
the loaded config file, 2) the `call_logfile` in the `loadconfig()` call, or 3) the console.
`loadconfig()` supports dynamic reloading of config files, hierarchy of config data via the `import`
feature, and intermittent loss of access to the config file.
    

### Parameters
`ldcfg_ll` (default 30/WARNING)
- Logging level used within `loadconfig()` code for debugging loadconfig() itself

`call_logfile` (default None)
- A relative or absolute path to a log file

`call_logfile_wins` (default False)
- If True, the `call_logfile` overrides any `LogFile` in the config file

`flush_on_reload` (default False)
- If the config file will be reloaded (due to a changed timestamp) then clean out `cfg` first

`force_flush_reload` (default False)
- Forces cfg to be cleaned out and the config file to be reloaded, regardless of whether the
config file timestamp has changed

`isimport` (default False)
- Internally set True when handling imports.  Not used by tool script calls.

`tolerate_missing` (default False)
- Used in a tool script service loop, return `-1` rather than raising `ConfigError` if the config file is inaccessible


### Returns
- `1` if the config files WAS reloaded
- `0` if the config file was NOT reloaded
- If the config file cannot be accessed
  - If tolerate_missing == False (default), then raises `ConfigError`
  - If tolerate_missing == True, then returns `-1`
- A ConfigError is raised if there are parsing issues
- A ConfigError is also raised if an imported config file cannot be loaded (non-existent)


### Behaviors and rules
- See `getcfg()`, below, for accessing loaded config data. `cfg` is a global dictionary which may be
  directly accessed as well.
- The format of a config file is param=value pairs (with no section or default as in the Python 
  configparser module).  Separating the param and value may be whitespace, `=` or `:`.
- **Native int, float, bool, list, tuple, dict, str support** - Bool true/false is case insensitive. A str
  type is stored in the cfg dictionary if none of the other types can be resolved for a given value.
  Automatic typing avoids most explicit type casting clutter in the tool script. Be careful to error trap
  for type errors (eg, expecting a float but user input error resulted in a str).
- **Logging setup** - `loadconfig()` calls `setuplogging()`.  The `logging` handle is available for
  import by other modules (`from cjnfuncs.cjnfuncs import logging`).  By default, logging will go to the
  console (stdout) filtered at the WARNING/30 level. Don't call `setuplogging()` directly if using loadconfig.
- **Logging level control** - Optional `LogLevel` in the config file will set the logging level after
  the config file has been loaded.  If LogLevel is not specified in the config file, then 
  the logging level is set to the Python default logging level, 30/WARNING.
  The tool script code may also manually/explicitly set the logging level - _after_ the initial `loadconifig()` call -
  and this value will be retained over later calls to loadconfig, thus allowing for a command line `--verbose`
  switch feature.  Note that logging done _within_ loadconfig() code is always done at the `ldcfg_ll` level.
- **Log file options** - Where to log has two separate fields:  `call_logifle` in the call to loadconfig(), and 
  `LogFile` in the loaded config file, with `call_logfile_wins` selecting which is used.  This mechanism allows for
  a command line `--log-file` switch to override a _default_ log file defined in the config file.  If the selected 
  logging location is `None` then output goes to the console (stdout).

  call_logfile_wins | call_logfile | Config LogFile | Results
  --|--|--|--
  False (default) | ignored | None (default) | Console
  False (default) | ignored | file_path | To the config LogFile
  True | None (default) | ignored | Console
  True | file_path | ignored | To the call_logfile

- **Logging format** - cjnfuncs has default format strings for console and file logging.
  These defaults may be overridden by defining `ConsoleLogFormat` and/or `FileLogFormat`
  in the config file.

- **Import nested config files** - loadconfig() supports `Import` (case insensitive). The imported file path
is relative to the `tool.config_dir` if not an absolute path.
The specified file is imported as if the params were in the main config file.  Nested imports are allowed. 
A prime usage of `import` is to place email server credentials in your home directory with user-only readability,
then import them in the tool script config file as such: `import ~/creds_SMTP`.  

- **Config reload if changed, `flush_on_reload`, and `force_flush_reload`** - loadconfig() may be called 
periodically by the tool script, such as in a service loop.
If the config file timestamp is unchanged then loadconfig() immediately returns `0`. 
If the timestamp has changed then the config file will be reloaded, and `1` is returned to indicate to 
the tool script to do any post-config-load operations. 
  - If `flush_on_reload=True` (default False) then the `cfg`
  dictionary will be cleaned/purged before the config file is reloaded. If `flush_on_reload=False` then the config
  file will be reloaded on top of the existing `cfg` dictionary contents (if a param was deleted in the config
  file it will still exist in `cfg` after the reload). [lanmonitor](https://github.com/cjnaz/lanmonitor) uses these
  features.
  - `force_flush_reload=True` (default False) forces both a clear/flush of the `cfg` dictionary and then a fresh
  reload of the config file. 
  - **Note** that if using threading then a thread should be paused while the config file 
  is being reloaded with `flush_on_reload=True` or `force_flush_reload=True` since the params will disappear briefly.
  - Changes to imported files are not tracked for changes.

- **Tolerating intermittent config file access** - When implementing a service loop, if `tolerate_missing=True` 
(default False) then loadconfig() will return `-1` if the config file cannot be accessed, informing the 
tool script of the problem for appropriate handling. If `tolerate_missing=False` then loadconfig() will raise
a ConfigError if the config file cannot be accessed.

- **Comparison to Python's configparser module** - configparser contains many customizable features. 
Here are a few key comparisons:

  Feature | loadconfig | Python configparser
  ---|---|---
  Native types | int, float, bool (true/false case insensitive), list, tuple, dict, str | str only, requires explicit type casting via getter functions
  Reload on config file change | built-in | not built-in
  Import sub-config files | Yes | No
  Section support | No | Yes
  Default support | No | Yes
  Fallback support | Yes (getcfg default) | Yes
  Whitespace in params | No | Yes
  Case sensitive params | Yes (always) | Default No, customizable
  Param/value delimiter | whitespace, ':', or '=' | ':' or '=', customizable
  Param only (no value) | No | Yes
  Multi-line values | No | Yes
  Comment prefix | '#' fixed, thus can't be part of the param or value | '#' or ';', customizable
  Interpolation | No | Yes
  Mapping Protocol Access | No | Yes
  Save to file | No (see `modify_configfile()`) | Yes
        """

        global cfg
        global initial_logging_setup
        global preexisting_loglevel

        if not initial_logging_setup:   # Do only once, globally
            # Initial logging will go to the console if no call_logfile is specified on the initial loadconfig call.
            # The logging level defaults to WARNING / 30.
            setuplogging (call_logfile=call_logfile, call_logfile_wins=call_logfile_wins)
            initial_logging_setup = True

        config = self.config_full_path

        try:
            if not isimport:                # Operations only on top level config file

                # Save externally set / prior log level for later restore
                preexisting_loglevel = logging.getLogger().level

                if force_flush_reload:
                    logging.getLogger().setLevel(ldcfg_ll)   # logging within loadconfig is always done at ldcfg_ll
                    logging.info("cfg dictionary force flushed (force_flush_reload)")
                    cfg.clear()
                    self.config_timestamp = 0       # Force reload of the config file

                if not config.exists():
                    if tolerate_missing:
                        logging.getLogger().setLevel(ldcfg_ll)
                        logging.info (f"Config file  <{config}>  is not currently accessible.  Skipping (re)load.")
                        logging.getLogger().setLevel(preexisting_loglevel)
                        return -1
                    else:
                        logging.getLogger().setLevel(preexisting_loglevel)
                        _msg = f"Could not find  <{config}>"
                        raise ConfigError (_msg)

                # Check if config file has changed.  If not then return 0
                current_timestamp = int(self.config_full_path.stat().st_mtime)  # integer-second resolution
                if self.config_timestamp == current_timestamp:
                    return 0

                # Initial load call, or config file has changed.  Do (re)load.
                self.config_timestamp = current_timestamp
                logging.getLogger().setLevel(ldcfg_ll)   # Set logging level for remainder of loadconfig call
                # logging.info (f"Config file timestamp: {current_timestamp}")
                logging.warning (f"Config file timestamp: {current_timestamp}")

                if flush_on_reload:
                    logging.info (f"cfg dictionary flushed due to changed config file (flush_on_reload)")
                    cfg.clear()

            logging.info (f"Loading  <{config}>")

            def parse_value(value_str):
                try:                                                # Integer
                    return int(value_str) 
                except:
                    pass
                try:                                                # Float
                    return float(value_str)
                except:
                    pass
                if value_str.lower() == "true":                     # Boolean True
                    return True
                if value_str.lower() == "false":                    # Boolean False
                    return False
                try:
                    if  (value_str.startswith('[') and value_str.endswith(']'))  or \
                        (value_str.startswith('{') and value_str.endswith('}'))  or \
                        (value_str.startswith('(') and value_str.endswith(')')):
                            return ast.literal_eval(value_str)      # List, Dictionary, or Tuple
                except:
                    pass
                return value_str                                    # String


            with config.open() as ifile:
                for line in ifile:

                    # Is an import line
                    if line.strip().lower().startswith("import"):
                        line = line.split("#", maxsplit=1)[0].strip()
                        target = mungePath(line.split(maxsplit=1)[1], self.config_dir)
                        try:
                            imported_config = config_item(target.full_path)
                            imported_config.loadconfig(ldcfg_ll, isimport=True)
                        except Exception as e:
                            logging.getLogger().setLevel(preexisting_loglevel)
                            _msg = f"Failed importing/processing config file  <{target.full_path}>"
                            raise ConfigError (_msg)

                    # Is a param/value line
                    else:
                        _line = line.split("#", maxsplit=1)[0].strip()  # line without comment
                        if len(_line) > 0:
                            out = CFGLINE.match(_line)
                            if out:
                                param = out.group(1)
                                rol   = out.group(2)        # rest of line (value portion)

                                value = parse_value(rol)
                                cfg[param] = value

                                logging.debug (f"Loaded {param} = <{value}>  ({type(value)})")
                            else: 
                                line = line.replace('\n','')
                                logging.warning (f"loadconfig:  Error on line <{line}>.  Line skipped.")

        except Exception as e:
            _msg = f"Failed opening/processing config file  <{config}>\n  {e}"
            raise ConfigError (_msg) from None


        # Operations only for finishing a top-level call
        if not isimport:
            setuplogging(config_logfile=getcfg("LogFile", None), call_logfile=call_logfile, call_logfile_wins=call_logfile_wins)

            if getcfg("DontEmail", False):
                logging.info ('DontEmail is set - Emails and Notifications will NOT be sent')
            elif getcfg("DontNotif", False):
                logging.info ('DontNotif is set - Notifications will NOT be sent')

            config_loglevel = getcfg("LogLevel", None)
            if config_loglevel is not None:
                logging.info (f"Logging level set to config LogLevel <{config_loglevel}>")
                logging.getLogger().setLevel(config_loglevel)
            else:
                logging.info (f"Logging level set to preexisting level <{preexisting_loglevel}>")
                logging.getLogger().setLevel(preexisting_loglevel)

        return 1    # 1 indicates that the config file was (re)loaded


#=====================================================================================
#=====================================================================================
#  m o d i f y _ c o n f i g f i l e
#=====================================================================================
#=====================================================================================
    def modify_configfile (self, param="", value="", remove=False, add_if_not_existing=False, save=False):
        # TODO Comment out / uncomment out a param
        """
## modify_configfile (param, value, remove=False, add_if_not_existing=False, save=False) - Make edits to the config file

Params in the config file may have their values changed, be deleted, or new lines added.  All added lines
are added at the bottom of the file.

On the first call to modify_configfile() the content of the file is read into memory.  Successive
calls to modify_configfile() may be made, with the changes applied to the in-memory copy.  When
all changes have been applied the final call to modify_configfile() must have `save=True` to 
cause the memory version to be written back to the config file.  If the script code checks for
modifications of the config file, then the modified content will be reloaded into the cfg dictionary.


### Parameters
`param` (default "")
- The param name, if modifing an existing param or adding a new param

`value` (default "")
- The new value to be applied to an existing param, or an added param
- Will be cast to str

`remove` (default False)
- If True, the `param` config file line is removed from the config file

`add_if_not_existing` (default False)
- Add the `param` `value` line at the bottom of the config file
- To add a blank line leave out both `param` and `value`, or set both the `""`
- To add a comment line specify the comment in the `param` field (eg, `modify_configfile("# My comment")`)

`save` (default False)
- Write the modified config file content back to the file
- `save=True` may be specified on the last modification call or an a standalone call.


### Returns
- No return value
- Warning messages are logged for attempting to modify or remove a non-existing param.


### Exmaple
```
config.modify_configfile("abc",                     remove=True)                # Removed
config.modify_configfile("def", "123456789 123456789")                          # Mofified value
config.modify_configfile("", "",                    add_if_not_existing=True)   # Blank line
config.modify_configfile("George", "was here",      add_if_not_existing=True)   # New param
config.modify_configfile("Snehal", "wasn't here")                               # Warning message
config.modify_configfile(                           add_if_not_existing=True)   # Another blank line
config.modify_configfile("# New comment line",      add_if_not_existing=True, save=True) # New comment and save
```
        """

        if self.config_content == "":
            self.config_content = self.config_full_path.read_text()
        found_param = False
        updated_content = ""
        value = str(value)

        for line in self.config_content.split("\n"):
            out = CFGLINE2.match(line)
            if out:
                # print (f"1: <{out.group(1)}>")    # Any leading whitespace
                # print (f"2: <{out.group(2)}>")    # param
                # print (f"3: <{out.group(3)}>")    # whitespace, '=', ':' between param and value
                # print (f"4: <{out.group(4)}>")    # value, with trailing whitespace
                # print (f"5: <{out.group(5)}>")    # comment

                if out.group(2) != param:
                    updated_content += line + "\n"
                else:
                    found_param = True
                    if remove == True:
                        continue                            # just don't save the line

                    # Update value for the current line
                    len_current_whitespace = len(out.group(4)) - len(out.group(4).strip())
                    len_new_whitespace = len_current_whitespace - (len(value) - len(out.group(4).strip()))
                    if len_new_whitespace < 1:
                        len_new_whitespace = 1
                    if len_current_whitespace == 0:
                        len_new_whitespace = 0
                    updated_content += out.group(1) + out.group(2) + out.group(3) + value + ' '*len_new_whitespace + out.group(5) + "\n"
            else:
                updated_content += line + "\n"

        if found_param == False:
            if add_if_not_existing == True:
                updated_content += f"{param}    {value}\n"
            elif param==""  and  value==""  and save==True: # Save-only call
                pass
            else:
                logging.warning (f"Modification of param <{param}> failed - not found in config file.  Modification skipped.")

        self.config_content = updated_content[:-1]          # Avoid adding extra \n at end of file

        if save:
            self.config_full_path.write_text(self.config_content + "\n")
            self.config_content = ""



#=====================================================================================
#=====================================================================================
#  g e t c f g
#=====================================================================================
#=====================================================================================
def getcfg(param, default="_nodefault"):
    """
## getcfg (param, default=None) - Get a param from the cfg dictionary

Returns the value of param from the cfg dictionary.  Equivalent to just referencing cfg[]
but with handling if the item does not exist.

NOTE: `getcfg()` is almost equivalent to `cfg.get()`, except that `getcfg()` does not default to `None`.
Rather, `getcfg()` raises a ConfigError if the param does not exist and no `default` is specified.
This can lead to cleaner tool script code.  Either access method may be used, along with `x = cfg["param"]`.


### Parameters
`param`
- String name of param to be fetched from cfg

`default` (default None)
- if provided, is returned if `param` does not exist in cfg


### Returns
- param value (cfg[param]), if param is in cfg
- `default` value if param not in cfg and `default` value provided
- raises ConfigError if param does not exist in cfg and no `default` provided.
    """
    
    try:
        return cfg[param]
    except:
        if default != "_nodefault":
            return default
    _msg = f"getcfg - Config parameter <{param}> not in cfg and no default."
    raise ConfigError (_msg)


#=====================================================================================
#=====================================================================================
#  C l a s s   t i m e v a l u e
#=====================================================================================
#=====================================================================================
class timevalue():
    def __init__(self, orig_val):
        """
## Class timevalue (orig_val) - Convert time value strings of various resolutions to seconds

`timevalue()` provides a convenience mechanism for working with time values and time/datetime calculations.
timevalues are generally an integer value with an attached single character time resolution, such as "5m".
Supported timevalue units are 's'econds, 'm'inutes, 'h'ours, 'd'ays, and 'w'eeks, and are case insensitive. 
`timevalue()` also accepts integer and float values, which are interpreted as seconds resolution. Also see retime().


### Parameters
`orig_val`
- The original, passed-in value of type str, int, or float


### Returns
- Handle to instance
- Raises ValueError if given an unsupported time unit suffix.


### Instance attributes
- `.orig_val` - orig_val value passed in, type str (converted to str if int or float passed in)
- `.seconds` - time value in seconds resolution, type float, useful for time calculations
- `.unit_char` - the single character suffix unit of the `orig_val` value.  's' for int and float orig_val values.
- `.unit_str` - the long-form units of the `orig_val` value useful for printing/logging ("secs", "mins", "hours", "days", or "weeks")


### Member functions
- timevalue.stats() - Return a str() listing all attributes of the instance


### Example
```
Given
    xx = timevalue("1m")
    print (xx.stats())
    print (f"Sleep <{xx.seconds}> seconds")
    time.sleep(xx.seconds)

Output:
    .orig_val   :  1m       <class 'str'>
    .seconds    :  60.0     <class 'float'>
    .unit char  :  m        <class 'str'>
    .unit_str   :  mins     <class 'str'>
    Sleep <60.0> seconds
```
        """
        self.orig_val = str(orig_val)

        if type(orig_val) in [int, float]:              # Case int or float
            self.seconds =  float(orig_val)
            self.unit_char = "s"
            self.unit_str =  "secs"
        else:
            try:
                self.seconds = float(orig_val)          # Case str without units
                self.unit_char = "s"
                self.unit_str = "secs"
                return
            except:
                pass
            self.unit_char =  orig_val[-1:].lower()     # Case str with units
            if self.unit_char == "s":
                self.seconds =  float(orig_val[:-1])
                self.unit_str = "secs"
            elif self.unit_char == "m":
                self.seconds =  float(orig_val[:-1]) * 60
                self.unit_str = "mins"
            elif self.unit_char == "h":
                self.seconds =  float(orig_val[:-1]) * 60*60
                self.unit_str = "hours"
            elif self.unit_char == "d":
                self.seconds =  float(orig_val[:-1]) * 60*60*24
                self.unit_str = "days"
            elif self.unit_char == "w":
                self.seconds =  float(orig_val[:-1]) * 60*60*24*7
                self.unit_str = "weeks"
            else:
                raise ValueError(f"Illegal time units <{self.unit_char}> in time string <{orig_val}>")

    def stats(self):
        stats = ""
        stats +=  f".orig_val   :  {self.orig_val:8} {type(self.orig_val)}\n"
        stats +=  f".seconds    :  {self.seconds:<8} {type(self.seconds)}\n"
        stats +=  f".unit char  :  {self.unit_char:8} {type(self.unit_char)}\n"
        stats +=  f".unit_str   :  {self.unit_str:8} {type(self.unit_str)}"
        return stats


#=====================================================================================
#=====================================================================================
#  r e t i m e
#=====================================================================================
#=====================================================================================
def retime(time_sec, unitC):
    """
## retime (time_sec, unitC) - Convert time value in seconds to unitC resolution

`retime()` translates a value is resolution seconds into a new target resolution


### Parameters
`time_sec`
- Time value in resolution seconds, type int or float.

`unitC`
- Target time resolution: "s", "m", "h", "d", or "w" (case insensitive)


### Returns
- `time_sec` value scaled for the specified `unitC`, type float
- Raises ValueError if not given an int or float value for `time_sec`, or given an unsupported 
  unitC time unit suffix.


### Example
```
Given
    xx = timevalue("210H")
    print (f"{xx.orig_val} = {xx.seconds} seconds = {retime(xx.seconds, 'W')} weeks")

Output
    210H = 756000.0 seconds = 1.25 weeks
```
    """
    unitC = unitC.lower()
    if type(time_sec) in [int, float]:
        if unitC == "s":  return time_sec
        if unitC == "m":  return time_sec /60
        if unitC == "h":  return time_sec /60/60
        if unitC == "d":  return time_sec /60/60/24
        if unitC == "w":  return time_sec /60/60/24/7
        raise ValueError(f"Invalid unitC value <{unitC}> passed to retime()")
    else:
        raise ValueError(f"Invalid seconds value <{time_sec}> passed to retime().  Must be type int or float.")


#=====================================================================================
#=====================================================================================
#  r e q u e s t l o c k
#=====================================================================================
#=====================================================================================
def requestlock(caller, lockfile=None, timeout=5):
    """
## requestlock (caller, lockfile, timeout=5) - Lock file request

For tool scripts that may take a long time to run and are run by CRON, the possibility exists that 
a job is still running when CRON wants to run it again, which may create a real mess.
This lock file mechanism is used in https://github.com/cjnaz/rclonesync-V2, as an example.

`requestlock()` places a file to indicate that the current process is busy.
Other processes then attempt to `requestlock()` the same `lockfile` before doing an operation
that would conflict with the process that set the lock.

The `lockfile` is written with `caller` information that indicates which tool script set the lock, and when.
Multiple lock files may be used simultaneously by specifying unique `lockfile` names.


### Parameters
`caller`
- Info written to the lock file and displayed in any error messages

`lockfile` (default /tmp/\<toolname>_LOCK)
- Lock file name, relative to the system tempfile.gettempdir(), or absolute path

`timeout` (default 5s)
- Time in seconds to wait for the lockfile to be removed by another process before returning with a `-1` result.
  `timeout` may be an int, float or timevalue string (eg, '5s').


### Returns
- `0` on successfully creating the `lockfile`
- `-1` if failed to create the `lockfile` (either file already exists or no write access).
  A WARNING level message is also logged.
    """

    if lockfile == None:
        lockfile = tool.toolname + "_LOCK"
    lock_file = mungePath(lockfile, tempfile.gettempdir())

    fail_time = time.time() + timevalue(timeout).seconds
    while True:
        if not lock_file.exists:
            try:
                mungePath(lock_file.parent, mkdir=True)     # Ensure directory path exists
                with lock_file.full_path.open('w') as ofile:
                    ofile.write(f"Locked by <{caller}> at {time.asctime(time.localtime())}.")
                    logging.debug (f"<{lock_file.full_path}> locked by <{caller}> at {time.asctime(time.localtime())}.")
                return 0
            except Exception as e:
                logging.warning(f"Unable to create lock file <{lock_file.full_path}>\n  {e}")
                return -1
        else:
            if time.time() > fail_time:
                break
        time.sleep(0.1)

    try:
        with lock_file.full_path.open() as ifile:
            lockedBy = ifile.read()
        logging.warning (f"Timed out waiting for lock file <{lock_file.full_path}> to be cleared.  {lockedBy}")
    except Exception as e:
        logging.warning (f"Timed out and unable to read existing lock file <{lock_file.full_path}>\n  {e}.")
    return -1


#=====================================================================================
#=====================================================================================
#  r e l e a s e l o c k
#=====================================================================================
#=====================================================================================
def releaselock(lockfile=None):
    """
## releaselock (lockfile) - Release a lock file

Any code can release a lock, even if that code didn't request the lock.
Generally, only the requester should issue the releaselock.
A common use is with a tool script that runs periodically by CRON, but may take a long time to complete.  Using 
file locks ensures that the tool script does not run if the prior run has not completed.


### Parameters
`lockfile` (default /tmp/\<toolname>_LOCK)
- Lock file name, relative to the system tempfile.gettempdir(), or absolute path


### Returns
- `0` on successfully `lockfile` release (lock file deleted)
- `-1` if failed to delete the `lockfile`, or the `lockfile` does not exist.  A WARNING level message is also logged.
    """

    if lockfile == None:
        lockfile = tool.toolname + "_LOCK"
    lock_file = mungePath(lockfile, tempfile.gettempdir())
    if lock_file.exists:
        try:
            lock_file.full_path.unlink()
        except Exception as e:
            logging.warning (f"Unable to remove lock file <{lock_file.full_path}>\n  {e}.")
            return -1
        logging.debug(f"Lock file removed: <{lock_file.full_path}>")
        return 0
    else:
        logging.warning(f"Attempted to remove lock file <{lock_file.full_path}> but the file does not exist.")
        return -1


#=====================================================================================
#=====================================================================================
#  s n d _ n o t i f
#=====================================================================================
#=====================================================================================
def snd_notif(subj="Notification message", msg="", to="NotifList", log=False):
    """
## snd_notif (subj="Notification message, msg="", to="NotifList", log=False) - Send a text message using info from the config file

Intended for use of your mobile provider's email-to-text bridge email address, eg, 
5405551212@vzwtxt.com for Verizon, but any eamil address will work.

The `to` string may be the name of a confg param (who's value is one or more email addresses, default 
"NotifList"), or a string with one or more email addresses. Using a config param name allows for customizing the
`to` addresses without having to edit the code.

The messages to send is passed in the `msg` parameter as a text string.

    
### Parameters
`subj` (default "Notification message")
- Text message subject field

`msg` (default "")
- Text message body

`to` (default "NotifList")
- To whom to send the message. `to` may be either an explicit string list of email addresses
(whitespace or comma separated) or a config param name (also listing one
or more whitespace or comma separated email addresses).  If the `to` parameter does not
contain an '@' it is assumed to be a config param.

`log` (default False)
- If True, logs that the message was sent at the WARNING level. If False, logs 
at the DEBUG level. Useful for eliminating separate logging messages in the tool script code.
The `subj` field is part of the log message.


### cfg dictionary params
`NotifList` (optional)
- string list of email addresses (whitespace or comma separated).  
Defining `NotifList` in the config is only required if any call to `snd_notif()` uses this
default `to` parameter value.

`DontNotif` (default False)
- If True, notification messages are not sent. Useful for debug. All email and notification
messages are also blocked if `DontEmail` is True.


### Returns
- NoneType
- Raises SndEmailError on error


### Behaviors and rules
- `snd_notif()` uses `snd_email()` to send the message. See `snd_email()` for related setup.
    """

    if getcfg('DontNotif', default=False)  or  getcfg('DontEmail', default=False):
        if log:
            logging.warning (f"Notification NOT sent <{subj}> <{msg}>")
        else:
            logging.debug (f"Notification NOT sent <{subj}> <{msg}>")
        return

    try:
        snd_email (subj=subj, body=msg, to=to)
        if log:
            logging.warning (f"Notification sent <{subj}> <{msg}>")
        else:
            logging.debug (f"Notification sent <{subj}> <{msg}>")
    except:
        # pass
        logging.warning (f"Notification send failed <{subj}> <{msg}>")
        raise


#=====================================================================================
#=====================================================================================
#  s n d _ e m a i l
#=====================================================================================
#=====================================================================================
def snd_email(subj, to, body=None, filename=None, htmlfile=None, log=False):
    """
## snd_email (subj, to, body=None, filename=None, htmlfile=None, log=False)) - Send an email message using info from the config file

The `to` string may be the name of a confg param (who's value is one or more email addresses),
or a string with one or more email addresses. Using a config param name allows for customizing the
`to` addresses without having to edit the code.

What to send may be a `body` string, the text contents of `filename`, or the HTML-formatted contents
of `htmlfile`, in this order of precendent.

    
### Parameters
`subj`
- Email subject text

`to`
- To whom to send the message. `to` may be either an explicit string list of email addresses
(whitespace or comma separated) or a config param name (also listing one
or more whitespace or comma separated email addresses).  If the `to` parameter does not
contain an '@' it is assumed to be a config param.

`body` (default None)
- A string message to be sent

`filename` (default None)
- A str or Path to the file to be sent, relative to the `tool.cache_dir`, or an absolute path.

`htmlfile` (default None)
- A str or Path to the html formatted file to be sent, relative to the `tool.cache_dir`, or an absolute path.

`log` (default False)
- If True, logs that the message was sent at the WARNING level. If False, logs 
at the DEBUG level. Useful for eliminating separate logging messages in the tool script code.
The `subj` field is part of the log message.


### cfg dictionary params
`EmailFrom`
- An email address, such as `me@myserver.com`

`EmailServer`
- The SMTP server name, such as `mail.myserver.com`

`EmailServerPort`
- The SMTP server port (one of `P25`, `P465`, `P587`, or `P587TLS`)

`EmailUser`
- Username for `EmailServer` login, if required by the server

`EmailPass`
- Password for `EmailServer` login, if required by the server

`DontEmail` (default False)
- If True, messages are not sent. Useful for debug. Also blocks `snd_notif()` messages.

`EmailVerbose` (default False)
- If True, detailed transactions with the SMTP server are sent to stdout. Useful for debug.


### Returns
- NoneType
- Raises SndEmailError on error


### Behaviors and rules
- One of `body`, `filename`, or `htmlfile` must be specified. Looked for in this order, and the first 
found is used.
- EmailServerPort must be one of the following:
  - P25:  SMTP to port 25 without any encryption
  - P465: SMTP_SSL to port 465
  - P587: SMTP to port 587 without any encryption
  - P587TLS:  SMTP to port 587 and with TLS encryption
- It is recommneded (not required) that the email server params be placed in a user-read-only
file in the user's home directory, such as `~/creds_SMTP`, and imported by the main config file.
Some email servers require that the `EmailFrom` address be of the same domain as the server, 
so it may be practical to bundle `EmailFrom` with the server specifics.  Place all of these in 
`~/creds_SMTP`:
  - `EmailFrom`, `EmailServer`, `EmailServerPort`, `EmailUser`, and `EmailPass`
- `snd_email()` does not support multi-part MIME (an html send wont have a plain text part).
- Checking the validity of email addresses is very basic... an email address must contain an '@'.
    """

    # Deal with what to send
    if body:
        msg_type = "plain"
        m_text = body

    elif filename:
        xx = mungePath(filename, tool.cache_dir)
        try:
            msg_type = "plain"
            with Path.open(xx.full_path) as ifile:
                m_text = ifile.read()
        except Exception as e:
            _msg = f"snd_email - Message subject <{subj}>:  Failed to load <{xx.full_path}>.\n  {e}"
            raise SndEmailError (_msg)

    elif htmlfile:
        xx = mungePath(htmlfile, tool.cache_dir)
        try:
            msg_type = "html"
            with Path.open(xx.full_path) as ifile:
                m_text = ifile.read()
        except Exception as e:
            _msg = f"snd_email - Message subject <{subj}>:  Failed to load <{xx.full_path}>.\n  {e}"
            raise SndEmailError (_msg)

    else:
        _msg = f"snd_email - Message subject <{subj}>:  No body, filename, or htmlfile specified."
        raise SndEmailError (_msg)
    m_text += f"\n(sent {time.asctime(time.localtime())})"

    # Deal with 'to'
    def extract_email_addresses(addresses):
        """Return list of email addresses from comma or whitespace separated string 'addresses'.
        """
        if ',' in addresses:
            tmp = addresses.split(',')
            addrs = []
            for addr in tmp:
                addrs.append(addr.strip())
        else:
            addrs = addresses.split()
        return addrs

    if '@' in to:
        To = extract_email_addresses(to)
    else:
        To = extract_email_addresses(getcfg(to, ""))
    if len(To) == 0:
        _msg = f"snd_email - Message subject <{subj}>:  'to' list must not be empty."
        raise SndEmailError (_msg)
    for address in To:
        if '@' not in address:
            _msg = f"snd_email - Message subject <{subj}>:  address in 'to' list is invalid: <{address}>."
            raise SndEmailError (_msg)

    # Send the message - After above to allow checking of input parameters
    if getcfg('DontEmail', default=False):
        if log:
            logging.warning (f"Email NOT sent <{subj}>")
        else:
            logging.debug (f"Email NOT sent <{subj}>")
        return

    try:
        msg = MIMEText(m_text, msg_type)
        msg['Subject'] = subj
        msg['From'] = getcfg('EmailFrom')
        msg['To'] = ", ".join(To)

        cfg_server = getcfg('EmailServer')
        cfg_port   = getcfg('EmailServerPort')
        if cfg_port == "P25":
            server = smtplib.SMTP(cfg_server, 25)
        elif cfg_port == "P465":
            server = smtplib.SMTP_SSL(cfg_server, 465)
        elif cfg_port == "P587":
            server = smtplib.SMTP(cfg_server, 587)
        elif cfg_port == "P587TLS":
            server = smtplib.SMTP(cfg_server, 587)
            server.starttls()
        else:
            raise ConfigError (f"Config EmailServerPort <{cfg_port}> is invalid")

        if 'EmailUser' in cfg:
            server.login (getcfg('EmailUser'), getcfg('EmailPass'))
        if getcfg("EmailVerbose", False):
            server.set_debuglevel(1)
        server.sendmail(getcfg('EmailFrom'), To, msg.as_string())
        server.quit()

        if log:
            logging.warning (f"Email sent <{subj}>")
        else:
            logging.debug (f"Email sent <{subj}>")
    except Exception as e:
        _msg = f"snd_email:  Send failed for <{subj}>:\n  <{e}>"
        raise SndEmailError (_msg)

