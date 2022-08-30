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

- [x] fix time correction for taph records and plot_ventil_dive (plot is not updated after a time shift)

- [x] build a trend save_roi the same way for trends as for waves

- [x] homogeneize the return elements of the plot function for trends

- [x] mwaves.data.columns :

  - [x] change sec by eTimeSec
  - [ ] append eTimeMin. -> NO to avoid increase in data size
  - [x] change time by dtime

- [x] mtrends.data.columns

  - [x] change datetime by dtime
  - [x] change eTime by etimesec

- [ ] trend_plot.py

  - [ ] externalize the save function

- [x] plot_roi_ekgbeat_overlap -> display the number of beats on the plot

- [x] check wave2video

- [x] plot_ventil_drive : add a grid

- [x] ventil : change axis label end tidal CO~2~ -> CO~2~

- [x] check filename in 'status line' of the plots for wave plotfig

- [x] ekg_to_hr

  implement a way to add or remove several beats for cleaning the detection
