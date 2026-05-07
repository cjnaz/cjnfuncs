# cjnfuncs - A framework and collection of utility functions for script writing

## cjnfuncs is comprised of several modules (follow links to respective documentation)

NOTE:  These link point to the github repo since relative links to other .md files do not work on PyPI.

module | Description/Purpose
--|--
[core](https://github.com/cjnaz/cjnfuncs/blob/main/core.md)                   | Set up the base environment
[configman](https://github.com/cjnaz/cjnfuncs/blob/main/configman.md)         | Feature-rich configuration file toolset
[timevalue](https://github.com/cjnaz/cjnfuncs/blob/main/timevalue.md)         | Handle time values with units, such as '5m' (5 minutes), and schedule future operations
[mungePath](https://github.com/cjnaz/cjnfuncs/blob/main/mungePath.md)         | Ease-of-use pathlib extension for constructing and manipulating file paths
[rwt / run_with_timeout](https://github.com/cjnaz/cjnfuncs/blob/main/rwt.md)  | Execute any function with an enforced timeout
[deployfiles](https://github.com/cjnaz/cjnfuncs/blob/main/deployfiles.md)     | Push bundled setup files within a package to the proper user/system locations
[resourcelock](https://github.com/cjnaz/cjnfuncs/blob/main/resourcelock.md)   | Inter-process resource lock mechanism
[SMTP](https://github.com/cjnaz/cjnfuncs/blob/main/SMTP.md)                   | Send notification and email messages

Developed and tested on Python 3.9.21 and supported on all higher Python versions.
Developed on Linux.  Supported on Windows, except for the resourcelock module (posix-ipc module dependency).

In this documentation, "tool script" refers to a Python project that imports and uses cjnfuncs. Some may be simple scripts, and others may themselves be installed packages.

<br/>

## Installation and usage

```
pip install cjnfuncs
```

A package template using cjnfuncs is available at https://github.com/cjnaz/tool_template, which 
is the basis of PyPI posted tools such as:
  - [lanmonitor](https://pypi.org/project/lanmonitor/)
  - [wanstatus](https://pypi.org/project/wanstatus/)
  - [routermonitor](https://pypi.org/project/routermonitor/)

Project repo:  https://github.com/cjnaz/cjnfuncs

<br/>

## Key changes since the prior major public release (version 3.0)

3.2 changes
- `persistent_config` - Layered on top of config_item, this new class provides a clean and simple tool for carrying runtime data across tool 
script restarts and system reboots.

- Shared memory block handling - Extending resourcelock's features, read/write access is provided to the shared memory block associated with
a user-defined lock.  


3.1 changes
- Several issues with Windows support were fixed.

- `configman.config_item()` now supports a safe_mode switch, which will speed up Windows usage of loadconfig() at some risk.  See the note on `config_item()`.

- Named child loggers are now implemented on several cjnfuncs modules.  By default, logging from cjnfuncs modules is disabled (internal logging events are usually at the INFO or DEBUG
level, while the default logging level is set to WARNING).  For example, logging from configman may be enabled by `logging.getLogger('cjnfuncs.configman').setLevel(logging.INFO)`,
or using `core.set_logging_level(logging.INFO, 'cjnfuncs.configman')`.

- Changed mungePath set_attributes from default True to default False to avoid long processing time on Windows by default.

- deployfiles can now create an empty target directory.

3.1.1 changes
- get_next_dt now supports a days or weeks offset for the days arg
- Added separate child logger `cjnfuncs.resourcelock_islocked` so that `is_locked()` may be called in a loop without flooding the log while `cjnfuncs.resourcelock` is set to debug

<br/>

## Revision history

- 3.2 - 260506 - New features:  persistent_config and shared memory block handling
- 3.1.1 260207 - separate resourcelock_islocked logger, get_next_dt days/weeks offset
- 3.1  251109
  Support for and use of child loggers, 
  deployfiles create empty dir, 
  Windows fixes, 
  config_item() safe_mode switch, 
  mungePath set_attributes from default False
- 3.0.1 251005 - Allow '.' in config section names
- 3.0 250705 - Added run_with_timeout, set / restore_logging_level, periodic_logging, get_next_dt.  Functional change to mungePath.
- 2.5 250206 - Added multi-line and quoted string support to configman
- 2.4.1 241118 - resource_lock only init lock_info if not existing
- 2.4 241105 - Twilio support in snd_notif, resource_lock trace/debug features, check_path_exists exception fix
- 2.3 240821 - Added mungePath ./ support.
  Resolved check_path_exists() memory leak.
  Added `same_process_ok` to resourcelock.getlock()
  Added prereload_callback to config_item.loadconfig()
- 2.2 240119 - Added SMTP DKIM support.  Set SMTP server connect timeout to EmailRetryWait.
- 2.1 240104 - Partitioned to separate modules.
  Added modify_configfile. 
  Added native support for float, list, tuple, and dict in loadconfig(). 
  Added getcfg() type checking. 
  Documentation touch for logging formats in config file. 
  Improved snd_notif failure logging. 
  Added email/notif send retries.
  Added resourcelock module.
- 2.0.1 230222 - deploy_files() fix for files from package
- 2.0 230208 - Refactored and converted to installed package.  Renamed funcs3 to cjnfuncs.
- ...
- 0.1 180524 - New.  First github posting