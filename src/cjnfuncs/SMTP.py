#!/usr/bin/env python3
"""cjnfuncs.SMTP - Send text message notifications and emails
"""

#==========================================================
#
#  Chris Nelson, 2018-2023
#
#==========================================================

import time
import smtplib
from email.mime.text import MIMEText
from pathlib import Path

from .core      import logging, SndEmailError
from .mungePath import mungePath
from .timevalue import timevalue
import cjnfuncs.core as core

# Configs / Constants
SND_EMAIL_NTRIES       = 3          # Number of tries to send email before aborting
SND_EMAIL_WAIT         = '5s'       # seconds between retries


#=====================================================================================
#=====================================================================================
#  s n d _ n o t i f
#=====================================================================================
#=====================================================================================

def snd_notif(subj='Notification message', msg='', to='NotifList', log=False, smtp_config=None):
    """
## snd_notif (subj='Notification message', msg=' ', to='NotifList', log=False, smtp_config=None) - Send a text message using info from the config file

Intended for use of your mobile provider's email-to-text bridge email address, eg, 
5405551212@vzwtxt.com for Verizon, but any email address will work.

The `to` string may be the name of a config param (who's value is one or more email addresses, default 
"NotifList"), or a string with one or more email addresses. Using a config param name allows for customizing the
`to` addresses without having to edit the code.

The message to send is passed in the `msg` parameter as a text string.
Three attempts are made to send the message.

    
### Parameters
`subj` (default 'Notification message')
- Text message subject field
- Some SMS/MMS apps display the subj field in bold, some in raw form, and some not at all.

`msg` (default ' ')
- Text message body

`to` (default 'NotifList')
- To whom to send the message. `to` may be either an explicit string list of email addresses
(whitespace or comma separated) or a config param name (also listing one
or more whitespace or comma separated email addresses).  If the `to` parameter does not
contain an '@' it is assumed to be a config param.
- Define `NotifList` in the config file to use the default `to` value.

`log` (default False)
- If True, logs that the message was sent at the WARNING level. If False, logs 
at the DEBUG level. Useful for eliminating separate logging messages in the tool script code.
The `subj` field is part of the log message.

`smtp_config` (required)
- config_item class instance containing the [SMTP] section and related params


### cfg dictionary params in the [SMTP] section
`NotifList` (optional)
- string list of email addresses (whitespace or comma separated).  
- Defining `NotifList` in the config is only required if any call to `snd_notif()` uses this
default `to` parameter value.

`DontNotif` (default False)
- If True, notification messages are not sent. Useful for debug. All email and notification
messages are also blocked if `DontEmail` is True.


### Returns
- NoneType
- Raises `SndEmailError` on error


### Behaviors and rules
- `snd_notif()` uses `snd_email()` to send the message. See `snd_email()` for related setup.
    """

    if smtp_config.getcfg('DontNotif', fallback=False, section='SMTP')  or  smtp_config.getcfg('DontEmail', fallback=False, section='SMTP'):
        if log:
            logging.warning (f"Notification NOT sent <{subj}> <{msg}>")
        else:
            logging.debug (f"Notification NOT sent <{subj}> <{msg}>")
        return

    try:
        snd_email (subj=subj, body=msg, to=to, smtp_config=smtp_config)
        if log:
            logging.warning (f"Notification sent <{subj}> <{msg}>")
        else:
            logging.debug (f"Notification sent <{subj}> <{msg}>")
    except:
        logging.warning (f"Notification send failed <{subj}> <{msg}>")
        raise


#=====================================================================================
#=====================================================================================
#  s n d _ e m a i l
#=====================================================================================
#=====================================================================================

