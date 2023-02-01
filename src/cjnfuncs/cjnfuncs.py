#!/usr/bin/env python3
"""cjnfuncs - A collection of support functions for simplifying writing tool scripts.

Functions:
    setuplogging             - Set up default logger (use if not using loadconfig)
    mungePath                - Paths made easy and functional
    set_toolname             - Set up base paths for site or user installations
    config class
        loadconfig
        getcfg               - Config file handlers
    timevalue, retime        - Handling time values used in config files
    requestlock, releaselock - Cross-tool/process safety handshake
    snd_notif, snd_email     - Send text and email messages

    Import this module from the main script as follows:
        from cjnfuncs.cjnfuncs import ...
            loadconfig, getcfg, cfg, timevalue, retime, setuplogging, logging, funcs3_min_version_check, funcs3_version, snd_notif, snd_email, requestlock, releaselock, ConfigError, SndEmailError
Globals:
    cfg - Dictionary that contains the info read from the config file
"""

# VERSION = "2.0.2 X"

#==========================================================
#
#  Chris Nelson, 2018-2023
#
# V2.0  230122  Converted to installed package.  Renamed funcs3 to cjnfuncs.
# V1.1  220412  Added timevalue and retime
# V1.0  220203  V1.0 baseline
# ...
# V0.1  180520  New
#
# Changes pending
#   
#==========================================================

import sys
import time
import os.path
import io
import smtplib
from email.mime.text import MIMEText
import logging
import tempfile
import inspect
try:
    from importlib.resources import files as ir_files
except ImportError:
    from importlib_resources import files as ir_files
import re
from pathlib import Path, PurePath
import shutil
import __main__
import appdirs

# Configs / Constants
# FILE_LOGGING_FORMAT    = '{asctime}/{module}/{funcName}/{levelname}:  {message}'    # Classic format
FILE_LOGGING_FORMAT    = '{asctime} {module:>15}.{funcName:20} {levelname:>8}:  {message}'
CONSOLE_LOGGING_FORMAT = '{module:>15}.{funcName:20} - {levelname:>8}:  {message}'
DEFAULT_LOGGING_LEVEL  = logging.WARNING
MAIN_MODULE_STEM       = Path(__main__.__file__).stem


# # from traceback import extract_stack
# # print(extract_stack()[0])
# # sys.exit()

# stack = inspect.stack()
# print (stack)
# parentframe = stack[-1] #[0]
# print (parentframe)
# module = inspect.getmodule(parentframe)
# print ("\n module.__name__:", module.__name__)


# if module.__name__ == "__main__":   # Caller is a script file, not an installed module
#     my_resources = mungePath(__main__.__file__).dir / "deployment_files"
# else:                               # Caller is an installed module
#     my_resources = ir_files(module) / "deployment_files" 


# Project globals
cfg = {}


#=====================================================================================
#=====================================================================================
#  Module exceptions
#=====================================================================================
#=====================================================================================
class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class ConfigError(Error):
    """Exceptions raised for config file function errors.
    Attributes:
        message -- error message including item in error
    Format:
        ConfigError:  <function> - <message>.
    """
    def __init__(self, message):
        self.message = message

class SndEmailError(Error):
    """Exceptions raised for snd_email and snd_notif errors.
    Attributes:
        message -- error message including item in error
    Format:
        SndEmailError:  <function> - <message>.
    """
    def __init__(self, message):
        self.message = message


#=====================================================================================
#=====================================================================================
#  Logging setup
#=====================================================================================
#=====================================================================================

def setuplogging(call_logfile_wins=False, call_logfile=None, config_logfile=None):
        # When running in interactive / non-service mode, call_logfile == None and 
        # call_logfile_wins ==True, which forces logging to the console, overriding
        # and LogFile in the config file.

    _lfp = "__console__" #None
    if call_logfile_wins == False  and  config_logfile:
        _lfp = mungePath(config_logfile, tool.log_dir_base)

    if call_logfile_wins == True   and  call_logfile:
        _lfp = mungePath(call_logfile, tool.log_dir_base)
        
    if _lfp != tool.log_full_path:
        logger = logging.getLogger()
        logger.handlers.clear()

        if _lfp == "__console__":
            try:
                log_format = logging.Formatter(__main__.CONSOLE_LOGGING_FORMAT, style='{')
            except:
                log_format = logging.Formatter(CONSOLE_LOGGING_FORMAT, style='{')
            handler = logging.StreamHandler(sys.stdout)                             
            handler.setLevel(logging.DEBUG) #loglevel)
            handler.setFormatter(log_format)
            logger.addHandler(handler)

            tool.log_dir = None
            tool.log_file = None
            tool.log_full_path = "__console__"

        else:
            mungePath(_lfp.parent, mkdir=True)  # Force make the target dir
            try:
                log_format = logging.Formatter(__main__.FILE_LOGGING_FORMAT, style='{')
            except:
                log_format = logging.Formatter(FILE_LOGGING_FORMAT, style='{')
            handler = logging.FileHandler(_lfp.full_path, "a") #, sys.stdout)                             
            handler.setLevel(logging.DEBUG) # loglevel)
            handler.setFormatter(log_format)
            logger.addHandler(handler)
        
            tool.log_dir = _lfp.parent
            tool.log_file = _lfp.name
            tool.log_full_path = _lfp.full_path



