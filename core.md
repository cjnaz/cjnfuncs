# core - Set up the base environment

Skip to [API documentation](#links)

The core module provides a foundation for writing tool scripts, such as configuring the base logger
and establishing standardized paths for configuration, logging, working files, etc.

<br>

## Setting up the base environment with set_toolname()

```
Given core_ex1.py:
    #!/usr/bin/env python3
    from cjnfuncs.core      import set_toolname
    import cjnfuncs.core as core

    set_toolname('core_ex1')
    print ("Path to the config dir:", core.tool.config_dir)
    print (core.tool)

Output:
    $ ./core_ex1.py 
    Path to the config dir: /home/me/.config/core_ex1

    Stats for set_toolname <core_ex1>:
    .toolname         :  core_ex1
    .main_module      :  <module '__main__' from '/mnt/share/dev/packages/cjnfuncs/tools/doc_code_examples/./core_ex1.py'>
    .main_full_path   :  /mnt/share/dev/packages/cjnfuncs/tools/doc_code_examples/core_ex1.py
    .main_dir         :  /mnt/share/dev/packages/cjnfuncs/tools/doc_code_examples
    General user and site paths:
    .user_config_dir  :  /home/me/.config/core_ex1
    .user_data_dir    :  /home/me/.local/share/core_ex1
    .user_state_dir   :  /home/me/.local/state/core_ex1
    .user_cache_dir   :  /home/me/.cache/core_ex1
    .user_log_dir     :  /home/me/.cache/core_ex1/log
    .site_config_dir  :  /etc/xdg/core_ex1
    .site_data_dir    :  /usr/share/core_ex1
    Based on found user or site dirs:
    .env_defined      :  user
    .config_dir       :  /home/me/.config/core_ex1
    .data_dir         :  /home/me/.local/share/core_ex1
    .state_dir        :  /home/me/.local/state/core_ex1
    .cache_dir        :  /home/me/.cache/core_ex1
    .log_dir_base     :  /home/me/.local/share/core_ex1
    .log_dir          :  None
    .log_file         :  None
    .log_full_path    :  None
```

In the above example, `set_toolname()` has determined that the system-wide directories don't exist
and therefore defaults to a user-specific setup.  The top-half of the output lists the _user_ and
_site_ attributes which may be used (eg:  x = core.tool.site_config_dir), and the bottom-half lists
attributes with the active/resolved paths. The `.user_` and `.site_`-prefixed attributes may be used with 
`cjnfuncs.deployfiles.deploy_files()` for installing a tool script's setup files into their proper homes.

- **Note** - `import cjnfuncs.core as core` provides access to the real/live `core.tool` global, which 
is needed as calls to setuplogging() will modify the `core.tool` attributes.  Just adding `core` to the 
`from cjnfuncs.core import set_toolname` line only provides a _copy_ of the variable, which isn't updated
by later changes.

### What does all this mean and what is it used for?
- A tool script may declare/load a config file (eg, `myconfig.cfg`).  `cjnfuncs.configman.config_item()` will look 
for that config file at `<core.tool.config_dir>/myconfig.cfg`.
- A tool script may specify a log file (eg, `mylogfile.txt`).  `cjnfuncs.core.setuplogging()` will write
log messages to `<core.tool.log_dir>/mylogfile.txt` (which is the same as `core.tool.log_full_path`).
- `set_toolname()` uses the [appdirs package](https://pypi.org/project/appdirs/), which is a close 
implementation of the
[XDG basedir specification](https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html).

- The `.user_` and `.site_`-prefixed attributes are as defined by the XDG spec and/or the appdirs package.  The 
non-such-prefixed attributes are resolved based on the existing user or site environment, and are the attributes
that generally should be used within tool scripts.
- See other important **Behaviors, rules, and variances from the XDG spec and/or the appdirs package**
in the [setuplogging](#setuplogging) API doc, below.


### Example for the wanstatus _package_ installed into user and then site-wide space

Note the base-path differences between a user-installed vs. site-installed tool script.  Also note the
differences in `.main_module` between a standalone script usage (as above) versus an installed package (below).

Example `print(core.tool)` for a user-specific setup:
```

    Stats for set_toolname <wanstatus>:
    .toolname         :  wanstatus
    .main_module      :  <module 'wanstatus.wanstatus' from '/<path-to-venv>/lib/python3.9/site-packages/wanstatus/wanstatus.py'>
    .main_full_path   :  /<path-to-venv>/lib/python3.9/site-packages/wanstatus/wanstatus.py
    .main_dir         :  /<path-to-venv>/lib/python3.9/site-packages/wanstatus
    General user and site paths:
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
    
Example `print(core.tool)` for a site setup (.site_config_dir and/or .site_data_dir exist):
```
    .toolname         :  wanstatus
    .main_module      :  <module 'wanstatus.wanstatus' from '/<path-to-venv>/lib/python3.9/site-packages/wanstatus/wanstatus.py'>
    .main_full_path   :  /<path-to-venv>/lib/python3.9/site-packages/wanstatus/wanstatus.py
    .main_dir         :  /<path-to-venv>/lib/python3.9/site-packages/wanstatus
    General user and site paths:
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

<br>

## Configuring the root logger with setuplogging()

setuplogging() provides a clean solution for configuring logging for a tool script. 
It comprehends whether logging should go to the `console` or to the `.log_dir_base`, what logging 
level to set, and the logging format to use.

```
Given core_ex2.py:
    #!/usr/bin/env python3
    from cjnfuncs.core      import set_toolname, setuplogging, logging
    import cjnfuncs.core as core

    set_toolname('core_ex2')

    setuplogging()
    logging.warning(f"This is a warning-level log message to the console.\n{core.tool}")

    setuplogging(call_logfile='mylogfile.txt', call_logfile_wins=True)
    logging.warning(f"This is a warning-level log message to the log file <{core.tool.log_full_path}>.\n{core.tool}")


Console output:
    $ ./core_ex2.py 
        core_ex2.<module>             -  WARNING:  This is a warning-level log message to the console.

    Stats for set_toolname <core_ex2>:
    .toolname         :  core_ex2
    .main_module      :  <module '__main__' from '/mnt/share/dev/packages/cjnfuncs/tools/doc_code_examples/./core_ex2.py'>
    .main_full_path   :  /mnt/share/dev/packages/cjnfuncs/tools/doc_code_examples/core_ex2.py
    .main_dir         :  /mnt/share/dev/packages/cjnfuncs/tools/doc_code_examples
    General user and site paths:
    .user_config_dir  :  /home/me/.config/core_ex2
    .user_data_dir    :  /home/me/.local/share/core_ex2
    .user_state_dir   :  /home/me/.local/state/core_ex2
    .user_cache_dir   :  /home/me/.cache/core_ex2
    .user_log_dir     :  /home/me/.cache/core_ex2/log
    .site_config_dir  :  /etc/xdg/core_ex2
    .site_data_dir    :  /usr/share/core_ex2
    Based on found user or site dirs:
    .env_defined      :  user
    .config_dir       :  /home/me/.config/core_ex2
    .data_dir         :  /home/me/.local/share/core_ex2
    .state_dir        :  /home/me/.local/state/core_ex2
    .cache_dir        :  /home/me/.cache/core_ex2
    .log_dir_base     :  /home/me/.local/share/core_ex2
    .log_dir          :  None
    .log_file         :  None
    .log_full_path    :  __console__


Log file output:
    $ cat /home/me/.local/share/core_ex2/mylogfile.txt
    2023-12-10 22:56:47,699        core_ex2.<module>              WARNING:  This is a warning-level log message to the log file </home/me/.local/share/core_ex2/mylogfile.txt>.

    Stats for set_toolname <core_ex2>:
    .toolname         :  core_ex2
    .main_module      :  <module '__main__' from '/mnt/share/dev/packages/cjnfuncs/tools/doc_code_examples/./core_ex2.py'>
    .main_full_path   :  /mnt/share/dev/packages/cjnfuncs/tools/doc_code_examples/core_ex2.py
    .main_dir         :  /mnt/share/dev/packages/cjnfuncs/tools/doc_code_examples
    General user and site paths:
    .user_config_dir  :  /home/me/.config/core_ex2
    .user_data_dir    :  /home/me/.local/share/core_ex2
    .user_state_dir   :  /home/me/.local/state/core_ex2
    .user_cache_dir   :  /home/me/.cache/core_ex2
    .user_log_dir     :  /home/me/.cache/core_ex2/log
    .site_config_dir  :  /etc/xdg/core_ex2
    .site_data_dir    :  /usr/share/core_ex2
    Based on found user or site dirs:
    .env_defined      :  user
    .config_dir       :  /home/me/.config/core_ex2
    .data_dir         :  /home/me/.local/share/core_ex2
    .state_dir        :  /home/me/.local/state/core_ex2
    .cache_dir        :  /home/me/.cache/core_ex2
    .log_dir_base     :  /home/me/.local/share/core_ex2
    .log_dir          :  /home/me/.local/share/core_ex2
    .log_file         :  mylogfile.txt
    .log_full_path    :  /home/me/.local/share/core_ex2/mylogfile.txt
```

Note the differences in the `.log_` prefixed attributes, above, for console and file logging.

`setuplogging()` works closely with `cjnfuncs.configman.loadconfig()`. These settings are 
reapplied each time the config file is reloaded:
- If the loaded config file defines `LogFile` then logging will be initialized to 
`core.tool.log_full_path`.
- If the loaded config file defines `LogLevel` then that logging level will be active.
- The console or file logging format may be changed from the defaults by defining `ConsoleLogFormat`
or `FileLogFormat` in the config file, respectively.

Typically, console logging is used for tool script interactive use, and file logging is used for a tool
script running as a service.


<a id="links"></a>
         
<br>

---

# Links to classes, methods, and functions

- [set_toolname](#set_toolname)
- [setuplogging](#setuplogging)



<br/>

<a id="set_toolname"></a>

---

# Class set_toolname (toolname) - Set target directories for config and data storage

set_toolname() centralizes and establishes a set of base directory path variables for use in
the tool script.  It looks for existing directories, based on the specified toolname, in
the site-wide (system-wide) and then user-specific locations.  Specifically, site-wide 
config and/or data directories are looked for at `/etc/xdg/<toolname>` and/or 
`/usr/share/<toolname>`.  If site-wide directories are not 
found then user-specific is assumed.  No directories are created.


### Parameter
`toolname` (str)
- Name of the tool


### Returns
- Handle to the `set_toolname()` instance.
- The handle is also stored in the `core.tool` global.  See examples for proper access.


### Behaviors, rules, and _variances from the XDG spec and/or the appdirs package_
- For a `user` setup, the `.log_dir_base` is initially set to the `.user_data_dir` (a variance from XDG spec).
If a config file is subsequently
loaded then the `.log_dir_base` is changed to the `.user_config_dir`.  (Not changed for a `site` setup.)
Thus, for a `user` setup, logging is done to the default configuration directory.  This is a 
style variance, and can be reset in the tool script by reassigning: `core.tool.log_dir_base = core.tool.user_log_dir` (or any
other directory) before calling cjnfuncs.configman.loadconfig() or setuplogging().
(The XDG spec says logging goes to the `.user_state_dir`, while appdirs sets it to the `.user_cache_dir/log`.)

- The `.log_dir`, `.log_file`, and `.log_full_path` attributes are set by calls to setuplogging() 
  (or loadconfig() which in turn calls setuplogging()) and are initially set to `None` by set_toolname().

- For a `site` setup, the `.site_data_dir` is set to `/usr/share/<toolname>`.  The XDG spec states that 
the `.cache_dir` and `.state_dir` should be in the root user tree; however, set_toolname() sets these two 
also to the `.site_data_dir`.

    
<br/>

<a id="setuplogging"></a>

---

# setuplogging (call_logfile=None, call_logfile_wins=False, config_logfile=None, ConsoleLogFormat=None, FileLogFormat=None) - Set up the root logger

Logging may be directed to the console (stdout), or to a file.  Each time setuplogging()
is called the current/active log file (or console) may be reassigned.

setuplogging() works standalone or in conjunction with `cjnfuncs.configman.loadconfig()`.
If a loaded config file has a `LogFile` parameter then loadconfig() passes it thru
`config_logfile`.  loadconfig() also passes along any `call_logfile` and `call_logfile_wins`
that were passed to loadconfig() from the tool script.  This mechanism allows the tool script
to override any config `LogFile`, such as for directing output to the console for a tool script's 
interactive use.  For example, this call will set logging output to the console regardless of 
the log file declared in the config file:

    setuplogging (call_logfile=None, call_logfile_wins=True, config_logfile='some_logfile.txt')

    
### Parameters
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
    