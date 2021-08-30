# -*- coding: utf-8 -*-
#%reset -f

"""
plot the waves of a waveRecording

"""
import matplotlib.animation as animation
import matplotlib.pyplot as plt

import anesplot.treatrec.wave_func as wf
import anesplot.plot.wave_plot as wp

#%% choose an area of interest

plt.close("all")


waves = ["wawp", "wflow"]
# waves = ['wco2']
# ['wekg', 'wap', 'wco2', 'wawp', 'wflow']
# fig, lines = wf.plot_wave(wdata.set_index('sec'), waves)
fig, lines = wp.plot_wave(wdata, waves)
fig.text(0.99, 0.01, "cDesbois", ha="right", va="bottom", alpha=0.4)
fig.text(0.01, 0.01, params["file"], ha="left", va="bottom", alpha=0.4)
# fig, lines = plotWave(wdata, waves)

# chooseTimeArea(wave)
print("expand the graph to find the interesting part")
print("then run returnPoints")

#%% extract the limits
roi = wf.returnPoints(wdata, fig)

#%% plot waves
plt.close("all")
figList = []
for key in ["wekg", "wap", "wco2", "wawp", "wflow"]:
    #    wf.plot_wave(wdata, [key], miniS= limsec[0], maxiS= limsec[1])
    fig = wp.plot_wave(wdata, [key], mini=roi["pt"][0], maxi=roi["pt"][1])
    figList.append(fig)
    # plotWave(wdata.set_index('sec'), [key], mini= limpt[0], maxi= limpt[1])

# figList[0] = EKG
# figList[1] = Pa
# figList[2] = co2
# figList[3] = paw
# figList[4] = airFlow
fig = wp.plot_wave(wdata, ["wekg", "wap"], mini=roi["pt"][0], maxi=roi["pt"][1])

#%% //////////////////////////////////////////////////////////////////////////
# +++++++++  build animations +++++++++++++++++++++
# restric the time base (ie build a new pd.DataFrame !!! fe
plt.close("all")

# mini = 610000
# maxi = 616000
# df = restrictTimeArea(wdata, mini, maxi)
# df = wf.restrictTimeArea(wdata, limpt[0], limpt[1])
df = wdata.iloc[roi["pt"][0] : roi["pt"][1]]
# hypovolemiaPEEP:

#%% build animation (save=True to save)
plt.close("all")


def animate(i):
    """
    animate frame[i], add 10 points to the lines
    return the two lines2D objects
    """
    #    print(i, len(df)/10)
    #    bol = (i > (len(df)/10 -40))
    #    print(bol)
    #    if bol:
    #        line0.set_data([],[])
    #        return line0,
    if len(keys) == 1:
        trace_name = keys[0]
        line0.set_data(
            df.index[0 : 10 * i].values, df.iloc[0 : 10 * i][trace_name].values
        )
        return (line0,)
    else:
        trace_name = keys[0]
        line0.set_data(
            df.index[0 : 10 * i].values, df.iloc[0 : 10 * i][trace_name].values
        )
        trace_name = keys[1]
        line1.set_data(
            df.index[0 : 10 * i].values, df.iloc[0 : 10 * i][trace_name].values
        )
        return (
            line0,
            line1,
        )


keys = ["wflow", "wco2"]
# keys = ['wco2']
# keys = ['wekg']
# keys = ['wflow']

# NB lag for co2 ie around -480 points

anim = True
save = False
speed = 5  # speed of the animation

saveName = "example"
paths["save"] = "/Users/cdesbois/toPlay"
# paths['saveAnim'] = '/Users/cdesbois/enva/clinique/recordings/principle/fig'
# paths['saveAnim'] = '/Users/cdesbois/enva/clinique/recordings/casClin/taphColic/mov'
# paths['saveAnim'] = '/Users/cdesbois/enva/enseignement/cours/techniques/techniques/capnie/fig'
fileName = os.path.join(paths["save"], saveName)

fig, lines = wp.plot_wave(df, keys=keys, mini=None, maxi=None)
fig.text(0.01, 0.01, file, ha="left", va="bottom", alpha=0.4)
fig.text(0.99, 0.01, "cDesbois", ha="right", va="bottom", alpha=0.4)

# adjust the limits
# fig.get_axes()[0].set_ylim(0,45)

