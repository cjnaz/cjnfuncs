#!/usr/bin/env python3
"""cjnfuncs - A collection of support functions for writing clean and effective tool scripts
"""

#==========================================================
#
#  Chris Nelson, 2018-2023
#
# 2.1   231125 - Partitioned on several modules.
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
import logging
import inspect
import platform
from pathlib import Path
import __main__
import appdirs

from .mungePath import mungePath


# Configs / Constants
# FILE_LOGGING_FORMAT    = '{asctime}/{module}/{funcName}/{levelname}:  {message}'    # Classic format
FILE_LOGGING_FORMAT    = '{asctime} {module:>15}.{funcName:20} {levelname:>8}:  {message}'
CONSOLE_LOGGING_FORMAT = '{module:>15}.{funcName:20} - {levelname:>8}:  {message}'
# CONSOLE_LOGGING_FORMAT = '{pathname:>15}.{funcName:20} - {levelname:>8}:  {message}'

DEFAULT_LOGGING_LEVEL  = logging.WARNING
MAIN_MODULE_STEM       = Path(__main__.__file__).stem
SND_EMAIL_NTRIES       = 3          # Number of tries to send email before aborting
SND_EMAIL_WAIT         = '5s'       # seconds between retries

# Project globals


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
# print ("calling_module.__package__:", calling_module.__package__)
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
def setuplogging(call_logfile=None, call_logfile_wins=False, config_logfile=None, ConsoleLogFormat=None, FileLogFormat=None):
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
        # log_format = logging.Formatter(getcfg("ConsoleLogFormat", CONSOLE_LOGGING_FORMAT), style='{')
        _fmt = CONSOLE_LOGGING_FORMAT  if ConsoleLogFormat == None  else  ConsoleLogFormat
        log_format = logging.Formatter(_fmt, style='{')
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(log_format)
        logger.addHandler(handler)

        tool.log_dir = None
        tool.log_file = None
        tool.log_full_path = "__console__"

    else:
        mungePath(_lfp.parent, mkdir=True)  # Force make the target dir
        # log_format = logging.Formatter(getcfg("FileLogFormat", FILE_LOGGING_FORMAT), style='{')
        _fmt = FILE_LOGGING_FORMAT  if FileLogFormat == None  else  FileLogFormat
        log_format = logging.Formatter(_fmt, style='{')
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
`\_\_repr\_\_()`
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
tool = set_toolname("wanstatus")
print (tool)
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
        global tool             # Tool info is accessed via core.tool...
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


    # def stats(self):
    #     return self.__repr__()

    def __repr__(self):
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
        stats +=  f".log_full_path    :  {self.log_full_path}" #\n"
        return stats

