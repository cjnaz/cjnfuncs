#!/usr/bin/env python3
"""cjnfuncs.configman - Configuration files made easy and useful
"""

#==========================================================
#
#  Chris Nelson, 2018-2025
#
#==========================================================

import re
import ast
import time
import sys
import datetime
from threading import Thread

from .core      import setuplogging, logging, ConfigError #, set_logging_level, restore_logging_level, pop_logging_level_stack, get_logging_level_stack
from .mungePath import mungePath, check_path_exists
from .rwt       import run_with_timeout
from .timevalue import timevalue, get_next_dt

import cjnfuncs.core as core

# Configs / Constants
RWT_NTRIES =    3
RWT_TIMEOUT =   2.0

# Logging events within this module are at the INFO and DEBUG levels.  With this module's child logger set to
# a minimum of WARNING level by default, then logging from this module is effectively disabled.  To enable
# logging from this module add this within your tool script code:
#       logging.getLogger('cjnfuncs.configman').setLevel(logging.DEBUG)
configman_logger = logging.getLogger('cjnfuncs.configman')


#=====================================================================================
#=====================================================================================
#  C l a s s   c o n f i g _ i t e m
#=====================================================================================
#=====================================================================================

initial_logging_setup_done = False   # Global since more than one config can be loaded


class config_item():
    """
## Class config_item (config_file=None, remap_logdirbase=True, force_str=False, secondary_config=False, safe_mode=False) - Create a configuration instance
The config_item() class provides handling of one or more config file instances.  Class methods include:
 - Config file loading and reloading - `loadconfig()`
 - Loading config data from strings and dictionaries - `read_string()`, `read_dict()`
 - Getting values from the loaded config, with defaults and fallback - `getcfg()`
 - Programmatically modifying the config file content - `modify_configfile()`
 - Getting instance status - `__repr__()`, `section()`, `dump()`

See the loadconfig() documentation for details on config file syntax and rules.


### Instantiation args
`config_file` (Path or str, default None)
- Path to the configuration file, relative to the `core.tool.config_dir` directory, or an absolute path.
- `None` may be used if the config will be loaded programmatically via `read_string()` or `read_dict()`.

`remap_logdirbase` (bool, default True)
- If `remap_logdirbase=True` and the tool script is running in _user_ mode (not site mode) 
then the `core.tool.log_dir_base` will be set to `core.tool.config_dir`.

`force_str` (bool, default False)
- Causes all params to be loaded as type `str`, overriding the default type identification.

`secondary_config` (bool, default False)
- Set to True when loading additional config files.  Disables logging setup related changes.
- The primary config file should be loaded first before any secondary_config loads, so that logging 
is properly set up.

`safe_mode` (bool, default False)
- If `safe_mode=True` then timeouts are enforced when checking for config files.
- If `safe_mode=False` then checks for the existence of config files runs the risk of application hang.
- See Behavior NOTE below.


### Useful class attributes
The current values of all public class attributes may be printed using `print(my_config)`.

`.cfg` (dict)
- Holds all loaded params.  May be access directly.  Sections are stored as sub-dictionaries of .cfg.
- The contents of the .cfg dictionary may be printed using `print(my_config.dump())`

`.defaults` (dict)
- Default params are stored here.

`.sections_list` (list)
- A list of string names for all defined sections

`.config_file` (str, or None)
- The `config_file` as passed in at instantiation

`.config_full_path` (Path or None)
- The full expanduser/expandvars path to the config file, relative to core.tool.config_dir if the
instantiation `config_file` is a relative path (uses mungePath)

`.config_dir` (Path or None)
- The directory above  `.config_full_path`


### Returns
- Handle to the `config_item()` instance
- Raises a `ConfigError` if the specified config file is not found


### Behaviors and rules
1. More than one `config_item()` may be created and loaded.  This allows for configuration data to be partitioned 
as desired.  Each defined config is loaded to its own instance-specific `cfg` dictionary. Only one config_item()
instance should be considered the primary, while other instances should be tagged with `secondary_config=True`. 
Logging setups are controlled only by the primary config instance.
Also see the loadconfig() `import` feature.

1. NOTE:  On Linux the cost of `safe_mode=True` when searching for a quickly found config file is negligible 
(Linux uses process fork), but on Windows (uses process spawn) the minimum execution time for a file 
existence check can be 1 to 2 seconds.  When `safe_mode=False` and the config file is on a network share 
drive, the file existence check can cause a indefinite blocking hang of your tool script if the network 
goes down (true for both Linux and Windows).  So, use `safe_mode=False` if your config files are on a local 
drive, and use `safe_mode=True` if your config files are on a network drive.  Recognize that on Windows 
this will perhaps cause significant delays.

1. Initially in _user_ mode, after the `set_toolname()` call, `core.tool.log_dir_base` 
(the log directory) is set to the `core.tool.user_data_dir`.
Once `config_item()` is called the `core.tool.log_dir_base` is _remapped_ to 
`core.tool.config_dir`.  This is the author's style preference (centralize primary files, and 
reduce spreading files around the file system).
To disable this remap, in the `config_item()` call set `remap_logdirbase=False`.
This remapping is not done in site mode.

1. A different log base directory may be set by user code by setting `core.tool.log_dir_base` to a different 
path after the `set_toolname()` call and before the `config_item()` call, for example 
`core.tool.log_dir_base = "/var/log"` may be desirable in site mode.

1. A different config directory may be set by user code by setting `core.tool.config_dir` to a different 
path after the `set_toolname()` call and before the `config_item()` call, for example 
`core.tool.config_dir = core.tool.main_dir` sets the config dir to the same as the tool script's 
directory.  With `remap_logdirbase=True`, the log dir will also be set to the tool script's directory.

1. Details of the configuration instance may be printed, eg, `print(my_config)`.

1. Logging of the operations within loadconfig() and (other configman methods) may be controlled with setting 
the named child logger `cjnfuncs.configman` to INFO or DEBUG level (the default logging level is WARNING which
produces no logging events from this module), eg:

        logging.getLogger('cjnfuncs.configman').setLevel(logging.INFO)
    """

    def __init__(self, config_file=None, remap_logdirbase=True, force_str=False, secondary_config=False, safe_mode=False, missing_ok=False):
        global tool

        self.force_str =            force_str
        self.secondary_config =     secondary_config
        self.safe_mode =            safe_mode
        self.loaded =               False
        self.cfg =                  {}
        self.current_section_name = ''
        self.sections_list =        []
        self.defaults =             {}

        if config_file == None:
            self.config_file =      None
            self.config_dir =       None
            self.config_full_path = None
            self.config_timestamp = 0
            self.config_content =   ''        # Used by modify_configfile()
        else:
            config_mp = mungePath(config_file, core.tool.config_dir)
            found_it = False
            if self.safe_mode:
                if run_with_timeout(config_mp.full_path.is_file, rwt_ntries=RWT_NTRIES, rwt_timeout=RWT_TIMEOUT):
                    found_it = True
            else:
                if config_mp.full_path.is_file():
                    found_it = True
            if found_it  or  missing_ok:
                self.config_file =      config_mp.name
                self.config_dir =       config_mp.parent
                self.config_full_path = config_mp.full_path
                self.config_timestamp = 0
                self.config_content =   ''    # Used by modify_configfile()
            else:
                raise ConfigError (f"Config file <{config_file}> not found.")

        if remap_logdirbase  and  core.tool.log_dir_base == core.tool.user_data_dir:
            core.tool.log_dir_base = core.tool.config_dir


    def _add_key(self, key, value, section=''):
        if section == '':
            self.cfg[key] = value
        elif section == 'DEFAULT':
            self.defaults[key] = value
        else:
            self.cfg[section][key] = value


