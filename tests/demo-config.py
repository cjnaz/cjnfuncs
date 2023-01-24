#!/usr/bin/env python3
"""Demo/test for cjnfuncs environment classes/functions
"""

#==========================================================
#
#  Chris Nelson, 2018-2023
#
#  2.0  220109  Restructured as a formal package
#
# Changes pending
#   
#==========================================================

__version__ = "1.0"
CONFIG_FILE = "testcfg.cfg"

import argparse
from cjnfuncs.cjnfuncs import *


parser = argparse.ArgumentParser(description=__doc__ + __version__, formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('--config-file', '-c', type=str, default=CONFIG_FILE,
                    help=f"Path to the config file (Default <{CONFIG_FILE})> in user/site config directory.")

args = parser.parse_args()


# print ("init")
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


config = config_item(CONFIG_FILE)
print (config.config_full_path)

print (f"\nLoad config {config.config_full_path}")
config.loadconfig(cfgloglevel=10)


# Test config loading exceptions
try:
    configX = config_item("nosuchfile.cfg")
    configX.loadconfig(cfgloglevel=10)
except ConfigError as e:
    # logging.error (f"In main...  {e}")
    print (f"In main...  {e}")
# configX.loadconfig(cfgloglevel=10)      # This one exercises untrapped error caught by Python


# Test config reload - Edit CfgLogLevel, LogLevel, LogFile, and testvar in testcfg.cfg
print (f"Initial logging level: {logging.getLogger().level}")
while True:
    reloaded = config.loadconfig (cfgloglevel=getcfg("CfgLogLevel", 30), flush_on_reload=True) #, cfglogfile="junk9.txt")#, cfgloglevel=10)
    if reloaded:
        print ("\nConfig file reloaded")
        print (f"Logging level: {logging.getLogger().level}")
        logging.debug   ("Debug   level message")
        logging.info    ("Info    level message")
        logging.warning ("Warning level message")
        print ("testvar", getcfg("testvar", None), type(getcfg("testvar", None)))
    time.sleep(.5)


#===================================================



# # Tests for getcfg with/without defaults
# print (f"Testing getcfg - Not in cfg with default: <{getcfg('NotInCfg', 'My Default Value')}>")
# try:
#     getcfg('NotInCfg-NoDef')
# except ConfigError as e:
#     print (e)
# getcfg('NotInCfg-NoDef')          # This one exercises untrapped error caught by Python

# # Test flush_on_reload, force_flush
# from pathlib import Path
# cfg["dummy"] = True
# print (f"var dummy in cfg: {getcfg('dummy', False)} (should be True)")
# loadconfig(cfgfile='testcfg.cfg', flush_on_reload=True, cfgloglevel=10)
# print (f"var dummy in cfg: {getcfg('dummy', False)} (should be True because not reloaded)")
# Path('testcfg.cfg').touch()
# loadconfig(cfgfile='testcfg.cfg', cfgloglevel=10)
# print (f"var dummy in cfg: {getcfg('dummy', False)} (should be True because not flushed on reload)")
# Path('testcfg.cfg').touch()
# loadconfig(cfgfile='testcfg.cfg', flush_on_reload=True, cfgloglevel=10)
# print (f"var dummy in cfg: {getcfg('dummy', False)} (should be False because flush_on_reload)")
# cfg["dummy"] = True
# loadconfig(cfgfile='testcfg.cfg', force_flush_reload=True, cfgloglevel=10)
# print (f"var dummy in cfg: {getcfg('dummy', False)} (should be False because force_flush_reload)")

# # ==== Tests for timevalue, retime =====
# def dump(xx):
#     print (f"Given <{xx}> (type {type(xx)}):")
#     yy = timevalue(xx)
#     print (f"    Original:   <{yy.original}>")
#     print (f"    Seconds:    <{yy.seconds}>")
#     print (f"    Unit char:  <{yy.unit_char}>")
#     print (f"    Unit str:   <{yy.unit_str}>")
#     print (f"    retimed:    <{retime(yy.seconds, yy.unit_char)}> {yy.unit_str}")

# dump (getcfg("Tint"))
# dump (getcfg("Tsec"))
# dump (getcfg("Tmin"))
# dump (getcfg("Thour"))
# dump (getcfg("Tday"))
# dump (getcfg("Tweek"))
# dump (2/7)
# dump ("5.123m")
# # dump ("3y")             # ValueError raised in mytime
# # retime (12345, "y")     # ValueError raised in retime
# sleeptime = timevalue("1.9s")
# print (f"Sleeping {sleeptime.seconds} {sleeptime.unit_str}")
# time.sleep (sleeptime.seconds)
# print ("done sleeping")

#===================================================

# import pathlib, __main__

# def touch (file_path):
#     file_path.open('w').close()
#     # io.open(file_path, 'w').close()

# def remove_file (file_path):
#     os.remove(file_path)

# def remove_tree (path):
#     shutil.rmtree(path)




# parser = argparse.ArgumentParser(description=__doc__ + __version__, formatter_class=argparse.RawTextHelpFormatter)
# parser.add_argument('--config-file', '-c', type=str, default=CONFIG_FILE,
#                     help=f"Path to the config file (Default <{CONFIG_FILE})> in user/site config directory.")

# args = parser.parse_args()

# toolname = set_toolname("envtest")
# toolname.dump()

# if toolname.env_defined == False:
#     print ("No user or site setup found.  Run with <--config-file = newuserconfig (or newsiteconfig)> to set up the environment.")


# if args.config_file == "newuserconfig":
#     deploy_files([
#         { "source": CONFIG_FILE, "target_dir": "USER_CONFIG_DIR",                   "file_stat": 0o644, "dir_stat": 0o777},
#         { "source": "creds_test", "target_dir": "$HOME/.config/junk2",              "file_stat": 0o600, "dir_stat": 0o707},
#         { "source": "creds_test", "target_dir": "USER_CONFIG_DIR"},
#         { "source": "test_dir", "target_dir": "USER_DATA_DIR/mydirs",               "file_stat": 0o633, "dir_stat": 0o770},
#         { "source": "test_dir/subdir/x4", "target_dir": "USER_CONFIG_DIR/mydirs",   "file_stat": 0o633, "dir_stat": 0o770},
#         # { "source": "doesnotexist", "target_dir": "USER_CONFIG_DIR",              "file_stat": 0o633, "dir_stat": 0o770},
#         # { "source": "creds_test", "target_dir": "/no_perm/junkdir",               "file_stat": 0o633, "dir_stat": 0o770},
#         ] , overwrite=True)
#     sys.exit()

# if args.config_file == "newsiteconfig":
#     deploy_files([
#         { "source": CONFIG_FILE, "target_dir": "SITE_CONFIG_DIR",                   "file_stat": 0o644, "dir_stat": 0o777},
#         { "source": "creds_test", "target_dir": "$HOME/.config/junk2",              "file_stat": 0o600, "dir_stat": 0o707},
#         { "source": "creds_test", "target_dir": "SITE_CONFIG_DIR"},
#         { "source": "test_dir", "target_dir": "SITE_DATA_DIR/mydirs",               "file_stat": 0o633, "dir_stat": 0o770},
#         { "source": "test_dir/subdir/x4", "target_dir": "SITE_CONFIG_DIR/mydirs",   "file_stat": 0o633, "dir_stat": 0o770},
#         # { "source": "doesnotexist", "target_dir": "SITE_CONFIG_DIR",              "file_stat": 0o633, "dir_stat": 0o770},
#         # { "source": "creds_test", "target_dir": "/no_perm/junkdir",               "file_stat": 0o633, "dir_stat": 0o770},
#         ] , overwrite=True)


#         # { "source": CONFIG_FILE, "target_dir": "SITE_CONFIG_DIR", "stat": 0o644 },
#         # { "source": "creds_test", "target_dir": "$HOME/.config", "stat": 0o600 },
#         # ])# , overwrite=True)
#     sys.exit()
