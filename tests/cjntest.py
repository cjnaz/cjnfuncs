#!/usr/bin/env python3

#==========================================================
#
#  Chris Nelson, 2018-2023
#
#  2.0  220109  Restructured as a formal package
#
# Changes pending
#   
#==========================================================

from cjnfuncs.cjnfuncs import *
import shutil
import os

# import pathlib, __main__

def dump_mungePath (in_path="", base_path="", is_dir=False, mkdir=False, note=None):
    print (f"\nGiven:  in_path: <{in_path}>, base_path: <{base_path}>, is_dir: <{is_dir}>, mkdir: <{mkdir}>")
    if note:
        print ("NOTE: ", note)
    xx = mungePath(in_path=in_path, base_path=base_path, is_dir=is_dir, mkdir=mkdir)
    print (f"{'full_path':12}:  {type(xx.full_path)}  {xx.full_path}")
    print (f"{'is_absolute':12}:  {xx.is_absolute}")
    print (f"{'parent':12}:  {type(xx.parent)}  {xx.parent}")
    print (f"{'dir':12}:  {type(xx.dir)}  {xx.dir}")
    print (f"{'name':12}:  {type(xx.name)}  {xx.name}")
    print (f"{'exists':12}:  {xx.exists}")
    print (f"{'is_dir':12}:  {xx.is_dir}")
    print (f"{'is_file':12}:  {xx.is_file}")


dump_mungePath ("~/xyz/file.exe", "~/.config")
dump_mungePath ("xyz/file.exe", "~/.config")
dump_mungePath ("xyz/file.exe", ".")
dump_mungePath ("xyz/file.exe", note="Default dir is the script dir")
dump_mungePath ("cjntest.py")
dump_mungePath ("../monitors.xml", "~/.config/junk", note="exists == False if junk subdir does not exist")
dump_mungePath ("../monitors.xml", "~/.config/junk", mkdir=True, note="Force make the junk subdir")
dump_mungePath ("../monitors.xml", "~/.config/junk", note="Now exists since junk was created above")

shutil.rmtree("/tmp/cjntest")
dump_mungePath ("", "/tmp/cjntest/junk", is_dir=True, note="Tree does not exist")
dump_mungePath ("", "/tmp/cjntest/junk", is_dir=True, mkdir=True)
io.open("/tmp/cjntest/junk/testfile.txt", 'w').close()

# shutil.copy ("testfile.txt", "/tmp/cjntest/junk")
dump_mungePath ("", "/tmp/cjntest/junk", is_dir=True)
dump_mungePath ("testfile.txt", "/tmp/cjntest/junk", is_dir=True, note="testfile.txt previously created")
dump_mungePath ("testfile.txt", "/tmp/cjntest/junk", is_dir=False)
dump_mungePath ("testfile.txt", "/tmp/cjntest/junk", is_dir=False, mkdir=True)
try:
    dump_mungePath ("testfile.txt", "/tmp/cjntest/junk", is_dir=True, mkdir=True, note="Exception raised due to trying to make a directory on top of an existing file")
except Exception as e:
    print (f"Exception: {e}")
dump_mungePath ("testxxxx.txt", "/tmp/cjntest/junk", is_dir=True, mkdir=True, note="Make a dir with a file-like name")
dump_mungePath ("junk/testxxxx.txt", "/tmp/cjntest/", note="Try a diff base_path")


# # xx = mungePath ("~/.config")
# print (mungePath ("~/.config").is_dir)
# mungePath ("~/.config/monitors.xml")
# mungePath ("../monitors.xml", "~/.config/junk")
# mungePath ("../monitors.xml", "~/.config/junk", mkdir=True)
# mungePath ("../monitors.xml", "~/.config/junk")
# mungePath ("../monitors.xml", "~/../cjn/.config/junk")

# here = Path(__main__.__file__).parent
# print (f"{type(here)}  {here}")
# mungePath ("cjntest.py", here)

# here = os.path.dirname(__file__)
# print (f"{type(here)}  {here}")
# mungePath ("cjntest.py", here)

# mungePath (here)
# mungePath (here, here)
# mungePath (base_path=here)

# exit()
exit()

deploy_files('a')
exit()

print ("init")
yy = settoolname("mytool")
hack()


xx = config_item("myconfig.cfg")
hack()

print ("\nload myconfig.cfg")
xx.loadconfig(cfgloglevel=10)

hack()
print ("config_file     ", xx.config_file)
print ("config_dir      ", xx.config_dir)
print ("config_full_path", xx.config_full_path)


config_item("", place_config_file="testcfg.cfg")

print ("\ndeclare testcfg.cfg")
zz = config_item("testcfg.cfg")

hack()
print ("config_file     ", zz.config_file)
print ("config_dir      ", zz.config_dir)
print ("config_full_path", zz.config_full_path)