#=====================================================================================
#=====================================================================================
#  l o a d c o n f i g
#=====================================================================================
#=====================================================================================

    def loadconfig(self,
            call_logfile =      None,
            call_logfile_wins = False,
            flush_on_reload =   False,
            force_reload =      False,
            isimport =          False,
            tolerate_missing =  False,
            prereload_callback= None):
        r"""
## loadconfig () - Load a configuration file into the cfg dictionary
```
loadconfig(
    call_logfile =      None,
    call_logfile_wins = False,
    flush_on_reload =   False,
    force_reload =      False,
    isimport =          False,
    tolerate_missing =  False,
    prereload_callback= None)
```
***config_item() class member function***

`Param = value` lines in the config_item()'s file are loaded to the instance-specific `cfg` dictionary, 
and can be accessed via `<config_item>.getcfg()`.  The _value_ is referred to as the _value_portion_ in 
this documentation.

`loadconfig()` initializes the root logger for logging either to 1) the `LogFile` specified in
the loaded config file, 2) the `call_logfile` in the `loadconfig()` call, or 3) the console.
`loadconfig()` supports dynamic reloading of config files, partitioning of config data via the `import`
feature, and intermittent loss of access to the config file.
    

### Args
`call_logfile` (Path or str, default None)
- If `call_logfile` is passed on the loadconfig() call, and `call_logfile_wins=True`, then any `LogFile`
specified in the config file is overridden.  This feature allows for interactive usage modes where
logging is directed to the console (with `call_logfile=None`) or an alternate file.
- An absolute path or relative to the `core.tool.log_dir_base` directory

`call_logfile_wins` (bool, default False)
- If True, the `call_logfile` overrides any `LogFile` defined in the config file

`flush_on_reload` (bool, default False)
- If the config file will be reloaded (due to a changed timestamp) then clean out the 
`cfg` dictionary first.  See Returns, below.

`force_reload` (bool, default False)
- Forces the config file to be reloaded regardless of whether the config file timestamp has changed.
- Also set `flush_on_reload=True` to clean out the `cfg` dictionary before reloading.

`isimport` (bool, default False)
- Internally set True when handling imports.  Not used by tool script calls.

`tolerate_missing` (bool, default False)
- Used in a tool script service loop, return `-1` rather than raising `ConfigError` if the config file is inaccessible

`prereload_callback` (function, default None)
- Allows user services to be managed (paused/terminated) before the config is reloaded and logging is reset.

### Returns
- `1` if the config files WAS reloaded
- `0` if the config file was NOT reloaded
- If the config file cannot be accessed
  - If tolerate_missing == False (default), then raises `ConfigError`
  - If tolerate_missing == True, then returns `-1`
- A ConfigError is raised if there are parsing issues
- A ConfigError is also raised if an imported config file cannot be loaded (non-existent)


### Behaviors and rules
1. See `getcfg()`, below, for accessing loaded config data. The class instance-specific `cfg` dictionary may be
  directly accessed as well.

1. The format of a config file is param=value pairs.
   - Separating the param and value_portion may be whitespace, `=` or `:` (multiples allowed).
   - Param names can contain all valid characters, except the separators or `#`, and cannot start with `[`.

1. Sections and a DEFAULT section are supported.  Section name are enclosed in `[ ]`.
   - Leading and trailing whitespace is trimmed off of the section name, and embedded whitespace is retained.
    EG: `[  hello my name  is  Fred  ]` becomes section name `'hello my name  is  Fred'`.
   - Section names can contain most all characters, except `]`.

1. **Native str, int, float, bool, list, tuple, dict, None support** - Bool true/false is case insensitive. A str
  type is stored in the `cfg` dictionary if none of the other types can be resolved for a given value_portion.
  Automatic typing avoids most explicit type casting clutter in the tool script. Be careful to error trap
  for type errors (eg, expecting a float but user input error resulted in a str). Also see the 
  getcfg() and setcfg() `types=[]` arg for basic type enforcement.

1. **Quoted strings** - If a value_portion cannot be resolved to a Python native type then it is loaded as a str,
  eg `My_name = George` loads George as a str.  A value_portion may be forced to be loaded as a str by using 
  quotes, eg `Some_number_as_str = "2.54"` forces the value_portion to be loaded as a str rather than a float. Supported
  quote types:  `"..."`, `'...'`, (triple-double quotes), and `'''...'''`. `My_name = George`, 
  `My_name : "George"`, `My_name '''George'''`, etc., are identical when loaded.
  Quoted strings may contain all valid characters, including '#' which normally starts a comment.  

1. **Multi-line values** - A param's value_portion may be specified over multiple lines for readability by placing 
  the `\` line continuation character as the last non-whitespace character on the line before any comment.
  The parser strips comments and leading/trailing whitespace, then concatenates the multi-line value_portion segments 
  into a single line (single space separated) in the loaded config.  Comments may be placed on each line.
  NOTE: For a multi-line param that will be loaded as a str, avoid using quotes as results may be strange.

1. **Logging setup** - `loadconfig()` calls `cjnfuncs.core.setuplogging()`.  The `logging` handle is available for
  import by other modules (`from cjnfuncs.core import logging`).  By default, logging will go to the
  console (stdout) filtered at the WARNING/30 level. Don't call `setuplogging()` directly if using loadconfig().

1. **Logging level control** - Optional `LogLevel` in the primary config file will set the root logging level after
  the config file has been loaded.  If LogLevel is not specified in the primary config file, then 
  the root logging level is left unchanged (the Python default logging level is 30/WARNING).
  The tool script code may also manually/explicitly set the root logging level _after the initial `loadconfig()` call_
  and this value will be retained over later calls to loadconfig, thus allowing for a command line `--verbose`
  switch feature.  Note that logging done _within_ loadconfig() uses the `cjnfuncs.configman` child/named logger.
  `logging.getLogger('cjnfuncs.configman').setLevel(logging.INFO)` (or DEBUG) enables diagnostic logging from
  loadconfig.

1. **Log file options** - Where to log has two separate fields:  `call_logfile` in the call to loadconfig(), and 
  `LogFile` in the loaded primary config file, with `call_logfile_wins` selecting which is used.  This mechanism allows for
  a command line `--log-file` switch to override a _default_ log file defined in the config file.  If the selected 
  logging location is `None` then output goes to the console (stdout).

    call_logfile_wins | call_logfile | Config LogFile | Results
    --|--|--|--
    False (default) | ignored | None (default) | Console
    False (default) | ignored | file_path | To the config LogFile
    True | None (default) | ignored | Console
    True | file_path | ignored | To the call_logfile

1. **Logging format** - cjnfuncs has default format strings for console and file logging.
  These defaults may be overridden by defining `ConsoleLogFormat` and/or `FileLogFormat`
  in the config file.

1. **Import nested config files** - loadconfig() supports `Import` (case insensitive). The imported file path
is relative to the `core.tool.config_dir`, if not an absolute path.
The specified file is imported as if the params were in the main config file.  Nested imports are allowed. 
Sections are not allowed within an imported file - only in the main/top-level config file.
A prime usage of `import` is to place email server credentials in your home directory with user-only readability,
then import them in the tool script config file as such: `import ~/creds_SMTP`.  

1. **Config reload if changed, `flush_on_reload`, and `force_reload`** - loadconfig() may be called 
periodically by the tool script, such as in a service loop.
If the config file timestamp is unchanged then loadconfig() immediately returns `0`. 
If the timestamp has changed then the config file will be reloaded and `1` is returned to indicate to 
the tool script to do any post-config-load operations. 
   - If `flush_on_reload=True` (default False) then the instance-specific `cfg` dictionary 
  will be cleaned/purged before the config file is reloaded. If `flush_on_reload=False` then the config
  file will be reloaded on top of the existing `cfg` dictionary contents (if a param was 
  deleted in the config
  file it will still exist in `cfg` after the reload). [lanmonitor](https://github.com/cjnaz/lanmonitor) uses the
  `flush_on_reload=True` feature.
   - `force_reload=True` (default False) forces a reload of the config file, either on top of existing loaded data
   with `flush_on_reload=False`, or replacing all existing data with `flush_on_reload=True`.
   - **Note** that if using threading, and a thread is accessing the config data, then the thread should be paused while the config file 
  is being reloaded with `flush_on_reload=True` since the params will disappear briefly.
  Use the `prereload_callback` mechanism to manage any code dependencies before the cfg dictionary is purged.
   - Changes to imported files are not tracked for changes.

1. **Tolerating intermittent config file access** - When implementing a service loop, if `tolerate_missing=True` 
(default False) then loadconfig() will return `-1` if the config file cannot be accessed, informing the 
tool script of the problem for appropriate handling (typically logging the event then ignoring the problem for
the current iteration). If `tolerate_missing=False` then loadconfig() will raise a ConfigError if the config file 
cannot be accessed.
        """

        global initial_logging_setup_done

        if not initial_logging_setup_done:
            # Initial logging will go to the console if no call_logfile is specified (and call_logfile_wins) on the initial loadconfig call.
            console_lf = self.getcfg('ConsoleLogFormat', None)
            file_lf = self.getcfg('FileLogFormat', None)
            setuplogging (call_logfile=call_logfile, call_logfile_wins=call_logfile_wins, ConsoleLogFormat=console_lf, FileLogFormat=file_lf)
            initial_logging_setup_done = True

        config = self.config_full_path

        # Operations only on top-level config file
        is_top_level = not isimport
        if is_top_level:

            if force_reload:
                if not flush_on_reload:
                    configman_logger.info(f"Config  <{self.config_file}>  Force reload, not flushed")
                else:
                    self.clear()
                    configman_logger.info(f"Config  <{self.config_file}>  Force reload, flushed first")
                # configman_logger.info(f"Config  <{self.config_file}>  force reloaded (force_reload)")
                # if flush_on_reload:
                #     self.clear()
                #     configman_logger.info(f"Config  <{self.config_file}>  flushed (flush_on_reload)")
                self.config_timestamp = 0                       # Force reload of the config file

            # Check if config file is available and has changed
            _exists = False
            if self.safe_mode:
                if check_path_exists(config, ntries=RWT_NTRIES, timeout=RWT_TIMEOUT):
                    _exists = True
            else:
                if config.exists():
                    _exists = True

            if not _exists:
                if tolerate_missing:
                    configman_logger.info (f"Config  <{self.config_file}>  file not currently accessible.  Skipping (re)load.")
                    return -1                                   # -1 indicates that the config file cannot currently be found
                else:
                    raise ConfigError (f"Could not find  <{self.config_file}>")

            current_timestamp = int(self.config_full_path.stat().st_mtime)  # force integer-second resolution   # Minor hang risk - above exists check should protect
            if self.config_timestamp == current_timestamp:
                return 0                                        # 0 indicates that the config file was NOT (re)loaded

            # It's an initial load call, or config file has changed, or force_reload...  Do (re)load
            self.config_timestamp = current_timestamp
            if prereload_callback:
                configman_logger.debug("Pre-reload callback user function called")
                prereload_callback()
            configman_logger.info (f"Config  <{self.config_file}>  file timestamp: {current_timestamp}")

            if not force_reload:
                if not self.loaded:
                    configman_logger.info(f"Config  <{self.config_file}>  Initial load")
                    # self.loaded = True
                else:
                    if not flush_on_reload:
                        configman_logger.info(f"Config  <{self.config_file}>  Reload due to changed file, not flushed")
                    else:
                        self.clear()
                        configman_logger.info(f"Config  <{self.config_file}>  Reload due to changed file, flushed first")

            # if flush_on_reload:
            #     if not force_reload:
            #         configman_logger.info (f"Config  <{self.config_file}>  flushed due to changed file (flush_on_reload)")
            #     self.clear()


        # Load the config
            # If there is an import then read_string() recursively calls loadconfig().  Imported configs can in-turn import configs.
            # An exception raised within read_string() while processing an imported config lands at this except clause, and is re-raised
            # to be handled at the next higher level, until we reach the top-level loadconfig() call, and the exception is passed to the 
            # tool script code.
        configman_logger.info (f"Loading  <{config}>")
        try:
            string_blob = config.read_text()        # Minor hang risk - above exists check should protect
            self.read_string (string_blob, isimport=isimport)
            self.loaded = True
        except:
            raise


        # Operations only for finishing a top-level call on the primary config
        if is_top_level  and  not self.secondary_config:

            # Re-setup the root logger, adjusting for config LogFile and logging formats
            console_lf = self.getcfg('ConsoleLogFormat', None)
            file_lf =    self.getcfg('FileLogFormat', None)
            setuplogging(config_logfile=self.getcfg('LogFile', None), call_logfile=call_logfile, call_logfile_wins=call_logfile_wins, ConsoleLogFormat=console_lf, FileLogFormat=file_lf)

            # Apply SMTP module control flags based on config params
            if 'SMTP' in self.sections_list:
                if self.getcfg('DontEmail', False, section='SMTP'):
                    configman_logger.info ("DontEmail is set - Emails and Notifications will NOT be sent")
                elif self.getcfg('DontNotif', False, section='SMTP'):
                    configman_logger.info ("DontNotif is set - Notifications will NOT be sent")

            # Apply LogLevel, if defined in the config
            config_loglevel = self.getcfg('LogLevel', None)
            if config_loglevel is not None:
                try:
                    config_loglevel = int(config_loglevel)      # Handles force_str=True
                except:
                    raise ConfigError (f"Config file <LogLevel> must be integer value (found <{config_loglevel}>)") from None
                configman_logger.info (f"Logging level set to config LogLevel <{config_loglevel}>")
                logging.getLogger().setLevel(config_loglevel)

        self.current_section_name = ''
        return 1                                                # 1 indicates that the config file was (re)loaded


