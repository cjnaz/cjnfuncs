#!/usr/bin/env python3
"""cjnfuncs.deployfiles - Push tool-specific files to their proper locations
"""

#==========================================================
#
#  Chris Nelson, 2018-2024
#
#==========================================================

# import sys
import os.path
from pathlib import PurePath
import shutil
import __main__

from cjnfuncs.core import logging
from .mungePath import mungePath, check_path_exists
import cjnfuncs.core as core

# if sys.version_info < (3, 9):
#     from importlib_resources import files as ir_files
# else:
      # Errors on Py3.9:  TypeError: <module ...> is not a package.  The module __spec__.submodule_search_locations is None
#     from importlib.resources import files as ir_files
from importlib_resources import files as ir_files


#=====================================================================================
#=====================================================================================
#  d e p l o y _ f i l e s
#=====================================================================================
#=====================================================================================

def deploy_files(files_list, overwrite=False, missing_ok=False):
    """
## deploy_files (files_list, overwrite=False, missing_ok=False) - Install initial tool script files in user or site space

`deploy_files()` is used to install initial setup files (and directory trees) from the module to the user 
or site config and data directories. Suggested usage is with the CLI `--setup-user` or `--setup-site` switches.
Distribution files and directory trees are hosted in `<module_root>/deployment_files/`.

`deploy_files()` accepts a list of dictionaries to be pushed to user or site space. 


### Parameters
`files_list` (list of dictionaries)
- A list of dictionaries, each specifying a `source` file or directory tree to be copied to a `target_dir`.
  - `source` - Either an individual file or directory tree within and relative to `<module_root>/deployment_files/`.
    No wildcard support.
  - `target_dir` - A directory target for the pushed `source`.  It is expanded for user and environment vars, 
    and supports these substitutions (per set_toolname()):
    - USER_CONFIG_DIR, USER_DATA_DIR, USER_STATE_DIR, USER_CACHE_DIR
    - SITE_CONFIG_DIR, SITE_DATA_DIR
    - Also absolute paths
  - `file_stat` - Permissions set on each created file (default 0o664)
  - `dir_stat` - Permissions set on each created directory (if not already existing, default 0o775)

`overwrite` (bool, default False)
- If overwrite=False (default) then only missing files will be copied.  If overwrite=True then all files will be overwritten 
if they exist - data may be lost!

`missing_ok` (bool, default False)
- If missing_ok=True then a missing source file or directory is tolerated (non-fatal).  This feature is used for testing.


### Returns
- NoneType
- Raises various exceptions on failure
    """

    mapping = [
        ["USER_CONFIG_DIR", core.tool.user_config_dir],
        ["USER_DATA_DIR",   core.tool.user_data_dir],
        ["USER_STATE_DIR",  core.tool.user_state_dir],
        ["USER_CACHE_DIR",  core.tool.user_cache_dir],
        ["SITE_CONFIG_DIR", core.tool.site_config_dir],
        ["SITE_DATA_DIR",   core.tool.site_data_dir],
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
        xx = mungePath(_targ, base_path, mkdir=mkdir)
        return xx

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


    if core.tool.main_module.__name__ == "__main__":   # Caller is a tool script file, not an installed module
        my_resources = mungePath(__main__.__file__).parent / "deployment_files"
        # print (f"Script case:  <{my_resources}>")
    else:                                       # Caller is an installed module
        my_resources = ir_files(core.tool.main_module).joinpath("deployment_files")
        # print (f"Module case:  <{my_resources}>")


    for item in files_list:
        source = my_resources.joinpath(item["source"])

        if source.is_file():
            target_dir = resolve_target(item["target_dir"], mkdir=True)
            if "dir_stat" in item:
                os.chmod(target_dir.full_path, item["dir_stat"])

            outfile = target_dir.full_path / PurePath(item["source"]).name
            if not check_path_exists(outfile)  or  overwrite:
                with outfile.open('w') as ofile:
                    ofile.write(source.read_text())
                if "file_stat" in item:
                    os.chmod(outfile, item["file_stat"])
                logging.info (f"Deployed  {item['source']:20} to  {outfile}")
            else:
                logging.info (f"File <{item['source']}> already exists at <{outfile}>.  Skipped.")

        elif source.is_dir():
                # ONLY WORKS if the source dir is on the file system (eg, not in a package .zip)
                target_dir = resolve_target(item["target_dir"])
                if not check_path_exists(target_dir.full_path)  or  overwrite:
                    target_dir.full_path.mkdir(parents=True, exist_ok=True)
                    if "dir_stat" in item:
                        os.chmod(target_dir.full_path, item["dir_stat"])
                    copytree(source, target_dir.full_path, file_stat=item.get("file_stat", None), dir_stat=item.get("dir_stat", None))
                    logging.info (f"Deployed  {source.name:20} to  {target_dir.full_path}")
                else:
                    logging.info (f"Directory <{target_dir.full_path}> already exists.  Copytree skipped.")
        
        elif missing_ok:
            logging.info (f"Can't deploy <{source.name}>.  Item not found and missing_ok=True.  Skipping.")
        
        else:
            raise FileNotFoundError (f"Can't deploy <{source.name}>.  Item not found.")