#=====================================================================================
#=====================================================================================
#  Base environment and path functions: set_toolname, mungePath, deploy_files
#=====================================================================================
#=====================================================================================

class set_toolname():
    """ Establish target directories for config and data storage per XDG spec (roughly) 
    using the appdirs module.

    Initial condition is no config file is known, but the directories to eventually look 
    for one are defined.
    TODO
    Logging defaults to the site_state_directory / toolname / toolname.log for root user.
    Logging defaults to the user_state_directory / toolname / toolname.log for non-root user.
    See the config_item class regarding selection of user or site dirs and redirecting the log_dir.
    """

    def __init__(self, tname):
        global tool             # handle used elsewhere in this module
        tool = self

        self.toolname  = tname
        self.user_config_dir    = Path(appdirs.user_config_dir(tname))
        self.user_data_dir      = Path(appdirs.user_data_dir(tname))
        self.site_config_dir    = Path(appdirs.site_config_dir(tname))  # /
        self.site_data_dir      = Path("/usr/share") / tname

        if self.site_config_dir.exists()  or  self.site_data_dir.exists():
            self.config_dir     = self.site_config_dir
            self.data_dir       = self.site_data_dir
            self.state_dir      = self.site_data_dir
            self.cache_dir      = self.site_data_dir
            self.log_dir_base   = self.site_data_dir
            self.env_defined= "site"
        else:
            self.config_dir     = self.user_config_dir
            self.data_dir       = self.user_data_dir
            self.state_dir      = self.user_data_dir    # Overriding Path(appdirs.user_state_dir (tname))
            self.cache_dir      = self.user_data_dir    # Overriding Path(appdirs.user_cache_dir (tname)) / tname
            self.log_dir_base   = self.user_data_dir
            self.env_defined= "user"

        self.log_file = self.log_dir = self.log_full_path = None


    def dump(self):
        stats = ""
        stats +=  f"\nStats for set_toolname <{self.toolname}>:\n"
        stats +=  f".toolname         :  {self.toolname}\n"
        stats +=  f".user_config_dir  :  {self.user_config_dir}\n"
        stats +=  f".user_data_dir    :  {self.user_data_dir}\n"
        stats +=  f".site_config_dir  :  {self.site_config_dir}\n"
        stats +=  f".site_data_dir    :  {self.site_data_dir}\n"
        stats +=  f".env_defined      :  {self.env_defined}\n"

        stats +=  f"Based on found user or site dirs:\n"
        stats +=  f".config_dir       :  {self.config_dir}\n"
        stats +=  f".data_dir         :  {self.data_dir}\n"
        stats +=  f".state_dir        :  {self.state_dir}\n"
        stats +=  f".cache_dir        :  {self.cache_dir}\n"
        stats +=  f".log_dir_base     :  {self.log_dir_base}\n"
        stats +=  f".log_dir          :  {self.log_dir}\n"
        stats +=  f".log_file         :  {self.log_file}\n"
        stats +=  f".log_full_path    :  {self.log_full_path}\n"
        return stats


