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
        core.tool.config_dir = '.'          # See note below

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
1. The config file is structured as lines of `param` - `value` pairs, with supported separators of whitespace, `=` or `:`.  Each pair is on a single line.  Comments are supported on lines by themselves or on the end of param lines.
1. A config file is loaded using `configman.loadconfig()`. The param values are loaded based on their parsed types. Most all types are supported...  `str`, `int`, `bool`, `float`, `list`, `dict`, `tuple`.  Types support makes for clean script code.
1. Params are accessed in script code using `configman.getcfg()`.  getcfg() supports fallback values and type checking.

***Note***: configman relies on the environment set up by `set_toolname()`, which creates a set of application path variables such as `core.tool.config_dir`.  In the case of a user-mode script, the .config_dir is set to `~/.config/<toolname>`, so by default that is the directory that configman will look in for `configman_ex1.cfg`.  For these examples we have overridden the default config directory to be the directory that we are running the example script from (`.`).
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
#   Sections, Defaults
#   Imports


# Logging setups
# **** NOTE 1
LogLevel=       20                  # Logging module levels: 10:DEBUG, 20:INFO, 30:WARNING (default), 40:ERROR, 50:CRITICAL
LogFile         configman_ex2.log   # Full path, or relative to core.tool.log_dir_base


# Example param definitions - name-value pairs that are whitespace, "=", or ":" separated
# **** NOTE 2
I'm_tall!       True        # Most any chars supported in a param name - All but '#' or separators, nor start with '['
Test.Bool       false       # '.' is not special.  True and false values not case sensitive, stored as bools
7893&(%$,.nasf||\a@=Hello   # '=' separator, with or without whitespace
again:true                  # ':' separator, with or without whitespace

# **** NOTE 3
a_str     =     6 * 7       # configman does not support calculations, so this is loaded as a str
a_int           7
a_bool    :     False       # True and false values not case sensitive, stored as bools
a_float         42.0
    a_list:         ["hello", 3.14, {"abc":42.}]    # Indentation is allowed, and ignored
    a_dict:         {"six":6, 3:3.0, 'pi':3.14}
    a_tuple=        ("Im a tuple", 7.0)


# Sections are supported
# **** NOTE 3, **** NOTE 4
[ Bad params ]              # Embedded whitespace retained, leading and trailing whitespace is trimmmed off
# If loadconfig() can't parse the value as a int/bool/float/list/dict/tuple, then the param is loaded as a str
# Strings within list/dict/tuple must be quoted with either single of double quotes.
# All of these are loaded as strings:
bad_list        ["hello", 3.14 {"abc":42.}]     # Missing comma
bad_tuple=      (Im a tuple, 7.0)               # String <Im a tuple> missing quotes
bad_dict:       {"six":6, 3:3.0, milk:3}        # String <milk> missing quotes
bad_float       52.3.5                          # Not a valid float


# The [DEFAULT] section can be declared.  Multiple [DEFAULT] sections are merged by loadconfig()
# **** NOTE 5
[DEFAULT]
my_def_param    my_def_value


# Section name "[]" resets to the top-level section.  Nested sections not supported.
# Any section may be re-opened for adding more params.  loadconfig() merges all params for the given section.
[  ]
more_top_level  George      # Strings _not_ in list/dict/tuple are _not_ quoted


# More DEFAULTs
[ DEFAULT ]
another_def     false


# The SMTP section is used by the cjnfuncs.SMTP module
[SMTP]
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
.config_timestamp       :  1701632145
.sections_list          :  ['Bad params', 'SMTP']
core.tool.log_dir_base  :  /home/me/.config/configman_ex2

***** Section [] *****
            LogLevel = 20  <class 'int'>
             LogFile = configman_ex2.log  <class 'str'>
           I'm_tall! = True  <class 'bool'>
           Test.Bool = False  <class 'bool'>
 7893&(%$,.nasf||\a@ = Hello  <class 'str'>
               again = True  <class 'bool'>
               a_str = 6 * 7  <class 'str'>
               a_int = 7  <class 'int'>
              a_bool = False  <class 'bool'>
             a_float = 42.0  <class 'float'>
              a_list = ['hello', 3.14, {'abc': 42.0}]  <class 'list'>
              a_dict = {'six': 6, 3: 3.0, 'pi': 3.14}  <class 'dict'>
             a_tuple = ('Im a tuple', 7.0)  <class 'tuple'>
      more_top_level = George  <class 'str'>
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
change the console or file logging format you may also define `ConsoleLogFormat` or `FileLogFormat`, respectively.  Logging setups only apply for the primary/master config (`config_item(secondary_config = False)`).  The logging level _within_ loadconfig() is set using the `ldcfg_ll` switch (default WARNING level).
2. loadconfig() accepts most any character in a param name, except the comment character `#`, or the param-value separator characters whitespace, `=`, or `:`.  
3. loadconfig() attempts to load a value as a type `int`, `bool`, `float`, `list`, `dict`, or `tuple`, if the value has the correct syntax for that type.  The fallback is to type `str`.  Loading all params as type `str` can be forced:  `my_config = config_item('configman_ex2.cfg', force_str=True)`.
4. Sections are supported, and are accessed as `my_config.getcfg('NotifList', section='SMTP')`.  Only 
one section depth level is allowed (no nested sections).  Section `[]` resets to the top-level; for example, `LogLevel` and `more_top_level` are in the same `[]` section.  Whitespace is allowed within section names, and leading and trailing whitespace is stripped - sections `[ Bad params ]`, `[Bad params ]`, `[Bad params]` are all the same section.
5. A `[DEFAULT]` section may be defined.  .getcfg() will attempt to get a param from the specified section, and if not found then will look in the DEFAULT section.  Params within the DEFAULT section apply to all sections, including the top-level section.
6. On imports (the `import` keyword is case insensitive), the specified file is looked for relative to  
`core.tool.config_dir` (normally `~/.config/configman_ex2`, in this example).  A full/absolute path may also be specified.  NOTE that in this example code `core.tool.config_dir` path has been jammed to `.`.
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
2. With `loadconfig(tolerate_missing=True)`, `-1` will be returned if the config file is not currently accessible. You will want to add code to output this warning only once, so as to not flood the log.  tolerate_missing=True allows the config file to be placed on a shared file system. 
3. loadconfig() will return `1` if the config file timestamp has changed (`0` if not changed).  The prior `loadconfig(flush_on_reload=True)` will have purged all cfg data and reloaded it from the file.
4. If this is a `reloaded` case (versus `first`), then cleanup work may be needed prior to the following resource setups.
5. Threads and asyncio should use local copies of cfg data so that they don't crash when the cfg data temporarily disappears during the loadconfig() reload.

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
- All instances of a param in the file receive the change, including in all sections and DEFAULT. (a shortcoming of this implementation.)
- The formatting of changed lines is closely retained, including comments.
- Blank lines and comments may be added (always at the end).
- The final call needs `save=True` in order to push the modifications to the file.
- Warning messages are logged for attempting to modify or remove a non-existing param.

<br>

## Using secondary configuration files

In some applications it's appropriate to load configuration data from more than one config file.  This example has three config files in use.  main_cfg is frequently changed as the application evolves and is tuned, while PCBSs_cfg and sensors_cfg are much more static and controlled.

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
  Whitespace in params | No | Yes
  Case sensitive params | Yes (always) | Default No, customizable
  Param/value delimiter | whitespace, ':', or '=' fixed | ':' or '=', customizable
  Param only (no value) | Yes (stored as True) | Yes
  Multi-line values | No | Yes
  Comment prefix | '#' fixed (thus '#' can't be part of the param or value) | '#' or ';', customizable
  Interpolation | No | Yes
  Mapping Protocol Access | No | Yes
  Save to file | Yes | Yes


<a id="links"></a>
         
<br>

---

# Links to classes, methods, and functions

- [config_item](#config_item)
- [sections](#sections)
- [clear](#clear)
- [dump](#dump)
- [loadconfig](#loadconfig)
- [read_string](#read_string)
- [read_dict](#read_dict)
- [getcfg](#getcfg)
- [modify_configfile](#modify_configfile)
- [write](#write)



<br/>

<a id="config_item"></a>

---

# Class config_item (config_file=None, remap_logdirbase=True, force_str=False, secondary_config=False) - Create a configuration instance

The config_item() class provides handling of one or more config file instances.  Class methods include:
 - Config file loading and reloading - `loadconfig()`
 - Loading config data from strings and dictionaries - `read_string()`, `read_dict()`
 - Getting values from the loaded config, with defaults and fallback - `getcfg()`
 - Programmatically modifiying the config file content - `modify_configfile()`
 - Getting instance status - `__repr__()`, `section()`, `dump()`


### Instantiation parameters
`config_file` (default None)
- Path to the configuration file, relative to the `core.tool.config_dir` directory, or an absolute path.
- `None` may be used if the config will be loaded programmatically via `read_string()` or `read_dict()`.

`remap_logdirbase` (default True)
- If `remap_logdirbase=True` and the tool script is running in _user_ mode (not site mode) 
then the `core.tool.log_dir_base` will be set to `core.tool.config_dir`.

`force_str` (default False)
- Causes all params to be loaded as type `str`, overriding the default type identification.

`secondary_config` (default False)
- Set to `True` when loading additional config files.  Disables logging setup related changes.
- The primary config file should be loaded first before any secondary_config loads, so that logging 
is properly set up.


### Returns
- Handle to the `config_item()` instance
- Raises a `ConfigError` if the specified config file is not found


### Behaviors and rules
- More than one `config_item()` may be created and loaded.  This allows for configuration data to be partitioned 
as desired.  Each defined config is loaded to its own instance-specific `cfg` dictionary. Only one config_item()
instance should be considered the primary, while other instances should be tagged with `secondary_config=True`. 
Logging setups are controlled only the primary instance.
Also see the loadconfig() `import` feature.
- Initially in _user_ mode, after the `set_toolname()` call, `core.tool.log_dir_base` 
(the log directory) is set to the `core.tool.user_data_dir`.
Once `config_item()` is called the `core.tool.log_dir_base` is _remapped_ to 
`core.tool.config_dir`.  This is the author's style preference (centralize primary files, and 
reduce spreading files around the file system).
To disable this remap, in the `config_item()` call set `remap_logdirbase=False`.
This remapping is not done in site mode.
- A different log base directory may be set by user code by setting `core.tool.log_dir_base` to a different 
path after the `set_toolname()` call and before the `config_item()` call, for example 
`core.tool.log_dir_base = "/var/log"` may be desireable in site mode.
- A different config directory may be set by user code by setting `core.tool.config_dir` to a different 
path after the `set_toolname()` call and before the `config_item()` call, for example 
`core.tool.config_dir = core.tool.main_dir`, which sets the config dir to the same as the tool script's 
directory.  With `remap_logdirbase=True`, the log dir will also be set to the tool script's directory.
- Details of the configuration instance may be printed, eg, `print (my_config)`.
    
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

# clear (section=' ') - Purge a portion of the cfg dictionary

***config_item() class member function***

### Parameters
`section` (default '')
- `section = ''` clears the entire cfg dictionary, including all sections and DEFAULT
- `section = '<section_name>'` clears just that section
- `section = 'DEFAULT'` clears just the DEFAULT section


### Returns
- A ConfigError is raised if attempting to remove a non-existing section
        
<br/>

<a id="dump"></a>

---

# dump () - Return the formatted content of the cfg dictionary

***config_item() class member function***
        
<br/>

<a id="loadconfig"></a>

---

# loadconfig () - Load a configuration file into the cfg dictionary
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
***config_item() class member function***

Param = value lines in the config_item()'s file are loaded to the instance-specific `cfg` dictionary, 
and can be accessed directly or via `<config_item>.getcfg()`.

`loadconfig()` initializes the root logger for logging either to 1) the `LogFile` specified in
the loaded config file, 2) the `call_logfile` in the `loadconfig()` call, or 3) the console.
`loadconfig()` supports dynamic reloading of config files, partitioning of config data via the `import`
feature, and intermittent loss of access to the config file.
    

### Parameters
`ldcfg_ll` (default 30/WARNING)
- Logging level used within `loadconfig()` code for debugging loadconfig() itself

`call_logfile` (default None)
- An absolute path or relative to the `core.tool.log_dir_base` directory

`call_logfile_wins` (default False)
- If True, the `call_logfile` overrides any `LogFile` in the config file

`flush_on_reload` (default False)
- If the config file will be reloaded (due to a changed timestamp) then clean out the 
`cfg` dictionary first

`force_flush_reload` (default False)
- Forces the `cfg` dictionary to be cleaned out and the config file to be reloaded, 
regardless of whether the config file timestamp has changed

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
- See `getcfg()`, below, for accessing loaded config data. The class instance-specific `cfg` dictionary may be
  directly accessed as well.

- The format of a config file is param=value pairs.
  - Separating the param and value may be whitespace, `=` or `:`.  
  - Param names can contain most all characters, except:  `#` or the separators, and cannot start with `[`.

- Sections and a DEFAULT section are supported.  Section name are enclosed in `[ ]`.
  - Leading and trailing whitespace is trimmed off of the section name, and embedded whitespace is retained.
    EG: `[  hello my name  is  Fred  ]` becomes section name `'hello my name  is  Fred'`.
  - Section names can contain most all characters, except `#` and `]`.

- **Native int, float, bool, list, tuple, dict, str support** - Bool true/false is case insensitive. A str
  type is stored in the `cfg` dictionary if none of the other types can be resolved for a given param value.
  Automatic typing avoids most explicit type casting clutter in the tool script. Be careful to error trap
  for type errors (eg, expecting a float but user input error resulted in a str). Also see the 
  `getcfg (param, types=[])` parameter for basic type checking.

- **Logging setup** - `loadconfig()` calls `cjnfuncs.core.setuplogging()`.  The `logging` handle is available for
  import by other modules (`from cjnfuncs.core import logging`).  By default, logging will go to the
  console (stdout) filtered at the WARNING/30 level. Don't call `setuplogging()` directly if using loadconfig().

- **Logging level control** - Optional `LogLevel` in the primary config file will set the logging level after
  the config file has been loaded.  If LogLevel is not specified in the primary config file, then 
  the logging level is set to the Python default logging level, 30/WARNING.
  The tool script code may also manually/explicitly set the logging level _after the initial `loadconifig()` call_
  and this value will be retained over later calls to loadconfig, thus allowing for a command line `--verbose`
  switch feature.  Note that logging done _within_ loadconfig() code is always done at the `ldcfg_ll` level.

- **Log file options** - Where to log has two separate fields:  `call_logifle` in the call to loadconfig(), and 
  `LogFile` in the loaded primary config file, with `call_logfile_wins` selecting which is used.  This mechanism allows for
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
is relative to the `core.tool.config_dir`, if not an absolute path.
The specified file is imported as if the params were in the main config file.  Nested imports are allowed. 
Sections are not allowed within an imported file - only in the main/top-level config file.
A prime usage of `import` is to place email server credentials in your home directory with user-only readability,
then import them in the tool script config file as such: `import ~/creds_SMTP`.  

- **Config reload if changed, `flush_on_reload`, and `force_flush_reload`** - loadconfig() may be called 
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
  - Changes to imported files are not tracked for changes.

- **Tolerating intermittent config file access** - When implementing a service loop, if `tolerate_missing=True` 
(default False) then loadconfig() will return `-1` if the config file cannot be accessed, informing the 
tool script of the problem for appropriate handling. If `tolerate_missing=False` then loadconfig() will raise
a ConfigError if the config file cannot be accessed.
        
<br/>

<a id="read_string"></a>

---

# read_string (str_blob, ldcfg_ll=DEFAULT_LOGGING_LEVEL, isimport=False) - Load content of a string into the cfg dictionary

***config_item() class member function***

read_string() does the actual work of loading lines of config data into the cfg dictionary. 
Loaded content is added to and/or modifies any previously loaded content.

Note that loadconfig() calls read_string() for the actual loading of config data. loadconfig()
handles the other loading features such as LogLevel, LogFile, logging formatting,
flush_on_reload, force_flush_reload, and tolerate_missing.


### Parameters
`str_blob`
- String containing the lines of config data

`ldcfg_ll` (default 30/WARNING)
- Logging level used within `read_string()` code for debugging read_string() itself

`isimport` (default False)
- Internally set True when handling imports.  Not used by tool script calls.


### Returns
- A ConfigError is raised if there are parsing issues
- A ConfigError is also raised if an imported config file cannot be loaded (non-existent)


### Behaviors and rules
- See loadconfig() for config loading Behaviors and rules.
        
<br/>

<a id="read_dict"></a>

---

# read_dict (param_dict, section_name=' ') - Load the content of a dictionary into the cfg dictionary

***config_item() class member function***

Loaded content is added to and/or modifies any previously loaded content.

### Parameters
`param_dict`
- dictionary to be loaded

`section_name` (default '' - top level)
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
    sect_contents = {
        'd' : ('hi', 'there'),
        'e' : {'hi':'Hi!', 'there':'There!'},
        'f' : [6, 7.0, 42, 'hi']
        }
    def_contents = {
        'g' : 'Hi',
        'h' : True,
        'i' : False
        }
    new_config.read_dict(main_contents)
    new_config.read_dict(sect_contents, 'A section')
    new_config.read_dict(def_contents, 'DEFAULT')
```
        
<br/>

<a id="getcfg"></a>

---

# getcfg (param, fallback=None, types=[ ], section=' ') - Get a param's value from the cfg dictionary

***config_item() class member function***

Returns the value of param from the class instance cfg dictionary.  Equivalent to just referencing `my_config.cfg[]`
but with 1) default & fallback support, 2) type checking, and 3) section support.

The search order for a param is 1) from the specified `section`, 2) from the `DEFAULT` section, and 3) from the 
`fallback` value. If the param is not found in any of these locations then a ConfigError is raised.

Type checking may be performed by listing one or more expected types via the optional `types` parameter.
If the loaded param is not one of the expected types then a ConfigError is raised.  This check may be 
useful for basic error checking of param values, eg, making sure the return value is a float and not
a str. (str is the loadconfig() default if the param type cannot be converted to another supported type.)

NOTE: `getcfg()` is almost equivalent to `cfg.get()`, except that `getcfg()` does not default to `None`.
Rather, `getcfg()` raises a ConfigError if the param does not exist and no `fallback` is specified.
This can lead to cleaner tool script code.  Either access method may be used, along with `x = my_config.cfg["param"]`.


### Parameters
`param`
- String name of param to be fetched from cfg

`fallback` (default None)
- if provided, is returned if `param` does not exist in cfg

`types` (default '[]' empty list)
- if provided, a ConfigError is raised if the param's value type is not in the list of expected types
- `types` may be a single type (eg, `types=int`) or a list of types (eg, `types=[int, float]`)
- Supported types: [str, int, float, bool, list, tuple, dict]

`section` (default '' - top-level)
- Select the section from which to get the param value.


### Returns
- The param value from 1) from the specified `section` if defined, 2) from the `DEFAULT` section if defined,
  or 3) from the `fallback` value if specified.
- If the param is not found, or the param's type is not in the `types` list, if specified, then a ConfigError is raised.
        
<br/>

<a id="modify_configfile"></a>

---

# modify_configfile (param=' ', value=' ', remove=False, add_if_not_existing=False, save=False) - Make edits to the config file

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

NOTE:  In some circumstances the OS-reported timestamp for the modified config file may be erratic.
It may be necessary to add a time.sleep(0.5) delay between saving the modified config and the loadconfig()
reload call to avoid multiple config reloads.


### Parameters
`param` (default ' ')
- The param name, if modifying an existing param or adding a new param

`value` (default ' ')
- The new value to be applied to an existing param, or an added param
- Any comment text (after a '#') in the new value will be prepended to any existing comment text

`remove` (default False)
- If True, the `param` config file line is removed from the config file

`add_if_not_existing` (default False)
- Modify an existing param line, or add at the bottom of the config file if it is not existing
- To add a blank line leave out both `param` and `value`, or set both the `""`
- To add a comment line specify the comment in the `param` field (eg, `my_config.modify_configfile("# My comment")`)

`save` (default False)
- Write the modified config file content back to the file
- `save=True` may be specified on the last modification call or an a standalone call.


### Returns
- No return value
- Warning messages are logged for attempting to modify or remove a non-existing param.
        
<br/>

<a id="write"></a>

---

# write (savefile) - Write config data to a file

***config_item() class member function***

### Parameter

`savefile`
- Path to the output file.  Path or str type.
- The config data will be written to an absolute path, or relative to the `core.tool.config_dir`


### Returns
- None on success
- Raises ConfigError if unable to write the file


### Behaviors and rules
- The created config file is as loaded in memory.  Any imports in the originally loaded config file
 are merged into the top-level.
        