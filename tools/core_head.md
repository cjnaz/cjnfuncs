# core - Set up the base environment and logging tools

Skip to [API documentation](#links)

The core module provides a foundation for writing tool scripts, such as configuring the base logger
and establishing standardized paths for configuration, logging, working files, etc.

<br>

## Setting up the base environment with `set_toolname()`

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

## Configuring the root logger with `setuplogging()`

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

<br>

## `set_logging_level()` and `restore_logging_level()` - Controlling logging level for sections of code

These functions may be used to temporarily set a logging level.  Here's a basic example for enabling 
debug-level logging while developing/testing myfunction().

```
#!/usr/bin/env python3
from cjnfuncs.core import set_toolname, logging, set_logging_level, restore_logging_level, get_logging_level_stack

set_toolname('core_ex3')    # Configures the root logger to defaults, including default logging level WARNING/30


def myfunction():
    # With set and restore_logging_level calls uncommented I get debug logging within myfunction

    set_logging_level(logging.DEBUG)    # Save current WARNING/30 level to the stack and set DEBUG/10 level
    # Do complicated stuff in this function
    logging.debug   (f"2 - Within myfunction()        - logging level: {logging.getLogger().level}. On the stack: {get_logging_level_stack()}")

    restore_logging_level()             # Restore (and pop) the pre-existing level from from stack
    return


logging.warning (f"1 - Before myfunction() call   - logging level: {logging.getLogger().level}. On the stack: {get_logging_level_stack()}")
myfunction()
logging.warning (f"3 - After  myfunction() return - logging level: {logging.getLogger().level}. On the stack: {get_logging_level_stack()}")
```
The output:
```
$ ./core_ex3.py 
       core_ex3.<module>             -  WARNING:  1 - Before myfunction() call   - logging level: 30. On the stack: []
       core_ex3.myfunction           -    DEBUG:  2 - Within myfunction()        - logging level: 10. On the stack: [30]
       core_ex3.<module>             -  WARNING:  3 - After  myfunction() return - logging level: 30. On the stack: []
```
`set_logging_level()` and `restore_logging_level()` are used extensively within `rwt.run_with_timeout()` for validation and regression testing, and within `configman.loadconfig()` additionally for handling the 
`LogLevel` setting from the config file.

<br>

## `periodic_log()` - Logging without flooding the log

`periodic_log()` provides an clean and easy method for logging important events in your tool script's execution without the risk of getting hundreds of the same log messages when there is a problem.
Log messages are tagged with a category (related messages can share the same category), and that category of messages will only be logged once in a specified period of time (eg, 5 minutes or 2 days). Any number of categories of messages may be used.

With this code:
```
#!/usr/bin/env python3
import time
from cjnfuncs.core import set_toolname, setuplogging, periodic_log, set_logging_level, logging

set_toolname ('core_ex4')
setuplogging (ConsoleLogFormat='{asctime} {module:>6}.{funcName:6} {levelname:>8}:  {message}')
set_logging_level (logging.INFO)

periodic_log ("mycat1 messages are logged once every 1s at log_level WARNING", category='mycat1', log_interval='1s', log_level=30)
periodic_log ("mycat2 messages are logged once every 3s at log_level INFO", category='mycat2', log_interval='3s', log_level=logging.INFO)

for n in range(100):
    periodic_log (f"Loop iteration {n}", category='mycat1')
    periodic_log (f"Loop iteration {n}", category='mycat2')

    time.sleep (0.1)
```

We get this output:
```
$ ./core_ex4.py 
2025-07-01 13:06:07,898   core.plog    WARNING:  [PLog-mycat1] mycat1 messages are logged once every 1s at log_level WARNING
2025-07-01 13:06:07,898   core.plog       INFO:  [PLog-mycat2] mycat2 messages are logged once every 3s at log_level INFO
2025-07-01 13:06:08,900   core.plog    WARNING:  [PLog-mycat1] Loop iteration 10
2025-07-01 13:06:09,901   core.plog    WARNING:  [PLog-mycat1] Loop iteration 20
2025-07-01 13:06:10,903   core.plog    WARNING:  [PLog-mycat1] Loop iteration 30
2025-07-01 13:06:10,903   core.plog       INFO:  [PLog-mycat2] Loop iteration 30
2025-07-01 13:06:11,904   core.plog    WARNING:  [PLog-mycat1] Loop iteration 40
2025-07-01 13:06:12,906   core.plog    WARNING:  [PLog-mycat1] Loop iteration 50
2025-07-01 13:06:13,907   core.plog    WARNING:  [PLog-mycat1] Loop iteration 60
2025-07-01 13:06:13,908   core.plog       INFO:  [PLog-mycat2] Loop iteration 60
2025-07-01 13:06:14,909   core.plog    WARNING:  [PLog-mycat1] Loop iteration 70
2025-07-01 13:06:15,911   core.plog    WARNING:  [PLog-mycat1] Loop iteration 80
2025-07-01 13:06:16,912   core.plog    WARNING:  [PLog-mycat1] Loop iteration 90
2025-07-01 13:06:16,913   core.plog       INFO:  [PLog-mycat2] Loop iteration 90
```