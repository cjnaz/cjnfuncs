#!/usr/bin/env python3
"""Demo/test for cjnfuncs snd_notif & snd_email functions

Produce / compare to golden results:
    ./demo-smtp.py --setup-user
        Customize the installed config files

    ./demo-smtp.py | diff demo-smtp-golden.txt -
        Should receive emails 1, 2, 3, 4, 5, 11
        Should receive text notifications 9, 10
        Test 14 (inval@i^*#d) produces 3 diffs with varying reference codes such as d9443c01a7336-211056efd01sm81645855ad.52

    ./demo-smtp.py --cleanup

Notes:
    There are no tests for message handler services (eg twilio) since debug logging includes account credentials.
    There are also no tests for DKIM signed messages.
    These features must be manually tested.
"""

#==========================================================
#
#  Chris Nelson, 2024-2025
#
#==========================================================

__version__ = "3.1"
TOOLNAME =    "cjnfuncs_testsmtp"
CONFIG_FILE = "demo_smtp.cfg"

import argparse
import re
import sys
import os
import shutil

from cjnfuncs.core          import set_toolname, logging, set_logging_level
from cjnfuncs.configman     import config_item
from cjnfuncs.deployfiles   import deploy_files
from cjnfuncs.mungePath     import mungePath
from cjnfuncs.SMTP          import snd_email, snd_notif, list_to
import cjnfuncs.core as core

parser = argparse.ArgumentParser(description=__doc__ + __version__, formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-t', '--test', default='0',
                    help="Test number to run (default 0) - 0 runs all tests")
parser.add_argument('--config-file', '-c', type=str, default=CONFIG_FILE,
                    help=f"Path to the config file (Default <{CONFIG_FILE})> in user config directory")
parser.add_argument('--dry-run', '-d', action='store_true',
                    help=f"Disable email sends (set DontEmail)")
parser.add_argument('--setup-user', action='store_true',
                    help=f"Install starter files in user space")
parser.add_argument('--cleanup', action='store_true',
                    help="Remove test dirs/files")
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
    config.loadconfig()         # Don't log credentials
    # print (config.dump())     # Enable for debug
except Exception as e:
    print ("No user or site setup found.  Run with <--setup-user> to set up the environment.")
    print (f"Then customize mail params in {CONFIG_FILE} and creds_SMTP as needed.")
    print ("To reload any individual file, delete the one then rerun with <--setup-user>")
    print (f"  {e}")
    sys.exit()

if args.dry_run:
    config.read_dict({'DontEmail':True}, section_name='SMTP')


# --------------------------------------------------------------------

def dotest (desc, expect, func, *args, **kwargs):
    logging.warning (f"\n\n==============================================================================================\n" +
                     f"Test {tnum} - {desc}\n" +
                     f"  GIVEN:      {args}, {kwargs}\n" +
                     f"  EXPECT:     {expect}")
    try:
        result = func (*args, subj=f"{tnum}: {desc}", smtp_config=config, **kwargs)
        logging.warning (f"  RETURNED:\n{result}")
        return result
    except Exception as e:
        logging.error (f"\n  RAISED:     {type(e).__name__}: {e}")
        # logging.exception (f"\n  RAISED:     {type(e).__name__}: {e}")
        return e


tnum_parse = re.compile(r"([\d]+)([\w]*)")
def check_tnum(tnum_in, include0='0'):
    global tnum
    tnum = tnum_in
    if args.test == include0  or  args.test == tnum_in:  return True
    try:
        if int(args.test) == int(tnum_parse.match(tnum_in).group(1)):  return True
    except:  pass
    return False

#===============================================================================================


set_logging_level(logging.DEBUG, 'cjnfuncs.smtp')

if check_tnum('1'):
    # This first send will fail with <[Errno -2] Name or service not known> if smtp server params are not valid
    dotest('body to EmailTo, logged', 'email send success, return None',
        snd_email, to="EmailTo", body="To be, or not to be...", log=True)


if check_tnum('2'):
    dotest('body to EmailTo - not logged', 'email send success, not logged, return None',
        snd_email, to="EmailTo", body="To be, or not to be...")


if check_tnum('3'):
    dotest('filename to EmailTo - not logged', 'email send success, not logged, return None',
        snd_email, to="EmailTo", filename=mungePath("testfile.txt", core.tool.config_dir).full_path)


if check_tnum('4'):
    dotest('htmlfile to EmailTo', 'email send success, logged, return None',
        snd_email, htmlfile="testfile.html", to="EmailTo", log=True)


if check_tnum('5'):
    dotest('body to EmailToMulti', 'email send success, logged, return None',
        snd_email, body="To be, or not to be...", to="EmailToMulti", log=True)


if check_tnum('6'):
    dotest('No such file nofile.txt', "SndEmailError... [Errno 2] No such file or directory: '/home/cjn/.cache/cjnfuncs_testsmtp/nofile.txt'",
        snd_email, filename="nofile.txt", to="EmailTo", log=True)