#=====================================================================================
#=====================================================================================
#  r e a d _ s t r i n g
#=====================================================================================
#=====================================================================================

    def read_string(self, str_blob, isimport=False):
        """
## read_string (str_blob, isimport=False) - Load content of a string into the cfg dictionary

***config_item() class member function***

read_string() does the actual work of loading lines of config data into the cfg dictionary. 
Loaded content is added to and/or modifies any previously loaded content.

Note that loadconfig() calls read_string() for the actual loading of config data. loadconfig()
handles the other loading features such as LogLevel, LogFile, logging formatting,
flush_on_reload, force_reload, and tolerate_missing.


### Args
`str_blob` (str)
- String containing the lines of config data

`isimport` (bool, default False)
- Internally set True when handling imports.  Not used by tool script calls.


### Returns
- A ConfigError is raised if there are parsing issues
- A ConfigError is also raised if an imported config file cannot accessed
        """
        continuation_line = False
        split_line_re =     re.compile(r'([^\s=:#]+)[\s=:]*(.*)')       # Identify param - value (with possible comment)
        xx = fr"""
            ('''|\""")                      # Match opening triple quotes
            (?:\\.|(?!\1).)*?\1             # Match content inside triple quotes until matching closing
            |                               # OR
            (["'])(?:\\.|(?!\2).)*?\2       # Match single or double quotes with matching pairs
            |                               # OR
            (\#)                            # Match unquoted # (group 3)
        """
        find_comment_re =   re.compile(xx, re.VERBOSE)                  # Find unquoted '#'
        section_name_re =   re.compile(r'\[([^\]]*)\]')                 # Get section name


        for line in str_blob.split('\n'):

            if line.strip().startswith('['):                            # Section
                section_name = None
                out = section_name_re.match(line.strip())
                if out:
                    section_name = out.group(1).strip()
                    if section_name != ''  and  section_name not in self.sections_list  and  section_name != 'DEFAULT':
                        self.cfg[section_name] = {}
                        self.sections_list.append(section_name)
                if section_name is None:
                    raise ConfigError (f"Malformed section line <{line}>")
                else:
                    if isimport:
                        raise ConfigError ("Section within imported file is not supported.")
                    self.current_section_name = section_name
                continue

            if not continuation_line:
                param_name = value_portion = ''
                out = split_line_re.match(line.strip())
                if out:
                    param_name =        out.group(1)
                    value_portion =     out.group(2)
            else:
                value_portion +=        ' ' + line.strip()
                continuation_line =     False

            if value_portion != '':
                # Remove after first '#' outside of quotes
                for match in find_comment_re.finditer(value_portion):
                    if match.group(3):
                        value_portion = value_portion[:match.start(3)].strip()
                        break

            if value_portion.endswith('\\'):                            # Continuation line
                value_portion =         value_portion[:-1].strip()
                continuation_line =     True
                continue

            if param_name != '':
                if param_name.lower().startswith('import'):             # import line
                    target = mungePath(value_portion, self.config_dir).full_path
                    imported_config = config_item(target, secondary_config=True)
                    imported_config.loadconfig(isimport=True)           # May raise exception, caught by higher level
                    for key in imported_config.cfg:
                        if self.current_section_name == '':
                            self.cfg[key] = imported_config.cfg[key]
                        elif self.current_section_name == 'DEFAULT':
                            self.defaults[key] = imported_config.cfg[key]
                        else:
                            self.cfg[self.current_section_name][key] = imported_config.cfg[key]
                else:                                                   # param - value line
                    if value_portion.lower() == 'true':
                        value_portion = 'True'
                    if value_portion.lower() == 'false':
                        value_portion = 'False'
                    if value_portion == '':
                        value_portion = 'True'
                    if not self.force_str:
                        try:
                            value_portion = ast.literal_eval(value_portion)
                        except:
                            pass                                        # default to str
                    self._add_key(param_name, value_portion, self.current_section_name)
                    configman_logger.debug (f"Loaded {param_name} = <{value_portion}>  ({type(value_portion)})")
        self.loaded = True


