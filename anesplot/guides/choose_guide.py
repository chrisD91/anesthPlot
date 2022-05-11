# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 10 08:37:18 2022

@author: cdesbois

a simple terminal dialog to choose the template and copy it to the clipboard

"""

import os

import pyperclip


def get_guide(pathsdict: dict) -> str:
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
    with open(guidename, "r", encoding="utf8") as file:
        pyperclip.copy(file.read())
    print(f"the content of '{guide}' is in your clipboard")
    return guidename


# %%

if __name__ == "__main__":
    import anesplot.record_main as rec

    get_guide(rec.paths)
