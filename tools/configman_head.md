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
