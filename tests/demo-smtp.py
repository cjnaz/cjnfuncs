#!/usr/bin/env python3
"""Demo/test for cjnfuncs snd_notif & snd_email functions
"""

#==========================================================
#
#  Chris Nelson, 2023
#
#==========================================================

__version__ = "1.1"
TOOLNAME =    "cjnfuncs_testsmtp"
CONFIG_FILE = "demo_smtp.cfg"

import argparse
from cjnfuncs.cjnfuncs import *

parser = argparse.ArgumentParser(description=__doc__ + __version__, formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-t', '--test', type=int, default=0,
                    help="Test number to run (default 0 = all).")
parser.add_argument('--config-file', '-c', type=str, default=CONFIG_FILE,
                    help=f"Path to the config file (Default <{CONFIG_FILE})> in user config directory.")
parser.add_argument('--setup-user', action='store_true',
                    help=f"Install starter files in user space.")
parser.add_argument('--cleanup', action='store_true',
                    help="Remove test dirs/files.")
args = parser.parse_args()


tool = set_toolname(TOOLNAME)
print(tool)

if args.setup_user: #config_file == "pushuser":
    deploy_files([
        { "source": CONFIG_FILE,        "target_dir": "USER_CONFIG_DIR" },
        { "source": "testfile.txt",     "target_dir": "USER_CONFIG_DIR" },
        # { "source": "testfile.html",    "target_dir": "USER_CONFIG_DIR" },
        { "source": "testfile.html",    "target_dir": "USER_CACHE_DIR" },
        { "source": "creds_SMTP",       "target_dir": "USER_CONFIG_DIR" },
        { "source": "cjn_demo_smtp.cfg","target_dir": "USER_CONFIG_DIR" },  # file not distributed to github
        ], overwrite=False, missing_ok=True )
    sys.exit()

if args.cleanup:
    if os.path.exists(tool.user_config_dir):
        print (f"Removing 1  {tool.user_config_dir}")
        shutil.rmtree(tool.user_config_dir)
    if os.path.exists(tool.user_cache_dir):
        print (f"Removing 2  {tool.user_cache_dir}")
        shutil.rmtree(tool.user_cache_dir)
    sys.exit()


# Initial load
try:
    config = config_item(args.config_file)
    print (f"\nLoad config {config.config_full_path}")
    config.loadconfig(ldcfg_ll=10)
except Exception as e:
    print ("No user or site setup found.  Run with <--setup-user> to set up the environment.")
    print (f"Then customize mail params in {CONFIG_FILE} and creds_SMTP as needed.")
    print ("To reload any individual file, delete the one then rerun with <--setup-user>")
    print (f"  {e}")
    sys.exit()

if args.test == 0  or args.test == 1:
    print ()
    try:    # This first send will fail with <[Errno -2] Name or service not known> if smtp server params are not valid
        snd_email (subj="1:  body to EmailTo", to="EmailTo", body="To be, or not to be...", log=True)
    except Exception as e:
        print (f"snd_email failed:  {e}")
        print ("The config files probably need to be customized.")
        sys.exit()

if args.test == 0  or args.test == 2:
    print ()
    try:
        snd_email (subj="2:  body to EmailTo - not logged", to="EmailTo", body="To be, or not to be...")
    except SndEmailError as e:
        print (f"snd_email failed:  {e}")

if args.test == 0  or args.test == 3:
    print ()
    try:
        snd_email (subj="3:  filename to EmailTo - not logged", to="EmailTo", filename=mungePath("testfile.txt", tool.config_dir).full_path)
    except SndEmailError as e:
        print (f"snd_email failed:  {e}")

if args.test == 0  or args.test == 4:
    print ()
    try:
        snd_email (subj="4:  htmlfile to EmailTo", htmlfile="testfile.html", to="EmailTo", log=True)
    except SndEmailError as e:
        print (f"snd_email failed:  {e}")

if args.test == 0  or args.test == 5:
    print ()
    snd_email (subj="5:  body to EmailToMulti", body="To be, or not to be...", to="EmailToMulti", log=True)

if args.test == 0  or args.test == 6:
    print ()
    try:
        snd_email (subj="6:  No such file nofile.txt", filename="nofile.txt", to="EmailTo", log=True)
    except SndEmailError as e:
        print (f"snd_email failed:  {e}")

if args.test == 0  or args.test == 7:
    print ()
    try:
        snd_email (subj="7:  No to=", body="Hello")
    except Exception as e:
        print (f"snd_email failed:  {e}")

if args.test == 0  or args.test == 8:
    print ()
    try:
        snd_email (subj="8:  Invalid to=", body="Hello", to="me@example.com, junkAtexample.com", log=True)
    except SndEmailError as e:
        print (f"snd_email failed:  {e}")

if args.test == 0  or args.test == 9:
    print ()
    snd_notif (subj="9:  This is a test subject - not logged", msg='This is the message body')       # to defaults to cfg["NotifList"]

if args.test == 0  or args.test == 10:
    print ()
    snd_notif (subj="10: This is another test subject", msg='This is another message body', log=True)

if args.test == 0  or args.test == 11:
    print ()
    snd_notif (subj="11: snd_notif with to='EmailTo'", msg='This is another message body', to="EmailTo", log=True)

if args.test == 0  or args.test == 12:
    print ()
    try:
        snd_email (subj="12: No body, filename, or htmlfile", to="EmailTo", log=True)
    except SndEmailError as e:
        print (f"snd_email failed:  {e}")

if args.test == 0  or args.test == 13:
    print ()
    try:
        snd_email (subj="13: Empty to=", to="", body="Hello", log=True)
    except SndEmailError as e:
        print (f"snd_email failed:  {e}")

if args.test == 0  or args.test == 14:
    print ()
    try:
        snd_email (subj="14: Invalid to='inval@i^*#d", to="inval@i^*#d", body="Hello", log=True)
    except SndEmailError as e:
        print (f"snd_email failed:  {e}")

if args.test == 0  or args.test == 15:
    print ()
    cfg['EmailServer'] = 'nosuchserver.nosuchmail.com'
    try:
        snd_email (subj="15:  Failed email server", to="EmailTo", body="To be, or not to be...", log=True)
    except SndEmailError as e:
        print (f"snd_email failed:  {e}")

if args.test == 0  or args.test == 16:
    print ()
    cfg['EmailServerPort'] = 'badport'
    try:
        snd_email (subj="16:  Bad server port", to="EmailTo", body="To be, or not to be...", log=True)
    except SndEmailError as e:
        print (f"snd_email failed:  {e}")