#=====================================================================================
#=====================================================================================
#  r e a d _ d i c t
#=====================================================================================
#=====================================================================================

    def read_dict(self, param_dict, section=''):
        """
## read_dict (param_dict, section='') - Load the content of a dictionary into the cfg dictionary

***config_item() class member function***

Loaded content is added to and/or modifies any previously loaded content.

### Args
`param_dict` (dict)
- dictionary to be loaded

`section` (str, default '' (top level))
- section to load the param_dict into.
- The section will be created if not yet existing.
- Content can only be loaded into one section per call to read_dict().


### Returns
- A ConfigError is raised if there are parsing issues


### Example:
```
    new_config = config_item()      # config need not be associated with a file

    main_contents = {
        'a' : 6,
        'b' : 7.0,
        'c' : [6, 7.0, 42, 'hi']
        }
    new_config.read_dict(main_contents)

    sect_contents = {
        'd' : ('hi', 'there'),
        'e' : {'hi':'Hi!', 'there':'There!'},
        'f' : [6, 7.0, 42, 'hi']
        }
    new_config.read_dict(sect_contents, 'A section')

    def_contents = {
        'g' : 'Hi',
        'h' : True,
        'i' : False
        }
    new_config.read_dict(def_contents, 'DEFAULT')
```
        """

        try:
            if section == '':
                for key in param_dict:
                    self.cfg[key] = param_dict[key]
            elif section == 'DEFAULT':
                for key in param_dict:
                    self.defaults[key] = param_dict[key]
            else:
                if section not in self.sections_list:
                    self.cfg[section] = {}
                    self.sections_list.append(section)
                for key in param_dict:
                    self.cfg[section][key] = param_dict[key]
        except Exception:
            raise ConfigError (f"Failed loading dictionary into cfg around key <{key}>")


