# cjnfuncs - A collection of core functions for script writing

Logging, Configuration files, Email, Lock files, Deploying tool script template files, ...  

- A package template using cjnfuncs is available at https://github.com/cjnaz/tool_template, which 
is the basis of PyPI posted tools such as:
  - [lanmonitor](https://pypi.org/project/lanmonitor/)
  - [wanstatus](https://pypi.org/project/wanstatus/)
  - [routermonitor](https://pypi.org/project/routermonitor/)

- Developed and tested on Python 3.6.8, and supported on all higher Python versions
- In this documentation, "tool script" refers to a Python project that imports and uses cjnfuncs.  
Some may be simple scripts, and others may themselves be installed packages.
- Developed on Linux, supported also on Windows (tested on Windows 10)


## Classes and functions
- [setuplogging](#setuplogging)
- [set_toolname](#set_toolname)
- [mungePath](#mungePath)
- [deploy_files](#deploy_files)
- [config_item](#config_item)
- [loadconfig](#loadconfig)
- [getcfg](#getcfg)
- [timevalue](#timevalue)
- [retime](#retime)
- [requestlock](#requestlock)
- [releaselock](#releaselock)
- [snd_notif](#snd_notif)
- [snd_email](#snd_email)

<br/>

<a id="setuplogging"></a>

---

# setuplogging (call_logfile=None, call_logfile_wins=False, config_logfile=None) - Set up the root logger

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


### Returns
- NoneType
    
<br/>

<a id="set_toolname"></a>

---

# Class set_toolname (toolname) - Set target directories for config and data storage

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
    Stats for set_toolname <cjnfuncs_testenv>:
    .toolname         :  cjnfuncs_testenv
    .user_config_dir  :  /home/me/.config/cjnfuncs_testenv
    .user_data_dir    :  /home/me/.local/share/cjnfuncs_testenv
    .user_state_dir   :  /home/me/.local/state/cjnfuncs_testenv
    .user_cache_dir   :  /home/me/.cache/cjnfuncs_testenv
    .user_log_dir     :  /home/me/.cache/cjnfuncs_testenv/log
    .site_config_dir  :  /etc/xdg/cjnfuncs_testenv
    .site_data_dir    :  /usr/share/cjnfuncs_testenv
    Based on found user or site dirs:
    .env_defined      :  user
    .config_dir       :  /home/me/.config/cjnfuncs_testenv
    .data_dir         :  /home/me/.local/share/cjnfuncs_testenv
    .state_dir        :  /home/me/.local/state/cjnfuncs_testenv
    .cache_dir        :  /home/me/.cache/cjnfuncs_testenv
    .log_dir_base     :  /home/me/.local/share/cjnfuncs_testenv
    .log_dir          :  None
    .log_file         :  None
    .log_full_path    :  None
```
    
Example stats() for a site setup (.site_config_dir and/or .site_data_dir exist):
```
    Stats for set_toolname <cjnfuncs_testenv>:
    .toolname         :  cjnfuncs_testenv
    .user_config_dir  :  /home/me/.config/cjnfuncs_testenv
    .user_data_dir    :  /home/me/.local/share/cjnfuncs_testenv
    .user_state_dir   :  /home/me/.local/state/cjnfuncs_testenv
    .user_cache_dir   :  /home/me/.cache/cjnfuncs_testenv
    .user_log_dir     :  /home/me/.cache/cjnfuncs_testenv/log
    .site_config_dir  :  /etc/xdg/cjnfuncs_testenv
    .site_data_dir    :  /usr/share/cjnfuncs_testenv
    Based on found user or site dirs:
    .env_defined      :  site
    .config_dir       :  /etc/xdg/cjnfuncs_testenv
    .data_dir         :  /usr/share/cjnfuncs_testenv
    .state_dir        :  /usr/share/cjnfuncs_testenv
    .cache_dir        :  /usr/share/cjnfuncs_testenv
    .log_dir_base     :  /usr/share/cjnfuncs_testenv
    .log_dir          :  None
    .log_file         :  None
    .log_full_path    :  None
```
    
<br/>

<a id="mungePath"></a>

---

# Class mungePath (in_path="", base_path="", mkdir=False) - A clean interface for dealing with filesystem paths

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
        
<br/>

<a id="deploy_files"></a>

---

# deploy_files (files_list, overwrite=False, missing_ok=False) - Install initial tool script files in user or site space

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
  - `file_stat` - Permissions set on each created file
  - `dir_stat` - Permissions set on each created directory (if not already existing)


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
    
<br/>

<a id="config_item"></a>

---

# Class config_item (config_file, remap_logdirbase=True) - Create a configuration instance for use with loadconfig()

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
- load_config() - Load the config file to the `cfg` dictionary.  See below.


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
    
<br/>

<a id="loadconfig"></a>

---

# loadconfig () (config_item() class member function) - Load a configuration file into the cfg dictionary
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
- **Native int, bool, and str support** - Integer values in the config file are stored as integers in 
  the cfg dictionary, True and False values (case insensitive) are stored as booleans, and 
  all other entries are stored as strings.  This avoids most explicit type casting clutter in the tool script.
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

- **Logging format** - cjnfuncs has built-in format strings for console and file logging.
  These defaults may be overridden by defining `CONSOLE_LOGGING_FORMAT` and/or `FILE_LOGGING_FORMAT`
  constants in the tool script file.

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
  Native types | int, bool (true/false case insensitive), str | str only, requires explicit type casting via getter functions
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
  Save to file | No | Yes
        
<br/>

<a id="getcfg"></a>

---

# getcfg (param, default=None) - Get a param from the cfg dictionary.

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
    
<br/>

<a id="timevalue"></a>

---

# Class timevalue (orig_val) - Convert time value strings of various resolutions to seconds

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
        
<br/>

<a id="retime"></a>

---

# retime (time_sec, unitC) - Convert time value in seconds to unitC resolution

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
    
<br/>

<a id="requestlock"></a>

---

# requestlock (caller, lockfile, timeout=5) - Lock file request

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
    
<br/>

<a id="releaselock"></a>

---

# releaselock (lockfile) - Release a lock file

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
    
<br/>

<a id="snd_notif"></a>

---

# snd_notif (subj="Notification message, msg="", to="NotifList", log=False) - Send a text message using info from the config file

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
    
<br/>

<a id="snd_email"></a>

---

# snd_email (subj, to, body=None, filename=None, htmlfile=None, log=False)) - Send an email message using info from the config file

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
    ` `
---
# Revision history
- 2.0 230208 - Refactored and converted to installed package.  Renamed funcs3 to cjnfuncs.
- ...
- 0.1 180524 - New.  First github posting
