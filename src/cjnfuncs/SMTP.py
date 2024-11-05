#!/usr/bin/env python3
"""cjnfuncs.SMTP - Send text message notifications and emails
"""

#==========================================================
#
#  Chris Nelson, 2018-2024
#
#==========================================================

import time
import sys
import importlib
import re
import smtplib
from email.mime.text import MIMEText
from email.utils import formatdate
from pathlib import Path
import dkim

from .core      import logging, SndEmailError
from .mungePath import mungePath, check_path_exists
from .timevalue import timevalue
import cjnfuncs.core as core

# Configs / Constants
SND_EMAIL_NTRIES =      3           # Number of tries to send email before aborting
RETRY_WAIT =            '2s'        # seconds between retries
SERVER_TIMEOUT =        '2s'        # server connection timeout

COUNTRY_CODE =          1           # US/Canada
PHONE_NUM_LENGTH =      10          # US/Canada


#=====================================================================================
#=====================================================================================
#  s n d _ n o t i f
#=====================================================================================
#=====================================================================================

def snd_notif(subj='Notification message', msg='', urls_list=[], to='NotifList', log=False, smtp_config=None):
    """
## snd_notif (subj='Notification message', msg='', urls_list=[], to='NotifList', log=False, smtp_config=None) - Send a text message using info from the config file

Intended for use the mobile provider's (carrier's) email-to-SMS gateway email address, eg, 
`5405551212@vzwtxt.com` for Verizon, but any email address will work.

The `to` string may be the name of a config param (who's value is one or more email addresses, default 
"NotifList"), or a string with one or more email addresses. Using a config param name allows for customizing the
`to` addresses without having to edit the code.

The message to send is passed in the `msg` parameter as a text string.
Three attempts are made to send the message.

    
### Parameters
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
or more whitespace or comma separated email addresses).  If the `to` parameter does not
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
default `to` parameter value.

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
- NoneType
- Raises `SndEmailError` on error


### Behaviors and rules
- `snd_notif()` uses `snd_email()` to send the message. See `snd_email()` for related setup.
    """

    if smtp_config.getcfg('DontNotif', fallback=False, section='SMTP'):
        if log:
            logging.warning (f"Notification NOT sent <{subj}> <{msg}>")
        else:
            logging.debug (f"Notification NOT sent <{subj}> <{msg}>")
        return

    msg_handler = smtp_config.getcfg('Msg_Handler', fallback=None, section='SMTP')

    if msg_handler:
        # Import the messaging service handler
        if msg_handler.startswith('/'):                 # Absolute path case
            if not check_path_exists(msg_handler):
                raise FileNotFoundError (f"Can't find SMS/MMS message handler <{msg_handler}>")
            if msg_handler.endswith('.py'):
                msg_handler = msg_handler[:-3]
            xx = mungePath(msg_handler)
            xx_parent = str(xx.parent)
            if xx_parent not in sys.path:
                sys.path.append(xx_parent)
            try:
                logging.info (xx)
                sender_plugin = __import__(xx.name)
            except Exception as e:
                raise ImportError (f"Can't import SMS/MMS message handler <{msg_handler}>\n  {e}")
            logging.debug (f"Imported message sender plugin <{msg_handler}>, version <{sender_plugin.__version__}>")
        else:                                           # package.module case
            try:
                sender_plugin = importlib.import_module(msg_handler)
            except Exception as e:
                raise ImportError (f"Can't import SMS/MMS message handler <{msg_handler}>\n  {e}")
            logging.debug (f"Imported message sender plugin <{sender_plugin.__name__}>, version <{sender_plugin.__version__}>")

        package = {'subj': subj,
                   'msg':  msg,
                   'urls': urls_list,
                   'to':   list_to(to, 'numbers', subj=subj, smtp_config=smtp_config) }

        sender_plugin.sender(package, smtp_config)

    else:
        snd_email (subj=subj, body=msg, to=to, smtp_config=smtp_config)


    if log:
        logging.warning (f"Notification sent <{subj}> <{msg}>")
    else:
        logging.debug (f"Notification sent <{subj}> <{msg}>")


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
of `htmlfile`, in this order of precedent.  MIME multi-part is not supported.

DKIM signing is optionally supported.

Three attempts are made to send the message (see `EmailNTries`, below).


### Parameters
`subj` (str)
- Email subject text

`to` (str)
- To whom to send the message. `to` may be either an explicit string list of email addresses
(whitespace or comma separated) or a config param name in the [SMTP] section (also listing one
or more whitespace or comma separated email addresses).  If the `to` parameter does not
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
  - If DKIM signing is used, also include `EmailDKIMDomain`, `EmailDKIMPem`, and `EmailDKIMSelector`