class mungePath():
    def __init__(self, in_path="", base_path="", mkdir=False):
        """
        mungePath provides a clean interface for dealing with filesystem paths
            - Enables a base_path to be defined so that code need to manage building full paths
                If in_path is not absolute then base_path is prepended.  Absolute in_path overrides base_path.
            - User (~user) and environment vars ($HOME) supported
                Must be at beginning of in_path or base_path
            - Hides Path vs. PurePath methods/attributes, providing a consistent interface
                in_path and base_path accept str, Path, or PurePath
            - Symlinks are not resolved

        Attributes
            .full_path      Path        The full expanduser/expandvars path to a file or directory (may not exist)
            .parent         Path        The directory above the .full_path
            .name           str         Just the name.suffix of the .full_path
            .is_absolute    Boolean     True if the .full_path starts from the filesystem root (isn't a relative path) 
            .is_relative    Boolean     Not .is_absolute
            .exists         Boolean     True if the .full_path item (file or dir) actually exists
            .is_file        Boolean     True if the .full_path item exists and is a file
		    .is_dir         Boolean     True if the .full_path item exists and is a directory

        """
        
        self.in_path = str(in_path)
        self.base_path = str(base_path)

        PP_in_path = PurePath(os.path.expandvars(os.path.expanduser(str(in_path))))

        if not PP_in_path.is_absolute():
            _base_path = str(base_path)
            if _base_path.startswith("."):
                _base_path = Path.cwd() / _base_path
            _base_path = PurePath(os.path.expandvars(os.path.expanduser(str(_base_path))))
            PP_in_path = _base_path / PP_in_path

        if mkdir:
            try:
                Path(PP_in_path).mkdir(parents=True, exist_ok=True)
            except Exception as e:
                raise FileExistsError (e)

        self.parent = Path(PP_in_path.parent)
        self.full_path = Path(PP_in_path)

        self.name = self.full_path.name
        self.exists =  self.full_path.exists()
        self.is_absolute = self.full_path.is_absolute()
        self.is_relative = not self.is_absolute
        self.is_dir =  self.full_path.is_dir()
        self.is_file = self.full_path.is_file()


    def dump(self):
        stats = ""
        stats +=  f"{'full_path'}    :  {self.full_path}\n"
        stats +=  f"{'parent'}       :  {self.parent}\n"
        # stats +=  f"{'dir'}          :  {self.dir}\n"
        stats +=  f"{'name'}         :  {self.name}\n"
        stats +=  f"{'is_absolute'}  :  {self.is_absolute}\n"
        stats +=  f"{'is_relative'}  :  {self.is_relative}\n"
        stats +=  f"{'exists'}       :  {self.exists}\n"
        stats +=  f"{'is_dir'}       :  {self.is_dir}\n"
        stats +=  f"{'is_file'}      :  {self.is_file}\n"
        return stats