#=====================================================================================
#=====================================================================================
#  g e t c f g
#=====================================================================================
#=====================================================================================

    def getcfg(self, param, fallback='_nofallback', types=[], section=''):
        """
## getcfg (param, fallback=None, types=[ ], section='') - Get a param's value from the cfg dictionary

***config_item() class member function***

Returns the value of param from the class instance cfg dictionary.  Equivalent to just referencing `my_config.cfg[]`
but with 1) default & fallback support, 2) type checking, and 3) section support.

The search order for a param is 1) from the specified `section`, 2) from the `DEFAULT` section, and 3) from the 
`fallback` value. If the param is not found in any of these locations then a ConfigError is raised.

Type checking may be performed by listing one or more expected types via the optional `types` arg.
If the loaded param is not one of the expected types then a ConfigError is raised.  This check may be 
useful for basic error checking of param values, eg, making sure the return value is a float and not
a str. (str is the loadconfig() default if the param type cannot be converted to another supported type.)

NOTE: `getcfg()` is almost equivalent to `cfg.get()`, except that `getcfg()` does not default to `None`.
Rather, `getcfg()` raises a ConfigError if the param does not exist and no `fallback` is specified.
This can lead to cleaner tool script code.  Either access method may be used, along with `x = my_config.cfg["param"]`.


### Args
`param` (str)
- String name of param to be fetched from cfg

`fallback` (any, default effectively `None`, technically '_nofallback')
- if provided, is returned if `param` does not exist in cfg
- No type enforcement - the fallback value need not be in the `types` list

`types` (single or list of as-expected types, default '[]' (any type accepted))
- if provided, a ConfigError is raised if the param's value type is not in the list of expected types
- `types` may be a single type (eg, `types=int`) or a list of types (eg, `types=[int, float]`)
- Supported types: [str, int, float, bool, list, tuple, dict, type(None)]

`section` (str, default '' (top-level))
- Select the section from which to get the param value


### Returns
- The param value from 1) from the specified `section` if defined, 2) from the `DEFAULT` section if defined,
  or 3) from the `fallback` value if specified.
- If the param is not found, or the param's type is not in the `types` list, if specified, then a ConfigError is raised.
        """

        _value = '__nonevalue__'
        if section == '':                           # Top-level case
            if param in self.cfg:
                _value = self.cfg[param]
            elif param in self.defaults:
                _value = self.defaults[param]
        else:
            if section in self.sections_list:       # Section exists case
                if param in self.cfg[section]:
                    _value = self.cfg[section][param]
                elif param in self.defaults:
                    _value = self.defaults[param]
            else:                                   # Section doesn't exist case
                if param in self.defaults:
                    _value = self.defaults[param]

        if _value == '__nonevalue__':
            if fallback != '_nofallback':
                return fallback
            else:
                raise ConfigError (f"Param <[{section}] {param}> not in <{self.config_file}> and no default or fallback.")
        else:
            # Optional type checking
            if isinstance(types, type):
                types = [types]

            if types == []:
                    return _value
            else:
                if type(_value) in types:
                    return _value
                else:
                    raise ConfigError (f"Config parameter <[{section}] {param}> value <{_value}> type {type(_value)} not of expected type(s): {types}")


#=====================================================================================
#=====================================================================================
#  s e t c f g
#=====================================================================================
#=====================================================================================

    def setcfg(self, param, value=True, types=[], section=''):
        """
## setcfg (param, value=True, types=[], section='') - Set a param's value in the cfg dictionary

***config_item() class member function***

### Args
`param` (str)
- String name of param to be set in cfg
- Created if not existing

`types` (single or list of as-expected types, default '[]' (any type accepted))
- if provided, a ConfigError is raised if the param's value type is not in the list of expected types
- `types` may be a single type (eg, `types=int`) or a list of types (eg, `types=[int, float]`)
- Supported types: [str, int, float, bool, list, tuple, dict, type(None)]

`section` (str, default '' (top-level))
- Select the section in which to save the param value


### Returns
- None on success
- Raises ConfigError if type of value is not in the optional types list
        """
        # Optional type checking
        if isinstance(types, type):
            types = [types]

        if types != []  and  type(value) not in types:
            raise ConfigError (f"Config parameter <[{section}] {param}> value <{value}> type {type(value)} not of expected type(s): {types}")


        if section == '':                           # Top-level case
            self.cfg[param] = value
        elif section == 'DEFAULT':                  # DEFAULT case
            self.defaults[param] = value
        else:                                       # section case - create section if doesn't exist
            if section not in self.sections_list:
                self.cfg[section] = {}
                self.sections_list.append(section)

            self.cfg[section][param] = value
        configman_logger.debug (f"Set [{section}] {param} = <{value}>  ({type(value)})")


