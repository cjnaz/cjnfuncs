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
from cjnfuncs.core        import set_toolname
from cjnfuncs.deployfiles import deploy_files

CONFIG_FILE = "tool_config.cfg"


tool = set_toolname("deployfiles_ex1")

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

Notables
- deploy_files() uses mungePath() for processing the target_dir path, so all of mungePath's features and rules apply, such as user and environment var expanstion, absolute and relative paths.
- Permissions may be set on deployed files and directories.  For example, `creds_SMTP` is set to user-read-write only.
- If you don't have write-access to the target directory then an error is printed and the script aborts with `sys.exit(1)`. Usage of deploy_files() is generally intended to be interactive, at tool setup time.
- By default, if the target file already exists then a warning in printed and that file deploy is skipped, leaving the existing file untouched. Setting `overwrite=True` does what you might expect.  One usage method is to simply delete a deployed file and run the tool script with `--setup-user` again to replace the file with a fresh copy.


### Where are the source files/dirs located?

In the case of a packaged tool, the source files are hosted in a `deployment_files` directory beneath the module's directory in the package:

    package-root
      | src
        | module_dir
           tool_script_module.py
           | deployment_files
              tool_config.cfg
              creds_SMTP
              template.service
              | test_dir

In the case of a standalone tool script (not a package), the source files are hosted in a `deployment_files` directory beneath the script's directory.


### target_dir path keyword substitutions

The `set_toolname()` call defines the environment paths for the tool.  These paths may be referenced in the target_dir field for files or directories to be deployed.  

Keyword | Maps to
-- | --
USER_CONFIG_DIR | core.tool.user_config_dir
USER_DATA_DIR   | core.tool.user_data_dir
USER_STATE_DIR  | core.tool.user_state_dir
USER_CACHE_DIR  | core.tool.user_cache_dir
SITE_CONFIG_DIR | core.tool.site_config_dir
SITE_DATA_DIR   | core.tool.site_data_dir

Target paths relative to the keywords may be specified, as well as filesystem absolute paths.