# adjust scale
# fig.get_axes()[0].set_ylim(40,100)
# fig.get_axes()[1].set_ylim(50, 130)


if anim:
    for line in lines:
        line.set_data([], [])
    line0 = lines[0]
    try:
        line1 = lines[1]
    except:
        line1 = None
    #
    ani = animation.FuncAnimation(
        fig,
        animate,
        frames=int(len(df) / 10),
        interval=30 / speed,
        repeat=False,
        blit=True,
        save_count=int(len(df) / 10),
    )
    for ax in fig.get_axes():
        ax.spines["top"].set_visible(False)
    if save:
        ani.save(fileName + ".mp4")
        fig.savefig(fileName + ".png")
plt.show()


#%% ventilatory loop
plt.close("all")
fig, lines = wp.plot_wave(wdata, keys=["wflow", "wawp"], mini=None, maxi=None)
lims = fig.get_axes()[0].get_xlim()
mini = int(lims[0])  # pt
maxi = int(lims[1])  # pt
#%%
plt.close("all")


def smooth(y, boxPts):
    """
    smoothing using a sliding window
    """
    box = np.ones(boxPts) / boxPts
    ySmooth = np.convolve(y, box, mode="same")
    return ySmooth


def makeArrow(ax, pos, function, direction):
    delta = 0.0001 if direction >= 0 else -0.0001
    ax.arrow(
        pos,
        function(pos),
        pos + delta,
        function(pos + delta),
        head_width=0.05,
        head_length=0.1,
    )


def flowPressureLoop(wdata, mini, maxi):
    mini = int(mini)
    maxi = int(maxi)
    df = wdata.set_index("sec").iloc[mini:maxi]
    fig = plt.figure()
    fig.suptitle("flow pressure loop")
    ax = fig.add_subplot(111)
    x = df.wawp.tolist()
    y = df.wflow.tolist()
    x = smooth(x, 9)
    y = smooth(y, 9)
    ax.plot(x, y, "r-")
    ax.set_xlabel("airway pressure (cmH20)")
    ax.set_ylabel("expiratory flow")
    lims = ax.get_xlim()
    ax.hlines(0, lims[0], lims[1], alpha=0.3)
    lims = ax.get_ylim()
    ax.vlines(0, lims[0], lims[1], alpha=0.3)


# flowPressureLoop(wdata, 105, 107.5)
flowPressureLoop(wdata, mini, maxi)

#%% volumetric CO2
plt.close("all")
fig, lines = wp.plot_wave(wdata, keys=["wco2", "wflow"], mini=mini, maxi=maxi)
fig, lines = wp.plot_wave(wdata, keys=["wflow", "wawp"], mini=mini, maxi=maxi)
fig.set_figwidth(12)
fig.set_figheight(6)

df = wdata.set_index("sec").iloc[mini:maxi][["wco2", "wflow", "wawp"]]
# remove the first part (ie before etCo2 min)
df = df.loc[df.wco2.idxmin() : df.wco2.idxmax()]
df.reset_index(inplace=True, drop=False)
# shifted the time base to satrt at 0
df.sec = df.sec - df.sec.iloc[0]
#%%
plt.close("all")


def plotQCo2(df, qco2=False):
    fig = plt.figure(figsize=(12, 6))
    fig.suptitle("expCO2 vs QCO2 (flow * expCO2)")
    ax = fig.add_subplot(111)
    x = df.sec.to_list()
    y = df.wco2
    ax.plot(x, y, "b-", alpha=0.6, linewidth=2, label="expCO2")
    axT = ax.twinx()
    if qco2:
        y = ((df.wco2 * df.wflow) / 760).to_list()
        axT.plot(x, y, "k-", alpha=0.5, label="QCO2")
        axT.set_ylabel("QCO2")
    for axe in [ax, axT]:
        lims = axe.get_ylim()
        axe.set_ylim(0, lims[1])
        axe.spines["top"].set_visible(False)
        axe.legend()
    ax.set_xlabel("time (sec)")
    ax.set_ylabel("expCO2 (mmHg)")
    fig.text(0.99, 0.01, "cDesbois", ha="right", va="bottom", alpha=0.4)
    fig.tight_layout()


fig = plotQCo2(df, qco2=False)
fig = plotQCo2(df, qco2=True)

