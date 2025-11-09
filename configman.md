# configman - A most excellent configuration file manager

Skip to [API documentation](#links)


## Getting started - A basic config file example

Given the following config file:

        # configman_ex1.cfg - My first config file

        My_name_is      Pat     # SNL reference
        The_Dog      =  Penguin
        Dog's_age    :  3

This config file is loaded and accessed by your script code:

        #!/usr/bin/env python3
        # ***** configman_ex1.py *****

        from cjnfuncs.core      import set_toolname
        from cjnfuncs.configman import config_item
        import cjnfuncs.core as core

        set_toolname('configman_ex1')
        core.tool.config_dir = '.'          # See Note below

        my_config = config_item('configman_ex1.cfg')
        my_config.loadconfig()

        print (f"My name is {my_config.getcfg('My_name_is')}")
        my_dog = my_config.getcfg('The_Dog')
        dogs_age = my_config.getcfg("Dog's_age")
        print (f"My dog's name is {my_dog}.  He is {dogs_age} years old.")
        print (f"The_Dog {type(my_dog)}, Dogs_age {type(dogs_age)}")

And the obvious output is...

        $ ./configman_ex1.py 
        My name is Pat
        My dog's name is Penguin.  He is 3 years old.
        The_Dog <class 'str'>, Dogs_age <class 'int'>


Notables:
1. The config file is structured as lines of `param = value` pairs, with supported separators of whitespace, `=` or `:`.  Each pair is typically on a single line.  Comments start with `#` and are supported on lines by themselves or on the end of param lines.
1. A config file is loaded using `my_config.loadconfig()`. The param values are loaded based on their parsed types. All Python types are supported...  `str`, `int`, `bool`, `float`, `list`, `dict`, `tuple`.  Types support makes for cleaner script code.  (Note: `my_config` is the example 
config_item instance name used throughout this documentation.)
1. Params are accessed in script code using `my_config.getcfg()`.  getcfg() supports fallback values and type checking.

***Note***: configman relies on the environment set up by `set_toolname()`, which creates a set of application path variables such as `core.tool.config_dir`.  In the case of a user-mode script, `core.tool.config_dir` is set to `~/.config/<toolname>`, so by default that is the directory that configman will look in for `configman_ex1.cfg`.  For these examples we have overridden the default config directory to be the directory that we are running the example script from (`.`).
Alternately, the full path to the config file may be passed to the `config_item()` call.
See the `cjnfuncs.core` module for more details.

<br>

## A full blown example - check out these nifty features...

The config file:

```
# configman_ex2.cfg 

# Demonstrating:
#   Logging control params
#   Param naming, Separators, Value types
#   Multi-line values
#   Sections, Defaults
#   Imports


# Logging setups
# **** NOTE 1
LogLevel=       20                              # Logging module levels: 10:DEBUG, 20:INFO, 30:WARNING (default), 40:ERROR, 50:CRITICAL
LogFile         configman_ex2.log               # Full path, or relative to core.tool.log_dir_base


# Example param definitions - name-value pairs separated by whitespace, '=', or ':'
# **** NOTE 2, **** NOTE 3
# All valid chars, except the separators, are allowed in a param name.
# A param name cannot start with '[', which starts a section name.
Im_tall!        True                            # Whitespace separator between name-value
Test.Bool       false                           # '.' is not special.  True and false values not case sensitive, stored as bools
No_Value_bool                                   # Param with no value becomes a True boolean
7893&(%$,.nasf||\a@=Hello                       # '=' separator, with or without whitespace
again:true                                      # ':' separator, with or without whitespace
a_str     =     6 * 7                           # configman does not support calculations, so this is loaded as a str
a_quoted_str =  "Value stored without the quotes" # equivalent to unquoted string
a_int           7
a_bool    :     false                           # True and false values not case sensitive, stored as bools
a_float         42.0
a_float_as_str  '42.0'                          # Force load as str
    a_list:     ["hello", 3.14, {"abc":42.}]    # Indentation (leading whitespace) is allowed, and ignored
    a_dict:     {"six":6, 3:3.0, 'pi':3.14}
    a_tuple=    ("Im a tuple", 7.0)


# Values may span multiple lines by using the '\' continuation character
multi_line_list = ['hello',   \                 # continuation line with discarded comment
    'goodbye',  \
\   # Full-line comment discarded.  Continuation character on each line.
\
                'another line', 5, True\        # Whitespace before/after continuation char is discarded
                ]
multi_line_str : Generally, \
    don't use quotes \
    within multi-line strings.\
    Check results carefully.


# Sections are supported
# **** NOTE 3, **** NOTE 4
[ Bad params ]              # Embedded whitespace retained, leading and trailing whitespace is trimmed off
# If loadconfig() can't parse the value as a int/bool/float/list/dict/tuple, then the param is loaded as a str
# Strings within list/dict/tuple must be quoted.
# All of these are loaded as strings:
bad_list        ["hello", 3.14 {"abc":42.}]     # Missing comma
bad_tuple=      (Im a tuple, 7.0)               # String <Im a tuple> missing quotes
bad_dict:       {"six":6, 3:3.0, milk:3}        # String <milk> missing quotes
bad_float       52.3.5                          # Not a valid float


# The [DEFAULT] section can be declared.  Multiple [DEFAULT] sections are merged.
# **** NOTE 5
[DEFAULT]
my_def_param    my_def_value


# Section name "[]" resets to the top-level section.  Nested sections are NOT supported.
# Any section may be re-opened for adding more params.  loadconfig() merges all params for the given section.
[  ]                                            # Leading/trailing whitespace is trimmed, so equivalent to []
more_top_level  George was here                 # Strings NOT in list/dict/tuple need not be quoted, but may be.
another_str     """The original George Tirebiter was a dog in Maine"""


# More DEFAULTs
[ DEFAULT ]
another_def     false


# The SMTP section is used by the cjnfuncs.SMTP module
[SMTP]                                          # comment
NotifList       4809991234@vzwpix.com

# Import definitions within the referenced file into the current section ([SMTP] in this case)
# **** NOTE 6
import          creds_SMTP


# Back to the top-level
[]
another_top_level   It's only a flesh wound!
```

The script code:

        #!/usr/bin/env python3
        # ***** configman_ex2.py *****

        from cjnfuncs.core      import set_toolname
        from cjnfuncs.configman import config_item
        import cjnfuncs.core as core

        set_toolname('configman_ex2')
        core.tool.config_dir = '.'                              # **** NOTE 6

        my_config = config_item('configman_ex2.cfg')            # **** NOTE 1
        my_config.loadconfig()                                  # **** NOTE 1

        print (my_config)
        print (my_config.dump())
        print ()
        print (f"Sections list: {my_config.sections()}")        # **** NOTE 7

        print ()
        print (f"a_float:       {my_config.getcfg('a_float', types=[int, float])}") # **** NOTE 10
        print (f"a_list:        {my_config.getcfg('a_list', types=list)}")
        print (f"my_def_param:  {my_config.getcfg('my_def_param')}")
        print (f"EmailUser:     {my_config.getcfg('EmailUser', section='SMTP')}")
        # **** NOTE 8
        print (f"not_defined:   {my_config.getcfg('not_defined', fallback='Using fallback value')}")

        r = my_config.getcfg('a_list')[2]['abc']
        print (f"Given radius {r}, the circle's area is {my_config.getcfg('a_dict')['pi'] * r ** 2}")

        print (f"a_float:       {my_config.cfg['a_float']}")    # **** NOTE 9
        print (f"bad_float:     {my_config.cfg['Bad params']['bad_float']}")

And the output:

```
$ ./configman_ex2.py 

Stats for config file <configman_ex2.cfg>:
.config_file            :  configman_ex2.cfg
.config_dir             :  /mnt/share/dev/packages/cjnfuncs/tools/doc_code_examples
.config_full_path       :  /mnt/share/dev/packages/cjnfuncs/tools/doc_code_examples/configman_ex2.cfg
.config_timestamp       :  1736462755
.sections_list          :  ['Bad params', 'SMTP']
.force_str              :  False
.secondary_config       :  False
core.tool.log_dir_base  :  .

***** Section [] *****
            LogLevel = 20  <class 'int'>
             LogFile = configman_ex2.log  <class 'str'>
            Im_tall! = True  <class 'bool'>
           Test.Bool = False  <class 'bool'>
       No_Value_bool = True  <class 'bool'>
 7893&(%$,.nasf||\a@ = Hello  <class 'str'>
               again = True  <class 'bool'>
               a_str = 6 * 7  <class 'str'>
        a_quoted_str = Value stored without the quotes  <class 'str'>
               a_int = 7  <class 'int'>
              a_bool = False  <class 'bool'>
             a_float = 42.0  <class 'float'>
      a_float_as_str = 42.0  <class 'str'>
              a_list = ['hello', 3.14, {'abc': 42.0}]  <class 'list'>
              a_dict = {'six': 6, 3: 3.0, 'pi': 3.14}  <class 'dict'>
             a_tuple = ('Im a tuple', 7.0)  <class 'tuple'>
     multi_line_list = ['hello', 'goodbye', 'another line', 5, True]  <class 'list'>
      multi_line_str = Generally, don't use quotes within multi-line strings. Check results carefully.  <class 'str'>
      more_top_level = George was here  <class 'str'>
         another_str = The original George Tirebiter was a dog in Maine  <class 'str'>
   another_top_level = It's only a flesh wound!  <class 'str'>
***** Section [Bad params] *****
            bad_list = ["hello", 3.14 {"abc":42.}]  <class 'str'>
           bad_tuple = (Im a tuple, 7.0)  <class 'str'>
            bad_dict = {"six":6, 3:3.0, milk:3}  <class 'str'>
           bad_float = 52.3.5  <class 'str'>
***** Section [SMTP] *****
           NotifList = 4809991234@vzwpix.com  <class 'str'>
         EmailServer = mail.myserver.com  <class 'str'>
     EmailServerPort = P587TLS  <class 'str'>
           EmailUser = outbound@myserver.com  <class 'str'>
           EmailPass = mypassword  <class 'str'>
           EmailFrom = me@myserver.com  <class 'str'>
***** Section [DEFAULT] *****
        my_def_param = my_def_value  <class 'str'>
         another_def = False  <class 'bool'>

Sections list: ['Bad params', 'SMTP']

a_float:       42.0
a_list:        ['hello', 3.14, {'abc': 42.0}]
my_def_param:  my_def_value
EmailUser:     outbound@myserver.com
not_defined:   Using fallback value
Given radius 42.0, the circle's area is 5538.96
a_float:       42.0
bad_float:     52.3.5

```

Notables (See **** NOTE # in the above example config file and code):
1. loadconfig() looks for `LogLevel` abd `LogFile` and sets the root logger accordingly.  If you want to
change the console or file logging format you may also define `ConsoleLogFormat` or `FileLogFormat`, respectively.  Logging setups only apply for the primary/master config (`config_item(secondary_config = False)`).  The logging level _within_ loadconfig() is controlled by the child logger `cjnfuncs.configman` (default WARNING level, see below).
2. loadconfig() accepts most any character in a param name, except the comment character `#`, or the param-value separator characters whitespace, `=`, or `:`.  
3. loadconfig() attempts to load a value as a type `int`, `bool`, `float`, `list`, `dict`, or `tuple`, if the value has the correct syntax for that type.  The fallback is to type `str`.  Loading all params as type `str` can be forced:  `my_config = config_item('configman_ex2.cfg', force_str=True)`.
4. Sections are supported, and are accessed as `my_config.getcfg('NotifList', section='SMTP')`.  Only 
one section depth level is allowed (no nested sections).  Section `[]` resets to the top-level; for example, `LogLevel` and `more_top_level` are in the same `[]` section.  Whitespace is allowed within section names, and leading and trailing whitespace is stripped - sections `[ Bad params ]`, `[Bad params ]`, `[Bad params]` are all the same section.
5. A `[DEFAULT]` section may be defined.  getcfg() will attempt to get a param from the specified section, and if not found then will look in the DEFAULT section.  Params within the DEFAULT section apply to all sections, including the top-level section.
6. On imports (the `import` keyword is case insensitive), the specified file is looked for relative to  
`core.tool.config_dir` (normally `~/.config/configman_ex2`, in this example).  A full/absolute path may also be specified.  NOTE that in this example code the `core.tool.config_dir` path has been jammed to `.`.
7. Any DEFAULT section is not included in the `my_config.sections()` list, consistent with the standard library configparser.
8. getcfg's search order is:  1) in the specified section, 2) in the DEFAULT section, and 3) the `fallback=` value, if specified.  If the param is not found and no fallback is specified then getcfg raises a ConfigError.
9. Params may be accessed directly by reaching into the <config>.cfg dictionary; however there is no default or fallback support, and a dictionary access KeyError is raised if the param is not found.
10. getcfg() optionally supports expected types enforcement.  Expected types may be specified as a single type or a list of allowed types.  A ConfigError is raised if the value is not of the expected type(s).  This feature can help keep script code cleaner by minimizing expected value checking.

<br>

## On-the-fly config file reloads for service scripts

Service scripts run endlessly, and periodically do their operations.  The operations and their repeat period are set in the config file.  If the config file is modified, the service script is set up to reload the data and reinitialize, thus eliminating the need to manually restart the service script each time the config file is edited.

```
#!/usr/bin/env python3
# ***** configman_ex3.py *****

import time

from cjnfuncs.core      import set_toolname, logging
from cjnfuncs.configman import config_item
import cjnfuncs.core as core

TOOL_NAME =   'configman_ex3'
CONFIG_FILE = 'configman_ex3.cfg'


def service_loop():

    first = True
    while True:
        reloaded = my_config.loadconfig(flush_on_reload=True, tolerate_missing=True)

        if reloaded == -1:              # **** NOTE 2
            logging.warning("Config file not currently accessible.  Skipping reload check for this iteration.")
            
        else:
            if first or reloaded == 1:  # **** NOTE 3
                first = False

                if reloaded:            # **** NOTE 4
                    logging.warning("Config file reloaded.  Refreshing setup.")
                    # Stop any operations, threads, etc that will need to refresh their setups

                logging.warning (my_config)
                # Do resource setups    # **** NOTE 5
        
        # Do normal periodic operations

        time.sleep(0.5)


if __name__ == '__main__':

    set_toolname(TOOL_NAME)
    core.tool.config_dir = '.'

    my_config = config_item(CONFIG_FILE)
    my_config.loadconfig()              # **** NOTE 1

    service_loop()
```

Example output shows the timestamp change when the config file is touched:
```
$ ./configman_ex3.py 
  configman_ex3.service_loop         -  WARNING:  
Stats for config file <configman_ex3.cfg>:
.config_file            :  configman_ex3.cfg
.config_dir             :  /mnt/share/dev/packages/cjnfuncs/tools/doc_code_examples
.config_full_path       :  /mnt/share/dev/packages/cjnfuncs/tools/doc_code_examples/configman_ex3.cfg
.config_timestamp       :  1701710699
.sections_list          :  []
core.tool.log_dir_base  :  /home/me/.config/configman_ex3

  configman_ex3.service_loop         -  WARNING:  Config file reloaded.  Refreshing setup.
  configman_ex3.service_loop         -  WARNING:  
Stats for config file <configman_ex3.cfg>:
.config_file            :  configman_ex3.cfg
.config_dir             :  /mnt/share/dev/packages/cjnfuncs/tools/doc_code_examples
.config_full_path       :  /mnt/share/dev/packages/cjnfuncs/tools/doc_code_examples/configman_ex3.cfg
.config_timestamp       :  1701712450
.sections_list          :  []
core.tool.log_dir_base  :  /home/me/.config/configman_ex3
```

Notables:
1. At the startup of the service script, with `loadconfig(tolerate_missing=False)`, the config file must be accessible or a `ConfigError` will be raised.  This should be trapped and gracefully handled.
2. With `loadconfig(tolerate_missing=True)`, `-1` will be returned if the config file is not currently accessible. You will want to add code to output this warning only once, so as to not flood the log.  tolerate_missing=True allows the config file to be placed on a network file system. Also see `core.periodic_log()`.
3. loadconfig() will return `1` if the config file timestamp has changed (`0` if not changed).  If the config file was changed the `loadconfig(flush_on_reload=True)` call will have purged all cfg data and reloaded it from the file.
4. If this is a `reloaded` case (versus `first`), then cleanup work may be needed prior to the following resource setups.
5. Threads and asyncio should use local copies of cfg data so that they don't crash when the cfg data temporarily disappears during the loadconfig() reload.  Also see loadconfig's `prereload_callback` parameter.

<br>

## Programmatic config file edits

One service script I use periodically recalculates its control parameters, then modifies the config file with the new values, which then triggers a reload of the config file.  Using this method allows the service script to be later restarted and continue to use the latest values. 

This code demonstrates changes that can be done using modify_configfile():
```
config = config_item('my_configfile.cfg')
config.modify_configfile("abc",                 remove=True)                # Removed
config.modify_configfile("def", "123456789 123456789")                      # Modified value
config.modify_configfile("", "",                add_if_not_existing=True)   # Add blank line
config.modify_configfile("George", "was here",  add_if_not_existing=True)   # Add param if not found
config.modify_configfile("Snehal", "wasn't here")                           # Warning message if not existing
config.modify_configfile(                       add_if_not_existing=True)   # Add another blank line
config.modify_configfile("# New comment line",  add_if_not_existing=True, save=True) # Add comment and save
```

Notables:
- modify_configfile() works _directly_ on the config file, not the loaded content in the instance cfg dictionary.  None of the changes are available without reloading the config file.
- Params may be changed, deleted, or added.
- All instances of a param in the file receive the change, including in all sections and DEFAULT. (a _artifact_ of this implementation.)
- The formatting of changed lines is closely retained, including comments.
- Blank lines and comments may be added (always at the end).
- The final call needs `save=True` in order to push the modifications to the file.
- Warning messages are logged for attempting to modify or remove a non-existing param.

<br>

## Using secondary configuration files

In some applications it is appropriate to load configuration data from more than one config file.  This example has three config files in use.  main_cfg is frequently changed as the application evolves and is tuned, while PCBSs_cfg and sensors_cfg are much more static and controlled.

```
main_cfg = config_item('my_app.cfg')
main_cfg.loadconfig()

PCBs_cfg = config_item('board_versions.cfg', secondary_config=True)
PCBs_cfg.loadconfig()

sensors_cfg = config_item('sensors.cfg', secondary_config=True)
sensors_cfg.loadconfig()

main_bd_version = main_cfg.getcfg('main_bd_version')        # returns 'V2'
ADC_addr = PCBs_cfg.getcfg('ADC_addr', section=main_bd_version)
# returns '0x15' if V1, or '0x73' if V2

sensor_serial = main_cfg.getcfg('sensor_serial')            # returns 'sn100328'
sensor_config = sensors_cfg.getcfg(sensor_serial, section=sensor_serial)
# returns {"name":"S100328_Orange",  "exp": -1.395, "mult": 689.5}

```
Notables:
- Params in the main_cfg make reference to PCB board versions, then PCBs_cfg is accessed to pick up version-specific chip addresses.
- Params in the main_cfg make reference to sensors by serial number, then sensors.cfg is accessed for the calibration data.
- main_cfg includes logging setups, and thus is the primary config file for this system.  All other loaded config files should be tagged as `secondary_config=True`.


<br>

## Comparison to Python's configparser module

  Feature | configman | Python configparser
  ---|---|---
  Native types | **int, float, bool (true/false case insensitive), list, tuple, dict, str** | str only, requires explicit type casting via getter functions
  Reload on config file change | **built-in** | not built-in
  Import sub-config files | **Yes** | No
  Section support | Yes | Yes
  Default support | Yes | Yes
  Fallback support | Yes (getcfg(fallback=)) | Yes
  Whitespace in param_names | No | Yes
  Case sensitive param_names | Yes (always) | Default No, customizable
  Param/value delimiter | whitespace, ':', or '=' fixed | ':' or '=', customizable
  Param only (no value) | Yes (stored as True) | Yes
  Multi-line values | Yes ('\\' continuation character) | Yes
  Comment prefix | '#' fixed (thus '#' can't be part of the param_name) | '#' or ';', customizable
  Interpolation | No | Yes
  Mapping Protocol Access | No | Yes
  Save to file | Yes | Yes

<br>

## Controlling logging from within configman code

Logging within the configman module uses the `cjnfuncs.configman` named/child logger.  By default this logger is set to the `logging.WARNING` level, 
meaning that no logging messages are produced from within the configman code.  For validation and debug purposes, logging from within configman code 
can be enabled by setting the logging level for this module's logger from within the tool script code:

        logging.getLogger('cjnfuncs.configman').setLevel(logging.DEBUG)     # or logging.INFO

        # Or alternately, use the core module set_logging_level() function:
        set_logging_level (logging.DEBUG, 'cjnfuncs.configman')




<a id="links"></a>
         
<br>

---

# Links to classes, methods, and functions

- [config_item](#config_item)
- [loadconfig](#loadconfig)
- [read_string](#read_string)
- [read_dict](#read_dict)
- [getcfg](#getcfg)
- [modify_configfile](#modify_configfile)
- [write](#write)
- [sections](#sections)
- [clear](#clear)
- [dump](#dump)



<br/>

<a id="config_item"></a>

---

# Class config_item (config_file=None, remap_logdirbase=True, force_str=False, secondary_config=False, safe_mode=False) - Create a configuration instance
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
- Set to `True` when loading additional config files.  Disables logging setup related changes.
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
- A list of string names for all defined sections.

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
    
<br/>

<a id="loadconfig"></a>

---

# loadconfig () - Load a configuration file into the cfg dictionary
```
loadconfig(
    call_logfile        = None,
    call_logfile_wins   = False,
    flush_on_reload     = False,
    force_flush_reload  = False,
    isimport            = False,
    tolerate_missing    = False,
    prereload_callback  = None)        
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

`force_flush_reload` (bool, default False)
- Forces the `cfg` dictionary to be cleaned out and the config file to be reloaded, 
regardless of whether the config file timestamp has changed

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

1. **Native int, float, bool, list, tuple, dict, str support** - Bool true/false is case insensitive. A str
  type is stored in the `cfg` dictionary if none of the other types can be resolved for a given value_portion.
  Automatic typing avoids most explicit type casting clutter in the tool script. Be careful to error trap
  for type errors (eg, expecting a float but user input error resulted in a str). Also see the 
  getcfg() `types=[]` arg for basic type enforcement.

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
  The tool script code may also manually/explicitly set the root logging level _after the initial `loadconifig()` call_
  and this value will be retained over later calls to loadconfig, thus allowing for a command line `--verbose`
  switch feature.  Note that logging done _within_ loadconfig() uses the `cjnfuncs.configmap` child/named logger.
  `logging.getLogger('cjnfuncs.configman').setLevel(logging.INFO)` (or DEBUG) enables diagnostic logging from
  loadconfig.

1. **Log file options** - Where to log has two separate fields:  `call_logifle` in the call to loadconfig(), and 
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

1. **Config reload if changed, `flush_on_reload`, and `force_flush_reload`** - loadconfig() may be called 
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
   - `force_flush_reload=True` (default False) forces both a clear/flush of the `cfg` dictionary and then a fresh
  reload of the config file. 
   - **Note** that if using threading then a thread should be paused while the config file 
  is being reloaded with `flush_on_reload=True` or `force_flush_reload=True` since the params will disappear briefly.
  Use the `prereload_callback` mechanism to manage any code dependencies before the cfg dictionary is purged.
   - Changes to imported files are not tracked for changes.

1. **Tolerating intermittent config file access** - When implementing a service loop, if `tolerate_missing=True` 
(default False) then loadconfig() will return `-1` if the config file cannot be accessed, informing the 
tool script of the problem for appropriate handling (typically logging the event then ignoring the problem for
the current iteration). If `tolerate_missing=False` then loadconfig() will raise a ConfigError if the config file 
cannot be accessed.
        
<br/>

<a id="read_string"></a>

---

# read_string (str_blob, isimport=False) - Load content of a string into the cfg dictionary

***config_item() class member function***

read_string() does the actual work of loading lines of config data into the cfg dictionary. 
Loaded content is added to and/or modifies any previously loaded content.

Note that loadconfig() calls read_string() for the actual loading of config data. loadconfig()
handles the other loading features such as LogLevel, LogFile, logging formatting,
flush_on_reload, force_flush_reload, and tolerate_missing.


### Args
`str_blob` (str)
- String containing the lines of config data

`isimport` (bool, default False)
- Internally set True when handling imports.  Not used by tool script calls.


### Returns
- A ConfigError is raised if there are parsing issues
- A ConfigError is also raised if an imported config file cannot accessed
        
<br/>

<a id="read_dict"></a>

---

# read_dict (param_dict, section_name='') - Load the content of a dictionary into the cfg dictionary

***config_item() class member function***

Loaded content is added to and/or modifies any previously loaded content.

### Args
`param_dict` (dict)
- dictionary to be loaded

`section_name` (str, default '' (top level))
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
        
<br/>

<a id="getcfg"></a>

---

# getcfg (param, fallback=None, types=[ ], section='') - Get a param's value from the cfg dictionary

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
- No type enforcement - the fallback value need not be in the `types` list.

`types` (single or list of as-expected types, default '[]' (any type accepted))
- if provided, a ConfigError is raised if the param's value type is not in the list of expected types
- `types` may be a single type (eg, `types=int`) or a list of types (eg, `types=[int, float]`)
- Supported types: [str, int, float, bool, list, tuple, dict]

`section` (str, default '' (top-level))
- Select the section from which to get the param value.


### Returns
- The param value from 1) from the specified `section` if defined, 2) from the `DEFAULT` section if defined,
  or 3) from the `fallback` value if specified.
- If the param is not found, or the param's type is not in the `types` list, if specified, then a ConfigError is raised.
        
<br/>

<a id="modify_configfile"></a>

---

# modify_configfile (param='', value='', remove=False, add_if_not_existing=False, save=False) - Make edits to the config file

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
        
<br/>

<a id="write"></a>

---

# write (savefile) - Write config data to a file

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
        
<br/>

<a id="sections"></a>

---

# sections () - Return a list of sections in the cfg dictionary

***config_item() class member function***

For compatibility with the standard library configparser.  Also available via `<config>.sections_list`.

Example:
```
code:
    print (my_config.sections())

output:
    ['Bad params', 'SMTP']
```
        
<br/>

<a id="clear"></a>

---

# clear (section='') - Purge a portion of the cfg dictionary

***config_item() class member function***

### Args
`section` (str, default '')
- `section = ''` clears the entire cfg dictionary, including all sections and DEFAULT
- `section = '<section_name>'` clears just that section
- `section = 'DEFAULT'` clears just the DEFAULT section


### Returns
- None
- A ConfigError is raised if attempting to remove a non-existing section
        
<br/>

<a id="dump"></a>

---

# dump () - Return the formatted content of the cfg dictionary

***config_item() class member function***


### Returns
- str type pretty formatted content of the cfg dictionary, along with any sections and defaults
        