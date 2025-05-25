#!/usr/bin/env python3
"""cjnfuncs - Establish the base environment for cjnfuncs
"""

#==========================================================
#
#  Chris Nelson, 2018-2025
#
# TODO Identification of the main module / tool script file may be wrong if a script imports a script that then imports cjnfuncs.
#==========================================================

import sys
import logging
import inspect
import platform
from pathlib import Path
import __main__
import appdirs
import datetime


# Configs / Constants
# FILE_LOGGING_FORMAT    = '{asctime}/{module}/{funcName}/{levelname}:  {message}'    # Classic format
FILE_LOGGING_FORMAT    = '{asctime} {module:>15}.{funcName:20} {levelname:>8}:  {message}'
CONSOLE_LOGGING_FORMAT = '{module:>15}.{funcName:20} - {levelname:>8}:  {message}'


# Get the main / calling module info (who imported cjnfuncs.core)
stack = inspect.stack()
calling_module = ""
for item in stack:  # Look for the import cjnfuncs line
    code_context = item[4]
    if code_context is not None:
        if "cjnfuncs" in code_context[0]:
            calling_module = inspect.getmodule(item[0])
            break


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
#  C l a s s   s e t _ t o o l n a m e
#=====================================================================================
#=====================================================================================

class set_toolname():
    """
## Class set_toolname (toolname) - Set target directories for config and data storage

set_toolname() centralizes and establishes a set of base directory path variables for use in
the tool script.  It looks for existing directories, based on the specified toolname, in
the site-wide (system-wide) and then user-specific locations.  Specifically, site-wide 
config and/or data directories are looked for at `/etc/xdg/<toolname>` and/or 
`/usr/share/<toolname>`.  If site-wide directories are not 
found then user-specific is assumed.  No directories are created.


### Args
`toolname` (str)
- Name of the tool


### Returns
- Handle to the `set_toolname()` instance.
- The handle is also stored in the `core.tool` global.  See examples for proper access.


### Behaviors, rules, and _variances from the XDG spec and/or the appdirs package_
- For a `user` setup, the `.log_dir_base` is initially set to the `.user_data_dir` (a variance from XDG spec).
If a config file is subsequently
loaded then the `.log_dir_base` is changed to the `.user_config_dir`.  (Not changed for a `site` setup.)
Thus, for a `user` setup, logging defaults to the configuration directory.  This is a 
style variance, and can be reset in the tool script by reassigning: `core.tool.log_dir_base = core.tool.user_log_dir` (or any
other directory) before a subsequent call to `loadconfig()` or `setuplogging()`.
(The XDG spec says logging goes to the `.user_state_dir`, while appdirs sets it to the `.user_cache_dir/log`.)

- The last operation within `set_toolname()` is to call `setuplogging()`, which initializes the root
logger to log to the console.  The `.log_dir` and `.log_file` attributes are set to `None`, while 
`.log_full_path` is set to `__console__`.  Having `set_toolname()` call `setuplogging()` ensures that any logging events
before a user-code call to `setuplogging()` or `loadconfig()` are properly logged.

- For a `site` setup, the `.site_data_dir` is set to `/usr/share/<toolname>`.  The XDG spec states that 
the `.cache_dir` and `.state_dir` should be in the root user tree; however, set_toolname() sets these two 
also to the `.site_data_dir`.

    """
    def __init__(self, toolname):
        global tool             # Tool info is accessed via core.tool...
        tool = self
        self.toolname  = toolname
        self.main_module        = calling_module
        try:
            self.main_full_path = Path(self.main_module.__file__)
            self.main_dir       = self.main_full_path.parent
        except:                 # Referencing an installed module's file/path may not be legal
            self.main_full_path = None
            self.main_dir       = None
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

        setuplogging()

    def __repr__(self):
        stats = ""
        stats +=  f"\nStats for set_toolname <{self.toolname}>:\n"
        stats +=  f".toolname         :  {self.toolname}\n"
        stats +=  f".main_module      :  {self.main_module}\n"
        stats +=  f".main_full_path   :  {self.main_full_path}\n"
        stats +=  f".main_dir         :  {self.main_dir}\n"

        stats +=  f"General user and site paths:\n"
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
        stats +=  f".log_full_path    :  {self.log_full_path}"
        return stats