#%% plot volume
# TODO build a volume column of wdata (identify the cycles first to reset 0 values)
df["vol"] = df.wflow.cumsum() * (-1)
fig = plt.figure()
ax = fig.add_subplot(111)
x = df.wawp.tolist()
y = df.vol.tolist()
# y = [item * -1 for item in df.vol.tolist()]
ax.plot(x, y)
#%% build a dico assossiating time and indices
# NB should return '1' if the index has been adjusted

ser = wdata.time

from collections import OrderedDict

dico = OrderedDict()
aList = []
for i, item in wdata.time[wdata.time.notnull()].iteritems():
    dico[item] = i
    aList.append(item)
firstKey, secondKey = "", ""

# through a dataFrame
df = wdata.time[wdata.time.notnull()]
df = pd.DataFrame(df)
# convert to dateTime
df.time = pd.to_datetime(df.time)

df["point"] = df.index
df.reset_index(inplace=True)

df["deltaTime"] = (df.time - df.time.shift(1)).dt.seconds
df["deltaPoint"] = df.point - df.point.shift(1)

# total duration :
totTime = df.time.iloc[-1] - df.time.iloc[0]
totTime = datetime.timedelta.total_seconds(totTime)
totPoint = df.point.iloc[-1] - df.point.iloc[0]

ptPerSec = totPoint / totTime
print("point per seconds are", ptPerSec)
# normally 300 points per seconds


import matplotlib.animation as animation
import matplotlib.pyplot as plt

#%% scope
import numpy as np
from matplotlib.lines import Line2D


class Scope(object):
    def __init__(self, ax, maxt=2, dt=0.02):
        self.ax = ax
        self.dt = dt
        self.maxt = maxt
        self.tdata = [0]
        self.ydata = [0]
        self.line = Line2D(self.tdata, self.ydata)
        self.ax.add_line(self.line)
        self.ax.set_ylim(-0.1, 1.1)
        self.ax.set_xlim(0, self.maxt)

    def update(self, y):
        lastt = self.tdata[-1]
        if lastt > self.tdata[0] + self.maxt:  # reset the arrays
            self.tdata = [self.tdata[-1]]
            self.ydata = [self.ydata[-1]]
            self.ax.set_xlim(self.tdata[0], self.tdata[0] + self.maxt)
            self.ax.figure.canvas.draw()

        t = self.tdata[-1] + self.dt
        self.tdata.append(t)
        self.ydata.append(y)
        self.line.set_data(self.tdata, self.ydata)
        return (self.line,)


#%%


def sendPoint(a=0):
    # def sendPoint(a=500000):
    #    a = 10000
    while a < len(df):
        yield df.iloc[a]
        print(a, df.iloc[a])
        a += 1


def extractDf(dataDf, key="wekg", dx=0.03, iMin=None, iMax=None):
    if key in dataDf.columns:
        # df = dataDf.reset_index()[key]
        df = dataDf.reset_index()[key].iloc[iMin:iMax]
    else:
        print(key, "is not in the dataFrame provided")
        return
    params = {}
    params["dx"] = dx
    params["key"] = key
    yScale = {
        "wco2": [0, 55],
        "wekg": [-2, 2],
        "wap": [40, 150],
        "wflow": [-5, 10],
        "wawp": [-5, 45],
    }
    try:
        params["yScale"] = yScale[key]
    except:
        params["yScale"] = []
    colors = {"wekg": "r", "wco2": "b", "wap": "r", "wflow": "g", "wawp": "y"}
    try:
        params["color"] = colors[key]
    except:
        params["color"] = None
    return df, params


def buildTheScope(params):
    fig, ax = plt.subplots()
    fig.suptitle(params["key"])
    ax.set_xlabel("time (sec)")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid()
    #    axT = ax.twinx()
    scope = Scope(ax, maxt=60, dt=0.01)
    scope.ax.set_ylim(params["yScale"])
    scope.line.set_color(params["color"])
    return fig, scope


# Trend: dx = 1/header['Sampling Rate']* 1000
# data : 'time', 'ip1s', 'ip1d', 'ip1m', 'hr', 'T1', 'co2insp', 'co2exp',
#       'co2RR', 'o2insp', 'o2exp', 'aaLabel', 'aaInsp', 'aaExp', 'pPeak',
#       'peep', 'pPlat', 'tvInsp', 'tvExp', 'compli', 'ipeep', 'pmean', 'raw',
#       'minVinsp', 'minVexp', 'epeep', 'ieRat', 'inspT', 'expT', 'eTime',
#       'eTimeMin'


