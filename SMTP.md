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



<a id="links"></a>
         
<br>

---

# Links to classes, methods, and functions

- [snd_notif](#snd_notif)
- [snd_email](#snd_email)



<br/>

<a id="snd_notif"></a>

---

# snd_notif (subj='Notification message', msg='', urls_list=[], to='NotifList', log=False, smtp_config=None) - Send a text message using info from the config file

Intended for use the mobile provider's (carrier's) email-to-SMS gateway email address, eg, 
`5405551212@vzwtxt.com` for Verizon, but any email address will work.

The `to` string may be the name of a config param (who's value is one or more email addresses, default 
"NotifList"), or a string with one or more email addresses. Using a config param name allows for customizing the
`to` addresses without having to edit the code.

The message to send is passed in the `msg` arg as a text string.
Three attempts are made to send the message.

    
### Args
`subj` (str, default 'Notification message')
- Text message subject field
- Some SMS/MMS apps display the subj field in bold, some in raw form, and some not at all.

`msg` (str, default '')
- Text message body

`urls_list` (list, default [])
- A list of url strings to be passed to the message sending plugin module, which should pass them to the messaging service.
- This list is discarded by `snd_notif()` if not using a messaging service.  If you want to send a message with
urls then included them in the `msg` body text.

`to` (str, default 'NotifList')
- To whom to send the message. `to` may be either an explicit string list of email addresses
(whitespace or comma separated) or a config param name (also listing one
or more whitespace or comma separated email addresses).  If the `to` arg does not
contain an '@' it is assumed to be a config param.
- Define `NotifList` in the config file to use the default `to` value.

`log` (bool, default False)
- If True, logs that the message was sent at the WARNING level. If False, logs 
at the DEBUG level. Useful for eliminating separate logging messages in the tool script code.
The `subj` field is part of the log message.

`smtp_config` (config_item class instance)
- config_item class instance containing the [SMTP] section and related params


### config dictionary params in the [SMTP] section, in addition to the config dictionary params required for snd_email

`NotifList` (optional)
- string list of email addresses (whitespace or comma separated).  
- Defining `NotifList` in the config is only required if any call to `snd_notif()` uses this
default `to` arg value.

`DontNotif` (default False)
- If True, notification messages are not sent. `log` is still honored. Useful for debug.
- Setting `DontEmail` True also blocks sending notification messages if using a carrier email-to-SMS gateway 
(not using a messaging service).  If using a messaging service then `DontEmail` has no effect.

`Msg_Handler` (str, absolute path or package.module, default None)
- If using a messaging service, such as Twilio, this param declares the path to the message sending plugin module.  
- The module must implement a `sender()` function, which will be called with a `package` dictionary containing `subj`, `msg`, `urls`, and `to` key:value pairs, and
  a reference to the `smtp_config`.  See the [SMTP.md](https://github.com/cjnaz/cjnfuncs/blob/main/SMTP.md) for an example Msg_Handler module implementation.
- `Msg_Handler` may be a full absolute path to a Python module (eg, `/path-to-module/twilioSender.py`), or an installed package.module reference (eg, `mypackage.twilioSender`).

`country_code` (int or str, default 1 (US/Canada), required only if `Msg_Handler` is defined in the config [SMTP] section)
- Number without a preceding '+', eg '1' for US/Canada phone numbers
- If `get_type='numbers'` then each phone number is prepended with `+` plus `country_code` (eg, '+1'), but only if the number does not already have a country code.
- If a `to` phone number has a different country code, it is retained.

`number_length` (int, default 10 (US/Canada), required only if `Msg_Handler` is defined in the config [SMTP] section)
- The number of digits in a valid phone number (not including the country code), eg 10 for US/Canada phone numbers


### Returns
- None
- Raises `SndEmailError` on error


### Behaviors and rules
- `snd_notif()` uses `snd_email()` to send the message. See `snd_email()` for related setup.
    
<br/>

<a id="snd_email"></a>

---

# snd_email (subj, to, body=None, filename=None, htmlfile=None, log=False, smtp_config=None) - Send an email message using info from the config file

The `to` string may be the name of a config param (who's value is one or more email addresses),
or a string with one or more email addresses. Using a config param name allows for customizing the
`to` addresses without having to edit the code.

What to send may be a `body` string, the text contents of `filename`, or the HTML-formatted contents
of `htmlfile`, in this order of precedent.  MIME multi-part is not supported.

DKIM signing is optionally supported.

Three attempts are made to send the message (see `EmailNTries`, below).


### Args
`subj` (str)
- Email subject text

`to` (str)
- To whom to send the message. `to` may be either an explicit string list of email addresses
(whitespace or comma separated) or a config param name in the [SMTP] section (also listing one
or more whitespace or comma separated email addresses).  If the `to` arg does not
contain an '@' it is assumed to be a config param.

`body` (str, default None)
- A string message to be sent

`filename` (str, default None)
- A str or Path to the file to be sent, relative to the `core.tool.cache_dir`, or an absolute path.

`htmlfile` (str, default None)
- A str or Path to the html formatted file to be sent, relative to the `core.tool.cache_dir`, or an absolute path.

`log` (bool, default False)
- If True, logs that the message was sent at the WARNING level. If False, logs 
at the DEBUG level. Useful for eliminating separate logging messages in the tool script code.
The `subj` field is part of the log message.

`smtp_config` (config_item class instance)
- config_item class instance containing the [SMTP] section and related params


### config dictionary params in the [SMTP] section
`EmailFrom`
- An email address, such as `me@myserver.com`

`EmailServer`
- The SMTP server name, such as `mail.myserver.com`

`EmailServerPort`
- The SMTP server port (one of `P25`, `P465`, `P587`, or `P587TLS`)

`EmailUser`
- Username for `EmailServer` login, if required by the server

`EmailPass`
- Password for `EmailServer` login, if required by the server

`DontEmail` (default False)
- If True, messages are not sent. Useful for debug. Also blocks `snd_notif()` messages.

`EmailVerbose` (default False)
- If True, detailed transactions with the SMTP server are sent to stdout. Useful for debug.

`EmailNTries` (type int, default 3)
- Number of tries to send email before aborting

`EmailRetryWait` (seconds, type int, float, or timevalue, default 2s)
- Number of seconds to wait between retry attempts

`EmailServerTimeout` (seconds, type int, float, or timevalue, default 2s)
- Server connection timeout

`EmailDKIMDomain` (required if using DKIM email signing)
- The domain of the public-facing SMTP server, eg `mydomain.com`
- Defining `EmailDKIMDomain` enables DKIM signing, and also requires `EmailDKIMPem` and `EmailDKIMSelector`

`EmailDKIMPem` (required if using DKIM email signing)
- Full path to the private key file of the public-facing SMTP server at the `EmailDomain`, eg `/home/me/creds_mydomain.com.pem`
- Make sure this file is readable only to the user
- You may be able to obtain this key in cPanel for your shared-hosting service

`EmailDKIMSelector` (required if using DKIM email signing)
- The DKIM selector string, eg 'default'


### Returns
- None
- Raises SndEmailError on error


### Behaviors and rules
- One of `body`, `filename`, or `htmlfile` must be specified. Looked for in this order, and the first 
found is used.
- EmailServerPort must be one of the following:
  - P25:  SMTP to port 25 without any encryption
  - P465: SMTP_SSL to port 465
  - P587: SMTP to port 587 without any encryption
  - P587TLS:  SMTP to port 587 and with TLS encryption
- It is recommended (not required) that the email server params be placed in a user-read-only
file in the user's home directory, such as `~/creds_SMTP`, and imported by the main config file.
Some email servers require that the `EmailFrom` address be of the same domain as the server, 
so it may be practical to bundle `EmailFrom` with the server specifics.  Place all of these in 
`~/creds_SMTP`:
  - `EmailFrom`, `EmailServer`, `EmailServerPort`, `EmailUser`, and `EmailPass`
  - If DKIM signing is used, also include `EmailDKIMDomain`, `EmailDKIMPem`, and `EmailDKIMSelector`
- `snd_email()` does not support multi-part MIME (an html send wont have a plain text part).
- Checking the validity of email addresses is very basic... an email address must contain an '@'.
    