#!/usr/bin/env python3
"""Demo/test for cjnfuncs config classes/functions

Produce / compare to golden results:
    ./demo-config.py -t 0 | diff demo-config-golden.txt -
        Config file timestamps will be different
        Line numbers in test T23.1a can vary

    ./demo-config.py --cleanup
"""

#==========================================================
#
#  Chris Nelson, 2024-2025
#
#==========================================================

__version__ = "3.1"
TOOLNAME    = "cjnfuncs_testcfg"
CONFIG_FILE = "demo_config.cfg"

import argparse
import os.path
import shutil
import sys
import re
import time

from cjnfuncs.core     import set_toolname, setuplogging, logging, ConfigError, set_logging_level
from cjnfuncs.deployfiles import deploy_files
from cjnfuncs.configman import config_item
from cjnfuncs.timevalue import timevalue, retime
from cjnfuncs.mungePath import mungePath
import cjnfuncs.core as core

parser = argparse.ArgumentParser(description=__doc__ + __version__, formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-t', '--test', default='3a',
                    help="Test number to run (default 3a).  0 runs most all tests (those without untrapped errors)")
parser.add_argument('--cleanup', action='store_true',
                    help="Remove test dirs/files.")
args = parser.parse_args()

set_toolname(TOOLNAME)


if args.cleanup:
    if os.path.exists(core.tool.config_dir):
        print (f"Removing 1  {core.tool.config_dir}")
        shutil.rmtree(core.tool.config_dir)
    sys.exit()


# --------------------------------------------------------------------

def remove_file (file_path):
    if os.path.exists(file_path):
        os.remove(file_path)


def dump_file(filepath):
    _file = mungePath(filepath, core.tool.config_dir)
    print (f"\n***** File <{_file.full_path}> content:")
    print (_file.full_path.read_text())


tnum_parse = re.compile(r"([\d]+)([\w]*)")
def check_tnum(tnum_in, include0='0'):
    global tnum
    tnum = tnum_in
    if args.test == include0  or  args.test == tnum_in:  return True
    try:
        if int(args.test) == int(tnum_parse.match(tnum_in).group(1)):  return True
    except:  pass
    return False


def print_test_header(header):
    global tnum
    print ("\n======================================================================================================")
    print (f"***** Test number {tnum}: {header} *****")
    print ("======================================================================================================\n")


def do_base_setup(safe_mode=False):
    global config
    set_toolname(TOOLNAME)
    deploy_files([                      # Reset for every test to ensure same results for -t 0 and -t n
        { "source": CONFIG_FILE,            "target_dir": "USER_CONFIG_DIR"},
        { "source": "creds_SMTP",           "target_dir": "USER_CONFIG_DIR"},
        ], overwrite=True )
    config = config_item(CONFIG_FILE, safe_mode=safe_mode)
    print (f"\nLoad config {config.config_full_path}")
    # logging.getLogger('cjnfuncs.configman').setLevel(config_load_ll)
    config.loadconfig()


#===============================================================================================

