# configman - A configuration manager made easy and powerful

## Getting started - A basic config file example

Given the following config file - `myconfig.cfg`:
```
# myconfig.cfg - My first config file

My_name_is      Pat     # SNL reference
The_Dog      =  Penguin
Dog's_age    :  3
```

This config file is loaded by your script code:
```
#!/usr/bin/env python3
from cjnfuncs.core      import set_toolname
from cjnfuncs.configman import config_item
import cjnfuncs.core as core

set_toolname('configman_ex1')
core.tool.config_dir = '.'          # See note below

my_config = config_item('configman_ex1.cfg')
my_config.loadconfig()

print (f"My name is {my_config.getcfg('My_name_is')}")
my_dog = my_config.getcfg('The_Dog')
dogs_age = my_config.getcfg("Dog's_age")
print (f"My dog's name is {my_dog}.  He is {dogs_age} years old.")
print (f"The_Dog {type(my_dog)}, Dogs_age {type(dogs_age)}")
```

And the obvious output is...
```
$ ./configman_ex1.py 
My name is Pat
My dog's name is Penguin.  He is 3 years old.
The_Dog <class 'str'>, Dogs_age <class 'int'>
```

Notables:
1. The config file is structured as lines of `param` - `value` pairs, with supported separators of whitespace, `=` or `:`.  Each pair is on a single line.  Comments are supported on lines by themselves or on the end of param lines.
1. A config file is loaded using `configman.loadconfig()`. The param values are loaded based on their parsed types. Most all types are supported...  `str`, `int`, `bool`, `float`, `list`, `dict`, `tuple`.  Types support makes for clean script code.
1. Params are accessed in script code using `configman.getcfg()`.  getcfg() supports fallback values and type checking.

***Note***: configman relies on the environment set up by `set_toolname()`, which creates a set of application path variables such as `core.tool.config_dir`.  In the case of a user-mode script, the .config_dir is set to `~/.config/<toolname>`, so by default that is the directory that configman will look in for `configman_ex1.cfg`.  For these examples we have overridden the default config directory to be the directory that we are running the example script from (`.`).
Alternately, the full path to the config file may be passed to the `config_item()` call.
See the `cjnfuncs.core` module for more details.


## A full blown example - check out these nifty features


ex 2:

    sections, defaults and fallbacks
    Expected types enforcement
    imports
    Logging setup - LogLevel, LogFile - not from secondary configs
        log file to the core.tool.logdir, unless full path specified
        separate logging level ll_ldcfg for loadconfig calls
    print the config, config.dump
    debug level loadconfig


## On-the-fly config file reloads for service scripts

ex 3

        Reloading if changed
            flush_on_reload, force_flush_reload
            tolerate missing


## Programmatic config file edits

ex 4

    modify_configfile


## Comparison to Python's configparser module

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


<a id="links"></a>
         
<br>

---

# Links to classes, methods, and functions

- [requestlock](#requestlock)
- [releaselock](#releaselock)



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
    