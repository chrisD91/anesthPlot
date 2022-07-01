# !/usr/bin/env python3
"""
Created on Thu Apr 28 16:20:07 2022

@author: cdesbois

the base wave for slow and fast waves
"""
from types import SimpleNamespace
from typing import Any, Optional

import matplotlib.pyplot as plt
import pandas as pd


from anesplot.config.load_recordrc import build_paths

paths = build_paths()


class Waves:  # pylint: disable=too-few-public-methods
    """the base object to store the records."""

    def __init__(self) -> None:
        """
        Initialise.

        :param filename: DESCRIPTION, defaults to None
        :type filename: str, optional
        :return: basic class for the records
        :rtype: wave object

        """
        self.filename: str
        self.data: pd.DataFrame
        self.fig: plt.Figure
        self.figures: SimpleNamespace = SimpleNamespace()
        self.roi: Optional[dict[str, Any]] = None
        self.header: dict[str, Any]
        self.param: dict[str, Any] = dict(
            dtmin=None,
            dtmax=None,
            xmin=None,
            xmax=None,
            ymin=0,
            ymax=None,
            path=paths.get("sFig", "~"),
            dtime=True,
            unit="dtime",
            save=False,
            memo=False,
            file=None,
            source=None,
            # source_abbr=None,
            sampling_freq=None,
        )

    def append_to_figures(self, figdico: dict[str, plt.Figure]) -> None:
        """
        Append fig to a self.figures (a SimpleNameSpace).

        Parameters
        ----------
        figdico : dict[str, plt.Figure]
            dico {name:fig}.

        Returns
        -------
        None.

        """
        for name, fig in figdico.items():
            # callname = name + "_".join([name, self.param["source_abbr"]])
            callname = name
            setattr(self.figures, callname, fig)