#=====================================================================================
#=====================================================================================
#  s e t u p l o g g i n g
#=====================================================================================
#=====================================================================================

def setuplogging(call_logfile=None, call_logfile_wins=False, config_logfile=None, ConsoleLogFormat=None, FileLogFormat=None):
    """
## setuplogging (call_logfile=None, call_logfile_wins=False, config_logfile=None, ConsoleLogFormat=None, FileLogFormat=None) - Set up the root logger

Logging may be directed to the console (stdout), or to a file.  Each time setuplogging()
is called the current/active log file (or console) may be reassigned.

setuplogging() works standalone or in conjunction with `cjnfuncs.configman.loadconfig()`.
If a loaded config file has a `LogFile` parameter then loadconfig() passes it's value thru
`config_logfile`.  loadconfig() also passes along any `call_logfile` and `call_logfile_wins`
that were passed to loadconfig() from the tool script.  This mechanism allows the tool script
to override any config `LogFile`, such as for directing output to the console for a tool script's 
interactive use.  For example, this call will set logging output to the console regardless of 
the log file declared in the config file:

    setuplogging (call_logfile=None, call_logfile_wins=True, config_logfile='some_logfile.txt')

    
### Args
`call_logfile` (Path or str, default None)
- Potential log file passed typically from the tool script.  Selected by `call_logfile_wins = True`.
call_logfile may be an absolute path or relative to the `core.tool.log_dir_base` directory.  
- `None` specifies the console.

`call_logfile_wins` (bool, default False)
- If True, the `call_logfile` is selected.  If False, the `config_logfile` is selected.

`config_logfile` (str, default None)
- Potential log file passed typically from loadconfig() if there is a `LogFile` param in the 
loaded config.  Selected by `call_logfile_wins = False`.
config_logfile may be an absolute path or relative to the `core.tool.log_dir_base` directory.  
- `None` specifies the console.

`ConsoleLogFormat` (str, default None)
- Overrides the default console logging format: `{module:>15}.{funcName:20} - {levelname:>8}:  {message}`.
- loadconfig() passes `ConsoleLogFormat` from the primary config file, if defined.

`FileLogFormat` (str, default None)
- Overrides the default file logging format: `{asctime} {module:>15}.{funcName:20} {levelname:>8}:  {message}`.
- loadconfig() passes `FileLogFormat` from the primary config file, if defined.


### Returns
- NoneType
    """

    from .mungePath import mungePath


    _lfp = "__console__"
    if call_logfile_wins == False  and  config_logfile:
        _lfp = mungePath(config_logfile, tool.log_dir_base)

    if call_logfile_wins == True   and  call_logfile:
        _lfp = mungePath(call_logfile, tool.log_dir_base)

    logger = logging.getLogger()

    if _lfp == "__console__":
        _fmt = CONSOLE_LOGGING_FORMAT  if ConsoleLogFormat == None  else  ConsoleLogFormat
        log_format = logging.Formatter(_fmt, style='{')
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(log_format)
        logger.handlers.clear()
        logger.addHandler(handler)

        tool.log_dir = None
        tool.log_file = None
        tool.log_full_path = "__console__"

    else:
        mungePath(_lfp.parent, mkdir=True)      # Force make the target dir
        _fmt = FILE_LOGGING_FORMAT  if FileLogFormat == None  else  FileLogFormat
        log_format = logging.Formatter(_fmt, style='{')
        handler = logging.FileHandler(_lfp.full_path, "a")
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(log_format)
        logger.handlers.clear()
        logger.addHandler(handler)
    
        tool.log_dir = _lfp.parent
        tool.log_file = _lfp.name
        tool.log_full_path = _lfp.full_path


