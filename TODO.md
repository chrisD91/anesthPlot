# animation from ipython terminal
    the figure is only updated on the background
    (need to close and show to observe the animation)


# bug with QApplication : (done)

- 211027 : works from terminal and  from IPython terminal, but not inside spyder

  see https://github.com/spyder-ide/spyder/issues/5409

  running

  ```python
   %gui qt5
    -> ERROR:root:Cannot activate multiple GUI eventloops
  ```

  - test:

    ```python
    import anesplot.record_main as rec
    trends = rec.MonitorTrend()
    -> QApplication freeze in the background
    ```

  - set pref/IPython Console / graphics /Backend:

    -  automatic -> Qt5 :

      freezing 'base'

    - Qt5 -> OsX

      freezing

    - OsX -> Inline

      dialog appeared ! ... but no figures !

    - inline -> Qt5

      - freeze !
      - but ok after restart kernel and %gui qt5 !

    - but pb returns

      - nb if restart kernal after fresh, help menu shows two "Ipython documentation" items
      - nb at start no 'spyder/preferences' menu (not new)

    - remove graphics activate support

      - widget worked ... but no visible graphics
      - works after %gui qt5"

    - backend = qt5 + deactivated matplotlib support + %gui qt5 -> worked !

    - backend = qt5 + deactivated matplotlib support

      - but without %gui qt5 -> no figure displayed !
      - %gui qt5 (afterwards) -> works for the figures and the loading process

- updated spyder to see what happened:

  [see](https://stackoverflow.com/questions/69704561/cannot-update-spyder-5-1-5-on-new-anaconda-install)

use of %gui qt5 is required to work inside spyder (and the code works fine outside )