def deploy_files(files_list, overwrite=False, missing_ok= False):
    """
    Install setup directories and files from the module to the user/site config and data directories.
    Distribution files and directory trees are hosted in package_root/src/module_name/deployment_files/.
	
    deploy_files() accepts a list of directories, eg:
        deploy_files( [
            { "source": "creds_test", "target_dir": "USER_CONFIG_DIR/example", "file_stat": 0o600, "dir_stat": 0o707},
            { "source": "test_dir",   "target_dir": "USER_DATA_DIR",           "file_stat": 0o633, "dir_stat": 0o770},
            ...
            ], overwrite=True )
    
    The first example will push the package_root/src/module_name/deployment_files/creds_test file to ~/.config/<toolname>/example/creds_test.
    <toolname> is set by the set_toolname() call, 'mytool' in this example.
    The directories ~/.config/mytool/ and ~/.config/mytool/example will have permissions 0o707 and files will have permission 0o600.
    Directory and file owner:group settings will be user:user, or root:root if called under sudo.

    The second example pushes a directory (with possible subdirectories) to ~/.local/share/mytool/.  The target_dir may specify a 
    subdirectory, such as "target_dir": "USER_DATA_DIR/mydirs"

    "source" is either an individual file or directory tree within and relative to module_name/deployment_files/.  No wildcard support.

    "target_dir" is expanded for user and environment vars, and supports these substitutions (per set_toolname()):
		USER_CONFIG_DIR, SITE_CONFIG_DIR
        USER_DATA_DIR, SITE_DATA_DIR
		Also absolute paths
        TODO - dir permissions only set at target_dir level and below.  Not set on parent dirs that were created.
            Be careful setting the dir_stat on the config and data root dir

    If overwrite == False (default) then only missing files will be copied.  If overwrite == True then all files will be overwritten 
    if they exist - data may be lost!

    If missing_ok == True then a missing file or directory to copy is tolerated (non-fatal).  This feature is used for testing.

    If deployment fails then execution aborts.  This functions is intended for interactive use.
    """

    global tool

    mapping = [
        ["USER_CONFIG_DIR", tool.user_config_dir],
        ["USER_DATA_DIR",   tool.user_data_dir],
        ["SITE_CONFIG_DIR", tool.site_config_dir],
        ["SITE_DATA_DIR",   tool.site_data_dir],
        # ["DATA_DIR",        tool.data_dir],      No need to push files to these dirs, correct?
        # ["STATE_DIR",       tool.state_dir],
        # ["CACHE_DIR",       tool.cache_dir],
        ]

    def resolve_target(_targ, mkdir=False):
        """Do any CONFIG/DATA replacements.  Return a fully resolved mungePath.
        """
        base_path = ""
        for remap in mapping:
            if remap[0] in _targ:
                _targ = _targ.replace(remap[0], "")
                if len(_targ) > 0:
                    _targ = _targ[1:]   # TODO This is weak.  Drops leading '/' after remap removed.
                base_path = remap[1]
                break
        try:
            xx = mungePath(_targ, base_path, mkdir=mkdir)
            return xx
        except Exception as e:
            print (f"Can't make target directory.  Aborting.\n  {e}")
            sys.exit(1)
    
    def copytree(src, dst, file_stat=None, dir_stat=None):
        """ Adapted from link, plus permissions settings feature.  No needed support for symlinks and ignore.
        https://stackoverflow.com/questions/1868714/how-do-i-copy-an-entire-directory-of-files-into-an-existing-directory-using-pyth
        """
        for item in os.listdir(src):
            s = os.path.join(src, item)
            d = os.path.join(dst, item)
            if os.path.isdir(s):
                if not os.path.exists(d):
                    os.makedirs(d)
                    if dir_stat:
                        os.chmod(d, dir_stat)
                copytree(s, d, file_stat=file_stat, dir_stat=dir_stat)
            else:
                shutil.copy2(s, d)
                if file_stat:
                    os.chmod(d, file_stat)


    stack = inspect.stack()
    parentframe = stack[1][0]
    module = inspect.getmodule(parentframe)
    if module.__name__ == "__main__":   # Caller is a script file, not an installed module
        my_resources = mungePath(__main__.__file__).parent / "deployment_files"
    else:                               # Caller is an installed module
        my_resources = ir_files(module) / "deployment_files" 

    for item in files_list:
        source = mungePath(item["source"], my_resources)
        if source.is_file:
            target_dir = resolve_target(item["target_dir"], mkdir=True)
            if "dir_stat" in item:
                os.chmod(target_dir.full_path, item["dir_stat"])

            if not target_dir.is_dir:
                print (f"Can't deploy {source.name}.  Cannot access target_dir <{target_dir.parent}>.  Aborting.")
                sys.exit(1)

            if not mungePath(source.name, target_dir.full_path).exists  or  overwrite:
                try:
                    shutil.copy(source.full_path, target_dir.full_path)
                    if "file_stat" in item:
                        os.chmod(mungePath(source.name, target_dir.full_path).full_path, item["file_stat"])
                except Exception as e:
                    print (f"File copy of <{source.name}> to <{target_dir.full_path}> failed.  Aborting.\n  {e}")
                    sys.exit(1)
                print (f"Deployed  {source.name:20} to  {target_dir.full_path}")
            else:
                print (f"File <{source.name}> already exists at <{target_dir.full_path}>.  Skipped.")

        elif source.is_dir:
                if not resolve_target(item["target_dir"]).exists  or  overwrite:
                    target_dir = resolve_target(item["target_dir"], mkdir=True)
                    try:
                        if "dir_stat" in item:
                            os.chmod(target_dir.full_path, item["dir_stat"])
                        copytree(source.full_path, target_dir.full_path, file_stat=item.get("file_stat", None), dir_stat=item.get("dir_stat", None))
                    except Exception as e:
                        print (f"Failed copying tree <{source.name}> to <{target_dir.full_path}>.  target_dir can't already exist.  Aborting.\n  {e}")
                        sys.exit(1)
                    print (f"Deployed  {source.name:20} to  {target_dir.full_path}")
                else:
                    print (f"Directory <{target_dir.full_path}> already exists.  Copytree skipped.")
        elif missing_ok:
            print (f"Can't deploy {source.name}.  Item not found.  Skipping.")
        else:
            print (f"Can't deploy {source.name}.  Item not found.  Aborting.")
            sys.exit(1)
        


#=====================================================================================
#=====================================================================================
#  Config file functions loadconfig, getcfg, timevalue, retime
#=====================================================================================
#=====================================================================================

_current_loglevel = None
_current_logfile  = None


