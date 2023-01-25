#!/usr/bin/env python3
"""Demo/test for cjnfuncs config classes/functions
"""

#==========================================================
#
#  Chris Nelson, 2018-2023
#
#==========================================================

__version__ = "1.0"
CONFIG_FILE = "demo_config.cfg"

import argparse
from cjnfuncs.cjnfuncs import *


parser = argparse.ArgumentParser(description=__doc__ + __version__, formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('Mode',
                    help="Test modes (1, 2, ...)")
parser.add_argument('--config-file', '-c', type=str, default=CONFIG_FILE,
                    help=f"Path to the config file (Default <{CONFIG_FILE})> in user config directory.")
args = parser.parse_args()


tool = set_toolname("cjnfuncs_testcfg")
tool.dump()

if args.config_file == "newuserconfig":
    deploy_files([
        { "source": CONFIG_FILE,       "target_dir": "USER_CONFIG_DIR"},
        { "source": "additional.cfg",  "target_dir": "USER_CONFIG_DIR"},
        { "source": "creds_SMTP",      "target_dir": "USER_CONFIG_DIR"},
        ], overwrite=True )
    sys.exit()

if tool.env_defined == False:
    print ("No user or site setup found.  Run with <--config-file = newuserconfig> to set up the environment.")
    sys.exit()


# Initial load
config = config_item(CONFIG_FILE)
print (f"\nLoad config {config.config_full_path}")
try:
    config.loadconfig(cfgloglevel=10)
except Exception as e:
    print (f"loadconfig raised exception: \n  {e}")
    sys.exit()


# Test config loading exceptions
if args.Mode == '1':
    try:
        configX = config_item("nosuchfile.cfg")
        configX.loadconfig(cfgloglevel=10)
    except ConfigError as e:
        print (f"In main...  {e}")

# Test untrapped config loading exceptions
if args.Mode == '2':
    configX = config_item("nosuchfile.cfg")
    configX.loadconfig(cfgloglevel=10)


# Test config reload - Edit CfgLogLevel, LogLevel, LogFile, and testvar in demo_config.cfg
if args.Mode == '3':
    print (f"Initial logging level: {logging.getLogger().level}")
    while True:
        try:
            reloaded = config.loadconfig (cfgloglevel=getcfg("CfgLogLevel", 30), flush_on_reload=True) #, cfglogfile="junk9.txt")#, cfgloglevel=10)
        except Exception as e:
            print (f"loadconfig raised exception: \n  {e}")
            sys.exit()
        if reloaded:
            print ("\nConfig file reloaded")
            print (f"Logging level:    {logging.getLogger().level}")
            print (f"Current log file: {tool.log_full_path}")
            print (f"testvar:          {getcfg('testvar', None)}  {type(getcfg('testvar', None))}")
            logging.debug   ("Debug   level message")
            logging.info    ("Info    level message")
            logging.warning ("Warning level message")
        time.sleep(.5)


# Tests for getcfg with/without defaults
if args.Mode == '4':
    print (f"Testing getcfg - Not in cfg with default: <{getcfg('NotInCfg', 'My Default Value')}>")
    try:
        getcfg('NotInCfg-NoDef')
    except ConfigError as e:
        print (f"ConfigError: {e}")
    sys.exit()

# This one exercises untrapped error caught by Python
if args.Mode == '5':
    getcfg('NotInCfg-NoDef')


# Test flush_on_reload, force_flush_reload
if args.Mode == '6':
    cfg["dummy"] = True
    print (f"var dummy in cfg: {getcfg('dummy', False)} (should be True)")

    config.loadconfig(flush_on_reload=True, cfgloglevel=10)
    print (f"var dummy in cfg: {getcfg('dummy', False)} (should be True because not reloaded)")

    config.config_full_path.touch()
    config.loadconfig(cfgloglevel=10)
    print (f"var dummy in cfg: {getcfg('dummy', False)} (should be True because not flushed on reload)")

    config.config_full_path.touch()
    config.loadconfig(flush_on_reload=True, cfgloglevel=10)
    print (f"var dummy in cfg: {getcfg('dummy', False)} (should be False because flush_on_reload)")

    cfg["dummy"] = True
    config.loadconfig(force_flush_reload=True, cfgloglevel=10)
    print (f"var dummy in cfg: {getcfg('dummy', False)} (should be False because force_flush_reload)")

    sys.exit()


# Tests for timevalue, retime

def dump(xx):
    print (f"Given <{xx}> (type {type(xx)}):")
    yy = timevalue(xx)
    print (f"    Original:   <{yy.original}>")
    print (f"    Seconds:    <{yy.seconds}>")
    print (f"    Unit char:  <{yy.unit_char}>")
    print (f"    Unit str:   <{yy.unit_str}>")
    print (f"    retimed:    <{retime(yy.seconds, yy.unit_char)}> {yy.unit_str}")

if args.Mode == '7':
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
    sys.exit()

if args.Mode == '8':
    dump ("3y")             # ValueError raised

if args.Mode == '9':
    retime (12345, "y")     # ValueError raised

