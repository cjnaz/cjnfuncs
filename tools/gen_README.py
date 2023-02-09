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

def get_linkname(block):
    funcline = block.group(1).split('\n')[0]
    return funcline.replace("Class ", "").split(maxsplit=1)[0]


with pathlib.Path(CODEFILE).open() as infile:
    all = infile.read()


# Build the links list
comment_block = re.compile(r'"""\s+##\s([\s\S]+?)(?:""")')
links = ""
for block in comment_block.finditer(all):
    link_name = get_linkname(block)
    links += f"- [{link_name}](#{link_name})\n"

    # link = funcline.replace(" ", "-").lower()
    # deleted = ":()\n,.=\"\'"
    # for char in deleted:
    #     link = link.replace(char, "")
    # links += f"- [{link_name}](#{link})\n"

# Write the README.md file
with pathlib.Path(README_OUT).open('w') as outfile:
    with pathlib.Path(README_HEAD).open() as head:
        outfile.write(head.read())

    outfile.write(links)

    for block in comment_block.finditer(all):
        link_name = get_linkname(block)
        outfile.write("\n<br/>\n\n")
        outfile.write(f'<a id="{link_name}"></a>\n\n')
        outfile.write("---\n\n")
        outfile.write("# ")
        outfile.write(block.group(1))

    with pathlib.Path(README_TAIL).open() as tail:
        outfile.write(tail.read())
