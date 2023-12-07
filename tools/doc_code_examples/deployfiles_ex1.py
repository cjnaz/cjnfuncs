#!/usr/bin/env python3
# ***** deployfiles_ex1.py *****

import argparse
import sys
from cjnfuncs.core        import set_toolname
from cjnfuncs.deployfiles import deploy_files

CONFIG_FILE = "tool_config.cfg"


set_toolname("deployfiles_ex1")

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