class config_item():
    def __init__(self, configname): #, top_level=True):
        global tool

        config = mungePath(configname, tool.config_dir)
        if config.is_file:
            self.config_file        = config.name
            self.config_dir         = config.parent
            self.config_full_path   = config.full_path
            self.config_timestamp   = 0
            if tool.env_defined == "user":
                tool.log_dir_base  = tool.config_dir
        else:
            _msg = f"Config file <{configname}> not found."
            raise ConfigError (_msg)


    def dump(self):
        stats = ""
        stats += f"\nStats for config file <{self.config_file}>:\n"
        stats += f".config_file        :  {self.config_file}\n"
        stats += f".config_dir         :  {self.config_dir}\n"
        stats += f".config_full_path   :  {self.config_full_path}\n"
        stats += f".config_timestamp   :  {self.config_timestamp}\n"
        stats += f"tool.log_base_dir   :  {tool.log_dir_base}\n"
        stats += f"tool.log_full_path  :  {tool.log_full_path}\n"
        return stats


    def loadconfig(self,
            ldcfg_ll         = DEFAULT_LOGGING_LEVEL,
            call_logfile        = None,
            call_logfile_wins   = False,
            flush_on_reload     = False,
            force_flush_reload  = False,
            isimport            = False):
        """Read config file into dictionary cfg, and set up logging.
        
        See README.md loadconfig documentation for important usage details.  Don't call setuplogging if using loadconfig.

        cfgfile
            Default is 'config.cfg' in the program directory.  Absolute path or relative path from
            the main program directory may be specified.
        ldcfg_ll
            Sets logging level during config file loading. Default is 30(WARNING).
        call_logfile
            Log file to open - optional
        call_logfile_wins
            call_logfile overrides any LogFile specified in the config file
        flush_on_reload
            If the config file will be reloaded (due to being changed) then clean out cfg first
        force_flush_reload
            Forces cfg to be cleaned out and the config file to be reloaded
        isimport
            Internally set True when handling imports.  Not used by top-level scripts.

        Returns True if cfg has been (re)loaded, and False if not reloaded, so that the
        caller can do processing only if the cfg is freshly loaded.

        A ConfigError is raised if there are file access or parsing issues.
        """

        global cfg
        global _current_loglevel
        global _current_logfile

        # this_config_has_LogFile = False Hello

        # Initial logging will go to the console if no call_logfile is specified on the initial loadconfig call.
        if _current_loglevel is None:
            setuplogging (call_logfile=call_logfile, call_logfile_wins=call_logfile_wins)
            _current_loglevel = ldcfg_ll
            _current_logfile  = call_logfile
        
        external_loglevel = logging.getLogger().level           # Save externally set log level for later restore
        # print (f"Incoming logging level: {external_loglevel}")

        if force_flush_reload:
            logging.getLogger().setLevel(ldcfg_ll)           # logging within loadconfig is always done at ldcfg_ll
            _current_loglevel = ldcfg_ll
            logging.debug("cfg dictionary flushed and forced reloaded (force_flush_reload)")
            cfg.clear()
            self.config_timestamp = 0

        config = self.config_full_path
        try:
            if not isimport:        # Top level config file
                current_timestamp = self.config_full_path.stat().st_mtime
                if self.config_timestamp == current_timestamp:
                    return False

                # Initial load call, or config file has changed.  Do (re)load.
                self.config_timestamp = current_timestamp
                logging.getLogger().setLevel(ldcfg_ll)   # Set logging level for remainder of loadconfig call
                _current_loglevel = ldcfg_ll

                if flush_on_reload:
                    cfg.clear()
                    logging.debug (f"cfg dictionary flushed and reloaded due to changed config file (flush_on_reload)")

            logging.info (f"Loading {config}")
            cfgline = re.compile(r"([^\s=:]+)[\s=:]+(.+)")
            with io.open(config, encoding='utf8') as ifile:
                for line in ifile:
                    if line.strip().lower().startswith("import"):           # Is an import line
                        line = line.split("#", maxsplit=1)[0].strip()
                        target = mungePath(line.split()[1], self.config_dir)
                        if target.is_file:
                            _xx = config_item(target.full_path) #, top_level=False)
                            _xx.loadconfig(ldcfg_ll, isimport=True)
                        else:
                            _msg = f"Could not find and import <{target.full_path}>"
                            raise ConfigError (_msg)
                    else:                                                   # Is a param/key line
                        _line = line.split("#", maxsplit=1)[0].strip()
                        if len(_line) > 0:
                            out = cfgline.match(_line)
                            if out:
                                key = out.group(1)
                                rol = out.group(2)              # rest of line
                                # if key == "LogFile":
                                #     this_config_has_LogFile = True
                                isint = False
                                try:
                                    cfg[key] = int(rol)         # add int to dict
                                    isint = True
                                except:
                                    pass
                                if not isint:
                                    if rol.lower() == "true":   # add bool to dict
                                        cfg[key] = True
                                    elif rol.lower() == "false":
                                        cfg[key] = False
                                    else:
                                        cfg[key] = rol          # add string to dict
                                logging.debug (f"Loaded {key} = <{cfg[key]}>  ({type(cfg[key])})")
                            else: 
                                line = line.replace('\n','')
                                logging.warning (f"loadconfig:  Error on line <{line}>.  Line skipped.")

        except Exception as e:
            _msg = f"Failed while attempting to open/process config file <{config}>.\n  {e}"
            raise ConfigError (_msg) from None


        # Operations only for finishing a top-level call
        if not isimport:
            setuplogging(config_logfile=getcfg("LogFile", None), call_logfile=call_logfile, call_logfile_wins=call_logfile_wins)

            if getcfg("DontEmail", False):
                logging.info ('DontEmail is set - Emails and Notifications will NOT be sent')
            elif getcfg("DontNotif", False):
                logging.info ('DontNotif is set - Notifications will NOT be sent')

            config_loglevel = getcfg("LogLevel", None)
            if config_loglevel is not None:
                if config_loglevel != _current_loglevel:
                    logging.info (f"Logging level set to config LogLevel <{config_loglevel}>")
                    logging.getLogger().setLevel(config_loglevel)       # Restore loglevel from that set by ldcfg_ll
                    _current_loglevel = config_loglevel

            else: # external_loglevel != _current_loglevel:
                logging.info (f"Logging level set to preexisting level <{external_loglevel}>")
                logging.getLogger().setLevel(external_loglevel)     # Restore loglevel from that set by ldcfg_ll
                _current_loglevel = external_loglevel

            # else:
            #     logging.info (f"Logging level changed to <{DEFAULT_LOGGING_LEVEL}>")
            #     logging.getLogger().setLevel(DEFAULT_LOGGING_LEVEL)     # Restore loglevel from that set by ldcfg_ll
            #     _current_loglevel = DEFAULT_LOGGING_LEVEL
                

        return True


