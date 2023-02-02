#!/usr/bin/env python3
"""Demo/test for cjnfuncs config classes/functions
"""

#==========================================================
#
#  Chris Nelson, 2018-2023
#
#==========================================================

__version__ = "1.0"
TOOLNAME    = "cjnfuncs_testcfg"
CONFIG_FILE = "demo_config.cfg"
# LOGFILE     = None

import argparse
from cjnfuncs.cjnfuncs import *


parser = argparse.ArgumentParser(description=__doc__ + __version__, formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('Mode',
                    help="Test modes (1, 2, ...)")
parser.add_argument('--config-file', '-c', type=str, default=CONFIG_FILE,
                    help=f"Path to the config file (Default <{CONFIG_FILE})> in user config directory.")
parser.add_argument('--setup-user', action='store_true',
                    help=f"Install starter files in user space.")
parser.add_argument('--cleanup', action='store_true',
                    help="Remove test dirs/files.")
args = parser.parse_args()


tool = set_toolname(TOOLNAME)
print(tool.dump())

# if args.setup_user:
#     deploy_files([
#         { "source": CONFIG_FILE,            "target_dir": "USER_CONFIG_DIR"},
#         { "source": "demo_config_T1.cfg",   "target_dir": "USER_CONFIG_DIR"},
#         { "source": "demo_config_T2.cfg",   "target_dir": "USER_CONFIG_DIR"},
#         { "source": "additional.cfg",       "target_dir": "USER_CONFIG_DIR"},
#         { "source": "creds_SMTP",           "target_dir": "USER_CONFIG_DIR"},
#         ], overwrite=True )
#     sys.exit()

if args.cleanup:
    if os.path.exists(tool.config_dir):
        print (f"Removing 1  {tool.config_dir}")
        shutil.rmtree(tool.config_dir)
    sys.exit()



def remove_file (file_path):
    if os.path.exists(file_path):
        os.remove(file_path)


def modify_configfile (cfg, key, value="", remove=False):
    """
    Relies on whitespace separation
    """
    cfg_temp = ""
    with cfg.config_full_path.open() as cfgfile:
        xx = cfgfile.read().split("\n")
    found_key = False
    for line in xx:
        try:
            if line.strip().split(maxsplit=1)[0] != key:    # Relies on whitespace separation
                cfg_temp += line + "\n"
            else:
                found_key = True
                if remove == False:
                    cfg_temp += f"{key}    {value}\n"
                # If remove == True, just don't write the line out
        except:
            cfg_temp += line # + "\n"
    if found_key == False  and  remove == False:
        cfg_temp += f"{key}    {value}\n"
    
    with cfg.config_full_path.open('w') as cfgfile:
        cfgfile.write(cfg_temp)

    time.sleep(.1)  # Seems to be needed to ensure diff timestamps.  ???

# if args.setup_user:
# deploy_files([
#     { "source": CONFIG_FILE,            "target_dir": "USER_CONFIG_DIR"},
#     { "source": "demo_config_T1.cfg",   "target_dir": "USER_CONFIG_DIR"},
#     { "source": "demo_config_T2.cfg",   "target_dir": "USER_CONFIG_DIR"},
#     { "source": "additional.cfg",       "target_dir": "USER_CONFIG_DIR"},
#     { "source": "creds_SMTP",           "target_dir": "USER_CONFIG_DIR"},
#     ], overwrite=True )
#     # sys.exit()


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
    modify_configfile (config_T1, "LogFile",   "cfg_logfile")
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
    modify_configfile (config_T1, "LogFile",   "cfg_logfile2")
    config_T1.loadconfig (ldcfg_ll=10, call_logfile="call_logfile", call_logfile_wins=False,   force_flush_reload=True)
    print (f"Current log file:              {tool.log_full_path}")
    logging.warning (f"T1.7 - Log to  <{tool.log_full_path}>")

    print ("\n----- T1.8:  LogFile='cfg_logfile', call_logfile='call_logfile', call_logfile_wins=True >>>>  Log file:  'call_logfile' (again)")
    config_T1.loadconfig (ldcfg_ll=10, call_logfile="call_logfile", call_logfile_wins=True,   force_flush_reload=True)
    print (f"Current log file:              {tool.log_full_path}")
    print (tool.dump())
    logging.warning (f"T1.8 - Log to  <{tool.log_full_path}>")

    print ("\n----- T1.9:  LogFile='cfg_logfile', call_logfile=None, call_logfile_wins=True >>>>  Log file:  __console__")
    config_T1.loadconfig (ldcfg_ll=10, call_logfile=None, call_logfile_wins=True,   force_flush_reload=True)
    print (f"Current log file:              {tool.log_full_path}")
    print (tool.dump())
    logging.warning (f"T1.9 - Log to  <{tool.log_full_path}>")

    print ("\n----- T1.10: LogFile=None, call_logfile=None, call_logfile_wins=False >>>>  Log file:  __console__")
    modify_configfile (config_T1, "LogFile",   remove=True)
    config_T1.loadconfig (ldcfg_ll=10, call_logfile=None, call_logfile_wins=True,   force_flush_reload=True)
    print (f"Current log file:              {tool.log_full_path}")
    logging.warning (f"T1.10 - Log to  <{tool.log_full_path}>")

    sys.exit()


if args.Mode == '2':
    print ("\n***** Tests for ldcfg_ll, config LogLevel, flush_on_reload, force_flush_reload *****")

    def print_stats ():
        print (f"(Re)loaded             :  {reloaded}")
        print (f"Config file timestamp  :  {config_T2.config_timestamp}")
        print (f"Config LogLevel        :  {getcfg('LogLevel', 'None')}")
        print (f"Current Logging level  :  {logging.getLogger().level}")
        print (f"testvar                :  {getcfg('testvar', None)}  {type(getcfg('testvar', None))}")
        print (f"var2                   :  {getcfg('var2', None)}")
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
        # loadconfig params:   ldcfg_ll=10, call_logfile=None, call_logfile_wins=True, flush_on_reload=True, force_flush_reload=True)
    print_stats()

    print ("\n----- T2.2:  No config change >>>>  Not reloaded")
    # modify_configfile (config_T2, "testvar",   "George")
    reloaded = config_T2.loadconfig(flush_on_reload=True) 
    print_stats()

    print ("\n----- T2.3:  LogLevel=10, ldcfg_ll=10 >>>>  loadconfig logging, Logging DEBUG, INFO, and WARNING messages")
    modify_configfile (config_T2, "LogLevel",   "10")
    reloaded = config_T2.loadconfig(ldcfg_ll=10, flush_on_reload=True)
    print_stats()

    print ("\n----- T2.4:  LogLevel=10, ldcfg_ll=30 (default) >>>>  No loadconfig logging, Logging DEBUG, INFO, and WARNING messages")
    modify_configfile (config_T2, "LogLevel",   "10")
    reloaded = config_T2.loadconfig(flush_on_reload=True)
    print_stats()

    print ("\n----- T2.5:  LogLevel=30, ldcfg_ll=30 (default),  >>>>  Log only WARNING")
    modify_configfile (config_T2, "LogLevel",   "30")
    reloaded = config_T2.loadconfig(flush_on_reload=True)
    print_stats()

    print ("\n----- T2.6:  ldcfg_ll=10, No LogLevel >>>>  Restore preexisting level (30)")
    modify_configfile (config_T2, "LogLevel",  remove=True)
    modify_configfile (config_T2, "testvar",   True)
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
    modify_configfile (config_T2, "LogLevel",   "20")
    modify_configfile (config_T2, "var2",   "Hello")
    reloaded = config_T2.loadconfig(ldcfg_ll=10, force_flush_reload=True)
    print_stats()

    print ("\n----- T2.11: ldcfg_ll=10, LogLevel=40, var2 removed from config >>>>  var2 still defined, no logging")
    modify_configfile (config_T2, "LogLevel",   "40")
    modify_configfile (config_T2, "var2",   remove=True)
    reloaded = config_T2.loadconfig(ldcfg_ll=10)
    print_stats()

    print ("\n----- T2.12: ldcfg_ll=10, LogLevel=30, force_flush_reload=True >>>>  var2 gone")
    modify_configfile (config_T2, "LogLevel",   "30")
    reloaded = config_T2.loadconfig(ldcfg_ll=10, force_flush_reload=True)
    print_stats()

    print ("\n----- T2.13: Externally set log level = 20")
    modify_configfile (config_T2, "LogLevel",   remove=True)
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
    # sys.exit()

try:
    config = config_item(CONFIG_FILE)
    print (f"\nLoad config {config.config_full_path}")
    config.loadconfig(ldcfg_ll=10)
except Exception as e:
    print (f"No user or site setup found.  Run with <--setup-user> to set up the environment.\n  {e}")
    sys.exit()


if args.Mode == '3':
    print ("\n***** Show tool.log_* values (LogFile NOT in config) *****")
    print(tool.dump())
    print(config.dump())


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
    print(config.dump())
    logging.warning (f"testvar:          {getcfg('testvar', None)}  {type(getcfg('testvar', None))}")
    logging.warning (f"another:          {getcfg('another', None)}  {type(getcfg('another', None))}")
    additional_config = config_item("additional.cfg")
    print(additional_config.dump())
    additional_config.loadconfig(ldcfg_ll=10)
    print(additional_config.dump())
    logging.warning (f"testvar:          {getcfg('testvar', None)}  {type(getcfg('testvar', None))}")
    logging.warning (f"another:          {getcfg('another', None)}  {type(getcfg('another', None))}")
    print (f"Current logging level:      {logging.getLogger().level}")


if args.Mode == '7':
    print ("\n***** Test unknown getcfg param with/without defaults *****")
    print (f"Testing getcfg - Not in cfg with default: <{getcfg('NotInCfg', 'My Default Value')}>")
    try:
        getcfg('NotInCfg-NoDef')
    except ConfigError as e:
        print (f"ConfigError: {e}")


if args.Mode == '8':
    print ("\n***** Test untrapped unknown getcfg param *****")
    getcfg('NotInCfg-NoDef')


if args.Mode == '9':
    print ("\n***** Test flush_on_reload  and  force_flush_reload cases *****")
    cfg["dummy"] = True
    print (f"\n----- T9.1:  var dummy in cfg:  {getcfg('dummy', False)}  (should be True - Initial state)\n")

    config.loadconfig(flush_on_reload=True, ldcfg_ll=10)
    print (f"----- T9.2:  var dummy in cfg:  {getcfg('dummy', False)}  (should be True because not reloaded)\n")

    config.config_full_path.touch()
    time.sleep(.1)  # Seems to be needed to ensure diff timestamps.  ???
    config.loadconfig(ldcfg_ll=10)
    print (f"----- T9.3:  var dummy in cfg:  {getcfg('dummy', False)}  (should be True because flush_on_reload == False)\n")

    config.config_full_path.touch()
    time.sleep(.1)
    config.loadconfig(flush_on_reload=True, ldcfg_ll=10)
    print (f"----- T9.4:  var dummy in cfg:  {getcfg('dummy', False)}  (should be False because flush_on_reload == True)\n")

    cfg["dummy"] = True
    config.loadconfig(force_flush_reload=True, ldcfg_ll=10)
    print (f"----- T9.5:  var dummy in cfg:  {getcfg('dummy', False)}  (should be False because force_flush_reload == True)\n")


def dump(xx):
    print (f"Given <{xx}> (type {type(xx)}):")
    yy = timevalue(xx)
    print (f"    Original:   <{yy.original}>")
    print (f"    Seconds:    <{yy.seconds}>")
    print (f"    Unit char:  <{yy.unit_char}>")
    print (f"    Unit str:   <{yy.unit_str}>")
    print (f"    retimed:    <{retime(yy.seconds, yy.unit_char)}> {yy.unit_str}")

if args.Mode == '10':
    print ("\n***** Test timevalue, retime *****")
    dump (getcfg("Tint"))
    dump (getcfg("Tsec"))
    dump (getcfg("Tmin"))
    dump (getcfg("Thour"))
    dump (getcfg("Tday"))
    dump (getcfg("Tweek"))
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
    print ("\n***** Test missing config *****")

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