if __name__ == '__main__':

    if check_tnum('1'):
        print_test_header ("Tests for log file control")
        set_logging_level (logging.DEBUG, 'cjnfuncs.configman')
        deploy_files([
            { "source": "demo_config_T1.cfg",   "target_dir": "USER_CONFIG_DIR"},
            ], overwrite=True )
        remove_file(mungePath('call_logfile', core.tool.config_dir).full_path)
        remove_file(mungePath('cfg_logfile',  core.tool.config_dir).full_path)
        remove_file(mungePath('cfg_logfile2', core.tool.config_dir).full_path)

        print ("\n----- T1.1:  setuplogging with call_logfile_wins=False, call_logfile=None, config_logfile=None >>>>  Log file: __console__ (setuplogging with no config)")
        setuplogging()      # Does not change logging level, left at preexisting logging level (30)
        print (f"Current log file:              {core.tool.log_full_path}")
        logging.info("Info level log (not displayed)")
        logging.warning (f"T1.1 - Log to  <{core.tool.log_full_path}>")

        print ("\n----- T1.2:  LogFile=None, call_logfile=None, call_logfile_wins=True >>>>  Log file: __console__")
        config_T1 = config_item("demo_config_T1.cfg")
        config_T1.loadconfig(call_logfile=None, call_logfile_wins=True,    force_flush_reload=True)
        print (f"Current log file:              {core.tool.log_full_path}")
        logging.warning (f"T1.2 - Log to  <{core.tool.log_full_path}>")

        print ("\n----- T1.3:  LogFile='cfg_logfile', call_logfile=None, call_logfile_wins=True >>>>  Log file:  __console__ (override cfg_logfile)")
        config_T1.modify_configfile ("LogFile",   "cfg_logfile", add_if_not_existing=True, save=True)
        config_T1.loadconfig (call_logfile=None, call_logfile_wins=True,   force_flush_reload=True)
        print (f"Current log file:              {core.tool.log_full_path}")
        logging.warning (f"T1.3 - Log to  <{core.tool.log_full_path}>")

        print ("\n----- T1.4:  LogFile='cfg_logfile', call_logfile='call_logfile', call_logfile_wins=True >>>>  Log file:  call_logfile")
        config_T1.loadconfig (call_logfile="call_logfile", call_logfile_wins=True,   force_flush_reload=True)
        print (f"Current log file:              {core.tool.log_full_path}")
        logging.warning (f"T1.4 - Log to  <{core.tool.log_full_path}>")

        print ("\n----- T1.5:  LogFile='cfg_logfile', call_logfile='call_logfile', call_logfile_wins=True >>>>  Log file:  'call_logfile' (no change)")
        config_T1.loadconfig (call_logfile="call_logfile", call_logfile_wins=True,   force_flush_reload=True)
        print (f"Current log file:              {core.tool.log_full_path}")
        logging.warning (f"T1.5 - Log to  <{core.tool.log_full_path}>")

        print ("\n----- T1.6:  LogFile='cfg_logfile', call_logfile='call_logfile', call_logfile_wins=False >>>>  Log file:  'cfg_logfile'")
        config_T1.loadconfig (call_logfile="call_logfile", call_logfile_wins=False,   force_flush_reload=True)
        print (f"Current log file:              {core.tool.log_full_path}")
        logging.warning (f"T1.6 - Log to  <{core.tool.log_full_path}>")

        print ("\n----- T1.7:  LogFile='cfg_logfile2', call_logfile='call_logfile', call_logfile_wins=False >>>>  Log file:  'cfg_logfile2'")
        config_T1.modify_configfile ("LogFile",   "cfg_logfile2", save=True)
        config_T1.loadconfig (call_logfile="call_logfile", call_logfile_wins=False,   force_flush_reload=True)
        print (f"Current log file:              {core.tool.log_full_path}")
        logging.warning (f"T1.7 - Log to  <{core.tool.log_full_path}>")

        print ("\n----- T1.8:  LogFile='cfg_logfile', call_logfile='call_logfile', call_logfile_wins=True >>>>  Log file:  'call_logfile' (again)")
        config_T1.loadconfig (call_logfile="call_logfile", call_logfile_wins=True,   force_flush_reload=True)
        print (f"Current log file:              {core.tool.log_full_path}")
        print (core.tool)
        logging.warning (f"T1.8 - Log to  <{core.tool.log_full_path}>")

        print ("\n----- T1.9:  Change core.tool.log_dir_base.  LogFile='cfg_logfile', call_logfile='call_logfile', call_logfile_wins=True >>>>  Log file:  mylogdir/call_logfile")
        core.tool.log_dir_base = core.tool.config_dir / "mylogdir"
        config_T1.loadconfig (call_logfile="call_logfile", call_logfile_wins=True,   force_flush_reload=True)
        print (f"Current log file:              {core.tool.log_full_path}")
        print (core.tool)
        logging.warning (f"T1.9 - Log to  <{core.tool.log_full_path}>")

        print ("\n----- T1.10:  LogFile='cfg_logfile2', call_logfile='call_logfile', call_logfile_wins=False >>>>  Log file:  mylogdir/cfg_logfile2")
        config_T1.loadconfig (call_logfile="call_logfile", call_logfile_wins=False,   force_flush_reload=True)
        print (f"Current log file:              {core.tool.log_full_path}")
        print (core.tool)
        logging.warning (f"T1.10 - Log to  <{core.tool.log_full_path}>")

        print ("\n----- T1.11:  LogFile='cfg_logfile', call_logfile=None, call_logfile_wins=True >>>>  Log file:  __console__")
        config_T1.loadconfig (call_logfile=None, call_logfile_wins=True,   force_flush_reload=True)
        print (f"Current log file:              {core.tool.log_full_path}")
        print (core.tool)
        logging.warning (f"T1.11 - Log to  <{core.tool.log_full_path}>")

        print ("\n----- T1.12: LogFile=None, call_logfile=None, call_logfile_wins=False >>>>  Log file:  __console__")
        config_T1.modify_configfile ("LogFile",   remove=True, save=True)
        config_T1.loadconfig (call_logfile=None, call_logfile_wins=True,   force_flush_reload=True)
        print (f"Current log file:              {core.tool.log_full_path}")
        logging.warning (f"T1.12 - Log to  <{core.tool.log_full_path}>")

        print ("\n----- T1.13: Modified console logging format >>>>  Log file:  __console__")
        config_T1.modify_configfile ("ConsoleLogFormat", "{levelname:>8}:  {message}", add_if_not_existing=True, save=True)
        config_T1.loadconfig (call_logfile=None, call_logfile_wins=True,   force_flush_reload=True)
        print (f"Current log file:              {core.tool.log_full_path}")
        logging.warning (f"T1.13 - Log to  <{core.tool.log_full_path}>")

        print ("\n----- T1.14: Modified file logging format >>>>  Log file:  call_logfile")
        config_T1.modify_configfile ("FileLogFormat", "{levelname:>8}:  {message}", add_if_not_existing=True, save=True)
        config_T1.loadconfig (call_logfile="call_logfile", call_logfile_wins=True,   force_flush_reload=True)
        print (f"Current log file:              {core.tool.log_full_path}")
        logging.warning (f"T1.14 - Log to  <{core.tool.log_full_path}>")


    #===============================================================================================
    if check_tnum('2'):
        print_test_header ("Tests for loadconfig logging level, config LogLevel, flush_on_reload, force_flush_reload")
        set_logging_level (logging.DEBUG, 'cjnfuncs.configman')

        def print_stats ():
            print (f"(Re)loaded                 {reloaded}")
            print (f"Config file timestamp      {config_T2.config_timestamp}")
            print (f"Config LogLevel            {config_T2.getcfg('LogLevel', 'None')}")
            print (f"root logging level         {logging.getLogger().level}")
            print (f"configman logging level    {logging.getLogger('cjnfuncs.configman').level}")
            print (f"testvar                    {config_T2.getcfg('testvar', None)}  {type(config_T2.getcfg('testvar', None))}")
            print (f"var2                       {config_T2.getcfg('var2', None)}")
            print (f"Current log file           {core.tool.log_full_path}")
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

        print ("\n----- T2.3:  LogLevel=10, loadconfig debug logging")
        time.sleep(1)  # 1 sec timestamp change sensitivity in loadconfig
        config_T2.modify_configfile ("LogLevel",   "10", add_if_not_existing=True, save=True)
        reloaded = config_T2.loadconfig(flush_on_reload=True)
        print_stats()

        print ("\n----- T2.4:  LogLevel=10, loadconfig logging=30 (default) >>>>  No loadconfig logging, Logging DEBUG, INFO, and WARNING messages")
        time.sleep(1)
        config_T2.modify_configfile ( "LogLevel",   "10", save=True)
        set_logging_level (logging.WARNING, 'cjnfuncs.configman')
        reloaded = config_T2.loadconfig(flush_on_reload=True)
        print_stats()

        print ("\n----- T2.5:  LogLevel=30, loadconfig logging=30 (default),  >>>>  Log only WARNING")
        time.sleep(1)
        config_T2.modify_configfile ("LogLevel",   "30", save=True)
        reloaded = config_T2.loadconfig(flush_on_reload=True)
        print_stats()

        print ("\n----- T2.6:  loadconfig debug logging, No LogLevel >>>>  Restore preexisting level (30)")
        time.sleep(1)
        set_logging_level (logging.DEBUG, 'cjnfuncs.configman')
        config_T2.modify_configfile ("LogLevel",  remove=True)
        config_T2.modify_configfile ("testvar",   "True", save=True)
        reloaded = config_T2.loadconfig(flush_on_reload=True)
        print_stats()

        print ("\n----- T2.7:  loadconfig logging=30 (default), No changes >>>>  NOT Reloaded")
        set_logging_level (logging.WARNING, 'cjnfuncs.configman')
        reloaded = config_T2.loadconfig(flush_on_reload=True)
        print_stats()

        print ("\n----- T2.8:  loadconfig debug logging, flush_on_reload >>>>  NOT Reloaded")
        set_logging_level (logging.DEBUG, 'cjnfuncs.configman')
        reloaded = config_T2.loadconfig(flush_on_reload=True)
        print_stats()

        print ("\n----- T2.9:  loadconfig debug logging, force_flush_reload >>>>  Loadconfig logging")
        reloaded = config_T2.loadconfig(force_flush_reload=True)
        print_stats()

        print ("\n----- T2.10:  loadconfig debug logging, LogLevel=20, var2 added >>>>  Reloaded")
        time.sleep(1)
        config_T2.modify_configfile ("LogLevel",   "20", add_if_not_existing=True)
        config_T2.modify_configfile ("var2",   "Hello", add_if_not_existing=True, save=True)
        reloaded = config_T2.loadconfig(force_flush_reload=True)
        print_stats()

        print ("\n----- T2.11: loadconfig debug logging, LogLevel=40, var2 removed from config >>>>  var2 still defined, no logging")
        time.sleep(1)
        config_T2.modify_configfile ("LogLevel",   "40")
        config_T2.modify_configfile ("var2",   remove=True, save=True)
        reloaded = config_T2.loadconfig()
        print_stats()

        print ("\n----- T2.12: loadconfig debug logging, LogLevel=30, force_flush_reload=True >>>>  var2 gone")
        config_T2.modify_configfile ("LogLevel",   "30", save=True)
        reloaded = config_T2.loadconfig(force_flush_reload=True)
        print_stats()

        print ("\n----- T2.13: Externally set log level = 20")
        time.sleep(1)
        config_T2.modify_configfile ("LogLevel",   remove=True, save=True)
        set_logging_level(20)
        reloaded = config_T2.loadconfig(force_flush_reload=True)
        print_stats()

        print ("\n----- T2.14: Externally set log level = 10")
        set_logging_level(10)
        reloaded = config_T2.loadconfig(force_flush_reload=True)
        print_stats()

        print ("\n----- T2.15: Externally set log level = 10 with loadconfig logging=30 (default)")
        set_logging_level(10)
        set_logging_level (logging.WARNING, 'cjnfuncs.configman')
        reloaded = config_T2.loadconfig(force_flush_reload=True)
        print_stats()


    #===============================================================================================
    if check_tnum('3a'):
        print_test_header("Basic test (Show core.tool.log_* values, LogFile NOT in config)")
        set_logging_level (logging.DEBUG, 'cjnfuncs.configman')
        do_base_setup()
        print(core.tool)
        print(config)
        print(config.dump())
        print(config.sections_list)
        print(config.sections())
        print (f"Logging level:  {logging.getLogger().level}")


    #===============================================================================================
    if check_tnum('3b'):
        print_test_header("Basic test - INFO logging")
        set_logging_level (logging.INFO, 'cjnfuncs.configman')
        do_base_setup()


    #===============================================================================================
    if check_tnum('3c'):
        print_test_header("Basic test - WARNING logging")
        set_logging_level (logging.WARNING, 'cjnfuncs.configman')
        do_base_setup()


    #===============================================================================================
    if check_tnum('3d'):
        print_test_header("Basic test - DEBUG logging, safe_mode=False")
        set_logging_level (logging.DEBUG, 'cjnfuncs.configman')
        do_base_setup(safe_mode=True)
        print(config)


    #===============================================================================================
    if check_tnum('4'):
        print_test_header ("Test trapped config loading exception")
        set_logging_level (logging.WARNING, 'cjnfuncs.configman')
        try:
            configX = config_item("nosuchfile.cfg")
            configX.loadconfig()
        except ConfigError as e:
            print (f"In main...  {type(e).__name__}: {e}")


    #===============================================================================================
    if check_tnum('5', include0=False):
        print_test_header ("Test untrapped config loading exception")
        set_logging_level (logging.DEBUG, 'cjnfuncs.configman')
        configX = config_item("nosuchfile.cfg")
        configX.loadconfig()


    #===============================================================================================
    if check_tnum('6'):
        print_test_header ("Co-loading an additional config")
        set_logging_level (logging.INFO, 'cjnfuncs.configman')
        do_base_setup()
        deploy_files([
            { "source": "additional.cfg",       "target_dir": "USER_CONFIG_DIR"},
            ], overwrite=True )

        print(config)
        set_logging_level (logging.DEBUG, 'cjnfuncs.configman')
        additional_config = config_item("additional.cfg", secondary_config=True)
        print(additional_config)
        logging.warning (f"testvar:          {config.getcfg('testvar', None)}  {type(config.getcfg('testvar', None))}")
        logging.warning (f"another:          {additional_config.getcfg('another', None)}  {type(additional_config.getcfg('another', None))}")
        set_logging_level(17)
        print (f"Logging level:  {logging.getLogger().level}")

        set_logging_level(logging.DEBUG, 'cjnfuncs.configman')
        additional_config.loadconfig()
        print(additional_config)

        logging.warning (f"testvar:          {config.getcfg('testvar', None)}  {type(config.getcfg('testvar', None))}")
        logging.warning (f"another:          {additional_config.getcfg('another', None)}  {type(additional_config.getcfg('another', None))}")
        print (f"Logging level:  {logging.getLogger().level}")
        print (core.tool)


    #===============================================================================================
    if check_tnum('7'):
        print_test_header ("Test unknown getcfg param with/without defaults and fallbacks")
        set_logging_level (logging.WARNING, 'cjnfuncs.configman')
        do_base_setup()

        print (f"Testing getcfg - Not in cfg with default:  <{config.getcfg('my_def_param')}>")

        print (f"Testing getcfg - Not in cfg with fallback: <{config.getcfg('NotInCfg', 'My fallback Value')}>")

        print (f"Testing getcfg - Section not in cfg with default:  <{config.getcfg('my_def_param', section='nosuchsection')}>")

        print (f"Testing getcfg - Section not in cfg with fallback: <{config.getcfg('NotInCfg', 'My fallback Value', section='nosuchsection')}>")


        try:
            config.getcfg('NotInCfg-NoFB')
        except ConfigError as e:
            print (f"{type(e).__name__}: {e}")

        try:
            config.getcfg('NotInCfg-NoFB', section='nosuchsection')
        except ConfigError as e:
            print (f"{type(e).__name__}: {e}")


    #===============================================================================================
    if check_tnum('8', include0=False):
        print_test_header ("Test untrapped unknown getcfg param")
        set_logging_level (logging.DEBUG, 'cjnfuncs.configman')
        do_base_setup()
        config.getcfg('NotInCfg-NoFB')


    #===============================================================================================
    if check_tnum('9'):
        print_test_header ("Test flush_on_reload  and  force_flush_reload cases, with callbacks")

        def mycallback():
            logging.info("In mycallback()")

        set_logging_level (logging.WARNING, 'cjnfuncs.configman')
        do_base_setup()
        config.cfg["dummy"] = True
        print (f"\n----- T9.1:  var dummy in cfg:  {config.getcfg('dummy', False)}  (should be True - Initial state)\n")

        config.loadconfig(flush_on_reload=True, prereload_callback=mycallback)
        print (f"----- T9.2:  var dummy in cfg:  {config.getcfg('dummy', False)}  (should be True because not reloaded)\n")

        time.sleep(1)  # 1 sec timestamp change sensitivity in loadconfig
        config.config_full_path.touch()
        set_logging_level (logging.DEBUG, 'cjnfuncs.configman')
        config.loadconfig(prereload_callback=mycallback)
        print (f"----- T9.3:  var dummy in cfg:  {config.getcfg('dummy', False)}  (should be True because flush_on_reload == False)\n")

        time.sleep(1)
        config.config_full_path.touch()
        config.loadconfig(flush_on_reload=True, prereload_callback=mycallback)
        print (f"----- T9.4:  var dummy in cfg:  {config.getcfg('dummy', False)}  (should be False because flush_on_reload == True)\n")

        config.cfg["dummy"] = True
        config.loadconfig(force_flush_reload=True, prereload_callback=mycallback)
        print (f"----- T9.5:  var dummy in cfg:  {config.getcfg('dummy', False)}  (should be False because force_flush_reload == True)\n")

        print (f"Logging level:  {logging.getLogger().level}")


    #===============================================================================================
    def dump(xx):
        print (f"\nGiven <{xx}>     {type(xx)}:")
        yy = timevalue(xx)
        print (yy)
        print (f"   retimed  :  <{retime(yy.seconds, yy.unit_char)}> {yy.unit_str}")

    if check_tnum('10'):
        print_test_header ("Test timevalue, retime")
        set_logging_level (logging.WARNING, 'cjnfuncs.configman')
        do_base_setup()
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


    #===============================================================================================
    if check_tnum('11', include0=False):
        print_test_header ("Test untrapped invalid time unit")
        dump ("3y")             # ValueError raised


    #===============================================================================================
    if check_tnum('12', include0=False):
        print_test_header ("Test untrapped retime with invalid unitC")
        retime (12345, "y")     # ValueError raised


    #===============================================================================================
    if check_tnum('13'):
        print_test_header ("Test missing config and externally set logging level")
        set_logging_level (logging.WARNING, 'cjnfuncs.configman')
        do_base_setup()

        print (f"\n----- T13.1:  Missing config, tolerate_missing=False (default) >>>>  Exception")
        remove_file(config.config_full_path)
        set_logging_level(7)
        try:
            config.loadconfig()
        except Exception as e:
            print (f"Config loading exception:\n  {type(e).__name__}: {e}")
            print (f"Logging level:  {logging.getLogger().level}")

        print (f"\n----- T13.2:  Missing config, tolerate_missing=True >>>>  Returned -1")
        set_logging_level(logging.DEBUG, 'cjnfuncs.configman')
        print (f"Returned:  <{config.loadconfig(tolerate_missing=True)}>")
        print (f"Logging level:  {logging.getLogger().level}")

        print (f"\n----- T13.3:  Working nested import")
        deploy_files([
            { "source": "import_nest_top.cfg",  "target_dir": "USER_CONFIG_DIR"},
            { "source": "import_nest_1.cfg",    "target_dir": "USER_CONFIG_DIR"},
            { "source": "import_nest_2.cfg",    "target_dir": "USER_CONFIG_DIR"},
            ], overwrite=True )
        nest_cfg = mungePath("import_nest_top.cfg", core.tool.config_dir).full_path
        xx = config_item(nest_cfg)
        xx.loadconfig(tolerate_missing=True, force_flush_reload=True)
        print (xx.dump())
        print (f"Logging level:  {logging.getLogger().level}")
        
        print (f"\n----- T13.4:  Missing nested imported config <import_nest_2.cfg> with tolerate_missing=True >>>>  Exception raised.")
        remove_file(mungePath("import_nest_2.cfg", core.tool.config_dir).full_path)
        try:
            xx.loadconfig(tolerate_missing=True, force_flush_reload=True)
        except ConfigError as e:
            print (f"Exception due to missing imported config file:\n  {type(e).__name__}: {e}")
            print (f"Logging level:  {logging.getLogger().level}")
        
        print (f"\n----- T13.5:  Missing imported config <import_nest_1.cfg> with tolerate_missing=True >>>>  Exception raised.")
        remove_file(mungePath("import_nest_1.cfg", core.tool.config_dir).full_path)
        try:
            xx.loadconfig(tolerate_missing=True, force_flush_reload=True)
        except Exception as e:
            print (f"Exception due to missing imported config file:\n  {type(e).__name__}: {e}")
            print (f"Logging level:  {logging.getLogger().level}")


    #===============================================================================================
    if check_tnum('14'):
        print_test_header ("Test modify_configfile")
        set_logging_level (logging.WARNING, 'cjnfuncs.configman')
        do_base_setup()
        config.modify_configfile(r"x_7893&(%$,.nasf||\a@",  "Goodbye!    # It was Hello")   # param match checks
        config.modify_configfile("param_no_value",          "new value   # Had no value")
        config.modify_configfile("testvar",                 "            # It was True")    # value removed

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
        config.modify_configfile("multi_line2",             [{"new":6, "list":7.0, "with dict":True}])

        config.modify_configfile("", "",                    add_if_not_existing=True)       # Blank line
        config.modify_configfile("George", "was here",      add_if_not_existing=True)       # New param
        config.modify_configfile("Snehal", "wasn't here")                                   # Warning message
        config.modify_configfile(                           add_if_not_existing=True)       # Another blank line
        config.modify_configfile("# New comment line",  "", add_if_not_existing=True)       # New comment
        config.modify_configfile("# New comment line",      add_if_not_existing=True)       # Non-unique, and both get added
        config.modify_configfile("new_param_no_value",      add_if_not_existing=True)       # No value
        
        config.modify_configfile("Bjorn",  "was here too   # With a comment and No newline at end of file", add_if_not_existing=True)

        config.modify_configfile("EmailTo",                  "Modify within SMTP section")
        config.modify_configfile("a",                        "Modify all occurrences")

        config.modify_configfile(save=True)
        config.loadconfig(force_flush_reload=True)

        print(config.dump())
        dump_file(config.config_full_path)


    #===============================================================================================
    if check_tnum('15'):
        print_test_header ("Access list, tuple, and dictionary params")
        set_logging_level (logging.WARNING, 'cjnfuncs.configman')
        do_base_setup()
        six      = config.getcfg("a_dict")["six"]
        seven    = config.getcfg("a_tuple")[1]
        fortytwo = config.getcfg("a_list")[2]["abc"]
        print (f"{six} times {seven} is {fortytwo}")


    #===============================================================================================
    if check_tnum('16'):
        print_test_header ("Test getcfg type checking")
        set_logging_level (logging.WARNING, 'cjnfuncs.configman')
        do_base_setup()

        def dump(param, types, section=''):
            try:
                _value = config.getcfg(param, types=types, section=section)
                print (f"Param <{param}> value <{_value}>, type <{type(_value)}>, expected types <{types}>")
            except Exception as e:
                print (f"Param <{param}> not expected type:\n  {type(e).__name__}: {e}")

        dump("Tint",   types=[int, float])
        dump("Tint",   types=int)
        dump("a_list", types=[list])
        dump("Tsec",   types=[int, str])
        dump("y",      types=float,    section='Test #section 2')
        dump("y",      types=bool,     section='Test #section 2')
        dump("Tint",   types=[     float, list, tuple, dict, bool, str])
        dump("a_list", types=[int, float,       tuple, dict, bool, str])
        dump("a_dict", types=[int, float, list, tuple,       bool, str])
        dump("Tsec",   types=[int, float, list, tuple, dict, bool     ])


    #===============================================================================================
    if check_tnum('17'):
        print_test_header ("Assign getcfg and cfg to config instance")
        set_logging_level (logging.WARNING, 'cjnfuncs.configman')
        do_base_setup()
        getcfg = config.getcfg
        cfg = config.cfg
        six      = getcfg("a_dict")["six"]
        seven    = cfg['a_tuple'][1]  # getcfg("a_tuple")[1]
        fortytwo = getcfg("a_list")[2]["abc"]
        print (f"{six} times {seven} is {fortytwo}")


    #===============================================================================================
    if check_tnum('18'):
        print_test_header ("Sections and DEFAULT")
        set_logging_level (logging.WARNING, 'cjnfuncs.configman')
        do_base_setup()
        print (config.dump())
        def dump(option, section='', desc=''):      # TODO option or param?
            try:
                xx = '[' + section + '][' + option + ']'
                _value = config.getcfg(option, section=section)
                print (f"{xx:19}   {_value:<12}    {desc}")
            except:
                print (f"{xx:19}   NOT DEFINED     {desc}")

        print (config)
        dump('a',                           desc='Expecting  <In top level> from [],   [DEFAULT] ignored')
        dump('b',                           desc='Expecting  <12> from [],             no default')
        dump('c',                           desc='Expecting  <42> from [DEFAULT],      not in []')
        dump('d',                           desc='Not in [] or [DEFAULT]')

        dump('a', section='Test section 1', desc='Expecting  <5>  from [Test section], [DEFAULT] ignored')
        dump('b', section='Test section 1', desc='Expecting  <25> from [Test section], no default')
        dump('c', section='Test section 1', desc='Expecting  <42> from [DEFAULT],      not in [Test section 1]')
        dump('e', section='Test section 1', desc='Not in [Test section 1] or [DEFAULT] and [] not considered')


    #===============================================================================================
    if check_tnum('19'):
        print_test_header ("Imports within Sections and DEFAULT")
        set_logging_level (logging.DEBUG, 'cjnfuncs.configman')
        deploy_files([
            { "source": "import_nest_top.cfg",  "target_dir": "USER_CONFIG_DIR"},
            { "source": "import_nest_1.cfg",    "target_dir": "USER_CONFIG_DIR"},
            { "source": "import_nest_2.cfg",    "target_dir": "USER_CONFIG_DIR"},
            ], overwrite=True )
        nest_cfg = mungePath("import_nest_top.cfg", core.tool.config_dir).full_path
        xx = config_item(nest_cfg)
        xx.loadconfig(tolerate_missing=True, force_flush_reload=True)
        print (f"Logging level:  {logging.getLogger().level}")
        print ("\n***** config contents *****")
        print (xx.dump())

    #===============================================================================================
    if check_tnum('20'):
        print_test_header ("Load dictionary into cfg. No file.")
        set_logging_level(15)
        set_logging_level (logging.WARNING, 'cjnfuncs.configman')
        new_config = config_item() # config has no file

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

        print (new_config)
        print (new_config.dump())
        print (f"Logging level:  {logging.getLogger().level}")


    #===============================================================================================
    if check_tnum('21'):
        print_test_header ("Load string blob into cfg. No file.  Delete/clear sections and top-level")
        set_logging_level (logging.WARNING, 'cjnfuncs.configman')
        new_config = config_item()

        string_blob = """
[  ]
a 9
b 12

[ Test section  ]
a 5
b 25

 [Test section 2]
a 50
b 250

[ DEFAULT]
a 10
c 42

[]
e 20

#[ Hello# ]
#f Hello
    """
        print (f"\n----- T21.0:  Initial state")
        set_logging_level(logging.DEBUG, 'cjnfuncs.configman')
        set_logging_level(logging.DEBUG)
        new_config.read_string(string_blob)
        print (new_config)
        print (new_config.dump())

        print (f"\n----- T21.1:  DEFAULTS cleared")
        new_config.clear('DEFAULT')
        print (new_config.dump())
        print ("Sections list:", new_config.sections_list)

        print (f"\n----- T21.2:  <Test section> cleared")
        new_config.clear('Test section')
        print (new_config.dump())
        print ("Sections list:", new_config.sections_list)

        print (f"\n----- T21.3:  <cfg> clear all")
        new_config.clear()
        new_config.read_string(string_blob)
        print (new_config.dump())
        print ("Sections list:", new_config.sections_list)
        new_config.clear()
        print (new_config.dump())
        print ("Sections list:", new_config.sections_list)

        print (f"\n----- T21.4:  Exception for attempting to clear non-existing section")
        try:
            new_config.clear('Test section')
        except ConfigError as e:
            print (f"{type(e).__name__}: {e}")
        print (f"Logging level:  {logging.getLogger().level}")


    #===============================================================================================
    if check_tnum('22'):
        print_test_header ("Force config load as strings")
        set_logging_level (logging.WARNING, 'cjnfuncs.configman')
        config = config_item(CONFIG_FILE, force_str=True)
        print (f"\nLoad config {config.config_full_path}")
        set_logging_level(logging.DEBUG, 'cjnfuncs.configman')
        config.loadconfig()
        print (config)
        print (config.dump())
        print (f"Logging level:  {logging.getLogger().level}")


    #===============================================================================================
    if check_tnum('23'):
        print_test_header ("Section-related errors")
        set_logging_level (logging.WARNING, 'cjnfuncs.configman')

        deploy_files([
            { "source": "demo_config_T23a.cfg",       "target_dir": "USER_CONFIG_DIR"},
            { "source": "demo_config_T23b.cfg",       "target_dir": "USER_CONFIG_DIR"},
            { "source": "demo_config_T23c.cfg",       "target_dir": "USER_CONFIG_DIR"},
            ], overwrite=True )

        set_logging_level(23)
        print (f"\n----- T23.1:  Section defined within imported config file")
        set_logging_level(logging.DEBUG, 'cjnfuncs.configman')
        try:
            T23_config = config_item("demo_config_T23a.cfg")
            T23_config.loadconfig()
        except ConfigError as e:
            print (f"{type(e).__name__}: {e}")
        print (f"Logging level:  {logging.getLogger().level}")


        print (f"\n----- T23.1a:  Section defined within imported config file")
        try:
            T23_config = config_item("demo_config_T23a.cfg")
            T23_config.loadconfig()
        except ConfigError as e:
            logging.exception ("----- T23.1a:  Section defined within imported config file")
        print (f"Logging level:  {logging.getLogger().level}")


        print (f"\n----- T23.2:  Malformed Section name")
        try:
            T23_config = config_item("demo_config_T23c.cfg")
            T23_config.loadconfig()
        except ConfigError as e:
            print (f"{type(e).__name__}: {e}")
        print (f"Logging level:  {logging.getLogger().level}")


    #===============================================================================================
    if check_tnum('24'):
        print_test_header ("Remap core.tool.config_dir and core.tool.log_dir_base")
        set_logging_level (logging.WARNING, 'cjnfuncs.configman')

        print (f"\n----- T24.1:  Both .config_dir and .log_dir_base remapped to same")
        set_toolname('T24.1')
        print (core.tool)
        core.tool.config_dir = '/both_path_T24_1'
        config_T24_1 = config_item()
        print (core.tool)

        print (f"\n----- T24.2:  Both .config_dir and .log_dir_base remapped to different dirs")
        set_toolname('T24.2')
        print (core.tool)
        core.tool.config_dir =   '/config_path_T24_2'
        core.tool.log_dir_base = '/log_dir_base_path_T24_2'
        config_T24_2 = config_item()
        print (core.tool)


    #===============================================================================================
    if check_tnum('25'):
        print_test_header ("Write the config to a file")
        set_logging_level (logging.WARNING, 'cjnfuncs.configman')

        set_logging_level(logging.DEBUG)
        set_toolname(TOOLNAME)
        do_base_setup()

        outfile = 'T25config.cfg'
        config.write(outfile)
        dump_file(outfile)

        xx = config_item(outfile)
        xx.loadconfig()
        print (f"Getting a value from the written then loaded <{outfile}>:  <a_tuple> = {xx.getcfg('a_tuple')}")
        print (f"Getting a value from the written then loaded <{outfile}>:  <bad_list> = {xx.getcfg('bad_list')}")

        print ("Comparing dumps of original and written configs...")
        if config.dump() == xx.dump():
            print ("They match!")


    #===============================================================================================
    if args.test == 50:
        print_test_header (50, "development")

        # def dump_file(filepath):
        #     _file = mungePath(filepath, core.tool.config_dir)
        #     print (f"\n***** File <{_file.full_path}> content:")
        #     print (_file.full_path.read_text())

        set_toolname(TOOLNAME)
        set_logging_level (logging.WARNING, 'cjnfuncs.configman')
        do_base_setup()

        print (config.getcfg('whatever'))

        # set_logging_level(10, 'cjnfuncs.configman')
        logging.getLogger().setLevel(10)
        # deploy_files([
        #     { "source": CONFIG_FILE,            "target_dir": "USER_CONFIG_DIR"},
        #     { "source": "creds_SMTP",           "target_dir": "USER_CONFIG_DIR"},
        #     ], overwrite=True )
        # config = config_item('./junk.cfg')
        # print (f"\nLoad config {config.config_full_path}")
        # config.loadconfig()

        # print(core.tool)
        # print(config)
        # print(config.dump())
        # print(config.sections_list)
        # print(config.sections())