def getcfg(param, default="_nodefault"):
    """Get a param from the cfg dictionary.

    Returns the value of param from the cfg dictionary.  Equivalent to just referencing cfg[]
    but with handling if the item does not exist.
    
    param
        String name of param/key to be fetched from cfg
    default
        if provided, is returned if the param doesn't exist in cfg

    Raises ConfigError if param does not exist in cfg and no default provided.
    """
    
    try:
        return cfg[param]
    except:
        if default != "_nodefault":
            return default
    _msg = f"getcfg - Config parameter <{param}> not in cfg and no default."
    raise ConfigError (_msg)


class timevalue():
    def __init__(self, original):
        """Convert short time value string/int/float in resolution seconds, minutes, hours, days,
        or weeks to seconds.
            EG:  20, 30s, 5m, 3D, 2w, 3.1415m.  
        Time unit suffix is case insensitive, and optional (defaults to seconds).

        Instance-specific vars:

        original
            The original passed-in value (type str)
        seconds
            Time value in seconds (type float or int)
        unit_char
            Unit character of the passed-in value ("s", "m", "h", "d", or "w")
        unit_str
            Unit string of the passed-in value ("secs", "mins", "hours", "days", or "weeks")
        
        Months (and longer) are not supported, since months start with 'm', as does minutes, and no practical use.

        Raises ValueError if given an unsupported time unit suffix.
        """
        self.original = str(original)

        if type(original) in [int, float]:              # Case int or float
            self.seconds =  float(original)
            self.unit_char = "s"
            self.unit_str =  "secs"
        else:
            try:
                self.seconds = float(original)          # Case str without units
                self.unit_char = "s"
                self.unit_str = "secs"
                return
            except:
                pass
            self.unit_char =  original[-1:].lower()     # Case str with units
            if self.unit_char == "s":
                self.seconds =  float(original[:-1])
                self.unit_str = "secs"
            elif self.unit_char == "m":
                self.seconds =  float(original[:-1]) * 60
                self.unit_str = "mins"
            elif self.unit_char == "h":
                self.seconds =  float(original[:-1]) * 60*60
                self.unit_str = "hours"
            elif self.unit_char == "d":
                self.seconds =  float(original[:-1]) * 60*60*24
                self.unit_str = "days"
            elif self.unit_char == "w":
                self.seconds =  float(original[:-1]) * 60*60*24*7
                self.unit_str = "weeks"
            else:
                raise ValueError(f"Illegal time units <{self.unit_char}> in time string <{original}>")