#=====================================================================================
#=====================================================================================
#  r e m o v e _ p a r a m
#=====================================================================================
#=====================================================================================

    def remove_param(self, param, section='', missing_ok=True):
        """
## remove_param (param, section='', missing_ok=True) - Remove a param from the cfg dictionary

***config_item() class member function***

### Args
`param` (str)
- String name of param to be removed

`section` (str, default '' (top-level))
- Specify the section in which the param is to be removed
- The param is only removed from the designated section
- The section itself is not removed.  See parent class `config_item.clear()` for removing sections

`missing_ok` (book, default True)
- If True, then if param does not exist in the designated section then remove_param simply returns
- If False, then if the param does not exist in the designated section the ConfigError is raised


### Returns
- None on success
- Raises ConfigError if missing_ok=False and the param does not exist in the designated section
        """

        if section == '':                           # Top-level case
            if param in self.cfg:
                del self.cfg[param]
                configman_logger.debug (f"Removed [{section}] {param}")
                return
            elif missing_ok:
                return
            raise ConfigError (f"Param <{param}> not found in config {self.config_file}")

        elif section == 'DEFAULT':                  # DEFAULT case
            if param in self.defaults:
                del self.defaults[param]
                configman_logger.debug (f"Removed [{section}] {param}")
                return
            elif missing_ok:
                return
            raise ConfigError (f"Param <[DEFAULT] {param}> not found in config {self.config_file}")

        else:                                       # section case
            if section not in self.sections_list  and  not missing_ok:
                raise ConfigError (f"Section <{section}> not found in config {self.config_file}")
            if param in self.cfg[section]:
                del self.cfg[section][param]
                configman_logger.debug (f"Removed [{section}] {param}")
                return
            elif missing_ok:
                return
            raise ConfigError (f"Param <[{section}] {param}> not found in config {self.config_file}")


#=====================================================================================
#=====================================================================================
#  m o d i f y _ c o n f i g f i l e
#=====================================================================================
#=====================================================================================

    def modify_configfile (self, param='', value='', remove=False, add_if_not_existing=False, save=False):
        # TODO Comment out / uncomment out a param
        # TODO Add section select parameter for selective changes.  Also all mode
        # TODO Add a section label
        """
## modify_configfile (param='', value='', remove=False, add_if_not_existing=False, save=False) - Make edits to the config file

***config_item() class member function***

Params in the config file may have their values changed, be deleted, or new lines added.
- All added lines are added at the bottom of the file.
- _All instances of the param (in all sections and DEFAULT) will be modified to the new value._

NOTE: This function modifies the instance's configuration file, not
the content currently loaded into the cfg dictionary.

On the first call to modify_configfile() the content of the file is read into memory.  Successive
calls to modify_configfile() may be made, with the changes applied to the in-memory copy.  When
all changes have been applied the final call to modify_configfile() must have `save=True` to 
cause the memory version to be written out to the config file.  If the script code checks for
modifications of the config file then the modified content will be reloaded into the cfg dictionary.


### Args
`param` (str, default '')
- The param name, if modifying an existing param or adding a new param

`value` (any, default '')
- The new value to be applied to an existing param, or an added param
- Any comment text (after a '#') in the new value will be prepended to any existing comment text

`remove` (bool, default False)
- If True, the `param` config file line is removed from the config file

`add_if_not_existing` (bool, default False)
- Modify an existing param line, or add at the bottom of the config file if it is not existing
- To add a blank line leave out both `param` and `value`, or set both the `""`
- To add a comment line specify the comment in the `param` field (eg, `my_config.modify_configfile("# My comment")`)

`save` (bool, default False)
- Write the modified config file content back to the file
- `save=True` may be specified on the last modification call or an a standalone call.


### Returns
- None
- Warning messages are logged for attempting to modify or remove a non-existing param.


### Behaviors and rules
- **How modify_config works with multi-line params -** If a multi-line param is modified, the new value is
written out on a single line, and the continuation lines for the original definition remain in place.
This effectively turns the continuation lines into a new param definition, which is usually benign.  Check
for param name conflicts.
- NOTE:  In some circumstances the OS-reported timestamp for the modified config file may be erratic.
It may be necessary to add a `time.sleep(0.5)` delay between saving the modified config and the loadconfig()
reload call to avoid multiple config reloads.
        """

        line_format_re = re.compile(r'(\s*)([^\s=:]+)([\s=:]+)([^#]+)(.*)')

        if self.config_file is None:
            raise ConfigError ("Config file is None. Cannot modify config not loaded from a file.")

        if self.config_content == '':
            if self.safe_mode:
                self.config_content = run_with_timeout(self.config_full_path.read_text, rwt_ntries=RWT_NTRIES, rwt_timeout=RWT_TIMEOUT)
            else:
                self.config_content = self.config_full_path.read_text()
        found_param = False
        updated_content = ''
        value = str(value)

        for line in self.config_content.split('\n'):
            out = line_format_re.match(line)
            if out:
                # print (f"1: <{out.group(1)}>")    # Any leading whitespace
                # print (f"2: <{out.group(2)}>")    # param
                # print (f"3: <{out.group(3)}>")    # whitespace, '=', ':' between param and value
                # print (f"4: <{out.group(4)}>")    # value, with trailing whitespace
                # print (f"5: <{out.group(5)}>")    # comment

                if out.group(2) != param:
                    updated_content += line + '\n'
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
                    updated_content += out.group(1) + out.group(2) + out.group(3) + value + ' '*len_new_whitespace + out.group(5) + '\n'
            else:
                updated_content += line + '\n'

        if found_param == False:
            if add_if_not_existing == True:
                updated_content += f"{param}    {value}\n"
            elif param==''  and  value==''  and  save==True: # Save-only call
                pass
            else:
                configman_logger.warning (f"Modification of param <{param}> failed - not found in config file.  Modification skipped.")

        self.config_content = updated_content[:-1]          # Avoid adding extra \n at end of file

        if save:
            if self.safe_mode:
                self.config_content = run_with_timeout(self.config_full_path.write_text, self.config_content, rwt_ntries=RWT_NTRIES, rwt_timeout=RWT_TIMEOUT)
            else:
                self.config_full_path.write_text(self.config_content)
            self.config_content = ''


#=====================================================================================
#=====================================================================================
#  w r i t e
#=====================================================================================
#=====================================================================================

    def write(self, savefile):
        """
## write (savefile) - Write config data to a file

***config_item() class member function***


### Arg
`savefile` (Path or str)
- Path to the output file.
- The config data will be written to an absolute path, or relative to the `core.tool.config_dir`


### Returns
- None on success
- Raises ConfigError if unable to write the file


### Behaviors and rules
- The created config file is as loaded in memory.  Any imports in the originally loaded config file
 are merged into the top-level.
        """

        cfg_list = ''
        for key in self.cfg:
            if key not in self.sections_list:
                if type(self.cfg[key]) is str  and  '#' in self.cfg[key]:
                    cfg_list += f"{key:20} = '''{self.cfg[key]}'''\n"
                else:
                    cfg_list += f"{key:20} = {self.cfg[key]}\n"
        cfg_list += '\n[DEFAULT]\n'
        for key in self.defaults:
            cfg_list += f"{key:20} = {self.defaults[key]}\n"
        for section in self.sections_list:
            cfg_list += f'\n[{section}]\n'
            for key in self.cfg[section]:
                cfg_list += f"{key:20} = {self.cfg[section][key]}\n"
        
        outfile = mungePath(savefile, core.tool.config_dir).full_path

        try:
            if self.safe_mode:
                run_with_timeout(outfile.write_text, cfg_list, rwt_ntries=RWT_NTRIES, rwt_timeout=RWT_TIMEOUT)
                stat = run_with_timeout(self.config_full_path.stat, rwt_ntries=RWT_NTRIES, rwt_timeout=RWT_TIMEOUT)
            else:
                outfile.write_text(cfg_list)
                stat = self.config_full_path.stat()
        except Exception as e:
            raise ConfigError (f"Failed to write config {self.config_file} to file {outfile}\n  {type(e).__name__}: {e}")

        self.config_timestamp = int(stat.st_mtime)