- `snd_email()` does not support multi-part MIME (an html send wont have a plain text part).
- Checking the validity of email addresses is very basic... an email address must contain an '@'.
    """

    if smtp_config is None:
        raise SndEmailError ("smtp_section required for SMTP params")

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
            raise SndEmailError (f"snd_email - Message subject <{subj}>:  Failed to load <{xx.full_path}>.\n  {e}") from None

    elif htmlfile:
        xx = mungePath(htmlfile, core.tool.cache_dir)
        try:
            msg_type = "html"
            with Path.open(xx.full_path) as ifile:
                m_text = ifile.read()
        except Exception as e:
            raise SndEmailError (f"snd_email - Message subject <{subj}>:  Failed to load <{xx.full_path}>.\n  {e}") from None

    else:
        raise SndEmailError (f"snd_email - Message subject <{subj}>:  No body, filename, or htmlfile specified.")
    m_text += f"\n(sent {time.asctime(time.localtime())})"

    # Deal with 'to'
    To = list_to(to, 'emails', subj, smtp_config=smtp_config)

    # Gather, check remaining config params
    ntries =            smtp_config.getcfg('EmailNTries', SND_EMAIL_NTRIES, types=int, section='SMTP')
    retry_wait =        timevalue(smtp_config.getcfg('EmailRetryWait', RETRY_WAIT, types=[int, float, str], section='SMTP')).seconds
    server_timeout =    timevalue(smtp_config.getcfg('EmailServerTimeout', SERVER_TIMEOUT, types=[int, float, str], section='SMTP')).seconds
    email_from =        smtp_config.getcfg('EmailFrom', types=str, section='SMTP')
    cfg_server =        smtp_config.getcfg('EmailServer', types=str, section='SMTP')
    cfg_port =          smtp_config.getcfg('EmailServerPort', types=str, section='SMTP').lower()
    if cfg_port not in ['p25', 'p465', 'p587', 'p587tls']:
        raise SndEmailError (f"snd_email - Config EmailServerPort <{cfg_port}> is invalid")

    email_user =        str(smtp_config.getcfg('EmailUser', None, types=[str, int, float], section='SMTP')) # username may be numeric - optional
    if email_user:
        email_pass =    str(smtp_config.getcfg('EmailPass', types=[str, int, float], section='SMTP'))      # password may be numeric - required if EmailUser provided

    dkim_domain =       smtp_config.getcfg('EmailDKIMDomain', None, types=str, section='SMTP')
    if dkim_domain:
        dkim_pem =      smtp_config.getcfg('EmailDKIMPem', None, types=str, section='SMTP')
        if not dkim_pem:
            raise SndEmailError (f"snd_email - Config <EmailDKIMPem> is required for SMTP DKIM signing")
        dkim_selector = smtp_config.getcfg('EmailDKIMSelector', None, types=str, section='SMTP')
        if not dkim_selector:
            raise SndEmailError (f"snd_email - Config <EmailDKIMSelector> is required for SMTP DKIM signing")

    # Send the message, with retries
    for trynum in range(ntries):
        try:
            msg = MIMEText(m_text, msg_type)
            msg['Subject'] = subj
            msg['From']    = email_from
            msg['To']      = ", ".join(To)
            msg["Date"]    = formatdate(localtime=True)

            # logging.debug (msg)

            if smtp_config.getcfg('DontEmail', fallback=False, types=bool, section='SMTP'):
                if log:
                    logging.warning (f"Email NOT sent <{subj}>")
                else:
                    logging.debug (f"Email NOT sent <{subj}>")
                return

            # Add DKIM signature if EmailDKIMDomain is specified
            if dkim_domain:
                privateKey = Path(dkim_pem).read_text()
                sig = dkim.sign(message=msg.as_bytes(),
                                selector=   bytes(dkim_selector, 'UTF8'),
                                domain=     bytes(dkim_domain, 'UTF8'),
                                privkey=    bytes(privateKey, 'UTF8'),
                                include_headers= ['from', 'to', 'subject', 'date'])
                sig = sig.decode()
                msg['DKIM-Signature'] = sig[len("DKIM-Signature: "):]

            logging.debug (f"Initialize the SMTP server connection for port <{cfg_port}>")
            if cfg_port == "p25":
                server = smtplib.SMTP(cfg_server, 25, timeout=server_timeout)
            elif cfg_port == "p465":
                server = smtplib.SMTP_SSL(cfg_server, 465, timeout=server_timeout)
            else: # cfg_port == "p587" or "p587tls"
                server = smtplib.SMTP(cfg_server, 587, timeout=server_timeout)

            if smtp_config.getcfg("EmailVerbose", False, types=[bool], section='SMTP'):
                logging.debug ("Set SMTP connection debuglevel(1)")
                server.set_debuglevel(1)

            if cfg_port == "p587tls":
                logging.debug ("Start TLS")
                server.starttls()

            # if email_user:
            if cfg_port.startswith('p587'):
                logging.debug (f"Logging into SMTP server")
                server.login (email_user, email_pass)

            logging.debug (f"Sending message <{subj}>")
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
                logging.debug(f"Email send try {trynum} failed.  Retry in <{retry_wait} sec>:\n  <{e}>")
                time.sleep(retry_wait)
            continue

    raise SndEmailError (f"snd_email:  Send failed for <{subj}>:\n  <{last_error}>")


#=====================================================================================
#=====================================================================================
#  l i s t _ t o
#=====================================================================================
#=====================================================================================

def list_to(raw_in, get_type, subj, smtp_config):
    """
