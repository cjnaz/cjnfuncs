#!/usr/bin/env python3
"""cjnfuncs.configman - Configuration files made easy and useful
"""

#==========================================================
#
#  Chris Nelson, 2018-2023
#
#==========================================================

import re
import ast

from .core      import setuplogging, logging, ConfigError
from .mungePath import mungePath, check_path_exists
import cjnfuncs.core as core


# Configs / Constants
DEFAULT_LOGGING_LEVEL  = logging.WARNING


#=====================================================================================
#=====================================================================================
#  C l a s s   c o n f i g _ i t e m
#=====================================================================================
#=====================================================================================
initial_logging_setup = False   # Global since more than one config can be loaded
CFGLINE =  re.compile(r"([^\s=:]+)[\s=:]+(.+)")                 # used in load_config() for param:value lines
CFGLINE2 = re.compile(r"(\s*)([^\s=:]+)([\s=:]+)([^#]+)(.*)")   # used in modify_configfile()
SECLINE =  re.compile(r"\[(.*)\]")                              # used for getting section names


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
- config_item.\_\_repr\_\_() - Return a str() listing all stats for the instance, plus the `tool.log_dir_base` value.
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
    print (config)
    config.loadconfig()
    print (config)

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
    """     # TODO doc secondary_config
    def __init__(self, config_file=None, remap_logdirbase=True, force_str=False, secondary_config=False):
        global tool

        self.force_str = force_str
        self.secondary_config = secondary_config
        self.cfg = {}
        self.current_section_name = ''
        self.sections_list = []
        self.defaults = {}

        if config_file == None:
            self.config_file        = None
            self.config_dir         = None
            self.config_full_path   = None
            self.config_timestamp   = 0
            self.config_content     = ""    # Used by modify_configfile()
        else:
            config = mungePath(config_file, core.tool.config_dir)
            if config.is_file:
                self.config_file        = config.name
                self.config_dir         = config.parent
                self.config_full_path   = config.full_path
                self.config_timestamp   = 0
                self.config_content     = ""    # Used by modify_configfile()
                # if remap_logdirbase  and  tool.log_dir_base == tool.user_data_dir:
                #     tool.log_dir_base = tool.user_config_dir
            else:
                # _msg = f"Config file <{config_file}> not found."
                raise ConfigError (f"Config file <{config_file}> not found.")
        if remap_logdirbase  and  core.tool.log_dir_base == core.tool.user_data_dir:
            core.tool.log_dir_base = core.tool.user_config_dir


    def _add_key(self, key, value, section_name=''):
        if section_name == '':
            self.cfg[key] = value
        elif section_name == 'DEFAULT':
            self.defaults[key] = value
        else:
            self.cfg[section_name][key] = value


    def _parse_value(self, value_str):
        if self.force_str:
            return value_str
        
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


    def _check_section(self, xyz):
        out = SECLINE.match(xyz)
        if out:
            section_name = out.group(1).strip()
            if section_name != ''  and  section_name not in self.sections_list  and  section_name != 'DEFAULT':
                self.cfg[section_name] = {}
                self.sections_list.append(section_name)
            return section_name
        else:
            return None


    def read_string(self, str_blob, ldcfg_ll=DEFAULT_LOGGING_LEVEL, isimport=False):
        for line in str_blob.split('\n'):

            # Is an import line
            if line.strip().lower().startswith("import"):
                line = line.split("#", maxsplit=1)[0].strip()
                target = mungePath(line.split(maxsplit=1)[1], self.config_dir)
                # try:
                #     imported_config = config_item(target.full_path)
                #     imported_config.loadconfig(ldcfg_ll, isimport=True)
                try:
                    imported_config = config_item(target.full_path)
                    imported_config.loadconfig(ldcfg_ll, isimport=True)
                except Exception as e:
                    logging.getLogger().setLevel(preexisting_loglevel)
                    raise ConfigError (e)
                try:
                    for key in imported_config.cfg:
                        if self.current_section_name == '':
                            self.cfg[key] = imported_config.cfg[key]
                        elif self.current_section_name == 'DEFAULT':
                            self.defaults[key] = imported_config.cfg[key]
                        else:
                            self.cfg[self.current_section_name][key] = imported_config.cfg[key]
                except Exception as e:
                    logging.getLogger().setLevel(preexisting_loglevel)
                    raise ConfigError (f"Failed importing/processing config file  <{target.full_path}>")

            # Is a param/value line or a [section] line
            else:
                _line = line.split("#", maxsplit=1)[0].strip()  # line without comment and leading/trailing whitespace
                if len(_line) > 0:
                    if _line.startswith('['):                       # TODO param cannot start with '['
                        xx = self._check_section(_line)
                        if xx is None:
                            logging.getLogger().setLevel(preexisting_loglevel)
                            raise ConfigError (f"Malformed section line <{line}>")
                        else:
                            if isimport:
                                logging.getLogger().setLevel(preexisting_loglevel)
                                raise ConfigError ("Section within imported file is not supported.")
                            self.current_section_name = xx

                    else:
                        out = CFGLINE.match(_line)
                        if out:
                            param = out.group(1)
                            rol   = out.group(2)        # rest of line (value portion)

                            value = self._parse_value(rol)
                            # logging.debug (f"Loaded [{self.current_section_name}][{param}] = <{value}>  ({type(value)})")
                            self._add_key(param, value, self.current_section_name)
                            logging.debug (f"Loaded {param} = <{value}>  ({type(value)})")
                        else: 
                            line = line.replace('\n','')
                            logging.warning (f"loadconfig:  Error on line <{line}>.  Line skipped.")



    def sections(self):
        return self.sections_list


    def clear(self, section=''):
        if section == '':
            self.cfg.clear()
            self.sections_list = []
        elif section in self.sections_list:
            self.cfg.pop(section, None)
            self.sections_list.remove(section)
        elif section == 'DEFAULT':
            self.defaults.clear()
        else:
            raise ConfigError (f"Failed attempt to remove non-existing section <{section}> from config")


    def __repr__(self):
        stats = ""
        stats += f"\nStats for config file <{self.config_file}>:\n"
        stats += f".config_file            :  {self.config_file}\n"
        stats += f".config_dir             :  {self.config_dir}\n"
        stats += f".config_full_path       :  {self.config_full_path}\n"
        stats += f".config_timestamp       :  {self.config_timestamp}\n"
        stats += f".sections_list          :  {self.sections_list}\n"
        stats += f"core.tool.log_dir_base  :  {core.tool.log_dir_base}\n"
        # stats += f"tool.log_full_path  :  {tool.log_full_path}\n"
        return stats


    def dump(self):
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
  for type errors (eg, expecting a float but user input error resulted in a str). Also see the 
  `getcfg (param, types=[])` parameter for basic type checking.

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
If the timestamp has changed then the config file will be reloaded and `1` is returned to indicate to 
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

# TODO doc DEFAULTs not flushed, but will be loaded
# TODO doc modify_config will change all occurrences in main, sections or DEFAULT
        # NOTE:  Failed importing/processing config file  </home/cjn/.config/cjnfuncs_testcfg/import_nest_1.cfg>
        # rather than saying can't import/process nest_2


        global initial_logging_setup
        global preexisting_loglevel

        if not initial_logging_setup:   # Do only once, globally  TODO and not self.secondary_config ??? to allow secondary before primary
            # Initial logging will go to the console if no call_logfile is specified on the initial loadconfig call.
            # The logging level defaults to WARNING / 30.
            console_lf = self.getcfg("ConsoleLogFormat", None)  # TODO Why get these when no config will have been loaded at this point?
            file_lf = self.getcfg("FileLogFormat", None)
            setuplogging (call_logfile=call_logfile, call_logfile_wins=call_logfile_wins, ConsoleLogFormat=console_lf, FileLogFormat=file_lf)
            initial_logging_setup = True

        config = self.config_full_path

        # Operations only on top-level config file
        if not isimport:

            # Save externally set / prior log level for later restore
            preexisting_loglevel = logging.getLogger().level

            if force_flush_reload:
                logging.getLogger().setLevel(ldcfg_ll)   # logging within loadconfig is always done at ldcfg_ll
                logging.info(f"Config  <{self.config_file}>  force flushed (force_flush_reload)")   # TODO - get the name of the config??  2+ places
                self.cfg.clear()
                self.sections_list = []
                self.config_timestamp = 0       # Force reload of the config file

            # Check if config file is available and has changed
            _exists = False
            for _ in range(3):
                if check_path_exists(config):
                    _exists = True
                    break

            if not _exists:
                if tolerate_missing:
                    logging.getLogger().setLevel(ldcfg_ll)
                    logging.info (f"Config  <{self.config_file}>  file not currently accessible.  Skipping (re)load.")
                    logging.getLogger().setLevel(preexisting_loglevel)
                    return -1           # -1 indicates that the config file cannot currently be found
                else:
                    logging.getLogger().setLevel(preexisting_loglevel)
                    raise ConfigError (f"Could not find  <{self.config_file}>")

            current_timestamp = int(self.config_full_path.stat().st_mtime)  # integer-second resolution
            if self.config_timestamp == current_timestamp:
                return 0                # 0 indicates that the config file was NOT (re)loaded

            # It's an initial load call, or config file has changed.  Do (re)load.
            self.config_timestamp = current_timestamp
            logging.getLogger().setLevel(ldcfg_ll)   # Set logging level for remainder of loadconfig call
            logging.info (f"Config  <{self.config_file}>  file timestamp: {current_timestamp}")

            if flush_on_reload:
                logging.info (f"Config  <{self.config_file}>  flushed due to changed file (flush_on_reload)")
                self.cfg.clear()
                self.sections_list = []


        # Load the config
        logging.info (f"Loading  <{config}>")
        string_blob = config.read_text()
        self.read_string (string_blob, ldcfg_ll=ldcfg_ll, isimport=isimport)


        # Operations only for finishing a top-level call
        if not isimport  and  not self.secondary_config:
            console_lf = self.getcfg("ConsoleLogFormat", None)
            file_lf = self.getcfg("FileLogFormat", None)
            setuplogging(config_logfile=self.getcfg("LogFile", None), call_logfile=call_logfile, call_logfile_wins=call_logfile_wins, ConsoleLogFormat=console_lf, FileLogFormat=file_lf)

            # if self.getcfg("DontEmail", False, section='SMTP'):
            #     logging.info ('DontEmail is set - Emails and Notifications will NOT be sent')
            # elif self.getcfg("DontNotif", False, section='SMTP'):
            #     logging.info ('DontNotif is set - Notifications will NOT be sent')

            config_loglevel = self.getcfg("LogLevel", None)
            if config_loglevel is not None:
                try:
                    config_loglevel = int(config_loglevel)
                except:
                    raise ConfigError (f"Config file <LogLevel> must be integer value (found {config_loglevel})")
                logging.info (f"Logging level set to config LogLevel <{config_loglevel}>")
                logging.getLogger().setLevel(config_loglevel)
            else:
                logging.info (f"Logging level set to preexisting level <{preexisting_loglevel}>")
                logging.getLogger().setLevel(preexisting_loglevel)

        # Secondary configs may not modify the Loglevel
        if self.secondary_config:
            logging.info (f"Logging level set to preexisting level <{preexisting_loglevel}>")
            logging.getLogger().setLevel(preexisting_loglevel)

        self.current_section_name = ''      # TODO.  Test reloading config with sections
        return 1                        # 1 indicates that the config file was (re)loaded


#=====================================================================================
#=====================================================================================
#  read_dict
#=====================================================================================
#=====================================================================================
    def read_dict(self, param_dict, section_name=''):
        """
