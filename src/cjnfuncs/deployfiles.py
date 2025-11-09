#!/usr/bin/env python3
"""cjnfuncs.deployfiles - Push tool-specific files to their proper locations
"""

#==========================================================
#
#  Chris Nelson, 2018-2025
#
#==========================================================

from pathlib import Path
import shutil
import __main__

from .core import logging
from .mungePath import mungePath
import cjnfuncs.core as core

from importlib_resources import files as ir_files

# Logging events within this module are at the INFO level.  With this module's child logger set to
# a minimum of WARNING level by default, then logging from this module is effectively disabled.  To enable
# logging from this module add this within your tool script code:
#       logging.getLogger('cjnfuncs.deployfiles').setLevel(logging.INFO)
deployfiles_logger = logging.getLogger('cjnfuncs.deployfiles')
deployfiles_logger.setLevel(logging.WARNING)


#=====================================================================================
#=====================================================================================
#  d e p l o y _ f i l e s
#=====================================================================================
#=====================================================================================

def deploy_files(files_list, overwrite=False, missing_ok=False):
    """
## deploy_files (files_list, overwrite=False, missing_ok=False) - Install initial tool script files in user or site space

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
    - No wildcard support
    - `source = ''` will create an empty `target_dir`, if not already existing.
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
    """

    default_file_stat = 0o644
    default_dir_stat  = 0o755

    mapping = [
        ["USER_CONFIG_DIR", core.tool.user_config_dir],
        ["USER_DATA_DIR",   core.tool.user_data_dir],
        ["USER_STATE_DIR",  core.tool.user_state_dir],
        ["USER_CACHE_DIR",  core.tool.user_cache_dir],
        ["SITE_CONFIG_DIR", core.tool.site_config_dir],
        ["SITE_DATA_DIR",   core.tool.site_data_dir],
        ["CONFIG_DIR",      core.tool.config_dir],
        ["DATA_DIR",        core.tool.data_dir],
        ["STATE_DIR",       core.tool.state_dir],
        ["CACHE_DIR     ",  core.tool.cache_dir],
        ]

    def resolve_target(_targ, mkdir=False):
        """Do any CONFIG/DATA replacements.  Return a pathlib full path.
        """
        base_path = ""
        _targ = str(_targ)              # Accept str and pathlib
        for remap in mapping:
            if remap[0] in _targ:
                _targ = _targ.replace(remap[0], "")
                if len(_targ) > 0:
                    _targ = _targ[1:]   # Drops leading '/' after remap removed.
                base_path = remap[1]
                break
        return mungePath(_targ, base_path, mkdir=mkdir).full_path


    def copytree(src_dir, dst_dir, overwrite, file_stat, dir_stat):
        """ Recursively deploy the contents of src_dir to dst_dir
        dst_dir is created by the level above, before calling copytree
        """

        for item in list(src_dir.iterdir()):
            out_item = dst_dir / item.name

            if item.is_dir():
                didnt_exist = False
                if not out_item.exists():
                    didnt_exist = True
                    out_item.mkdir(parents=True)
                    deployfiles_logger.info (f"Created   {out_item}")
                if didnt_exist or overwrite:
                    out_item.chmod(dir_stat)
                copytree(item, out_item, overwrite=overwrite, file_stat=file_stat, dir_stat=dir_stat)

            else:   # is_file
                if not out_item.exists()  or  overwrite:
                    shutil.copy2(item, out_item)
                    if file_stat:
                        out_item.chmod(file_stat)
                    deployfiles_logger.info (f"Deployed  {out_item}")
                else:
                    deployfiles_logger.info (f"File <{out_item}> already exists.  Skipped.")


    if core.tool.main_module.__name__ == "__main__":    # Caller is a tool script file, not an installed module
        my_resources = mungePath(__main__.__file__).parent / "deployment_files"
        # print (f"Script case:  <{my_resources}>")
    else:                                               # Caller is an installed module
        my_resources = ir_files(core.tool.main_module).joinpath("deployment_files")
        # print (f"Module case:  <{my_resources}>")


    # ***** Start of iteration thru dictionaries *****
    for item in files_list:
        file_stat=  item.get("file_stat", default_file_stat)
        dir_stat=   item.get("dir_stat",  default_dir_stat)
        source = item["source"]
        if source != '':
            source =    Path(my_resources.joinpath(item["source"]))

        if source == ''  or  source.is_file():
            target_dir = resolve_target(item["target_dir"])
            didnt_exist = False
            if not target_dir.exists():         # TODO hang risk
                didnt_exist = True
                target_dir.mkdir(parents=True)
                deployfiles_logger.info (f"Created   {target_dir}")
            if didnt_exist or overwrite:
                target_dir.chmod(dir_stat)

            if source != '':
                outfile = target_dir / source.name
                if not outfile.exists()  or  overwrite:
                    shutil.copy2 (source, outfile)
                    outfile.chmod(file_stat)
                    deployfiles_logger.info (f"Deployed  {outfile}")
                else:
                    deployfiles_logger.info (f"File <{outfile}> already exists.  Skipped.")

        elif source.is_dir():
            # TODO ONLY WORKS if the source dir is on the file system (eg, not in a package .zip) ????

            target_dir = resolve_target(item["target_dir"]) / source.name

            didnt_exist = False
            if not target_dir.exists():
                didnt_exist = True
                target_dir.mkdir(parents=True)
                deployfiles_logger.info (f"Created   {target_dir}")
            if didnt_exist or overwrite:
                target_dir.chmod(dir_stat)

            copytree(source, target_dir, overwrite=overwrite, file_stat=file_stat, dir_stat=dir_stat)

        elif missing_ok:
            deployfiles_logger.info (f"Can't deploy source <{source.name}>.  Item not found and missing_ok=True.  Skipping.")
        
        else:
            raise FileNotFoundError (f"Can't deploy <{source.name}>.  Item not found.")
