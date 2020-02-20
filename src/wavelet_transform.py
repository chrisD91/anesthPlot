
import numpy as np
from scipy import signal

def ricker(t, f, t0):
    """
    Ricker wavelet of frequency 'f' centered in t0 and  over and signal length.
    """
    fact = (np.pi**2) * (f**2) * ((t - t0)**2)
    y = (1.0 - 2.0 * fact) * np.exp(-fact)
    return y

def make_ricker_of_right_size(freq, dt, with_t=False, factor_freq=2.):
    """
    returns a ricker of size int(factor_freq*/(freq*dt))
    centered in the middle of the array (for use with convolve)

    Note factor_freq = 2 covers well the extent of the ricker
    """
    tstop = factor_freq/freq
    t = np.arange(int(tstop/dt))*dt
    if with_t:
        return t-tstop/2., ricker(t, freq, t[-1]/2.)
    else:
        return ricker(t, freq, t[-1]/2.) 

def from_fourier_to_morlet(freq):
    x = np.linspace(0.1/freq, 2.*freq, 1e3)
    return x[np.argmin((x-freq*(1-np.exp(-freq*x)))**2)]
    
def make_morlet_of_right_size(freq, dt,
                              with_t=False, s=5.):
    """
    returns a ricker of size int(factor_freq*/(freq*dt))
    centered in the middle of the array (for use with convolve)

    Note factor_freq = 2 covers well the extent of the ricker
    """
    tstop = 2.*np.pi/freq
    t = np.arange(int(tstop/dt))*dt
    # sigma = from_fourier_to_morlet(freq)
    w = len(t)*freq*dt/(2.*s)
    
    if with_t:
        return t-tstop/2., np.real(signal.morlet(len(t), w, s=s))
    else:
        return np.real(signal.morlet(len(t), w, s=1.))
    
def my_cwt(data, frequencies, dt, wavelet='ricker'):
    """
    Continuous wavelet transform, adapted from:
    https://github.com/scipy/scipy/blob/v0.18.1/scipy/signal/wavelets.py#L311-L365

    Performs a continuous wavelet transform on `data`,
    using the `wavelet` function. A CWT performs a convolution
    with `data` using the `wavelet` function, which is characterized
    by a frequency parameter.

    Parameters
    ----------
    data : (N,) ndarray
        data on which to perform the transform.
    frequencies : (M,) sequence
        Widths to use for transform.
    Returns
    -------
    cwt: (M, N) ndarray
        Will have shape of (len(frequencies), len(data)).
                                    width[ii]), mode='same')
    """
    output = np.zeros([len(frequencies), len(data)])

    if wavelet=='ricker':
        make_wavelet_of_right_size = make_ricker_of_right_size
    elif wavelet=='morlet':
        make_wavelet_of_right_size = make_morlet_of_right_size
    
    for ind, freq in enumerate(frequencies):
        wavelet_data = make_wavelet_of_right_size(freq, dt)
        # the wavelets have different integrals
        # conv_number compensates for the number of summed points (i.e. also integral of wavelet)
        conv_number = signal.convolve(np.ones(len(data)), np.ones(len(wavelet_data)),
                                      mode='same')
        # the sliding mean that depends on the frequency
        sliding_mean = signal.convolve(data, np.ones(len(wavelet_data)),
                                       mode='same')/conv_number
        # the final convolution
        output[ind, :] = signal.convolve(data-sliding_mean, wavelet_data,
                                         mode='same')/conv_number
    return output

def illustration_plot(t, freqs, data, coefs, dt, tstop, freq1, freq2, freq3):
    """
    a plot to illustrate the output of the wavelet analysis
    """
    import matplotlib.pylab as plt
    fig = plt.figure(figsize=(12,6))
    plt.subplots_adjust(wspace=.8, hspace=.5, bottom=.2)
    # signal plot
    plt.subplot2grid((3, 8), (0,0), colspan=6)
    plt.plot(1e3*t, data, 'k-', lw=2)
    plt.ylabel('signal')
    for f, tt in zip([freq2, freq1, freq3], [200,500,800]):
        plt.annotate(str(int(f))+'Hz', (tt, data.max()))
    plt.xlim([1e3*t[0], 1e3*t[-1]])
    # time frequency power plot
    ax1 = plt.subplot2grid((3, 8), (1,0), rowspan=2, colspan=6)
    c = plt.contourf(1e3*t, freqs, coefs, cmap='PRGn', aspect='auto')
    plt.xlabel('time (ms)')
    plt.ylabel('frequency (Hz)')
    plt.yticks([10, 40, 70, 100]);
    # inset with legend
    acb = plt.axes([.4, .4, .02, .2])
    plt.colorbar(c, cax=acb, label='coeffs (a.u.)', ticks=[-1, 0, 1])
    # mean power plot over intervals
    plt.subplot2grid((3, 8), (1, 6), rowspan=2)
    for t1, t2 in zip([0,300e-3,700e-3], [300e-3,700e-3, 1000e-3]):
        cond = (t>t1) & (t<t2)
        plt.barh(freqs, np.power(coefs[:,cond],2).mean(axis=1)*dt,\
                 label='t$\in$['+str(int(1e3*t1))+','+str(int(1e3*t2))+']')
    plt.legend(prop={'size':'small'}, loc=(0.1,1.1))
    plt.yticks([10, 40, 70, 100]);
    plt.xticks([]);
    plt.xlabel(' mean \n power \n (a.u.)')
    # max of power over intervals
    plt.subplot2grid((3, 8), (1, 7), rowspan=2)
    for t1, t2 in zip([0,300e-3,600e-3], [300e-3,600e-3, 1000e-3]):
        cond = (t>t1) & (t<t2)
        plt.barh(freqs, np.power(coefs[:,cond],2).max(axis=1)*dt,\
                 label='t$\in$['+str(int(1e3*t1))+','+str(int(1e3*t2))+']')
    plt.yticks([10, 40, 70, 100]);
    plt.xticks([]);
    plt.xlabel(' max. \n power \n (a.u.)');
    return fig