#=====================================================================================
#=====================================================================================
#  s e c t i o n s
#=====================================================================================
#=====================================================================================

    def sections(self):
        """
## sections () - Return a list of sections in the cfg dictionary

***config_item() class member function***

For compatibility with the standard library configparser.  Also available via `<config>.sections_list`.

Example:
```
code:
    print (my_config.sections())

output:
    ['Bad params', 'SMTP']
```
        """

        return self.sections_list


#=====================================================================================
#=====================================================================================
#  c l e a r
#=====================================================================================
#=====================================================================================

    def clear(self, section=''):
        """
## clear (section='') - Purge a portion of the cfg dictionary

***config_item() class member function***

### Args
`section` (str, default '')
- `section = ''` clears the entire cfg dictionary, including all sections and DEFAULT
- `section = '<section_name>'` clears just that section
- `section = 'DEFAULT'` clears just the DEFAULT section


### Returns
- None
- A ConfigError is raised if attempting to remove a non-existing section
        """

        if section == '':
            self.cfg.clear()
            self.sections_list = []
            self.defaults.clear()
            self.loaded = False
        elif section in self.sections_list:
            self.cfg.pop(section, None)
            self.sections_list.remove(section)
        elif section == 'DEFAULT':
            self.defaults.clear()
        else:
            raise ConfigError (f"Failed attempt to remove non-existing section <{section}> from config")


#=====================================================================================
#=====================================================================================
#  _ _ r e p r _ _
#=====================================================================================
#=====================================================================================

    def __repr__(self):
        stats = ""
        stats += f"\nStats for config file <{self.config_file}>:\n"
        stats += f".config_file            :  {self.config_file}\n"
        stats += f".config_dir             :  {self.config_dir}\n"
        stats += f".config_full_path       :  {self.config_full_path}\n"
        stats += f".config_timestamp       :  {self.config_timestamp}\n"
        stats += f".safe_mode              :  {self.safe_mode}\n"
        stats += f".sections_list          :  {self.sections_list}\n"
        stats += f".force_str              :  {self.force_str}\n"
        stats += f".secondary_config       :  {self.secondary_config}\n"
        stats += f"core.tool.log_dir_base  :  {core.tool.log_dir_base}\n"
        return stats


#=====================================================================================
#=====================================================================================
#  d u m p
#=====================================================================================
#=====================================================================================

    def dump(self):
        """
## dump () - Return the formatted content of the cfg dictionary

***config_item() class member function***


### Returns
- str type pretty formatted content of the cfg dictionary, along with any sections and defaults
        """

        cfg_list = "***** Section [] *****\n"
        for key in self.cfg:
            if key not in self.sections_list:
                cfg_list += f"{key:>20} = {self.cfg[key]}  {type(self.cfg[key])}\n"
        for section in self.sections_list:
            cfg_list += f"***** Section [{section}] *****\n"
            for key in self.cfg[section]:
                cfg_list += f"{key:>20} = {self.cfg[section][key]}  {type(self.cfg[section][key])}\n"
        cfg_list += f"***** Section [DEFAULT] *****\n"
        for key in self.defaults:
            cfg_list += f"{key:>20} = {self.defaults[key]}  {type(self.defaults[key])}\n"
        return cfg_list[:-1]    # drop final '\n'



#=====================================================================================
#=====================================================================================
#   C l a s s   p e r s i s t e n t _ c o n f i g
#=====================================================================================
#=====================================================================================

