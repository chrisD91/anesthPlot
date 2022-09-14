# !/usr/bin/env python3
"""
Created on Thu Mar 10 08:37:18 2022

@author: cdesbois

a simple terminal dialog to choose the template and copy it to the clipboard

"""

import os
from typing import Any, Optional

import pyperclip

from anesplot.config.load_recordrc import build_paths


def get_basic_debrief_commands() -> str:
    """Copy in clipboard the usual commands to build a debrief."""
    lines = [
        "filename = None   #<- add filename here (if you know it)",
        "mtrends = rec.MonitorTrend(filename)",
        "mwaves = rec.MonitorWave((mtrends.wavename()))",
        "ttrends = rec.TaphTrend(monitorname = mtrends.filename)",
        "ttrends.shift_datetime(60)",
    ]
    message = "basic debrief commands are in the clipboard"
    # logging.debug(message)
    splitlines = " \n".join(lines)
    pyperclip.copy(splitlines)
    return message


def get_guide(pathsdict: Optional[dict[str, Any]] = None) -> str:
    """
    Load the specified template file and copy it to the clipboard.

    Parameters
    ----------
    pathsdict : dict
        typically rec.paths

    Returns
    -------
    str
        guide filename.

    """
    if pathsdict is None:
        pathsdict = build_paths()

    guides_dir = os.path.join(pathsdict["recordMain"], "guides")
    guides = sorted(os.listdir(guides_dir))
    guides = [_ for _ in guides if _.endswith(".txt")]
    guides_list = []
    for i, guide in enumerate(guides):
        txt = f"{i} \t {guide}"
        guides_list.append(txt)
    dialog = guides_list.copy()
    dialog.insert(0, f"{'-'*25}")
    dialog.append(f"{'-'*25}")
    dialog.insert(0, "type the index of the file")
    dialog.append("\n")

    choice = input("\n".join(dialog))
    num = int(choice)
    guide = guides[num]
    #    print(f"you have choised {guide}")
    guidename = os.path.join(guides_dir, guide)
    with open(guidename, encoding="utf8") as file:
        pyperclip.copy(file.read())
    print(f"the content of '{guide}' is in your clipboard")
    return guidename


# %%

if __name__ == "__main__":
    get_guide(build_paths())