### list_to(raw_in, get_type, subj, smtp_config) - Build list of phone numbers or email addresses from raw_in

`list_to` handles several translations, controlled by `get_type` ('numbers' or 'emails'), including dereferencing through
config param, extracting and constructing a proper phone number list for messaging services (eg, Twilio), and constructing an 
email address list.

### Parameters
`raw_in` (str or int (in the case of a single phone number))
- A string list of phone numbers or email addresses, separated by either whitespace or ','
- If the value is the name of a param in the smtp_config [SMTP] section then that param's value is used, else `raw_in` is directly parsed
- Phone numbers may optionally include '+<country_code>', eg +14325551212

`get_type` (str)
- 'numbers' - a list of 1 or more phone numbers will be returned
  - '+<country_code>', eg '+1' is prepended to each number, if not provided
  - If the `raw_in` is one or more email-to-SMS gateway addresses (eg, 4805551212@vzwpix.com), then the local-part (the part before '@') is extracted as a phone number.
  This feature enables a config parameter containing a list of carrier email-to-SMS gateway addresses to be directly used with a SMS/MMS messaging service such as Twilio.
- 'emails' - a list of 1 or more email addresses will be returned
  - Address validity checking is minimal:  Email addresses must contain an '@'.

`subj` (str)
- The notification or email subject field - used only for raised errors to aid debug tracing

`smtp_config` (config_item class instance)
- config_item class instance containing the [SMTP] section and related params


### config dictionary params in the [SMTP] section
`country_code` (int or str, default 1 (US/Canada), required only if `get_type='numbers'`)
- Number without a preceding '+', eg '1' for US/Canada phone numbers
- If `get_type='numbers'` then each phone number is prepended with `+` plus `country_code` (eg, '+1'), but only if the number does not already have a country code.
- If a `raw_in` phone number has a different country code, it is retained.

`number_length` (int, default 10 (US/Canada), required only if `get_type= 'numbers'`)
- The number of digits in a valid phone number (not including the country code) for the given `country_code`, eg 10 for US/Canada phone numbers

### Returns
- Either a list of phone numbers or a list of email addresses, eg:
  - ['+14325551212']
  - ['+14325551212', '+14802345678']
  - ['4325551212@txt.att.net', '4802345678@vxwpix.com', 'myemail@tmomail.net']
- Raises SndEmailError on any errors
    """

    xx = smtp_config.getcfg(raw_in, fallback=None, section='SMTP')
    if xx:              # raw_in is a config-defined param (of 1 or more phone numbers)
        raw_in = xx

    items =     re.split(r'[,\s]+', str(raw_in))
    cc =        None    # Force load once per call
    to_list =   []

    for item in items:
        if get_type == 'numbers':
            if not cc:
                cc =        '+' + str(smtp_config.getcfg('country_code', COUNTRY_CODE, section='SMTP'))     # '+1'
                num_len =   smtp_config.getcfg('number_length', PHONE_NUM_LENGTH, section='SMTP')           # 10
            if '@' in item:
                num_part = item.split('@')[0]
            else:
                num_part = item

            if num_part.startswith(cc):                                 # Strip optional default country code prefix
                num_part = num_part.replace(cc,'')

            if num_part.startswith('+')  and  num_part[1:].isdigit():   # Non-default country code
                to_list.append(num_part)
            elif num_part.isdigit()  and  len(num_part) == num_len:     # No country code prefix remaining
                to_list.append(cc + num_part)
            else:
                raise SndEmailError (f"Message subject <{subj}>:  <{num_part}> is not a valid phone number")

        elif get_type == 'emails':
            if '@' not in item:
                raise SndEmailError (f"Message subject <{subj}>:  <{item}> is not a valid email address")
            to_list.append(item)
        
        else:
            raise SndEmailError (f"Message subject <{subj}>:  <{get_type}> is not a valid get_type for list_to()")

    return (to_list)