## read_dict(param_dict, section='') - Load the content of a dictionary into the config

since section_name is passed along with a dict, then only one section may be written to on each call.

Returns the value of param from the cfg dictionary.  Equivalent to just referencing cfg[]
but with handling if the item does not exist.

Type checking may be performed by listing one or more expected types via the optional `types` parameter.
If the loaded param is not one of the expected types then a ConfigError is raised.  This check may be 
useful for basic error checking of param values, EG making sure the return value is a float and not
a str. (str is the loadconig default if the param type cannot be converted to another supported type.)
"""
        try:
            if section_name == '':
                for key in param_dict:
                    self.cfg[key] = param_dict[key]
            elif section_name == 'DEFAULT':
                for key in param_dict:
                    self.defaults[key] = param_dict[key]
            else:
                if section_name not in self.sections_list:
                    self.cfg[section_name] = {}
                    self.sections_list.append(section_name)
                for key in param_dict:
                    self.cfg[section_name][key] = param_dict[key]
        except Exception as e:
            raise ConfigError (f"Failed loading dictionary into cfg around key <{key}>")


#=====================================================================================
#=====================================================================================
#  g e t c f g
#=====================================================================================
#=====================================================================================
    def getcfg(self, param, fallback="_nofallback", types=[], section=''):
        """
