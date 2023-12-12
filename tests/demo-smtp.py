#!/usr/bin/env python3
"""Demo/test for cjnfuncs snd_notif & snd_email functions
"""

#==========================================================
#
#  Chris Nelson, 2023
#
#==========================================================

__version__ = "1.3"
TOOLNAME =    "cjnfuncs_testsmtp"
CONFIG_FILE = "demo_smtp.cfg"

import argparse
import sys
import os
import shutil

from cjnfuncs.core     import set_toolname, SndEmailError, logging
from cjnfuncs.configman import config_item
from cjnfuncs.deployfiles import deploy_files
from cjnfuncs.mungePath import mungePath
from cjnfuncs.SMTP import snd_email, snd_notif
import cjnfuncs.core as core

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


set_toolname(TOOLNAME)
print(core.tool)

if args.setup_user:
    deploy_files([
        { "source": CONFIG_FILE,        "target_dir": "USER_CONFIG_DIR" },
        { "source": "testfile.txt",     "target_dir": "USER_CONFIG_DIR" },
        { "source": "testfile.html",    "target_dir": "USER_CACHE_DIR" },
        { "source": "creds_SMTP",       "target_dir": "USER_CONFIG_DIR" },
        { "source": "cjn_demo_smtp.cfg","target_dir": "USER_CONFIG_DIR" },  # file not distributed to github
        ], overwrite=False, missing_ok=True )
    sys.exit()

if args.cleanup:
    if os.path.exists(core.tool.user_config_dir):
        print (f"Removing 1  {core.tool.user_config_dir}")
        shutil.rmtree(core.tool.user_config_dir)
    if os.path.exists(core.tool.user_cache_dir):
        print (f"Removing 2  {core.tool.user_cache_dir}")
        shutil.rmtree(core.tool.user_cache_dir)
    sys.exit()


# Initial load
try:
    config = config_item(args.config_file)
    print (f"\nLoad config {config.config_full_path}")
    config.loadconfig(ldcfg_ll=10)
    print (config.dump())
except Exception as e:
    print ("No user or site setup found.  Run with <--setup-user> to set up the environment.")
    print (f"Then customize mail params in {CONFIG_FILE} and creds_SMTP as needed.")
    print ("To reload any individual file, delete the one then rerun with <--setup-user>")
    print (f"  {e}")
    sys.exit()

if args.test == 0  or  args.test == 1:
    print ("\n\n=====================================================================")
    test_desc = '1:  body to EmailTo'
    try:    # This first send will fail with <[Errno -2] Name or service not known> if smtp server params are not valid
        snd_email (subj=test_desc, to="EmailTo", body="To be, or not to be...", log=True, smtp_config=config)
    except Exception:
        logging.exception (f"Test failed:  <{test_desc}>. The config files need to be customized?")
        # print (f"snd_email failed:  {e}")
        # print ("The config files probably need to be customized.")
        sys.exit()

if args.test == 0  or  args.test == 2:
    print ("\n\n=====================================================================")
    test_desc = '2:  body to EmailTo - not logged'
    try:
        snd_email (subj=test_desc, to="EmailTo", body="To be, or not to be...", smtp_config=config)
    except Exception:
        logging.exception (f"Test failed:  <{test_desc}>")
    # except SndEmailError as e:
    #     print (f"snd_email failed:  {e}")

if args.test == 0  or  args.test == 3:
    print ("\n\n=====================================================================")

    test_desc = '3:  filename to EmailTo - not logged'
    try:
        snd_email (subj=test_desc, to="EmailTo", filename=mungePath("testfile.txt", core.tool.config_dir).full_path, smtp_config=config)
    except Exception:
        logging.exception (f"Test failed:  <{test_desc}>")

if args.test == 0  or  args.test == 4:
    print ("\n\n=====================================================================")

    test_desc = '4:  htmlfile to EmailTo'
    try:
        snd_email (subj=test_desc, htmlfile="testfile.html", to="EmailTo", log=True, smtp_config=config)
    except Exception:
        logging.exception (f"Test failed:  <{test_desc}>")

if args.test == 0  or  args.test == 5:
    print ("\n\n=====================================================================")

    test_desc = '5:  body to EmailToMulti'
    try:
        snd_email (subj=test_desc, body="To be, or not to be...", to="EmailToMulti", log=True, smtp_config=config)
    except Exception:
        logging.exception (f"Test failed:  <{test_desc}>")