# wdata : wekg', 'wap', 'wco2', 'wawp', 'wflow'  /// interval = 3 (msec)
key = "wekg"

df, params = extractDf(wdata, key, iMin=260000, iMax=300000)
fig, scope = buildTheScope(params)

ani = animation.FuncAnimation(fig, scope.update, sendPoint, interval=0, blit=True)
# NB interval in msec


#%% ? for two lines


class twoScope(object):
    def __init__(self, ax1, ax2, maxt=2, dt=0.02):
        self.ax1 = ax1
        self.ax2 = ax2
        self.dt = dt
        self.maxt = maxt
        self.tdata = [0]
        self.y1data = [0]
        self.y2data = [0]
        self.line1 = Line2D(self.tdata, self.y1data)
        self.line2 = Line2D(self.tdata, self.y2data)
        self.ax1.add_line(self.line1)
        self.ax2.add_line(self.line2)
        self.ax1.set_ylim(-0.1, 1.1)
        self.ax2.set_ylim(-0.1, 1.1)
        self.ax1.set_xlim(0, self.maxt)
        self.ax2.set_xlim(0, self.maxt)

    def update(self, yVals):
        y1 = yVals[0]
        y2 = yVals[1]
        lastt = self.tdata[-1]
        if lastt > self.tdata[0] + self.maxt:  # reset the arrays
            self.tdata = [self.tdata[-1]]
            self.y1data = [self.y1data[-1]]
            self.y2data = [self.y2data[-1]]
            self.ax1.set_xlim(self.tdata[0], self.tdata[0] + self.maxt)
            self.ax1.figure.canvas.draw()
            self.ax2.set_xlim(self.tdata[0], self.tdata[0] + self.maxt)
            # self.ax2.figure.set_facecolor('white')
            self.ax2.figure.canvas.draw()
            # self.ax2.figure.set_facecolor('white')
            # doesnt't work : the canvas facecolor is black
        t = self.tdata[-1] + self.dt
        self.tdata.append(t)
        self.y1data.append(y1)
        self.y2data.append(y2)
        self.line1.set_data(self.tdata, self.y1data)
        self.line2.set_data(self.tdata, self.y2data)
        return (
            self.line1,
            self.line2,
        )


#%% to include the data in the object


class twoScopeAndData(object):
    def __init__(self, df, ax1, ax2, maxt=2, dt=0.02):
        self.df = df
        self.ax1 = ax1
        self.ax2 = ax2
        self.dt = dt
        self.maxt = maxt
        self.tdata = [0]
        self.y1data = [0]
        self.y2data = [0]
        self.line1 = Line2D(self.tdata, self.y1data)
        self.line2 = Line2D(self.tdata, self.y2data)
        self.ax1.add_line(self.line1)
        self.ax2.add_line(self.line2)
        self.ax1.set_ylim(-0.1, 1.1)
        self.ax2.set_ylim(-0.1, 1.1)
        self.ax1.set_xlim(0, self.maxt)
        self.ax2.set_xlim(0, self.maxt)

    def update(self, a):
        if a > len(df):
            return
        y1 = df.iloc[a][0]
        y2 = df.iloc[a][1]
        lastt = self.tdata[-1]
        if lastt > self.tdata[0] + self.maxt:  # reset the arrays
            self.tdata = [self.tdata[-1]]
            self.y1data = [self.y1data[-1]]
            self.y2data = [self.y2data[-1]]
            self.ax1.set_xlim(self.tdata[0], self.tdata[0] + self.maxt)
            self.ax1.figure.canvas.draw()
            self.ax2.set_xlim(self.tdata[0], self.tdata[0] + self.maxt)
            # self.ax2.figure.set_facecolor('white')
            self.ax2.figure.canvas.draw()
            # self.ax2.figure.set_facecolor('white')
            # doesnt't work : the canvas facecolor is black
        t = self.tdata[-1] + self.dt
        self.tdata.append(t)
        self.y1data.append(y1)
        self.y2data.append(y2)
        self.line1.set_data(self.tdata, self.y1data)
        self.line2.set_data(self.tdata, self.y2data)
        return (
            self.line1,
            self.line2,
        )