## getcfg (param, fallback=None, types=[]) - Get a param from the cfg dictionary

Returns the value of param from the cfg dictionary.  Equivalent to just referencing cfg[]
but with handling if the item does not exist.

Type checking may be performed by listing one or more expected types via the optional `types` parameter.
If the loaded param is not one of the expected types then a ConfigError is raised.  This check may be 
useful for basic error checking of param values, EG making sure the return value is a float and not
a str. (str is the loadconig default if the param type cannot be converted to another supported type.)

NOTE: `getcfg()` is almost equivalent to `cfg.get()`, except that `getcfg()` does not default to `None`.
Rather, `getcfg()` raises a ConfigError if the param does not exist and no `fallback` is specified.
This can lead to cleaner tool script code.  Either access method may be used, along with `x = cfg["param"]`.


### Parameters
`param`
- String name of param to be fetched from cfg

`fallback` (default None)
- if provided, is returned if `param` does not exist in cfg

`types` (default '[]' empty list)
- if provided, a ConfigError is raised if the param's value type is not in the list of expected types
- `types` may be a single type (eg, `types=int`) or a list of types (eg, `types=[int, float]`)
- Supported types: [str, int, float, bool, list, tuple, dict]

### Returns
- param value (cfg[param]), if param is in cfg
- `fallback` value if param not in cfg and `fallback` value provided
- raises ConfigError if param does not exist in cfg and no `fallback` provided, or if not of the expected type(s).
    """
        _value = None
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

        if _value is None:
            if fallback != "_nofallback":
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


        # if section == '':                           # Top-level case
        #     if param in self.cfg:
        #         _value = self.cfg[param]
        #     elif param in self.defaults:
        #         _value = self.defaults[param]
        #     else:
        #         if fallback != "_nofallback":
        #             return fallback
        #         else:
        #             raise ConfigError (f"getcfg - Param <[{section}] {param}> not in <{self.config_file}> and no default or fallback.")
        # else:                                       # Section specified case
        #     if section not in self.sections_list:       # Section doesn't exist case
        #         if param in self.defaults:
        #             _value = self.defaults[param]
        #         else:
        #             if fallback != "_nofallback":
        #                 return fallback
        #             else:
        #                 raise ConfigError (f"getcfg - Param <[{section}] {param}> not in <{self.config_file}> and no default or fallback.")
        #     else:                                       # Section exists case
        #         if param in self.cfg[section]:
        #             _value = self.cfg[section][param]
        #         elif param in self.defaults:
        #             _value = self.defaults[param]
        #         else:
        #             if fallback != "_nofallback":
        #                 return fallback
        #             else:
        #                 raise ConfigError (f"getcfg - Param <[{section}] {param}> not in <{self.config_file}> and no default or fallback.")

        # if isinstance(types, type):
        #     types = [types]

        # if types == []:
        #         return _value
        # else:
        #     if type(_value) in types:
        #         return _value
        #     else:
        #         raise ConfigError (f"getcfg - Config parameter <{param}> value <{_value}> type {type(_value)} not of expected type(s): {types}")


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
modifications of the config file then the modified content will be reloaded into the cfg dictionary.

NOTE:  In some circumstances the OS-reported timestamp for the modified config file may be erratic.
It may be necessary to add a time.sleep(0.5) delay between saving the modified config and the loadconfig()
reload call to avoid multiple config reloads.


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
        if self.config_file is None:
            raise ConfigError ("Config file is None. Cannot modify config not loaded from a file.")

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
            self.config_full_path.write_text(self.config_content) # + "\n")
            self.config_content = ""

