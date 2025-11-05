# SMTP - Wrapper functions for sending text notification and email messages

Skip to [API documentation](#links)

`snd_notif()` and `snd_email()` are convenience functions that rely on configuration file params in the `[SMTP]` section of the designated config file. 

A notification message is typically a text message sent to a cell phone number via the carrier's Email-to-SMS gateway, such as vzwpix.com, and has the message text specified in-line rather than attached.

For sending notifications, SMS/MMS messaging services, such as Twilio, are also supported.  See [Using a Messaging Service, such as Twilio](#ms), below.

<br>

## A fully working example (enter your own credentials and send-to addresses):

Given the following config file - `SMTP_ex1.cfg`:
```
# SMTP_ex1.cfg

LogLevel =      20

# Email and Notifications params
[SMTP]
NotifList =     5205551212@vzwpix.com, 6132125555@vzwpix.com  # Notifications - white space or comma separated list
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
- The [SMTP] section of the specified config file (eg, `myconfig`) holds all of the static email settings, while the individual calls to snd_notif() and snd_email() contain the message specifics.
- A SndEmailError is raised for any issues, and should be trapped in the script code.

<br>

## Sending DKIM signed messages

DKIM signed messages can greatly reduce the chance that the recipient's email server (eg, gmail) classifies your messages as spam.
You will want to configure DKIM if you are sending through a shared-hosting SMTP server. Your shared-hosting SMTP server should 
also have SPF configured (no action required on your part). 
If you are sending through your ISP's SMTP server it may be adding DKIM signing (and SPF) for you (don't configure DKIM here).

For shared-hosting SMTP you may be able to obtain the server's private key from the
cPanel interface for your account (check in Email Deliverability). 
Save this key to a user-read-only file, eg, `/home/me/creds_mydomain.com.pem`. 
Set the `EmailDKIMSelector` as defined on your SMTP server, eg `default` if your server's DKIM Name filed is `default._domainkey.mydomain.com.`.

Add these params to the `creds_SMTP` file:

```
EmailDKIMDomain     mydomain.com
EmailDKIMPem        /home/me/creds_mydomain.com.pem
EmailDKIMSelector   default
```


<a id="ms"></a>

<br>

## Using a Messaging Service, such as Twilio

snd_notif() supports sending SMS messages either using the phone number carrier's Email-to-SMS gateway (eg, 4805551212@txt.att.net), or
using an SMS messaging service, such as Twilio.  To configure a messaging service, specify the path to a message sender plugin module 
via the `Msg_Handler` config param (within the [SMTP] section).  If `Msg_Handler` is defined, then the plugin's sender() function will be called
instead of sending the message via snd_email().

### Example twilioSender.py plugin:

```
__version__ = '1.0'

from twilio.rest import Client
import logging

DEFAULT_LOGLEVEL =  30


def sender (package, config):
    logging.debug (package)

    account_sid =   config.getcfg('account_sid', section='SMTP')
    auth_token =    config.getcfg('auth_token', section='SMTP')
    ms_sid =        config.getcfg('messaging_service_sid', section='SMTP'),

    # Twilio REST API generates tons of INFO level logging, thus a separate Twilio_LogLevel control
    preexisting_loglevel = logging.getLogger().level
    logging.getLogger().setLevel(config.getcfg('Twilio_LogLevel', DEFAULT_LOGLEVEL, section='SMTP'))

    client = Client(account_sid, auth_token)
    for to_number in package['to']:
        message = client.messages.create(
            to =                    to_number,
            messaging_service_sid = ms_sid,
            media_url =             package['urls'],
            body =                  f"Subject: {package['subj']}\n{package['msg']}")

        logging.debug (message.body)
    
    logging.getLogger().setLevel(preexisting_loglevel)
```

### Example creds_twilio file:

Messaging service credentials should be stored in a private, secured file, and imported into script's config SMTP section.
In this example, all messaging service related params are being declared in the credential file:

```
Msg_Handler =           /<abs-path-to>/twilioSender.py
# country_code =          1       # No leading '+', default 1
# number_length =         10      # Default 10
# Twilio_LogLevel =       10      # Log level within twilloSender, default 30

account_sid =           AC9b0ad6...
auth_token =            05975652...
messaging_service_sid = MG3a225f...
```

### Notables

- If using a messaging service, such as Twilio, the config `Msg_Handler` param declares the path to the message sending plugin module.  The module must implement a `sender()`
function, which will be called with a `package` dictionary containing `subj`, `msg`, `urls`, and `to` key:value pairs, and a reference to the `smtp_config` (the user script 
config that contains the [SMTP] section).
- snd_notif() and snd_email() use the `list_to()` helper function (see `SMTP.py`) for parsing and translating phone numbers and email addresses.  `list_to()` supports:
  - Extracting phone numbers from Email-to-SMS gateway email addresses (eg, 48045551212@vzwpix.com)
  - Prepending the country code, if not provided for a number
  - Basic validity checking of the phone number (all digits and proper length for the specified country code)
  - Dereferencing numbers/email addresses thru config params (eg, `NotifList`)
  - Building a list of numbers for the plugin handler to iterate thru
  - Example:  Given `'4805551212@vzwpix.com 4805551213 +14805551214, +44123456'`, list_to() returns:  `['+14805551212', '+14805551213', '+14805551214', '+44123456']`


<br>

## Controlling logging from within smtp code

Logging within the SMTP module uses the `cjnfuncs.smtp` named/child logger.  By default this logger is set to the `logging.WARNING` level, 
meaning that no logging messages are produced from within the SMTP code.  For validation and debug purposes, logging from within SMTP code 
can be enabled by setting the logging level for this module's logger from within the tool script code:

        logging.getLogger('cjnfuncs.smtp').setLevel(logging.DEBUG)

        # Or alternately, use the core module set_logging_level() function:
        set_logging_level (logging.DEBUG, 'cjnfuncs.smtp')