def time_freq_plot(t, freqs, data, coefs):
    """
    a plot to illustrate the output of the wavelet analysis
    """
    dt = t[1]-t[0]
    import matplotlib.pylab as plt

    fig = plt.figure(figsize=(8,5))
    plt.subplots_adjust(wspace=.8, hspace=.5, bottom=.2)
    # signal plot
    plt.subplot2grid((3, 8), (0,0), colspan=6)
    plt.plot(1e3*t, data, 'k-', lw=2)
    plt.ylabel('signal')
    plt.xlim([1e3*t[0], 1e3*t[-1]])
    # time frequency power plot
    ax1 = plt.subplot2grid((3, 8), (1,0), rowspan=2, colspan=6)
    c = plt.contourf(1e3*t, freqs, coefs, cmap='PRGn', aspect='auto')
    plt.xlabel('time (ms)')
    plt.ylabel('frequency (Hz)')
    # inset with legend
    acb = plt.axes([.4, .4, .02, .2])
    plt.colorbar(c, cax=acb, label='coeffs (a.u.)', ticks=[-1, 0, 1])
    # mean power plot over intervals
    plt.subplot2grid((3, 8), (1, 6), rowspan=2)
    plt.barh(freqs, np.power(coefs,2).mean(axis=1)*dt)
    plt.xticks([]);
    plt.xlabel(' mean \n power \n (a.u.)')
    # max of power over intervals
    plt.subplot2grid((3, 8), (1, 7), rowspan=2)
    plt.barh(freqs, np.power(coefs,2).max(axis=1)*dt)
    plt.xticks([]);
    plt.xlabel(' max. \n power \n (a.u.)');
    return fig

if __name__ == '__main__':

    import argparse
    parser=argparse.ArgumentParser(description='Wavelet',
                                   formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("-w", "--wavelet", default='ricker')
    parser.add_argument("--noise_level",help="noise level",\
                        type=float, default=0.)
    parser.add_argument("--nfreq",help="discretization of frequencies",\
                        type=int, default=20)
    parser.add_argument("-sw", "--show_wavelet", help="show_wavelet", action="store_true")
    args = parser.parse_args()
    
    import numpy as np
    import matplotlib.pylab as plt

    plt.style.use('ggplot')

    # temporal sampling
    dt, tstop = 1e-4, 1.
    t = np.arange(int(tstop/dt))*dt
    
    if args.wavelet=='ricker':
        make_wavelet_of_right_size = make_ricker_of_right_size
    elif args.wavelet=='morlet':
        make_wavelet_of_right_size = make_morlet_of_right_size
        
    if args.show_wavelet:
        for f in [10., 40., 70.]:
            plt.plot(*make_wavelet_of_right_size(f, dt, with_t=True))
    else:

        # ### artificially generated signal, transient oscillations
        freq1, width1, freq2, width2, freq3, width3 = 10., 100e-3, 40., 40e-3, 70., 20e-3
        data  = 3.2+np.cos(2*np.pi*freq1*t)*np.exp(-(t-.5)**2/2./width1**2)+\
                np.cos(2*np.pi*freq2*t)*np.exp(-(t-.2)**2/2./width2**2)+\
                np.cos(2*np.pi*freq3*t)*np.exp(-(t-.8)**2/2./width3**2)

        # ### adding colored noise to test robustness
        data += args.noise_level*np.convolve(np.exp(-np.arange(1000)*dt/400e-3),\
                            np.random.randn(len(t)), mode='same') # a slow one
        data += args.noise_level*np.convolve(np.exp(-np.arange(1000)*dt/5e-3),\
                            np.random.randn(len(t)), mode='same') # a faster one

        # Continuous Wavelet Transform analysis
        freqs = np.linspace(1, 90, args.nfreq)
        coefs = my_cwt(data, freqs, dt, wavelet=args.wavelet)

        time_freq_plot(t, freqs, data, coefs)
    plt.show()
