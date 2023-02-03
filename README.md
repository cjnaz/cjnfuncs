# cjnfuncs - A collection of core functions for script writing

Classes and functions
- setuplogging()
- set_toolname() class
- mungePath() class
- deploy_files()
- config_item() class, including loadconfig()
- getcfg()
- timevalue(), retime()
- requestlock() and releaselock()
- snd_notif() and snd_email()

TODO links above, and intro text

A companion template script file is provided, along with template.cfg and template.service files.  I use these as the 
starter files for new tools.

` `

---

## setuplogging (call_logfile=None, call_logfile_wins=False, config_logfile=None) - Set up the root logger

Logging may be directed to the console (stdout), or to a file.  Each time setuplogging()
is called the current/active log file (or console) may be reassigned.

setuplogging() works standalone (without a config file) or in conjunction with loadconfig().
If a loaded config file has a `LogFile` parameter then loadconfig() passes it thru
`config_logfile`.  loadconfig() also passes along any `call_logfile` and `call_logfile_wins`
that were passed to loadconfig() from the main script.  This mechanism allows the main script
to override any config `LogFile`, such as for directing output to the console for a tool's 
interactive use, eg:
    `setuplogging (call_logfile=None, call_logfile_wins=True, config_logfile='some_logfile.txt')`

### Parameters
`call_logfile`
- Potential log file passed from the main script.  Selected by `call_logfile_wins = True`.
call_logfile may be an absolute path or relative to the tool.log_dir_base directory.  
`None` specifies the console.

`call_logfile_wins`
- If True, the `call_logfile` is selected.  If False, the `config_logfile` is selected.

`config_logfile`
- Potential log file passed from loadconfig() if there is a `LogFile` param in the 
loaded config.  Selected by `call_logfile_wins = False`.
config_logfile may be absolute path or relative to the tool.log_dir_base directory.  
`None` specifies the console.

Returns None

` `

---

## Class set_toolname (toolname) - Set target directories for config and data storage

set_toolname() centralizes and establishes a set of base directory path variables for use in
the script.  It looks for existing directories, based on the specified toolname, in
the site-wide and then user-specific locations.  Specifically, site-wide 
config and/or data directories are looked for at (eg) `/etc/xdg/cjnfuncs_testenv` and/or 
`/usr/share/cjnfuncs_testenv`.  If site-wide directories are not 
found then user-specific is assumed.  No directories are created.

Member function stats() returns a str() listing of the available attributes of the
set_toolname() class.

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

### Important notes and variances from the XDG spec and/or the appdirs package:

- set_toolname() uses the [appdirs package](https://pypi.org/project/appdirs/), which is a 
close implementation of the
[XDG basedir specification](https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html).

- The `user` and `site`-prefixed attributes are as defined by the XDG spec and/or the appdirs package.  The 
non-such-prefixed attributes are resolved based on the existing user or site environment, and are the attributes
that generally should be used within tool scripts.

- For a `user` setup, the `.log_dir_base` is initially set to the `.user_data_dir` (variance from XDG spec).
If a config file is subsequently
loaded then the `.log_dir_base` is changed to the `.user_config_dir`.  (Not changed for a `site` setup.)
Thus, for a `user` setup, logging is done to the default configuration directory.  This is a 
style variance, and can be reset in the script by reassigning: `tool.log_dir_base = tool.user_log_dir` (or any
other directory) before calling loadconfig() or setuplogging().
(The XDG spec says logging goes to the `.user_state_dir`, while appdirs sets it to the `.user_cache_dir/log`.)

- The `.log_dir`, `log_file`, and `.log_full_path` attributes are set by calls to setuplogging() or loadconfig(),
and are initially set to `None` by set_toolname().

- For a `site` setup, the `.site_data_dir` is set to `/usr/share/toolname`.  The XDG spec states that 
the `.cache_dir` and `.state_dir` should be in the root user tree; however, set_toolname() sets these two 
to the `.site_data_dir`.

` `

---

## Class mungePath (in_path="", base_path="", mkdir=False) - A clean interface for dealing with filesystem paths

### Features and benefits:
- Based on pathlib, yielding Path type `.full_path` and `.parent` attributes, which may be used with all
pathlib.Path methods, such as .open().
- Enables paths to be handled as a two parts - an application-specific portion (`in_path`) and a `base_path`.
- The returned object's attributes may cleanly be used in script code.  
- User (~user/) and environment vars ($HOME/) are supported and expanded
- Hides Path vs. PurePath methods/attributes, providing a consistent interface

### Parameters
`in_path`
- An absolute or relative path to a file or directory, such as `mydir/myfile.txt`.  

`base_path`
- An absolute or relative path to a file or directory, such as `~/.config/mytool`, prepended to `in_path` if
`in_path` is a relative path.

`mkdir`
- Force-make a full directory path.  `in_path` / `base_path` is understood to be to a directory.

### Behaviors and rules:
- If `in_path` is a relative path (eg, `mydir/myfile.txt`) portion then the `base_path` is prepended.  
- If both `in_path` and `base_path` are relative then the combined path will also be relative, usually to
the script directory (generally not useful).
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

### Class attributes
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

` `

---

## deploy_files (files_list, overwrite=False, missing_ok=False) - Install initial tool files in user or site space

`deploy_files()` is used to install initial setup files (and directory trees) from the module to the user 
or site config and data directories. Suggested usage is with the CLI `--setup-user` or `--setup-site` switches.
Distribution files and directory trees are hosted in `<module_root>/deployment_files/`.

`deploy_files()` accepts a list of dictionaries to be pushed to user or site space. 
If deployment fails then execution aborts.  This functions is intended for interactive use.

### Example call
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
The target_dir may specify a subdirectory, such as `"target_dir": "USER_DATA_DIR/mydirs"`.  Any _new directories_ in the  `target_dir` path will be created with the `dir_stat` permissions, and files will be created with the `file_stat` permissions.

### Parameters
`source`
- Either an individual file or directory tree within and relative to `<module_root>/deployment_files/`.
No wildcard support.

`target_dir`
- A directory target for the pushed `source`.  It is expanded for user and environment vars, and supports these 
substitutions (per set_toolname()):
  - USER_CONFIG_DIR, SITE_CONFIG_DIR
  - USER_DATA_DIR, SITE_DATA_DIR
  - Also absolute paths

`overwrite`
- If overwrite=False (default) then only missing files will be copied.  If overwrite=True then all files will be overwritten 
if they exist - data may be lost!

`missing_ok`
- If missing_ok=True then a missing source file or directory is tolerated (non-fatal).  This feature is used for testing.




# -------------------------------------------


` `
# funcs3 Features

**_See the function documentation within the funcs3.py module for usage details._**

## Logging framework
Function & module var
- `setuplogging()` - Set up console or target file logging
- `logging` - Handle for logging calls in your code (i.e. `logging.info("Hello")`)

Python's logging framework is quite valuable for tracing more complicated scripts.  funcs3's `setuplogging` implementation is lean and functional.  It's 
especially valuable for scripts that will be run by CRON or as systemd services in order to provide debug info. Note that:
  - Logging goes to stderr.
  - If using loadconfig, then don't also call setuplogging.  loadconfig calls setuplogging.  See the logging notes in loadconfig, below.

## funcs3 minimum version check
Function & module var
- `funcs3_min_version_check()` - Compare min version required by the main script to the imported version of funcs3.
- `funcs3_version` - Content of the funcs3_version var 

Since the interfaces and features of func3 functions may change over time, 
`funcs3_min_version_check` allows for enforcing a minimum version rev level of the funcs3 
module from the calling script.  See example in wanipcheck.

## Configuration file and cfg dictionary
Functions & module vars
- `loadconfig()` - Read a configuration file into the cfg dictionary
- `getcfg()` - Retrieve a var from the cfg dictionary, with error check and default support
- `cfg{}` - Dictionary containing the config file keys
- `timevalue()` - Converts time value strings (i.e., 10s, 5m, 3h, 4d 5w) to seconds
- `retime()` - Converts a seconds value to an alternate time units

Config files make for easily customized and modified tools, rather than touching the code for such config edits.  The config file 
contents are read into the `cfg` dictionary.  The dictionary may be referenced directly as usual, such as `xx = cfg['EmailTo']`.  Alternately, use `getcfg` for accessing vars: `xx = getcfg('EmailTo')`.  `getcfg` provides error checking for 
if the var does not exist (maybe a typo?), and also supports a default mechanism.  On error, `getcfg` raises a `ConfigError` exception, which may be caught and handled in the main code.

The format of a config file is key/value pairs (with no section or default as in the Python configparser module).  Separating the key and value may be whitespace, `=` or `:`.See [testcfg.cfg](testcfg.cfg) for examples.



Notable loadconfig Features:

- **Native Ints, Bools, and Strings support** - Integer values in the config file are stored as integers in the cfg dictionary, True and False values (case insensitive) are stored as booleans, and 
all other entries are stored as strings.  This avoids having to clutter the script with explicit type casting.  If the config file has 
`xyz 5` then the script can be cleanly written as `if getcfg('xyz') > 3: ...`, or `print (cfg['xyz'] * 10)`. 
Similarly, `MyBool true` in the config file allows `if getcfg('MyBool'):` to be written.
- **Setup Logging** - The first call to loadconfig will set up a logging handler (calls funcs3.setuplogging, which calls basicConfig).  The `logging` handle is available for import by other modules (`from funcs3 import logging ...`).  By default, logging will go to the console at the WARNING/30 level and above.    
  - **Log level options** - Optional `LogLevel` in the config file will set the logging level after
  the config has been loaded.  If LogLevel is not specified in the config file, then 
  the logging level is set to the cfgloglevel passed to loadconfig (default 30:WARNING).
  The script code may also manually/explicitly set the logging level (after the initial loadconifig call, and config LogLevel not specified) and this value will be retained over later calls to loadconfig, thus allowing for a command line verbose switch feature.
  In any case, logging done within loadconfig is always done at the cfgloglevel.
  Logging module levels: 10(DEBUG), 20(INFO), 30(WARNING), 40(ERROR), 50(CRITICAL)
  - **Log file options** - The log file may be specified on the loadconfig call (cfglogfile), or may be
  specified via the `LogFile` param in the config file.  If cfglogfile is None (default) and no
  LogFile is specified in the loaded config file then logging will go to the console.  By default,
  specifying LogFile in the config file takes precedent over cfglogfile passed to loadconfig.
  Specifying `cfglogfile_wins=True` on the loadconfig call causes the specified cfglogfile to
  override any value specified in the loaded config file.  This may be useful for debug for directing log output to the console by overriding the config file LogFile value.
  Note that if LogFile is changed that logging will switch to the new file when the config file
  is reloaded.  Switching logging from a file back to the console is not supported.
  - **Logging format** - funcs3 has built-in format strings for console and file logging.  These defaults may be overridden by defining `CONSOLE_LOGGING_FORMAT` and/or `FILE_LOGGING_FORMAT` constants in the main script file.  See wanipcheck for an example.

- **Import nested config files** - loadconfig supports `Import` (keyword is case insensitive).  The listed file is imported as if the vars were in the main config file.  Nested imports are allowed.  A prime usage of `import` is to all placing email server credentials in your home directory with user-only readability.  
- **Config reload if changed** - loadconfig may be called periodically by the main script.  loadconfig detects
if the main/top-level config file modification time has changed and then reloads the file.  If `flush_on_reload=True` (default False) then the `cfg` dictionary is cleared/purged before reloading the config file.  If `force_flush_reload=True` (default False) then cfg is unconditionally cleared and the config file is reloaded.  loadconfig returns True if the config file was (re)loaded, so main code logic can run only when the config file was changed.  Reloading the config file when changed is especially useful for tools that run as services, such as [lanmonitor](https://github.com/cjnaz/lanmonitor).   This allows the main script to efficiently and dynamically track changes to the config file while the script is looping, such as for a service running forever in a loop.  See [lanmonitor](https://github.com/cjnaz/lanmonitor) for a working example.  Note that if using threading then a thread should be caused to pause while the config file is being reloaded with `flush_on_reload=True` or `force_flush_reload=True` since the params will disappear briefly.
- **timevalue and retime** - Time values in the form of "10s" (seconds) or "2.1h" (hours) may be reasonable as config file values.  `timevalue` is a class that accepts such time values and provides class vars for ease of use within your script.  `xx = timevalue("5m")` provides `xx.seconds` (float 300.0), `xx.original` ("5m" - the original string/int/float value passed), `xx.unit_str` ("mins"), and `xx.unit_char` ("m"). Supported resolutions are "s" (seconds), "m" (minutes), "h" (hours), "d" (days), and "w" (weeks), all case insensitive.
`retime` allows for converting (often for printing) a seconds-resolution time value to an alternate resolution.`retime` accepts an int or float seconds value and returns a float at the specified unit_char resolution.  For example, `print (retime(timevalue("3w").seconds, "d"))` prints "21.0".
- **ConfigError** - Critical errors within loadconfig and getcfg raise a `ConfigError`.  Such errors include loadconfig file access or parsing issues, and getcfg accesses to non-existing keys with no default.
- **Comparison to Python's configparser module** - configparser contains many customizable features.  Here are a few key comparisons:

  Feature | loadconfig | Python configparser
  ---|---|---
  Native types | Int, Bool (true/false case insensitive), String | String only, requires explicit type casting with getter functions
  Reload on config file change | built-in | requires coding
  Import sub-config files | Yes | No
  Section support | No | Yes
  Default support | No | Yes
  Fallback support | Yes (getcfg default) | Yes
  Whitespace in keywords | No | Yes
  Case sensitive keywords | Yes (always) | Default No, customizable
  Key/value delimiter | whitespace, ':', or '=' | ':' or '=', customizable
  Key only, no value | No | Yes
  Multi-line values | No | Yes
  Comment prefix | '#', fixed, thus can't be part of the value | '#' or ';', customizable
  Interpolation | No | Yes
  Mapping Protocol Access | No | Yes
  Save to file | No | Yes


## Email and text message sending
Functions
- `snd_notif()` - Tailored to sending text message notifications
- `snd_email()` - Sends an email

Features
- `snd_email` and `snd_notif` provide nice basic wrappers around Python's smtplib and use setup info from the config file.  The send-to target (config file `NotifList` default for snd_notif, or the function call `to=` parameter) is one or more email addresses (white space or comma separated).
Email 'to' address checking is very rudimentary - an email address must contain an `@` or a SndEmailError is raised.
- `snd_notif` is targeted to be used with mobile provider 
email-to-text-message bridge addresses, such as Verizon's xxxyyyzzzz@vzwpix.com.  [wanipcheck](wanipcheck) demonstrates sending a message
out when some circumstance comes up.  
Suggested application:  Write a script that checks status on critical processes on your server, and if anything
is wrong then send out a notification.  (Wait, rather than writing this, see [lanmonitor](https://github.com/cjnaz/lanmonitor).)
- `snd_email` supports sending a message built up by the script code as a python string, or by pointing to a text or html-formatted file.  
- The `EmailServer` and `EmailServerPort` settings in the config file support port 25 (plain text), port 465 (SSL), port 587 with plain text, and port 587 with TLS.
- `EmailUser` and `EmailPass` should be placed in a configuration file in your home directory, with access mode `600`, and `import`ed from your tool config file.
- On error, these functions raise an SndEmailError exception, which may be caught and handled in the main code.

## Lock file

Functions
- `requestlock()` - Set a file indicating to others that your tool is in-process
- `releaselock()` - Remove the lock file

Features
- For scripts that may take a long time to run and are run by CRON, the possibility exists that a job is still running when CRON wants to 
run it again, which may create a real mess.  The lock file mechanism is used in https://github.com/cjnaz/rclonesync-V2.  


## PROGDIR
Module var
- `PROGDIR` contains the absolute path to the main script directory.

PROGDIR is useful for building references to other files in the directory where the main script resides.  For example the default config file is at `os.path.join(PROGDIR, 'config.cfg'`).

` `
# Revision history
- V1.1 220412 - Added timevalue and retime
- V1.0 220131 - V1.0 baseline
- ...
- V0.1 180524 - New.  First github posting