#=====================================================================================
#=====================================================================================
#   s e t _ l o g g i n g _ l e v e l ,   r e s t o r e _ l o g g i n g _ l e v e l
#=====================================================================================
#=====================================================================================

ll_history = []
def set_logging_level(new_level, clear=False, save=True):
    """
## set_logging_level (new_level, clear=False) - Save the current logging level and set the new_level

The current logging level is saved on a stack and can be restored by a call to restore_logging_level.


### Args
`new_level` (int)
- The new logging level to be set.  Values may be set to the logging module defined levels, or their integer 
equivalents (or to any integer value that makes sense):  logging.DEBUG (10), logging.INFO (20), logging.WARNING (30), 
logging.ERROR (40), or logging.CRITICAL (50).

`clear` (bool, default False)
- If True, the logging level history stack is cleared.

`save` (bool, default True)
- If True, the current logging level is saved to the stack
- If clear=True, then the clear is done first.  If save=True also then the stack will have only the prior logging level


### Returns
- NoneType
    """     # TODO clear stack
    global ll_history
    if clear:
        ll_history = []
    if save:
        ll_history.append(logging.getLogger().level)
    logging.getLogger().setLevel(new_level)



def restore_logging_level():
    """
## restore_logging_level () - Restore the prior logging level from the stack

The prior saved logging level (from the prior set_logging_level call) is popped from the stack and set as the current logging level.
If the stack is empty then the logging level is set to logging.WARNING (30).


### Returns
- NoneType
    """
    global ll_history
    try:
        logging.getLogger().setLevel(ll_history.pop())
    except:
        logging.getLogger().setLevel(logging.WARNING)


def get_logging_level_stack():
    """
## get_logging_level_stack () - Return the content of the stack

Useful for debug.  The stack may be cleared with a call to `set_logging_level()`.


### Returns
- A list of the prior saved logging levels.
"""
    return ll_history


#=====================================================================================
#=====================================================================================
#   p e r i o d i c _ l o g
#=====================================================================================
#=====================================================================================

cats = {}

class _periodic_log:
    def __init__(self, log_interval, log_level):

        from .timevalue import timevalue

        self.next_dt = datetime.datetime.now()
        self.log_interval = datetime.timedelta(seconds=timevalue(log_interval).seconds)
        self.log_level = log_level

    def plog(self, message, log_level, cat):
        now_dt = datetime.datetime.now()
        if now_dt > self.next_dt:
            if log_level is None:
                log_level = self.log_level
            logging.log(log_level, f"[PLog-{cat}] {message}")
            self.next_dt = now_dt + self.log_interval


def periodic_log(message, category='Cat1', log_interval='10m', log_level=None):
    """## periodic_log(message, category='Cat1', log_interval='10m', log_level=30)

Log a message infrequently, so as to avoid flooding the log.  The `category` arg provides for independent
log intervals for different types of logging events.


### Args

`message` (str)
- The message text to be logged, if the first time for this `category` or the log_interval has expired

`category` (int or str, default 'Cat1')
- Allows for multiple, independent concurrent periodic_log streams
- `category` should typically be an int or str.  Used as a dict key.

`log_interval` (timevalue, default '10m')
- How often this category's messages will be logged.  Only remembered on the first log call
for this category (ignored of subsequent calls)

`log_level` (int, default logging.WARNING/30)
- The default for this category is set on first call
- This default value may be overridden on subsequent calls for this category


### Returns
- NoneType
      """
    if category not in cats:
        if log_level is None:
            log_level = logging.WARNING
        xx = _periodic_log(log_interval, log_level)
        cats[category] = xx
    
    p_logger = cats[category]
    p_logger.plog(message, log_level, category)