#%%
def send2Point(a=0):
    # def sendPoint(a=500000):
    #    a = 10000
    while a < len(df):
        yield [df.iloc[a][0], df.iloc[a][1]]
        print(a * 0.003)
        #        print(a, df.iloc[a])
        a += 1


def extractsDf(dataDf, keys=["wekg", "wap"], dx=0.03, iMin=None, iMax=None):
    """
    extract a pdDataframe from target within bounds of iMin and iMax (index in sec)
    input :
        dataDf = pdDataframe (typically wdata), dx typically 0.03
        keys : list of 2 column headers
        iMin, iMax : limits in seconds
    output :
        dataFrame
    """
    for key in keys:
        if key not in dataDf.columns:
            print(key, "is not in the dataFrame provided")
            return
    #    df = dataDf[keys].loc[iMin:iMax].reset_index()
    df = dataDf.loc[iMin:iMax].reset_index()[keys]
    df.index *= dx
    params = {}
    params["dx"] = dx
    #    params['key'] = key
    #    yScale = {'wco2':[0, 55],
    #              'wekg':[-2, 2],
    #              'wap' : [40,150],
    #              'wflow': [-5,10],
    #              'wawp' : [-5, 45],
    #            }
    #    try:
    #        params['yScale'] = yScale[key]
    #    except:
    #        params['yScale'] = []
    #    colors = {'wekg': 'r','wco2':'b', 'wap':'r', 'wflow':'g', 'wawp': 'y'}
    #    try:
    #        params['color'] = colors[key]
    #    except:
    #        params['color'] = None
    return df, params


yScale = {
    "wco2": [0, 55],
    "wekg": [-2, 2],
    "wap": [40, 150],
    "wflow": [-5, 10],
    "wawp": [-5, 45],
}
colors = {"wekg": "k", "wco2": "b", "wap": "r", "wflow": "g", "wawp": "y"}

keys = ["wekg", "wap"]
df, _ = extractsDf(wdata, keys=keys, iMin=2000, iMax=3000)

# plt.rcParams['axes.facecolor']='white'
# fig = plt.figure(facecolor='white', edgecolor='white')
fig = plt.figure()
# fig.set_facecolor('white')
ax1 = fig.add_subplot(211)
ax2 = fig.add_subplot(212)
for i, ax in enumerate(fig.axes):
    ax.grid()
    ax.set_ylabel(keys[i])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    if i == 1:
        ax.set_xlabel("time")
# maxt = 15, dt = 0.003 -> 15 sec scope
# scope = twoScope(ax1, ax2, maxt = 15, dt= 0.003)
scope = twoScopeAndData(df, ax1, ax2, maxt=15, dt=0.003)

scope.ax1.set_ylim(yScale[keys[0]])
scope.ax2.set_ylim(yScale[keys[1]])
scope.line1.set_color(colors[keys[0]])
scope.line2.set_color(colors[keys[1]])

# ani = animation.FuncAnimation(fig, scope.update, send2Point,
#                              interval=1, blit=True)

fr = int(len(df) / 30 / 10)
# fr = None
print("saveDur=", fr * 1 / 60)
print("plotDur=", fr * 1 / 1000)

ani = animation.FuncAnimation(fig, scope.update, frames=fr, interval=1, blit=True)
# NB with blit=True, savedTrace = fillfrom0, without: OK for the save.
ani.save("test.mp4", fps=60, dpi=74, writer="ffmpeg")
# ani.save('test.mp4', fps=1, dpi=200)
# NB saved animation: duration = frames * (1/fps)   (in sec)
# display animation: duration = frames * interval / 1000 (in sec)

# plt.show()

#%% animation duration (display, save)
# see https://stackoverflow.com/questions/22010586/matplotlib-animation-duration

fig = plt.figure(figsize=(16, 12))
ax = fig.add_subplot(111)
# You can initialize this with whatever
im = ax.imshow(np.random.rand(6, 10), cmap="bone_r", interpolation="nearest")


def animate(i):
    aux = np.zeros(60)
    aux[i] = 1
    image_clock = np.reshape(aux, (6, 10))
    im.set_array(image_clock)


ani = animation.FuncAnimation(fig, animate, frames=60, interval=1000)
ani.save("clock.mp4", fps=10.0, dpi=200)
plt.show()
