# cjnfuncs - A framework and collection of utility functions for script writing

cjnfuncs is comprised of several modules (links to respective documentation):

module | Description/Purpose
--|--
[core](./core.md)               | Set up the base environment
[configman](./configman.md)     | Feature-rich configuration file toolset
[timevalue](./timevalue.md)     | Handle time values with units, such as '5m' (5 minutes)
[mungePath](./mungePath.md)     | Ease-of-use pathlib extenstion for constructing and manipulating file paths
[deployfiles](./deployfiles.md) | Push bundled setup files within a package to the proper user/system locations
[resourcelock](./resourcelock.md) | Inter-process resource lock mechanism
[SMTP](./SMTP.md)               | Send notification and email messages

Developed and tested on Python 3.6.8, and supported on all higher Python versions.
Developed on Linux, supported also on Windows (tested on Windows 10).

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

## Revision history
- 2.1 230914 - Added modify_configfile. 
  Added native support for float, list, tuple, and dict in loadconfig(). 
  Added getcfg() type checking. 
  Documentation touch for logging formats in config file. 
  Improved snd_notif failure logging. 
  Added email/notif send retries.
- 2.0.1 230222 - deploy_files() fix for files from package
- 2.0 230208 - Refactored and converted to installed package.  Renamed funcs3 to cjnfuncs.
- ...
- 0.1 180524 - New.  First github posting