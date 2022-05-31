- [x] animation from ipython terminal

  the figure is only updated on the background
  (need to close and show to observe the animation)

- [x] bug with QApplication : (done)

    use a app as global
    use of %gui qt5

- [x] mwaves.save_a_roi()
  /Users/cdesbois/pg/chrisPg/anesthPlot/anesplot/plot/wave_plot.py:259: FutureWarning: Passing method to DatetimeIndex.get_loc is deprecated and will raise in a future version. Use index.get_indexer([item], method=...) instead.
    datadf.set_index("datetime").index.get_loc(_, method="nearest")

- [x] module 'plot.wave_plot' has no attribute 'plot_systolic_pressure_variations'

- [x] build a function to choose a plot from a list for monitor  or taph record

- [ ] fix time correction for taph records and plot_ventil_dive (plot is not updated after a time shift)

- [x] build a trend save_roi the same way for trends as for waves

- [x] homogeneize the return elements of the plot function for trends

- [ ] mwaves.data.columns :

    - [ ] change sec by eTimeSec
    - [ ] append eTimeMin
    - [ ] change time by dtime

- [ ] mtrends.data.columns

    - [ ] change datetime by dtime
    - [ ] change eTime by eTimeSec

- [ ] trend_plot.py

    - [ ] externalize the save function