print ("\nload testcfg.cfg")
zz.loadconfig( cfgloglevel=10)
hack()
print ("config_file     ", zz.config_file)
print ("config_dir      ", zz.config_dir)
print ("config_full_path", zz.config_full_path)

print ("\nload myconfig.cfg")
xx.loadconfig(cfgloglevel=10)
hack()
print ("config_file     ", xx.config_file)
print ("config_dir      ", xx.config_dir)
print ("config_full_path", xx.config_full_path)



# print (PROGDIR)


# findconfig("mytool", "myconfig.cfg")
# hack()

# findconfig("mytool", "~cjn/.config/mytool/myconfig.cfg")
# hack()
# findconfig("mytool", "$HOME/.config/mytool/myconfig.cfg")
# hack()
# findconfig("mytool", "$HOME/.config/mytoolX/myconfig.cfg")
# hack()
# findconfig("mytool", "~/.config/mytool/myconfigX.cfg")
# hack()

# findconfig("mytool", "../$HOME/myconfig.cfg")
# hack()
# findconfig("mytoolX", "myconfig.cfg")
# hack()
# findconfig("mytool", "myconfigX.cfg")
# hack()
# findconfig("mytool5", "myconfig.cfg", place_config_file="../package_data/testcfg.cfg")




#loadconfig (cfgfile='testcfg.cfg', cfgloglevel=10)



# # ===== Tests for funcs3_min_version_check =====
# if not funcs3_min_version_check(2):
#     print(f"ERROR:  funcs3 module must be at least version 2.0.  Found <{funcs3_version}>.")
# if funcs3_min_version_check(1):
#     print(f"funcs3_min_version_check passes.  Found <{funcs3_version}>.")


# ===== Tests for loadconfig, getcfg =====
# # Test config loading exceptions
# try:
#     loadconfig("nosuchfile.cfg", cfgloglevel=getcfg("CfgLogLevel", 30))
# except ConfigError as e:
#     logging.error (f"In main...  {e}")
# loadconfig("nosuchfile.cfg")      # This one exercises untrapped error caught by Python

# # Test config reload - Edit CfgLogLevel, LogLevel, LogFile, and testvar in testcfg.cfg
# print (f"Initial logging level: {logging.getLogger().level}")
# while True:
#     reloaded = loadconfig (cfgfile='testcfg.cfg', cfgloglevel=getcfg("CfgLogLevel", 30), flush_on_reload=True) #, cfglogfile="junk9.txt")#, cfgloglevel=10)
#     if reloaded:
#         print ("\nConfig file reloaded")
#         print (f"Logging level: {logging.getLogger().level}")
#         logging.debug   ("Debug   level message")
#         logging.info    ("Info    level message")
#         logging.warning ("Warning level message")
#         print ("testvar", getcfg("testvar", None), type(getcfg("testvar", None)))
#     time.sleep(.5)

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


# # ===== Tests for snd_notif and snd_email =====
# # Set debug LogLevel in testcfg.cfg
# # cfg['DontEmail'] = True     # Comment these in/out here or in the testcfg.cfg
# # cfg['DontNotif'] = True
# snd_email (subj="body to EmailTo", body="To be, or not to be...", to="EmailTo", log=True)
# snd_email (subj="body to EmailTo - not logged", body="To be, or not to be...", to="EmailTo")
# snd_email (subj="filename to EmailTo - not logged", filename="textfile.txt", to="EmailTo")
# snd_email (subj="htmlfile to EmailTo", htmlfile="testfile.html", to="EmailTo", log=True)
# snd_email (subj="body to EmailToMulti", body="To be, or not to be...", to="EmailToMulti", log=True)
# try:
#     snd_email (subj="No such file nofile.txt", filename="nofile.txt", to="EmailTo", log=True)
# except SndEmailError as e:
#     print (f"snd_email failed:  {e}")
# try:
#     snd_email (subj="No to=", body="Hello")
# except SndEmailError as e:
#     print (f"snd_email failed:  {e}")
# try:
#     snd_email (subj="Invalid to=", body="Hello", to="me@example.com, junkAtexample.com", log=True)
# except SndEmailError as e:
#     print (f"snd_email failed:  {e}")
# snd_notif (subj="This is a test subject - not logged", msg='This is the message body')       # to defaults to cfg["NotifList"]
# snd_notif (subj="This is another test subject", msg='This is another message body', log=True)


# # ===== Tests for lock files =====
# stat = requestlock ("try1")
# print (f"got back from 1st requestLock.  stat = {stat}")
# stat = requestlock ("try2")
# print (f"got back from 2nd requestLock.  stat = {stat}")
# stat = releaselock ()
# print (f"got back from 1st releaseLock.  stat = {stat}")
# stat = releaselock ()
# print (f"got back from 2nd releaseLock.  stat = {stat}")