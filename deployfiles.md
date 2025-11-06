# deployfiles - Push bundled setup files within a package to the proper user/system locations

Skip to [API documentation](#links)

Often to install a tool script or packaged module, installation-related files need to be placed in their proper homes on the filesystem. 
deploy_files() provides the mechanism to push files and directories from the tool distribution package to their proper locations.  deploy_files() works with both packaged tools (eg, installed using pip) or standalone tool scripts.


### Example
```
#!/usr/bin/env python3
# ***** deployfiles_ex1.py *****

import argparse
import sys
from cjnfuncs.core        import set_toolname, logging
from cjnfuncs.deployfiles import deploy_files

CONFIG_FILE = "tool_config.cfg"


set_toolname("deployfiles_ex1")
logging.getLogger('cjnfuncs.deployfiles').setLevel(logging.INFO)

parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('--setup-user', action='store_true',
                    help=f"Install starter files in user space.")
parser.add_argument('--setup-site', action='store_true',
                    help=f"Install starter files in system-wide space. Run with root prev.")
args = parser.parse_args()


# Deploy tool script setup template files
if args.setup_user:
    deploy_files([
        { "source": CONFIG_FILE,        "target_dir": "USER_CONFIG_DIR", "file_stat": 0o644, "dir_stat": 0o755},
        { "source": "creds_SMTP",       "target_dir": "USER_CONFIG_DIR", "file_stat": 0o600},
        { "source": "template.service", "target_dir": "USER_CONFIG_DIR", "file_stat": 0o644},
        { "source": "test_dir",         "target_dir": "USER_DATA_DIR/mydirs", "file_stat": 0o633, "dir_stat": 0o770},
        ]) #, overwrite=True)
    sys.exit()

if args.setup_site:
    deploy_files([
        { "source": CONFIG_FILE,        "target_dir": "SITE_CONFIG_DIR", "file_stat": 0o644, "dir_stat": 0o755},
        { "source": "creds_SMTP",       "target_dir": "SITE_CONFIG_DIR", "file_stat": 0o600},
        { "source": "template.service", "target_dir": "SITE_CONFIG_DIR", "file_stat": 0o644},
        { "source": "test_dir",         "target_dir": "SITE_DATA_DIR/mydirs", "file_stat": 0o633, "dir_stat": 0o770},
        ]) #, overwrite=True)
    sys.exit()
```
And when run:
```
$ ./deployfiles_ex1.py --setup-user
    deployfiles.deploy_files         -     INFO:  Created   /home/me/.config/deployfiles_ex1
    deployfiles.deploy_files         -     INFO:  Deployed  /home/me/.config/deployfiles_ex1/tool_config.cfg
    deployfiles.deploy_files         -     INFO:  Deployed  /home/me/.config/deployfiles_ex1/creds_SMTP
    deployfiles.deploy_files         -     INFO:  Deployed  /home/me/.config/deployfiles_ex1/template.service
    deployfiles.deploy_files         -     INFO:  Created   /home/me/.local/share/deployfiles_ex1/mydirs/test_dir
    deployfiles.copytree             -     INFO:  Deployed  /home/me/.local/share/deployfiles_ex1/mydirs/test_dir/x3
    deployfiles.copytree             -     INFO:  Deployed  /home/me/.local/share/deployfiles_ex1/mydirs/test_dir/x1
    deployfiles.copytree             -     INFO:  Created   /home/me/.local/share/deployfiles_ex1/mydirs/test_dir/subdir
    deployfiles.copytree             -     INFO:  Deployed  /home/me/.local/share/deployfiles_ex1/mydirs/test_dir/subdir/x4
    deployfiles.copytree             -     INFO:  Created   /home/me/.local/share/deployfiles_ex1/mydirs/test_dir/subdir/emptydir
    deployfiles.copytree             -     INFO:  Deployed  /home/me/.local/share/deployfiles_ex1/mydirs/test_dir/x2
```

Notables
- deploy_files() uses mungePath() for processing the target_dir path, so all of mungePath's features and rules apply, such as user and environment var expansion, absolute and relative paths.
- Permissions may be set on deployed files and directories.  For example, `creds_SMTP` is set to user-read-write only.
- Various exceptions may be raised, including PermissionError, FileNotFoundError, FileExistsError.  If untrapped then 
these will cause the tool script to exit.  If usage is interactive only then exception handling may be unnecessary.
- By default, if the target file already exists then a warning in printed and that file deploy is skipped, leaving the existing file untouched. Setting `overwrite=True` does what you might expect.  One usage method is to simply delete a deployed file and run the tool script with `--setup-user` again to replace the file with a fresh copy.


### Where are the source files/dirs located?

In the case of a packaged tool, the source files are hosted in a `deployment_files` directory beneath the `package_dir`:

    package-root
      | src
        | package_dir
           __init.py__
           tool_script_module1.py
           tool_script_module2.py
           | deployment_files
              tool_config.cfg
              creds_SMTP
              template.service
              | test_dir

In the case of a standalone tool script (not a package), the source files are hosted in a `deployment_files` directory beneath the script's directory.


### target_dir path keyword substitutions

The `set_toolname()` call defines the environment paths for the tool.  These paths may be referenced in the `target_dir` field for files or directories to be deployed. Target paths relative to the keywords may be specified, as well as filesystem absolute paths.

Keyword | Maps to
-- | --
USER_CONFIG_DIR | core.tool.user_config_dir
USER_DATA_DIR   | core.tool.user_data_dir
USER_STATE_DIR  | core.tool.user_state_dir
USER_CACHE_DIR  | core.tool.user_cache_dir
SITE_CONFIG_DIR | core.tool.site_config_dir
SITE_DATA_DIR   | core.tool.site_data_dir
CONFIG_DIR      | core.tool.config_dir **
DATA_DIR        | core.tool.data_dir **
STATE_DIR       | core.tool.state_dir **
CACHE_DIR       | core.tool.cache_dir **

** Note: These keywords are set to the user-mode or site-mode absolute paths by `set_toolname()`.  For example, `USER_CONFIG_DIR` maps to `core.tool.user_config_dir`, and `CONFIG_DIR` maps to `core.tool.config_dir`, and in user mode both of these variables contain the path `/home/<me>/.config/<toolname>/`. In site mode, `CONFIG_DIR` will map to the same path as `SITE_CONFIG_DIR`.

<br>

## Controlling logging from within deployfiles code

Logging within the deployfiles module uses the `cjnfuncs.deployfiles` named/child logger.  By default this logger is set to the `logging.WARNING` level, 
meaning that no logging messages are produced from within the deployfiles code.  For validation and debug purposes, logging from within deployfiles code 
can be enabled by setting the logging level for this module's logger from within the tool script code:

        logging.getLogger('cjnfuncs.deployfiles').setLevel(logging.INFO)

        # Or alternately, use the core module set_logging_level() function:
        set_logging_level (logging.INFO, 'cjnfuncs.deployfiles')


<a id="links"></a>
         
<br>

---

# Links to classes, methods, and functions

- [deploy_files](#deploy_files)



<br/>

<a id="deploy_files"></a>

---

# deploy_files (files_list, overwrite=False, missing_ok=False) - Install initial tool script files in user or site space

`deploy_files()` is used to install initial setup files (and directory trees) from the installed package (or tool script) 
to the user or site config and data directories. Suggested usage is with the CLI `--setup-user` or `--setup-site` switches.
Distribution files and directory trees are hosted in `<package_dir>/deployment_files/`.

`deploy_files()` accepts a list of dictionaries defining items to be pushed to user or site space.
Each dictionary defines
the `source` file or directory root to be pushed, the `target_dir` for where to push the source, and optionally
the file and directory permissions for the pushed items.  Ownership matches the running user.


### Args
`files_list` (list of dictionaries)
- A list of dictionaries, each specifying a `source` file or directory tree to be copied to a `target_dir`.
  - `source` - Either an individual file or directory tree within and relative to `<package_dir>/deployment_files/`.
    No wildcard support.
  - `target_dir` - A directory target for the pushed `source`.  It is expanded for user and environment vars, 
    and supports these substitutions (per `set_toolname()`):
    - USER_CONFIG_DIR, USER_DATA_DIR, USER_STATE_DIR, USER_CACHE_DIR
    - SITE_CONFIG_DIR, SITE_DATA_DIR
    - CONFIG_DIR, DATA_DIR, STATE_DIR, CACHE_DIR as determined by the existence of site directories (maybe only useful for testing)
    - Also absolute paths
  - `file_stat` - Permissions set on created files (default 0o644) - See Behaviors and rules, below.
  - `dir_stat` - Permissions set on created directories (default 0o755) - See Behaviors and rules, below.

`overwrite` (bool, default False)
- If `overwrite=False` (default) then only missing files/directories will be deployed, with `file_stat`/`dir_stat` applied.
- If `overwrite=True` then all files/directories will be (re)deployed (using the new `file_stat`/`dir_stat`),
potentially overwriting existing data.

`missing_ok` (bool, default False)
- If `missing_ok=True` then a missing `source` file or directory is tolerated (non-fatal).  This feature is used for testing.
- If `missing_ok=False` (default) and the `source` is missing then a FileNotFoundError exception is raised.  Any files deployed before
the exception will be left in place.


### Returns
- None
- Raises various exceptions on failure


### Behaviors and rules
- An empty directory may be deployed, eg: `{"source": "test_dir/emptydir",  "target_dir": "USER_CONFIG_DIR"}`
deploys the source directory named `emptydir` to `$HOME/.config/<toolname>/emptydir`.

- If the `source` points to an individual file, even if within a subdirectory of `deployment_files`,
that file, and not its nested path, will be deployed.
For example, `{"source": "test_dir/x1",  "target_dir": "USER_CONFIG_DIR/subdir"}` 
deploys just the file `x1` to `$HOME/.config/<toolname>/subdir/x1`. 
If you want to deploy a file and retain the source directory structure, then deploy the entire
source subdirectory, eg: `{"source": "test_dir",  "target_dir": "USER_CONFIG_DIR/subdir"}`, which
deploys the entire test_dir directory structure to `$HOME/.config/<toolname>/subdir/test_dir`.

- `dir_stat` is applied to the parent directory where a file is deployed.
When `source` points to a directory tree, `dir_stat` is also applied to
deployed subdirectories _but not the parent directory_ 
(the leaf dir of the `target_dir`). Higher-level created directories are assigned the user-default permissions
(typically 0o755 - umask).

- The permissions on a directory (the `dir_stat`) are set the first time a file
is deployed to that directory.
With `overwrite=False`, for subsequent file deployments to that directory the first `dir_stat` settings are 
retained (the new `dir_stat` setting is disregarded). 
With `overwrite=True`, an existing directory where a file is deployed will be updated 
to the new `dir_stat` value.

- Directory and file permissions on Windows do not support separate permissions for User, Group and Other, 
and Windows ACLs are not currently supported.
When setting permissions on deployed items on Windows, only the User permission is used even on a file share
hosted on Linux.  Eg, a file permission of 0x644 will deploy with permission 0x666 (only the first octet is used).
    