def retime(time_sec, unitC):
    """ Convert time value in seconds to unitC resolution, return type float

    time_sec
        Time value in resolution seconds, type int or float.
    unitC
        Target time resolution ("s", "m", "h", "d", or "w")
    
    Raises ValueError if not given an int or float seconds value or given an unsupported unitC time unit suffix.
    """
    if type(time_sec) in [int, float]:
        if unitC == "s":  return time_sec
        if unitC == "m":  return time_sec /60
        if unitC == "h":  return time_sec /60/60
        if unitC == "d":  return time_sec /60/60/24
        if unitC == "w":  return time_sec /60/60/24/7
        raise ValueError(f"Invalid unitC value <{unitC}> passed to retime()")
    else:
        raise ValueError(f"Invalid seconds value <{time_sec}> passed to retime().  Must be type int or float.")


#=====================================================================================
#=====================================================================================
#  Lock file management functions
#=====================================================================================
#=====================================================================================

def requestlock(caller, lockfile=MAIN_MODULE_STEM, timeout=5):
    """Lock file request.

    caller
        Info written to the lock file and displayed in any error messages
    lockfile  TODO relative to tempfile or abs.  lock filename defaults to the main module name
        Lock file name.  Various lock files may be used simultaneously
    timeout
        Default 5s

    Returns
        0:  Lock request successful
       -1:  Lock request failed.  Warning level log messages are generated.
    """
    lock_file = mungePath(lockfile, tempfile.gettempdir())

    fail_time = time.time() + timeout
    while True:
        if not lock_file.exists:
            try:
                mungePath(lock_file.parent, mkdir=True)     # Ensure directory path exists
                with lock_file.full_path.open('w') as ofile:
                    ofile.write(f"Locked by <{caller}> at {time.asctime(time.localtime())}.")
                    logging.debug (f"<{lock_file.full_path}> locked by <{caller}> at {time.asctime(time.localtime())}.")
                return 0
            except Exception as e:
                logging.warning(f"Unable to create lock file <{lock_file.full_path}>\n  {e}")
                return -1
        else:
            if time.time() > fail_time:
                break
        time.sleep(0.1)

    try:
        with lock_file.full_path.open() as ifile:
            lockedBy = ifile.read()
        logging.warning (f"Timed out waiting for lock file <{lock_file.full_path}> to be cleared.  {lockedBy}")
    except Exception as e:
        logging.warning (f"Timed out and unable to read existing lock file <{lock_file.full_path}>\n  {e}.")
    return -1


def releaselock(lockfile=MAIN_MODULE_STEM):
    """Lock file release.

    Any code can release a lock, even if that code didn't request the lock.
    Generally, only the requester should issue the releaselock.

    lockfile
        Lock file to remove/release

    Returns
        0:  Lock release successful (lock file deleted)
       -1:  Lock release failed.  Warning level log messages are generated.
    """
    lock_file = mungePath(lockfile, tempfile.gettempdir())
    if lock_file.exists:
        try:
            lock_file.full_path.unlink()
        except Exception as e:
            logging.warning (f"Unable to remove lock file <{lock_file.full_path}>\n  {e}.")
            return -1
        logging.debug(f"Lock file removed: <{lock_file.full_path}>")
        return 0
    else:
        logging.warning(f"Attempted to remove lock file <{lock_file.full_path}> but the file does not exist.")
        return -1


#=====================================================================================
#=====================================================================================
#  Notification and email functions
#=====================================================================================
#=====================================================================================

def snd_notif(subj='Notification message', msg='', to='NotifList', log=False):
    """Send a text message using the cfg NotifList.

    subj
        Subject text string
    msg
        Message text string
    to
        To whom to send the message.  'to' may be either an explicit string list of email addresses
        (whitespace or comma separated) or the name of a config file keyword (also listing one
        or more whitespace/comma separated email addresses).  If the 'to' parameter does not
        contain an '@' it is assumed to be a config keyword - default 'NotifList'.
    log
        If True, elevates log level from DEBUG to WARNING to force logging

    cfg NotifList is required in the config file (unless 'to' is always explicitly passed)
    cfg DontNotif and DontEmail are optional, and if == True no text message is sent. Useful for debug.

    Raises SndEmailError on call errors and sendmail errors
    """

    if getcfg('DontNotif', default=False)  or  getcfg('DontEmail', default=False):
        if log:
            logging.warning (f"Notification NOT sent <{subj}> <{msg}>")
        else:
            logging.debug (f"Notification NOT sent <{subj}> <{msg}>")
        return

    snd_email (subj=subj, body=msg, to=to)
    if log:
        logging.warning (f"Notification sent <{subj}> <{msg}>")
    else:
        logging.debug (f"Notification sent <{subj}> <{msg}>")