def snd_email(subj, to, body=None, filename=None, htmlfile=None, log=False, smtp_config=None):
    """
## snd_email (subj, to, body=None, filename=None, htmlfile=None, log=False, smtp_config=None) - Send an email message using info from the config file

The `to` string may be the name of a config param (who's value is one or more email addresses),
or a string with one or more email addresses. Using a config param name allows for customizing the
`to` addresses without having to edit the code.

What to send may be a `body` string, the text contents of `filename`, or the HTML-formatted contents
of `htmlfile`, in this order of precedent.

Three attempts are made to send the message.


    
### Parameters
`subj`
- Email subject text

`to`
- To whom to send the message. `to` may be either an explicit string list of email addresses
(whitespace or comma separated) or a config param name in the [SMTP] section (also listing one
or more whitespace or comma separated email addresses).  If the `to` parameter does not
contain an '@' it is assumed to be a config param.

`body` (default None)
- A string message to be sent

`filename` (default None)
- A str or Path to the file to be sent, relative to the `core.tool.cache_dir`, or an absolute path.

`htmlfile` (default None)
- A str or Path to the html formatted file to be sent, relative to the `core.tool.cache_dir`, or an absolute path.

`log` (default False)
- If True, logs that the message was sent at the WARNING level. If False, logs 
at the DEBUG level. Useful for eliminating separate logging messages in the tool script code.
The `subj` field is part of the log message.

`smtp_config` (required)
- config_item class instance containing the [SMTP] section and related params


### cfg dictionary params in the [SMTP] section
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

`EmailRetryWait` (seconds, type int, float, or timevalue, default 5s)
- Number of seconds to wait between retry attempts


### Returns
- NoneType
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
- `snd_email()` does not support multi-part MIME (an html send wont have a plain text part).
- Checking the validity of email addresses is very basic... an email address must contain an '@'.
    """

    # Deal with what to send
    if body:
        msg_type = "plain"
        m_text = body

    elif filename:
        xx = mungePath(filename, core.tool.cache_dir)
        try:
            msg_type = "plain"
            with Path.open(xx.full_path) as ifile:
                m_text = ifile.read()
        except Exception as e:
            raise SndEmailError (f"snd_email - Message subject <{subj}>:  Failed to load <{xx.full_path}>.\n  {e}")

    elif htmlfile:
        xx = mungePath(htmlfile, core.tool.cache_dir)
        try:
            msg_type = "html"
            with Path.open(xx.full_path) as ifile:
                m_text = ifile.read()
        except Exception as e:
            raise SndEmailError (f"snd_email - Message subject <{subj}>:  Failed to load <{xx.full_path}>.\n  {e}")

    else:
        raise SndEmailError (f"snd_email - Message subject <{subj}>:  No body, filename, or htmlfile specified.")
    m_text += f"\n(sent {time.asctime(time.localtime())})"

    # Deal with 'to'
    def extract_email_addresses(addresses):
        """Return list of email addresses from comma or whitespace separated string 'addresses'.
        """
        if ',' in addresses:
            tmp = addresses.split(',')
            addrs = []
            for addr in tmp:
                addrs.append(addr.strip())
        else:
            addrs = addresses.split()
        return addrs

    if '@' in to:
        To = extract_email_addresses(to)
    else:
        To = extract_email_addresses(smtp_config.getcfg(to, "", section='SMTP'))
    if len(To) == 0:
        raise SndEmailError (f"snd_email - Message subject <{subj}>:  'to' list must not be empty.")
    for address in To:
        if '@' not in address:
            raise SndEmailError (f"snd_email - Message subject <{subj}>:  address in 'to' list is invalid: <{address}>.")

    # Gather, check remaining config params
    ntries     = smtp_config.getcfg('EmailNTries', SND_EMAIL_NTRIES, types=int, section='SMTP')
    retry_wait = timevalue(smtp_config.getcfg('EmailRetryWait', SND_EMAIL_WAIT, types=[int, float, str], section='SMTP')).seconds
    email_from = smtp_config.getcfg('EmailFrom', types=str, section='SMTP')
    cfg_server = smtp_config.getcfg('EmailServer', types=str, section='SMTP')
    cfg_port   = smtp_config.getcfg('EmailServerPort', types=str, section='SMTP').lower()
    if cfg_port not in ['p25', 'p465', 'p587', 'p587tls']:
        raise SndEmailError (f"snd_email - Config EmailServerPort <{smtp_config.getcfg('EmailServerPort', fallback='', section='SMTP')}> is invalid")
    email_user = str(smtp_config.getcfg('EmailUser', None, types=[str, int, float], section='SMTP'))    # username may be numeric
    if email_user:
        email_pass = str(smtp_config.getcfg('EmailPass', types=[str, int, float], section='SMTP'))      # password may be numeric

    if smtp_config.getcfg('DontEmail', fallback=False, types=bool, section='SMTP'):
        if log:
            logging.warning (f"Email NOT sent <{subj}>")
        else:
            logging.debug (f"Email NOT sent <{subj}>")
        return

    # Send the message, with retries
    for trynum in range(ntries):
        try:
            msg = MIMEText(m_text, msg_type)
            msg['Subject'] = subj
            msg['From'] = email_from
            msg['To'] = ", ".join(To)

            if cfg_port == "p25":
                server = smtplib.SMTP(cfg_server, 25)
            elif cfg_port == "p465":
                server = smtplib.SMTP_SSL(cfg_server, 465)
            elif cfg_port == "p587":
                server = smtplib.SMTP(cfg_server, 587)
            else: # cfg_port == "P587TLS":
                server = smtplib.SMTP(cfg_server, 587)
                server.starttls()

            if email_user:
                server.login (email_user, email_pass)
            if smtp_config.getcfg("EmailVerbose", False, types=[bool], section='SMTP'):
                server.set_debuglevel(1)
            server.sendmail(email_from, To, msg.as_string())
            server.quit()

            if log:
                logging.warning (f"Email sent <{subj}>")
            else:
                logging.debug (f"Email sent <{subj}>")
            return

        except Exception as e:
            last_error = e
            if trynum < ntries -1:
                logging.warning(f"Email send try {trynum} failed.  Retry in <{retry_wait} sec>:\n  <{e}>") # TODO change to debug or info
                time.sleep(retry_wait)
            continue

    raise SndEmailError (f"snd_email:  Send failed for <{subj}>:\n  <{last_error}>")