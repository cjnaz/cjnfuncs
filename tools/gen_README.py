#!/usr/bin/env python3
"""Extract doc strings from cjnfuncs and build the README.md
"""

#==========================================================
#
#  Chris Nelson, 2023
#
#==========================================================

import pathlib
import re

CODEFILE = "../src/cjnfuncs/cjnfuncs.py"
README_HEAD = "README.head"
README_TAIL = "README.tail"
README_OUT = "../README.md"     # Root of package directory

# Doc string format example:
'''
def snd_notif(subj="Notification message", msg="", to="NotifList", log=False):
    """
## snd_notif (subj="Notification message, msg="", to="NotifList", log=False) - Send a text message using info from the config file
(...documentation...)
    """
'''

with pathlib.Path(CODEFILE).open() as infile:
    all = infile.read()


# Build the links list
comment_block = re.compile(r'"""\s+##\s([\s\S]+?)(?:""")')
links = ""
for match in comment_block.finditer(all):
    funcline = match.group(1).split('\n')[0]
    link_name = funcline.replace("Class ", "").split(maxsplit=1)[0]

    link = funcline.replace(" ", "-").lower()
    deleted = ":()\n,.=\"\'"
    for char in deleted:
        link = link.replace(char, "")

    links += f"- [{link_name}](#{link})\n"

# Write the README.md file
with pathlib.Path(README_OUT).open('w') as outfile:
    with pathlib.Path(README_HEAD).open() as head:
        outfile.write(head.read())

    outfile.write(links)

    for match in comment_block.finditer(all):
        outfile.write("\n` `\n")
        outfile.write("---\n")
        outfile.write("---\n")
        outfile.write("# ")
        outfile.write(match.group(1))

    with pathlib.Path(README_TAIL).open() as tail:
        outfile.write(tail.read())
