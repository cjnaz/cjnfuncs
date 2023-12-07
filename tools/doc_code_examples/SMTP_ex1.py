#!/usr/bin/env python3
# ***** SMTP_ex1.py *****

from cjnfuncs.core        import set_toolname, logging, SndEmailError
from cjnfuncs.configman   import config_item
from cjnfuncs.deployfiles import deploy_files
from cjnfuncs.SMTP        import snd_notif, snd_email

tool = set_toolname('SMTP_ex1')


deploy_files([
    { 'source': 'SMTP_ex1.cfg',      'target_dir': 'USER_CONFIG_DIR' },
    { 'source': 'creds_SMTP',        'target_dir': 'USER_CONFIG_DIR' },
    ])

myconfig = config_item('SMTP_ex1.cfg')
myconfig.loadconfig()

try:
    snd_notif(subj='My first text message', 
              msg='This is pretty clean interface!', 
              to='NotifTech', 
              log=True, 
              smtp_config=myconfig)
except SndEmailError as e:
    logging.warning(f"snd_notif() failed:\n  {e}")

try:
    snd_email(subj='My first email send',
              to='me@gmail.com',
              body='This is the body text of the message',
              log=True,
              smtp_config=myconfig)
except SndEmailError as e:
    logging.warning(f"snd_email() failed:\n  {e}")
    