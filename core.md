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
- [set_logging_level](#set_logging_level)
- [restore_logging_level](#restore_logging_level)
- [get_logging_level_stack](#get_logging_level_stack)
- [pop_logging_level_stack](#pop_logging_level_stack)
- [periodic_log(message,](#periodic_log(message,)



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

    
<br/>

<a id="setuplogging"></a>

---

# setuplogging (call_logfile=None, call_logfile_wins=False, config_logfile=None, ConsoleLogFormat=None, FileLogFormat=None) - Set up the root logger

Logging may be directed to the console (stdout), or to a file.  Each time setuplogging()
is called the current/active log file (or console) may be reassigned.

Calling `setuplogging()` with no args results in:
- Logging output to the console
- Logging format set to the default console logging format
- Logging level is unchanged (the Python default is 30/WARNING)

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
- None
    
<br/>

<a id="set_logging_level"></a>

---

# set_logging_level (new_level, clear=False, save=True) - Save the current logging level and set the new_level

The current logging level is saved on a stack and can be restored by a call to restore_logging_level.


### Args
`new_level` (int)
- The new logging level to be set.  Values may be set to the logging module defined levels, or their integer 
equivalents (or to any integer value that makes sense):  logging.DEBUG (10), logging.INFO (20), logging.WARNING (30), 
logging.ERROR (40), or logging.CRITICAL (50).

`clear` (bool, default False)
- If True, the logging level history stack is cleared

`save` (bool, default True)
- If True, the current logging level is saved to the stack
- If clear=True, then the clear is done first.  If save=True also then the stack will have only the prior logging level.


### Returns
- None
    
<br/>

<a id="restore_logging_level"></a>

---

# restore_logging_level () - Restore the prior logging level from the stack

The prior saved logging level (from the prior set_logging_level call) is popped from the stack and set as the current logging level.
If the stack is empty then the logging level is set to logging.WARNING (30).


### Returns
- None
    
<br/>

<a id="get_logging_level_stack"></a>

---

# get_logging_level_stack () - Return the content of the stack

Useful for debug.  The stack may be cleared with a call to `set_logging_level(clear=True)` or `pop_logging_level_stack(clear=True)`.


### Returns
- A list of the prior saved logging levels

<br/>

<a id="pop_logging_level_stack"></a>

---

# pop_logging_level_stack () - Discard top of the stack

Useful if the preexisting logging level was saved to the stack, but should be discarded 
when a new level is set.  Used in loadconfig() when a new logging level is assigned from
the config file.


### Args
`clear` (bool, default False)
- If True, the logging level history stack is cleared, without setting a new logging level


### Returns
- Logging level stack after pop

<br/>

<a id="periodic_log(message,"></a>

---

# periodic_log(message, category='Cat1', log_interval='10m', log_level=30)

Log a message infrequently, so as to avoid flooding the log.  The `category` arg provides for independent
log intervals for different types of logging events.


### Args

`message` (str)
- The message text to be logged
- Only logged if the first time for this `category` or the log_interval has expired

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
- None
      