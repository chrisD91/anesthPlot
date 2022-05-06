#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 28 16:20:07 2022

@author: cdesbois

the base wave for slow and fast waves
"""

from anesplot.config.load_recordrc import build_paths

paths = build_paths()


class _Waves:
    """the base object to store the records."""

    def __init__(self):
        """
        :param filename: DESCRIPTION, defaults to None
        :type filename: str, optional
        :return: basic class for the records
        :rtype: wave object

        """
        self.data = None
        self.fig = None
        self.roi = None
        self.header = None
        self.param = dict(
            xmin=None,
            xmax=None,
            ymin=0,
            ymax=None,
            path=paths.get("sFig", "~"),
            unit="min",
            save=False,
            memo=False,
            file=None,
            source=None,
            sampling_freq=None,
            dtime=True,
        )