if check_tnum('7'):
    dotest('No to=', "TypeError: snd_email() missing 1 required positional argument: 'to'",
        snd_email, body="Hello")


if check_tnum('8'):
    dotest('Invalid to=', "SndEmailError: Message subject <8: Invalid to=>:  <junkAtexample.com> is not a valid email address",
        snd_email, body="Hello", to="me@example.com, junkAtexample.com", log=True)


if check_tnum('9'):
    dotest('snd_notif to= defaults to cfg["NotifList"]', "notif send success, not logged, return None",
        snd_notif, msg='This is the message body')


if check_tnum('10'):
    dotest('snd_notif logged', "notif send success, logged, return None",
        snd_notif, msg='This is another message body', log=True)


if check_tnum('11'):
    dotest('This is another test subject', "notif send success, not logged, return None",
        snd_notif, msg='This is another message body', to="EmailTo", log=True)


if check_tnum('12'):
    dotest('No body, filename, or htmlfile', "SndEmailError ... No body, filename, or htmlfile specified.",
        snd_email, to="EmailTo", log=True)


if check_tnum('13'):
    dotest('Empty to=', "SndEmailError ... <> is not a valid email address",
        snd_email, to="", body="Hello", log=True)


if check_tnum('14'):
    dotest("Invalid to='inval@i^*#d", "SndEmailError ... The recipient address <inval@i^*#d> is not a valid RFC 5321 address",
        snd_email, to="inval@i^*#d", body="Hello", log=True)


if check_tnum('15'):
    orig_server = config.getcfg('EmailServer', section='SMTP')
    config.cfg['SMTP']['EmailServer'] = 'nosuchserver.nosuchmail.com'
    dotest("Failed email server", "SndEmailError ... <[Errno -2] Name or service not known> / <[Errno 11001] getaddrinfo failed>",
        snd_email, to="EmailTo", body="To be, or not to be...", log=True)
    config.cfg['SMTP']['EmailServer'] = orig_server


if check_tnum('16'):
    orig_port = config.getcfg('EmailServerPort', section='SMTP')
    config.read_dict({'EmailServerPort':'badport'}, section_name='SMTP')
    dotest("Bad server port", "SndEmailError ... Config EmailServerPort <badport> is invalid",
        snd_email, to="EmailTo", body="To be, or not to be...", log=True)
    config.read_dict({'EmailServerPort':orig_port}, section_name='SMTP')


if check_tnum('17'):
    orig_server = config.cfg['SMTP']['EmailServer']

    config.cfg['SMTP']['EmailServer'] = 'nosuchserver.nosuchmail.com'
    config.cfg['SMTP']['EmailNTries'] = 2
    config.cfg['SMTP']['EmailRetryWait'] = 0.5
    dotest("snd_notif Failed email server", "SndEmailError ... <[Errno -2] Name or service not known> / <[Errno 11001] getaddrinfo failed>",
        snd_notif, msg='This is the message body')
    config.cfg['SMTP']['EmailServer'] = orig_server


if check_tnum('18'):
    print ("\n\n=====  Test 18:  list_to tests  =====")

    def list_to_test(desc, to, get_type):
        try:
            print (f"{desc:40} {list_to(to, get_type, desc, config)}")
        except Exception as e:
            print (f"Exception:  {e}")

    list_to_test ('1:   Single email address', 'me@home', 'emails')
    list_to_test ('2:   Multiple email addresses', 'me@home you@home, me@example.com', 'emails')

    list_to_test ('3:   Single number', '4805551212', 'numbers')
    list_to_test ('3a:  Single number with cc', '+14805551212', 'numbers')
    list_to_test ('3b:  Single number int', 4805551212, 'numbers')
    list_to_test ('4:   Multiple numbers', '4805551212, 4805551213', 'numbers')

    list_to_test ('5:   Email-to-SMS addresses', '4805551212@vzwpix.com, 4805551213@txt.att.net', 'emails')
    list_to_test ('6:   Numbers from email addresses', '4805551212@vzwpix.com, 4805551213@txt.att.net', 'numbers')

    list_to_test ('7:   Other country code', '+14805551212, +4448055512', 'numbers')

    list_to_test ('8:   Number too short', '+14805551212, 480555121', 'numbers')
    list_to_test ('8a:  Number too long', '+14805551212, 480222555121', 'numbers')
    list_to_test ('8b:  Int Number too long', 480222555121, 'numbers')
    list_to_test ('9:   Invalid phone number', '+14805551212, 480a555121', 'numbers')
    list_to_test ('10:  No phone number', '', 'numbers')
    list_to_test ('11:  No email address', '', 'emails')
    list_to_test ('12:  Invalid mode', '', 'emailsX')

    list_to_test ('20:  README example', '4805551212@vzwpix.com, 4805551213, +14805551214, +44123456', 'numbers')

    
    