def snd_email(subj='', body='', filename='', htmlfile='', to='', log=False):
    """Send an email message using email account info from the config file.

    Either body, filename, or htmlfile must be passed.  Call with only one of body, filename, 
    or htmlfile, or results may be bogus.  snd_email does not support multi-part MIME (an 
    html send wont have a plain text part).

    subj
        Email subject text
    body
        A string message to be sent
    filename    TODO no basepath.  Caller must be absolute.  Error trap is not absolute?
        A string full path to the file to be sent.  Default path is the PROGDIR.
        Absolute and relative paths from PROGDIR accepted.
    htmlfile    TODO no basepath
        A string full path to an html formatted file to be sent.  Default path is the PROGDIR.
        Absolute and relative paths from PROGDIR accepted.
    to
        To whom to send the message.  'to' may be either an explicit string list of email addresses
        (whitespace or comma separated) or the name of a config file keyword (also listing one
        or more whitespace/comma separated email addresses).  If the 'to' parameter does not
        contain an '@' it is assumed to be a config keyword - no default.
    log
        If True, elevates log level from DEBUG to WARNING to force logging of the email subj

    cfg EmailFrom, EmailServer, and EmailServerPort are required in the config file.
        EmailServerPort must be one of the following:
            P25:  SMTP to port 25 without any encryption
            P465: SMTP_SSL to port 465
            P587: SMTP to port 587 without any encryption
            P587TLS:  SMTP to port 587 and with TLS encryption
    cfg EmailUser and EmailPass are optional in the config file.
        Needed if the server requires credentials.  Recommend that these params be in a secure file in 
        one's home dir and import the file via the config file.
    cfg DontEmail is optional, and if == True no email is sent.
        Also blocks snd_notifs.  Useful for debug.
    cfg EmailVerbose = True enables the emailer debug level.

    Raises SndEmailError on call errors and sendmail errors
    """

    # if getcfg('DontEmail', default=False):
    #     if log:
    #         logging.warning (f"Email NOT sent <{subj}>")
    #     else:
    #         logging.debug (f"Email NOT sent <{subj}>")
    #     return

    # Deal with what to send
    if body != '':
        msg_type = "plain"
        m_text = body
    elif os.path.exists(filename):
        msg_type = "plain"
        with io.open(filename, encoding='utf8') as ifile:
            m_text = ifile.read()
    elif os.path.exists(htmlfile):
        msg_type = "html"
        with io.open(htmlfile, encoding='utf8') as ifile:
            m_text = ifile.read()
    else:
        _msg = f"snd_email - Message subject <{subj}>:  No body and can't find filename <{filename}> or htmlfile <{htmlfile}>."
        raise SndEmailError (_msg)
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
        To = extract_email_addresses(getcfg(to, ""))
    if len(To) == 0:
        _msg = f"snd_email - Message subject <{subj}>:  'to' list must not be empty."
        raise SndEmailError (_msg)
    for address in To:
        if '@' not in address:
            _msg = f"snd_email - Message subject <{subj}>:  address in 'to' list is invalid: <{address}>."
            raise SndEmailError (_msg)

    # Send the message
    if getcfg('DontEmail', default=False):
        if log:
            logging.warning (f"Email NOT sent <{subj}>")
        else:
            logging.debug (f"Email NOT sent <{subj}>")
        return

    try:
        msg = MIMEText(m_text, msg_type)
        msg['Subject'] = subj
        msg['From'] = getcfg('EmailFrom')
        msg['To'] = ", ".join(To)

        cfg_server = getcfg('EmailServer')
        cfg_port   = getcfg('EmailServerPort')
        if cfg_port == "P25":
            server = smtplib.SMTP(cfg_server, 25)
        elif cfg_port == "P465":
            server = smtplib.SMTP_SSL(cfg_server, 465)
        elif cfg_port == "P587":
            server = smtplib.SMTP(cfg_server, 587)
        elif cfg_port == "P587TLS":
            server = smtplib.SMTP(cfg_server, 587)
            server.starttls()
        else:
            raise ConfigError (f"Config EmailServerPort <{cfg_port}> is invalid")

        if 'EmailUser' in cfg:
            server.login (getcfg('EmailUser'), getcfg('EmailPass'))
        if getcfg("EmailVerbose", False):
            server.set_debuglevel(1)
        server.sendmail(getcfg('EmailFrom'), To, msg.as_string())
        server.quit()

        if log:
            logging.warning (f"Email sent <{subj}>")
        else:
            logging.debug (f"Email sent <{subj}>")
    except Exception as e:
        _msg = f"snd_email:  Send failed for <{subj}>:\n  <{e}>"
        raise SndEmailError (_msg)

