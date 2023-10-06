#!/usr/bin/env python3
"""Demo/test for cjnfuncs config classes/functions
"""

#==========================================================
#
#  Chris Nelson, 2023
#
#==========================================================

__version__ = "1.1"
TOOLNAME    = "cjnfuncs_testcfg"
CONFIG_FILE = "demo_config.cfg"

import argparse
import os.path
import shutil
import sys
import time
# from cjnfuncs.cjnfuncs import set_toolname, setuplogging, logging, deploy_files, config_item, getcfg, cfg, timevalue, retime, mungePath, ConfigError
from cjnfuncs.cjnfuncs import set_toolname, setuplogging, logging, deploy_files, config_item, timevalue, retime, mungePath, ConfigError


parser = argparse.ArgumentParser(description=__doc__ + __version__, formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('Mode',
                    help="Test modes (1, 2, ...)")
parser.add_argument('--config-file', '-c', type=str, default=CONFIG_FILE,
                    help=f"Path to the config file (Default <{CONFIG_FILE})> in user config directory.")
parser.add_argument('--cleanup', action='store_true',
                    help="Remove test dirs/files.")
args = parser.parse_args()


tool = set_toolname(TOOLNAME)
print(tool)

if args.cleanup:
    if os.path.exists(tool.config_dir):
        print (f"Removing 1  {tool.config_dir}")
        shutil.rmtree(tool.config_dir)
    sys.exit()


def remove_file (file_path):
    if os.path.exists(file_path):
        os.remove(file_path)



if args.Mode == '1':
    print ("\n***** Tests for log file control *****")
    deploy_files([
        { "source": "demo_config_T1.cfg",   "target_dir": "USER_CONFIG_DIR"},
        ], overwrite=True )
    remove_file(mungePath('call_logfile', tool.config_dir).full_path)
    remove_file(mungePath('cfg_logfile',  tool.config_dir).full_path)
    remove_file(mungePath('cfg_logfile2', tool.config_dir).full_path)

    print ("\n----- T1.1:  setuplogging with call_logfile_wins=False, call_logfile=None, config_logfile=None >>>>  Log file: __console__ (setuplogging with no config)")
    setuplogging()
    print (f"Current log file:              {tool.log_full_path}")
    logging.info("Info level log (not displayed)")
    logging.warning (f"T1.1 - Log to  <{tool.log_full_path}>")

    print ("\n----- T1.2:  LogFile=None, call_logfile=None, call_logfile_wins=True >>>>  Log file: __console__")
    config_T1 = config_item("demo_config_T1.cfg")
    config_T1.loadconfig(ldcfg_ll=10, call_logfile=None, call_logfile_wins=True,    force_flush_reload=True)
        # loadconfig params:   ldcfg_ll=10, call_logfile=None, call_logfile_wins=True, flush_on_reload=True, force_flush_reload=True)
    print (f"Current log file:              {tool.log_full_path}")
    logging.warning (f"T1.2 - Log to  <{tool.log_full_path}>")

    print ("\n----- T1.3:  LogFile='cfg_logfile', call_logfile=None, call_logfile_wins=True >>>>  Log file:  __console__ (override cfg_logfile)")
    config_T1.modify_configfile ("LogFile",   "cfg_logfile", add_if_not_existing=True, save=True)
    config_T1.loadconfig (ldcfg_ll=10, call_logfile=None, call_logfile_wins=True,   force_flush_reload=True)
    print (f"Current log file:              {tool.log_full_path}")
    logging.warning (f"T1.3 - Log to  <{tool.log_full_path}>")

    print ("\n----- T1.4:  LogFile='cfg_logfile', call_logfile='call_logfile', call_logfile_wins=True >>>>  Log file:  call_logfile")
    config_T1.loadconfig (ldcfg_ll=10, call_logfile="call_logfile", call_logfile_wins=True,   force_flush_reload=True)
    print (f"Current log file:              {tool.log_full_path}")
    logging.warning (f"T1.4 - Log to  <{tool.log_full_path}>")

    print ("\n----- T1.5:  LogFile='cfg_logfile', call_logfile='call_logfile', call_logfile_wins=True >>>>  Log file:  'call_logfile' (no change)")
    config_T1.loadconfig (ldcfg_ll=10, call_logfile="call_logfile", call_logfile_wins=True,   force_flush_reload=True)
    print (f"Current log file:              {tool.log_full_path}")
    logging.warning (f"T1.5 - Log to  <{tool.log_full_path}>")

    print ("\n----- T1.6:  LogFile='cfg_logfile', call_logfile='call_logfile', call_logfile_wins=False >>>>  Log file:  'cfg_logfile'")
    config_T1.loadconfig (ldcfg_ll=10, call_logfile="call_logfile", call_logfile_wins=False,   force_flush_reload=True)
    print (f"Current log file:              {tool.log_full_path}")
    logging.warning (f"T1.6 - Log to  <{tool.log_full_path}>")

    print ("\n----- T1.7:  LogFile='cfg_logfile2', call_logfile='call_logfile', call_logfile_wins=False >>>>  Log file:  'cfg_logfile2'")
    config_T1.modify_configfile ("LogFile",   "cfg_logfile2", save=True)
    config_T1.loadconfig (ldcfg_ll=10, call_logfile="call_logfile", call_logfile_wins=False,   force_flush_reload=True)
    print (f"Current log file:              {tool.log_full_path}")
    logging.warning (f"T1.7 - Log to  <{tool.log_full_path}>")

    print ("\n----- T1.8:  LogFile='cfg_logfile', call_logfile='call_logfile', call_logfile_wins=True >>>>  Log file:  'call_logfile' (again)")
    config_T1.loadconfig (ldcfg_ll=10, call_logfile="call_logfile", call_logfile_wins=True,   force_flush_reload=True)
    print (f"Current log file:              {tool.log_full_path}")
    print (tool)
    logging.warning (f"T1.8 - Log to  <{tool.log_full_path}>")

    print ("\n----- T1.9:  Change tool.log_dir_base.  LogFile='cfg_logfile', call_logfile='call_logfile', call_logfile_wins=True >>>>  Log file:  mylogdir/call_logfile")
    tool.log_dir_base = tool.config_dir / "mylogdir"
    config_T1.loadconfig (ldcfg_ll=10, call_logfile="call_logfile", call_logfile_wins=True,   force_flush_reload=True)
    print (f"Current log file:              {tool.log_full_path}")
    print (tool)
    logging.warning (f"T1.9 - Log to  <{tool.log_full_path}>")

    print ("\n----- T1.10:  LogFile='cfg_logfile2', call_logfile='call_logfile', call_logfile_wins=False >>>>  Log file:  mylogdir/cfg_logfile2")
    config_T1.loadconfig (ldcfg_ll=10, call_logfile="call_logfile", call_logfile_wins=False,   force_flush_reload=True)
    print (f"Current log file:              {tool.log_full_path}")
    print (tool)
    logging.warning (f"T1.10 - Log to  <{tool.log_full_path}>")

    print ("\n----- T1.11:  LogFile='cfg_logfile', call_logfile=None, call_logfile_wins=True >>>>  Log file:  __console__")
    config_T1.loadconfig (ldcfg_ll=10, call_logfile=None, call_logfile_wins=True,   force_flush_reload=True)
    print (f"Current log file:              {tool.log_full_path}")
    print (tool)
    logging.warning (f"T1.11 - Log to  <{tool.log_full_path}>")

    print ("\n----- T1.12: LogFile=None, call_logfile=None, call_logfile_wins=False >>>>  Log file:  __console__")
    config_T1.modify_configfile ("LogFile",   remove=True, save=True)
    config_T1.loadconfig (ldcfg_ll=10, call_logfile=None, call_logfile_wins=True,   force_flush_reload=True)
    print (f"Current log file:              {tool.log_full_path}")
    logging.warning (f"T1.12 - Log to  <{tool.log_full_path}>")

    print ("\n----- T1.13: Modified console logging format >>>>  Log file:  __console__")
    config_T1.modify_configfile ("ConsoleLogFormat", "{levelname:>8}:  {message}", add_if_not_existing=True, save=True)
    config_T1.loadconfig (ldcfg_ll=10, call_logfile=None, call_logfile_wins=True,   force_flush_reload=True)
    print (f"Current log file:              {tool.log_full_path}")
    logging.warning (f"T1.13 - Log to  <{tool.log_full_path}>")

    print ("\n----- T1.14: Modified file logging format >>>>  Log file:  call_logfile")
    config_T1.modify_configfile ("FileLogFormat", "{levelname:>8}:  {message}", add_if_not_existing=True, save=True)
    config_T1.loadconfig (ldcfg_ll=10, call_logfile="call_logfile", call_logfile_wins=True,   force_flush_reload=True)
    print (f"Current log file:              {tool.log_full_path}")
    logging.warning (f"T1.14 - Log to  <{tool.log_full_path}>")

    sys.exit()


if args.Mode == '2':
    print ("\n***** Tests for ldcfg_ll, config LogLevel, flush_on_reload, force_flush_reload *****")

    def print_stats ():
        print (f"(Re)loaded             :  {reloaded}")
        print (f"Config file timestamp  :  {config_T2.config_timestamp}")
        print (f"Config LogLevel        :  {config_T2.getcfg('LogLevel', 'None')}")
        print (f"Current Logging level  :  {logging.getLogger().level}")
        print (f"testvar                :  {config_T2.getcfg('testvar', None)}  {type(config_T2.getcfg('testvar', None))}")
        print (f"var2                   :  {config_T2.getcfg('var2', None)}")
        print (f"Current log file       :  {tool.log_full_path}")
        logging.warning ("Warning level message")
        logging.info    ("Info    level message")
        logging.debug   ("Debug   level message")

    deploy_files([
        { "source": "demo_config_T2.cfg",   "target_dir": "USER_CONFIG_DIR"},
        ], overwrite=True )
    config_T2 = config_item("demo_config_T2.cfg")
    

    print ("\n----- T2.1:  Initial load.  Default logging level 30")
    reloaded = config_T2.loadconfig()
    print_stats()

    print ("\n----- T2.2:  No config change >>>>  Not reloaded")
    reloaded = config_T2.loadconfig(flush_on_reload=True) 
    print_stats()

    print ("\n----- T2.3:  LogLevel=10, ldcfg_ll=10 >>>>  loadconfig logging, Logging DEBUG, INFO, and WARNING messages")
    time.sleep(1)  # 1 sec timestamp change sensitivity in loadconfig
    config_T2.modify_configfile ("LogLevel",   "10", add_if_not_existing=True, save=True)
    reloaded = config_T2.loadconfig(ldcfg_ll=10, flush_on_reload=True)
    print_stats()

    print ("\n----- T2.4:  LogLevel=10, ldcfg_ll=30 (default) >>>>  No loadconfig logging, Logging DEBUG, INFO, and WARNING messages")
    time.sleep(1)
    config_T2.modify_configfile ( "LogLevel",   "10", save=True)
    reloaded = config_T2.loadconfig(flush_on_reload=True)
    print_stats()

    print ("\n----- T2.5:  LogLevel=30, ldcfg_ll=30 (default),  >>>>  Log only WARNING")
    time.sleep(1)
    config_T2.modify_configfile ("LogLevel",   "30", save=True)
    reloaded = config_T2.loadconfig(flush_on_reload=True)
    print_stats()

    print ("\n----- T2.6:  ldcfg_ll=10, No LogLevel >>>>  Restore preexisting level (30)")
    time.sleep(1)
    config_T2.modify_configfile ("LogLevel",  remove=True)
    config_T2.modify_configfile ("testvar",   "True", save=True)
    reloaded = config_T2.loadconfig(ldcfg_ll=10, flush_on_reload=True)
    print_stats()

    print ("\n----- T2.7:  ldcfg_ll=30 (default), No changes >>>>  NOT Reloaded")
    reloaded = config_T2.loadconfig(flush_on_reload=True)
    print_stats()

    print ("\n----- T2.8:  ldcfg_ll=10, flush_on_reload >>>>  NOT Reloaded")
    reloaded = config_T2.loadconfig(ldcfg_ll=10, flush_on_reload=True)
    print_stats()

    print ("\n----- T2.9:  ldcfg_ll=10, force_flush_reload >>>>  Loadconfig logging")
    reloaded = config_T2.loadconfig(ldcfg_ll=10, force_flush_reload=True)
    print_stats()

    print ("\n----- T2.10:  ldcfg_ll=10, LogLevel=20, var2 added >>>>  Reloaded")
    time.sleep(1)
    config_T2.modify_configfile ("LogLevel",   "20", add_if_not_existing=True)
    config_T2.modify_configfile ("var2",   "Hello", add_if_not_existing=True, save=True)
    reloaded = config_T2.loadconfig(ldcfg_ll=10, force_flush_reload=True)
    print_stats()

    print ("\n----- T2.11: ldcfg_ll=10, LogLevel=40, var2 removed from config >>>>  var2 still defined, no logging")
    time.sleep(1)
    config_T2.modify_configfile ("LogLevel",   "40")
    config_T2.modify_configfile ("var2",   remove=True, save=True)
    reloaded = config_T2.loadconfig(ldcfg_ll=10)
    print_stats()

    print ("\n----- T2.12: ldcfg_ll=10, LogLevel=30, force_flush_reload=True >>>>  var2 gone")
    config_T2.modify_configfile ("LogLevel",   "30", save=True)
    reloaded = config_T2.loadconfig(ldcfg_ll=10, force_flush_reload=True)
    print_stats()

    print ("\n----- T2.13: Externally set log level = 20")
    time.sleep(1)
    config_T2.modify_configfile ("LogLevel",   remove=True, save=True)
    logging.getLogger().setLevel(20)
    reloaded = config_T2.loadconfig(ldcfg_ll=10, force_flush_reload=True)
    print_stats()

    print ("\n----- T2.14: Externally set log level = 10")
    logging.getLogger().setLevel(10)
    reloaded = config_T2.loadconfig(ldcfg_ll=10, force_flush_reload=True)
    print_stats()

    print ("\n----- T2.15: Externally set log level = 10 with ldcfg_ll=30 (default)")
    logging.getLogger().setLevel(10)
    reloaded = config_T2.loadconfig(force_flush_reload=True)
    print_stats()

    sys.exit()


# Initial load for following tests
deploy_files([
    { "source": CONFIG_FILE,            "target_dir": "USER_CONFIG_DIR"},
    { "source": "additional.cfg",       "target_dir": "USER_CONFIG_DIR"},
    { "source": "creds_SMTP",           "target_dir": "USER_CONFIG_DIR"},
    ], overwrite=True )

try:
    config = config_item(CONFIG_FILE)
    print (f"\nLoad config {config.config_full_path}")
    config.loadconfig(ldcfg_ll=10)
except Exception as e:
    print (f"No user or site setup found.  Run with <--setup-user> to set up the environment.\n  {e}")
    sys.exit()


if args.Mode == '3':
    print ("\n***** Show tool.log_* values (LogFile NOT in config) *****")
    print(tool)
    print(config)
    print(config.dump())
    print(config.sections_list)
    print(config.sections())


if args.Mode == '4':
    print ("\n***** Test trapped config loading exception *****")
    try:
        configX = config_item("nosuchfile.cfg")
        configX.loadconfig(ldcfg_ll=10)
    except ConfigError as e:
        print (f"In main...  {e}")


if args.Mode == '5':
    print ("\n***** Test untrapped config loading exception *****")
    configX = config_item("nosuchfile.cfg")
    configX.loadconfig(ldcfg_ll=10)


if args.Mode == '6':
    print ("\n***** Co-loading an additional config *****")
    print(config)
    additional_config = config_item("additional.cfg")
    print(additional_config)
    logging.warning (f"testvar:          {config.getcfg('testvar', None)}  {type(config.getcfg('testvar', None))}")
    logging.warning (f"another:          {additional_config.getcfg('another', None)}  {type(additional_config.getcfg('another', None))}")

    additional_config.loadconfig(ldcfg_ll=10)
    print(additional_config)

    logging.warning (f"testvar:          {config.getcfg('testvar', None)}  {type(config.getcfg('testvar', None))}")
    logging.warning (f"another:          {additional_config.getcfg('another', None)}  {type(additional_config.getcfg('another', None))}")
    print (f"Current logging level:      {logging.getLogger().level}")


if args.Mode == '7':
    print ("\n***** Test unknown getcfg param with/without fallbacks *****")
    print (f"Testing getcfg - Not in cfg with fallback: <{config.getcfg('NotInCfg', 'My fallback Value')}>")
    try:
        config.getcfg('NotInCfg-NoDef')
    except ConfigError as e:
        print (f"ConfigError: {e}")


if args.Mode == '8':
    print ("\n***** Test untrapped unknown getcfg param *****")
    config.getcfg('NotInCfg-NoDef')


if args.Mode == '9':
    print ("\n***** Test flush_on_reload  and  force_flush_reload cases *****")
    config.cfg["dummy"] = True
    print (f"\n----- T9.1:  var dummy in cfg:  {config.getcfg('dummy', False)}  (should be True - Initial state)\n")

    config.loadconfig(flush_on_reload=True, ldcfg_ll=10)
    print (f"----- T9.2:  var dummy in cfg:  {config.getcfg('dummy', False)}  (should be True because not reloaded)\n")


    time.sleep(1)  # 1 sec timestamp change sensitivity in loadconfig
    config.config_full_path.touch()
    config.loadconfig(ldcfg_ll=10)
    print (f"----- T9.3:  var dummy in cfg:  {config.getcfg('dummy', False)}  (should be True because flush_on_reload == False)\n")

    time.sleep(1)
    config.config_full_path.touch()
    config.loadconfig(flush_on_reload=True, ldcfg_ll=10)
    print (f"----- T9.4:  var dummy in cfg:  {config.getcfg('dummy', False)}  (should be False because flush_on_reload == True)\n")

    config.cfg["dummy"] = True
    config.loadconfig(force_flush_reload=True, ldcfg_ll=10)
    print (f"----- T9.5:  var dummy in cfg:  {config.getcfg('dummy', False)}  (should be False because force_flush_reload == True)\n")


def dump(xx):
    print (f"\nGiven <{xx}>     {type(xx)}:")
    yy = timevalue(xx)
    print (yy)
    print (f"   retimed  :  <{retime(yy.seconds, yy.unit_char)}> {yy.unit_str}")

if args.Mode == '10':
    print ("\n***** Test timevalue, retime *****")
    dump (config.getcfg("Tint"))
    dump (config.getcfg("Tsec"))
    dump (config.getcfg("Tmin"))
    dump (config.getcfg("Thour"))
    dump (config.getcfg("Tday"))
    dump (config.getcfg("Tweek"))
    dump (2/7)
    dump ("5.123m")
    sleeptime = timevalue("1.9s")
    print (f"Sleeping {sleeptime.seconds} {sleeptime.unit_str}")
    time.sleep (sleeptime.seconds)
    print ("done sleeping")


if args.Mode == '11':
    print ("\n***** Test untrapped invalid time unit *****")
    dump ("3y")             # ValueError raised


if args.Mode == '12':
    print ("\n***** Test untrapped retime with invalid unitC *****")
    retime (12345, "y")     # ValueError raised


if args.Mode == '13':
    print ("\n***** Test missing config and externally set logging level *****")

    print (f"\n----- T13.1:  Missing config, tolerate_missing=False (default) >>>>  Exception")
    remove_file(config.config_full_path)
    logging.getLogger().setLevel(7)
    try:
        config.loadconfig(ldcfg_ll=10)
    except Exception as e:
        print (f"Config loading exception:\n  {e}")
        print (f"Logging level back in the main code:  {logging.getLogger().level}")

    print (f"\n----- T13.2:  Missing config, tolerate_missing=True >>>>  Returned -1")
    print (f"Returned:  <{config.loadconfig(ldcfg_ll=10, tolerate_missing=True)}>")
    print (f"Logging level back in the main code:  {logging.getLogger().level}")

    print (f"\n----- T13.3:  Working nested import")
    deploy_files([
        { "source": "import_nest_top.cfg",  "target_dir": "USER_CONFIG_DIR"},
        { "source": "import_nest_1.cfg",    "target_dir": "USER_CONFIG_DIR"},
        { "source": "import_nest_2.cfg",    "target_dir": "USER_CONFIG_DIR"},
        ], overwrite=True )
    nest_cfg = mungePath("import_nest_top.cfg", tool.config_dir).full_path
    xx = config_item(nest_cfg)
    xx.loadconfig(ldcfg_ll=10, tolerate_missing=True, force_flush_reload=True)
    print (xx.dump())
    print (f"Logging level back in the main code:  {logging.getLogger().level}")
    
    print (f"\n----- T13.4:  Missing nested imported config <import_nest_2.cfg> with tolerate_missing=True >>>>  Exception raised.")
    remove_file(mungePath("import_nest_2.cfg", tool.config_dir).full_path)
    try:
        xx.loadconfig(ldcfg_ll=9, tolerate_missing=True, force_flush_reload=True)
    except Exception as e:
        print (f"Exception due to missing imported config file:\n  {e}")
        # NOTE:  Failed importing/processing config file  </home/cjn/.config/cjnfuncs_testcfg/import_nest_1.cfg>
        # rather than saying can't import/process nest_2
        print (f"Logging level back in the main code:  {logging.getLogger().level}")
    
    print (f"\n----- T13.5:  Missing imported config <import_nest_1.cfg> with tolerate_missing=True >>>>  Exception raised.")
    remove_file(mungePath("import_nest_1.cfg", tool.config_dir).full_path)
    try:
        xx.loadconfig(ldcfg_ll=10, tolerate_missing=True, force_flush_reload=True)
    except Exception as e:
        print (f"Exception due to missing imported config file:\n  {e}")
        print (f"Logging level back in the main code:  {logging.getLogger().level}")


if args.Mode == '14':
    print ("\n***** Test modify_configfile *****")
    config.modify_configfile(r"x_7893&(%$,.nasf||\a@",  "Goodbye!    # It was Hello")   # param match check
    config.modify_configfile("x_removeX", remove=True)                                  # Warning message
    config.modify_configfile("x_removed", remove=True)                                  # Removed

    config.modify_configfile("x_shorter",               "12345")                        # Whitespace between value and comment tests
    config.modify_configfile("x_longer",                "123456789 123456789")
    config.modify_configfile("x_same",                  "54321 987654321")
    config.modify_configfile("x_really_long",           "123456789 123456789 123456789 12345")
    config.modify_configfile("x_no_trailing_whitespace","123456789 123456789")
    config.modify_configfile("x_indented_param",        "False")
    
    config.modify_configfile("x_float",                 6.5)                            # Check various value types
    config.modify_configfile("x_int",                   12)
    config.modify_configfile("x_list",                  ["hello", 3.14, {"abc":42}])
    config.modify_configfile("x_dict",                  {"one":6, "two":7.0})

    config.modify_configfile("", "",                    add_if_not_existing=True)       # Blank line
    config.modify_configfile("George", "was here",      add_if_not_existing=True)       # New param
    config.modify_configfile("Snehal", "wasn't here")                                   # Warning message
    config.modify_configfile(                           add_if_not_existing=True)       # Another blank line
    config.modify_configfile("# New comment line",  "", add_if_not_existing=True)       # New comment
    config.modify_configfile("# New comment line",  "", add_if_not_existing=True)       # Non-unique, and both get added
    config.modify_configfile("Bjorn",  "was here too   # With a comment and No newline at end of file", add_if_not_existing=True) #, save=True) # New line
    config.modify_configfile(save=True)
    config.loadconfig(ldcfg_ll=10, force_flush_reload=True)
    print (f"Compare <{config.config_full_path}> to golden copy.")


if args.Mode == '15':
    print ("\n***** Access list, tuple, and dictionary params *****")
    # a_list:         ["hello", 3.14, {"abc":42.}]
    # a_tuple=        ("Im a tuple", 7.0)
    # a_dict:         {"six":6, 3:3.0}
    six      = config.getcfg("a_dict")["six"]
    seven    = config.getcfg("a_tuple")[1]
    fortytwo = config.getcfg("a_list")[2]["abc"]
    print (f"{six} times {seven} is {fortytwo}")


if args.Mode == '16':
    print ("\n***** Test getcfg type checking *****")

    def dump(param, types):
        try:
            _value = config.getcfg(param, types=types)
            print (f"Param <{param}> value <{_value}>, type <{type(_value)}>, expected types <{types}>")
        except Exception as e:
            print (f"Param <{param}> not expected type:\n  {e}")

    dump("Tint",   types=[int, float])
    dump("Tint",   types=int)
    dump("a_list", types=[list])
    dump("Tsec",   types=[int, str])
    dump("Tint",   types=[     float, list, tuple, dict, bool, str])
    dump("a_list", types=[int, float,       tuple, dict, bool, str])
    dump("a_dict", types=[int, float, list, tuple,       bool, str])
    dump("Tsec",   types=[int, float, list, tuple, dict, bool     ])


if args.Mode == '17':
    print ("\n***** Assign getcfg and cfg to config instance *****")
    getcfg = config.getcfg
    cfg = config.cfg
    six      = getcfg("a_dict")["six"]
    seven    = cfg['a_tuple'][1]  # getcfg("a_tuple")[1]
    fortytwo = getcfg("a_list")[2]["abc"]
    print (f"{six} times {seven} is {fortytwo}")


if args.Mode == '18':
    print ("\n***** Sections and DEFAULT *****")
    def dump(option, section='', desc=''):
        try:
            xx = '[' + section + '][' + option + ']'
            _value = config.getcfg(option, section=section)
            print (f"{xx:17}   {_value:<11}  {desc}")
        except:
            print (f"{xx:17}   NOT DEFINED  {desc}")

    print (config)
    dump('a',                         desc='Expecting  <9>  from [],             [DEFAULT] ignored')
    dump('b',                         desc='Expecting  <12> from [],             no default')
    dump('c',                         desc='Expecting  <42> from [DEFAULT],      not in []')
    dump('d',                         desc='Not in [] or [DEFAULT]')

    dump('a', section='Test section', desc='Expecting  <5>  from [Test section], [DEFAULT] ignored')
    dump('b', section='Test section', desc='Expecting  <25> from [Test section], no default')
    dump('c', section='Test section', desc='Expecting  <42> from [DEFAULT],      not in [Test section]')
    dump('e', section='Test section', desc='Not in [Test section] or [DEFAULT] and [] not considered')


if args.Mode == '19':
    print ("\n***** Imports within Sections and DEFAULT *****")
    deploy_files([
        { "source": "import_nest_top.cfg",  "target_dir": "USER_CONFIG_DIR"},
        { "source": "import_nest_1.cfg",    "target_dir": "USER_CONFIG_DIR"},
        { "source": "import_nest_2.cfg",    "target_dir": "USER_CONFIG_DIR"},
        ], overwrite=True )
    nest_cfg = mungePath("import_nest_top.cfg", tool.config_dir).full_path
    xx = config_item(nest_cfg)
    xx.loadconfig(ldcfg_ll=10, tolerate_missing=True, force_flush_reload=True)
    print ("\n***** config contents *****")
    print (xx.dump())


# TODO test for section within import