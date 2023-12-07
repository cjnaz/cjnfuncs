# SMTP - Wrapper functions for sending text notification and email messages

Skip to [API documentation](#links)

`snd_notif()` and `snd_email()` are convenience functions that rely on configuration file params in the `[SMTP]` section of the designated config file. A notification message is typically a text message sent to a cell phone number via the carrier's email-to-text bridge, such as vzwpix.com, and has the message text specified in-line rather than attached.


## A fully working example (enter your own credentials and send-to addresses):

Given the following config file - `SMTP_ex1.cfg`:
```
# SMTP_ex1.cfg

LogLevel =      20

# Email and Notifications params
[SMTP]
NotifList =     5205551212@vzwpix.com, 6132125555@vzwpix.com  # Notifications - white space or comma separeated list
NotifTech =     8185551212@vzwpix.com  # Notifs for code problems
EmailSummary =  George123@gmail.com    # Summary reports - white space or comma separated list
import          creds_SMTP             # Provides EmailServer, EmailServerPort, EmailUser, EmailPass, and EmailFrom
#EmailVerbose   True                   # True turns on smtplib diagnostic logging
```

And this `creds_SMTP`:
```
# creds_SMTP - Email server credentials
EmailServer         mail.myserver.com
EmailServerPort     P587TLS
EmailUser           outbound@myserver.com
EmailPass           mypassword
EmailFrom           me@myserver.com
```

And running this code:
```
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
```

And finally, running the code produces this output, and a couple sent messages:
```
$ ./SMTP_ex1.py 
Deployed  SMTP_ex1.cfg         to  /home/me/.config/SMTP_ex1/SMTP_ex1.cfg
Deployed  creds_SMTP           to  /home/me/.config/SMTP_ex1/creds_SMTP
           SMTP.snd_notif            -  WARNING:  Notification sent <My first text message> <This is pretty clean interface!>
           SMTP.snd_email            -  WARNING:  Email sent <My first email send>
```

Notables:
- The [SMTP] section of the specified config file holds all of the static email settings, while the individual calls to snd_notif() and snd_email contain the message specifics.
- A SndEmailError is raised for any issues, and should be trapped in the script code.

