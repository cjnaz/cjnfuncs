#!/usr/bin/env python3
"""Demo/test for cjnfuncs snd_notif & snd_email functions
"""

#==========================================================
#
#  Chris Nelson, 2018-2023
#
#==========================================================

__version__ = "1.0"
TOOLNAME =    "cjnfuncs_testsmtp"
CONFIG_FILE = "demo_smtp.cfg"


import argparse
from cjnfuncs.cjnfuncs import *


parser = argparse.ArgumentParser(description=__doc__ + __version__, formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('--config-file', '-c', type=str, default=CONFIG_FILE,
                    help=f"Path to the config file (Default <{CONFIG_FILE})> in user config directory.")
args = parser.parse_args()


tool = set_toolname(TOOLNAME)
tool.dump()

if args.config_file == "newuserconfig":
    deploy_files([
        { "source": CONFIG_FILE,        "target_dir": "USER_CONFIG_DIR" },
        { "source": "testfile.txt",     "target_dir": "USER_CONFIG_DIR" },
        { "source": "testfile.html",    "target_dir": "USER_CONFIG_DIR" },
        { "source": "creds_SMTP",       "target_dir": "USER_CONFIG_DIR" },
        { "source": "cjn_demo_smtp.cfg","target_dir": "USER_CONFIG_DIR" },  # file not distributed to github
        ], overwrite=False, missing_ok=True )
    sys.exit()

if args.config_file == "cleanup":
    if os.path.exists(tool.user_config_dir):
        print (f"Removing 1  {tool.user_config_dir}")
        shutil.rmtree(tool.user_config_dir)
    sys.exit()


if tool.env_defined == False:
    print ("No user or site setup found.  Run with <--config-file = newuserconfig> to set up the environment.")
    print (f"Then customize mail params in {CONFIG_FILE} and creds_SMTP as needed.")
    print ("To reload any individual file, delete the one then rerun with <--config-file = newuserconfig>")
    sys.exit()


# Initial load
config = config_item(CONFIG_FILE)
print (f"\nLoad config {config.config_full_path}")
try:
    config.loadconfig(cfgloglevel=10)
except Exception as e:
    print (f"loadconfig raised exception: \n  {e}")
    sys.exit()


print ()
try:    # This first send will fail with <[Errno -2] Name or service not known> if smtp server params are not valid
    snd_email (subj="1: body to EmailTo", body="To be, or not to be...", to="EmailTo", log=True)
except Exception as e:
    print (f"snd_email failed:  {e}")
    sys.exit()

print ()
snd_email (subj="2: body to EmailTo - not logged", body="To be, or not to be...", to="EmailTo")

print ()
snd_email (subj="3:  filename to EmailTo - not logged", filename=mungePath("testfile.txt", tool.config_dir).full_path, to="EmailTo")

print ()
snd_email (subj="4:  htmlfile to EmailTo", htmlfile=mungePath("testfile.html", tool.config_dir).full_path, to="EmailTo", log=True)

print ()
snd_email (subj="5:  body to EmailToMulti", body="To be, or not to be...", to="EmailToMulti", log=True)

print ()
try:
    snd_email (subj="6:  No such file nofile.txt", filename="nofile.txt", to="EmailTo", log=True)
except SndEmailError as e:
    print (f"snd_email failed:  {e}")

print ()
try:
    snd_email (subj="7:  No to=", body="Hello")
except SndEmailError as e:
    print (f"snd_email failed:  {e}")

print ()
try:
    snd_email (subj="8:  Invalid to=", body="Hello", to="me@example.com, junkAtexample.com", log=True)
except SndEmailError as e:
    print (f"snd_email failed:  {e}")

print ()
snd_notif (subj="9:  This is a test subject - not logged", msg='This is the message body')       # to defaults to cfg["NotifList"]

print ()
snd_notif (subj="10: This is another test subject", msg='This is another message body', log=True)