class persistent_config (config_item):
    """
## Class persistent_config (config_file, force_new=False, safe_mode=False, save_schedule=None) - Create (if not existing) and load a persistent_config data file

***`persistent_config` is a derived class of `config_item`***

The `persistent_config` class provides a mechanism for runtime data to survive a tool script restart or system reboot. 
Behaviors on instantiation:
- Create the persistent `config_file` if not existing, and set the `new` attribute accordingly
- Load the config file
- Start a thread for scheduled saves, if specified

NOTE:  Documentation for this class assumes that a persistent_config has been loaded as:

    persist = persistent_config('my_persistent_file')


### Instantiation args
`config_file` (Path or str)
- Path to the configuration file, relative to the `core.tool.data_dir` directory, or an absolute path
- Note that if a relative path is provided then persistent_config uses mungePath to create an absolute path based on `core.tool.data_dir`.

`force_new` (bool, default False)
- If True, any pre-existing config_file is deleted
- If False, any pre-existing `config_file` is left in place
- If `config_file` does not exist (due to never existed or being deleted) then an empty file is created and the instance attribute `new` is set True.

`safe_mode` (bool, default False)
- If True, all potentially blocking filesystem operations are wrapped in `run_with_timeout()` calls.  TimeoutError exceptions may be raised.
- If False, all filesystem operations are called directly, with potential hang risk if accessing non-local filesystems.  See the `safe_mode` notes 
in `config_item` _Behaviors and rules_, above.

`save_schedule` (None, int, str, or list)
- If an int or str, such as `7200` or `'2h'`, the value is interpreted as a timevalue between automatic saves
- If a str clock time or a list of clock times, such as `'15:00'` or `['06:00', '18:00']` then automatic saves will be executed at these times
- If None, no scheduled saves will be active
- If `save_schedule` is used the tool script should exit with a call to `persist.save(exit=True)` to force a final save of the persistent data 
and terminate the schedule save thread


### Useful class attributes
Since `persistent_config` is a derived class of `config_item`, all of `config_item`'s methods and instance attributes are also available.
The current values of all public class attributes may be printed using `print(persist)`.

`.new`
- True if `force_new = True` or if the `config_file` doesn't exist at instantiation, otherwise False
- User code may check this attribute after instantiation and do one-time initialization of the config data, as needed
- Remains True or False for the remainder of the run unless changed by the tool script

`.save_schedule`
- The value passed in at instantiation.  `None` indicates no automatic saves are scheduled.

`.next_save_dt`
- If `persist.save_schedule is not None`, then this is the datetime of the next scheduled save
- `None` if `persist.save_schedule is None`


### Returns
- Handle to the `persistent_config()` instance
- Raises `TimeoutError` if `safe_mode=True` and upon any filesystem access issues
- Raises other exceptions, such as `PermissionError` and `OSError`, as appropriate


### Behaviors and rules
1. Instantiating a persistent_config object also loads the config file into memory.
1. The config data may be accessed via `xx = persist.getcfg('myvar')` and `persist.setcfg('myvar', 5)`, and by direct access to the 
config data, e.g., `xx = persist.cfg['myvar']` and `persist.cfg['myvar'] = 5`
1. If the `config_file` is not found then it will be created and the instance attribute `new` will be set to True.
The path to the parent dir will also be created, as needed.
1. The `save()` method must be called on controlled termination of your tool script in order to save the most recent data and to 
terminate any schedule save thread.  Alternately (if not using scheduled saves), you may wish to 
save after critical data has been written to the config.
1. A persistent_config is considered a `config_item` secondary_config - loaded as an independent config, with no changes to the logging setup.

"""
    def __init__(self, config_file, force_new=False, safe_mode=False, save_schedule=None):
        self.safe_mode =        safe_mode
        self.save_schedule =    save_schedule

        conf_file_mp =          mungePath(config_file, core.tool.data_dir)
        self.config_full_path = conf_file_mp.full_path

        # Make the target directory
        if self.safe_mode:
            run_with_timeout(conf_file_mp.parent.mkdir, exist_ok=True, rwt_ntries=RWT_NTRIES, rwt_timeout=RWT_TIMEOUT)
        else:
            conf_file_mp.parent.mkdir(exist_ok=True)

        # Delete any existing file if force_new
        if force_new:
            self.del_persistent_file()

        # If config non-existing then create it and set new flag
        self.new =          False
        if self.safe_mode:
            if not check_path_exists(self.config_full_path):
                run_with_timeout(self.config_full_path.touch, rwt_ntries=RWT_NTRIES, rwt_timeout=RWT_TIMEOUT)
                self.new =  True
        else:
            if not self.config_full_path.exists():
                self.config_full_path.touch()
                self.new =  True

        # Load the config
        super().__init__(config_file=conf_file_mp.full_path, secondary_config=True, safe_mode=safe_mode, missing_ok=force_new)
        configman_logger.debug (f"Loading <{self.config_file}> data")
        super().loadconfig(force_reload=True, flush_on_reload=True)

        # Set up scheduled saves
        if self.save_schedule:
            self.periodic_save_exit = False
            self.save_thread = Thread(target=self._scheduled_save, name=f'{config_file} scheduled save')
            self.save_thread.start()
        else:
            self.next_save_dt = None
            self.save_thread = None


#=====================================================================================
#=====================================================================================
#   s a v e
#=====================================================================================
#=====================================================================================

    def save(self, exit=False):
        """
## save (exit=False) - Force an explicit save to the config_file and terminate the scheduled save thread if running

***persistent_config() class member function***


### Args
`exit` (bool, default False)
- If True, informs the scheduled save thread to do a final save and then terminate
- If False, or no scheduled save thread is running, the persistent_config data is directly written to the `config_file`


### Returns
- None on successful save and scheduled save thread exit (if enabled)
- Raises ConfigError if the schedule save thread does not terminate within 5 seconds.  The config data has not been saved.
- Raises other exceptions, such as `PermissionError` and `OSError`, as appropriate
        """
        if exit  and  self.save_thread:
            self.periodic_save_exit = True      # _scheduled_save saves on exit
            self.save_thread.join(timeout=5)
            if self.save_thread.is_alive():
                raise ConfigError (f"Failed to save config {self.config_file} - save_thread did not terminate")
            return

        configman_logger.info (f"Saving <{self.config_file}> data")
        super().write(self.config_full_path)
        return True


#=====================================================================================
#=====================================================================================
#   d e l _ p e r s i s t e n t _ f i l e
#=====================================================================================
#=====================================================================================

    def del_persistent_file(self):
        """
## del_persistent_file () - Delete the config_file

***persistent_config() class member function***

This method does _not_ delete any _loaded_ persistent data - if followed by a call to `save()` the file will 
be written with the currently loaded config content.
To purge the loaded config data call `persist.clear()` (provided by the `config_item` parent class).

This method is normally not called from tool script code.  It is called during instantiation when `force_new=True`.


### Returns
- `None` if the file is successfully deleted, or the file does not exist
- Raises TimeoutError if safe_mode = False and config_file cannot be accessed
- Raises other errors as appropriate
        """
        configman_logger.debug (f"Deleting <{self.config_full_path}> data file")
        if self.safe_mode:
            run_with_timeout(self.config_full_path.unlink, missing_ok=True, rwt_ntries=RWT_NTRIES, rwt_timeout=RWT_TIMEOUT)
        else:
            self.config_full_path.unlink(missing_ok=True)


#=====================================================================================
#=====================================================================================
#   _ s c h e d u l e d _ s a v e
#=====================================================================================
#=====================================================================================

    def _scheduled_save(self):
        # Private class method
        # loop time is 0.2s:  Longest time to respond to periodic_save_exit + any time required for the file write

        configman_logger.debug (f"Starting <{self.config_file}> scheduled save thread")
        self.next_save_dt = get_next_dt(self.save_schedule)
        configman_logger.debug (f"Next save <{self.next_save_dt}>")

        while 1:
            if self.periodic_save_exit:
                configman_logger.debug (f"Stopping <{self.config_file}> scheduled save thread")
                self.save()
                # time.sleep(1)
                sys.exit(0)         # Exit the scheduled save thread

            if datetime.datetime.now() > self.next_save_dt:
                self.save()
                self.next_save_dt = get_next_dt(self.save_schedule)
                configman_logger.debug (f"Next save <{self.next_save_dt}>")

            time.sleep (0.2)


#=====================================================================================
#=====================================================================================
#  _ _ r e p r _ _
#=====================================================================================
#=====================================================================================

    def __repr__(self):
        repr_str  =     super().__repr__()
        repr_str +=     f".new                    :  {self.new}\n"
        repr_str +=     f".save_schedule          :  {self.save_schedule}\n"
        if self.save_schedule:
            repr_str += f".save_thread            :  {self.save_thread}\n"
            repr_str += f".next_save_dt           :  {self.next_save_dt}\n"
            repr_str += f".periodic_save_exit     :  {self.periodic_save_exit}\n"
        return repr_str
    