if args.test == 0  or  args.test == 6:
    print ("\n\n=====================================================================")

    test_desc = '6:  No such file nofile.txt'
    try:
        snd_email (subj=test_desc, filename="nofile.txt", to="EmailTo", log=True, smtp_config=config)
    except Exception:
        logging.exception (f"Test failed:  <{test_desc}>")

if args.test == 0  or  args.test == 7:
    print ("\n\n=====================================================================")

    test_desc = '7:  No to='
    try:
        snd_email (subj=test_desc, body="Hello", smtp_config=config)
    except Exception:
        logging.exception (f"Test failed:  <{test_desc}>")

if args.test == 0  or  args.test == 8:
    print ("\n\n=====================================================================")

    test_desc = '8:  Invalid to='
    try:
        snd_email (subj=test_desc, body="Hello", to="me@example.com, junkAtexample.com", log=True, smtp_config=config)
    except Exception:
        logging.exception (f"Test failed:  <{test_desc}>")

if args.test == 0  or  args.test == 9:
    print ("\n\n=====================================================================")

    test_desc = '9:  This is a test subject - not logged'
    try:
        snd_notif (subj=test_desc, msg='This is the message body', smtp_config=config)       # to defaults to cfg["NotifList"]
    except Exception:
        logging.exception (f"Test failed:  <{test_desc}>")

if args.test == 0  or  args.test == 10:
    print ("\n\n=====================================================================")

    test_desc = '10: This is another test subject'
    try:
        snd_notif (subj=test_desc, msg='This is another message body', log=True, smtp_config=config)
    except Exception:
        logging.exception (f"Test failed:  <{test_desc}>")

if args.test == 0  or  args.test == 11:
    print ("\n\n=====================================================================")

    test_desc = "11: snd_notif with to='EmailTo'"
    try:
        snd_notif (subj=test_desc, msg='This is another message body', to="EmailTo", log=True, smtp_config=config)
    except Exception:
        logging.exception (f"Test failed:  <{test_desc}>")

if args.test == 0  or  args.test == 12:
    print ("\n\n=====================================================================")

    test_desc = '12: No body, filename, or htmlfile'
    try:
        snd_email (subj=test_desc, to="EmailTo", log=True, smtp_config=config)
    except Exception:
        logging.exception (f"Test failed:  <{test_desc}>")

if args.test == 0  or  args.test == 13:
    print ("\n\n=====================================================================")

    test_desc = '13: Empty to='
    try:
        snd_email (subj=test_desc, to="", body="Hello", log=True, smtp_config=config)
    except Exception:
        logging.exception (f"Test failed:  <{test_desc}>")

if args.test == 0  or  args.test == 14:
    print ("\n\n=====================================================================")

    test_desc = "14: Invalid to='inval@i^*#d"
    try:
        snd_email (subj=test_desc, to="inval@i^*#d", body="Hello", log=True, smtp_config=config)
    except Exception:
        logging.exception (f"Test failed:  <{test_desc}>")

if args.test == 0  or  args.test == 15:
    print ("\n\n=====================================================================")

    test_desc = '15:  Failed email server'
    config.cfg['SMTP']['EmailServer'] = 'nosuchserver.nosuchmail.com'
    try:
        snd_email (subj=test_desc, to="EmailTo", body="To be, or not to be...", log=True, smtp_config=config)
    except Exception:
        logging.exception (f"Test failed:  <{test_desc}>")

if args.test == 0  or  args.test == 16:
    print ("\n\n=====================================================================")

    test_desc = '16:  Bad server port'
    config.read_dict({'EmailServerPort':'badport'}, section_name='SMTP')
    try:
        snd_email (subj=test_desc, to="EmailTo", body="To be, or not to be...", log=True, smtp_config=config)
    except Exception:
        logging.exception (f"Test failed:  <{test_desc}>")

if args.test == 0  or  args.test == 17:
    print ("\n\n=====================================================================")

    test_desc = '17:  snd_notif Failed email server'
    config.cfg['SMTP']['EmailServer'] = 'nosuchserver.nosuchmail.com'
    try:
        snd_notif (subj=test_desc, msg='This is the message body', smtp_config=config)
        # snd_email (subj=test_desc, to="EmailTo", body="To be, or not to be...", log=True, smtp_config=config)
    except Exception:
        logging.exception (f"Test failed:  <{test_desc}>")

