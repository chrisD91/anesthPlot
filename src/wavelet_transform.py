import numpy as np
from scipy import signal

### MORLET WAVELET, definition, properties and normalization
def Morlet_Wavelet(t, f, w0=6.0):
    x = 2.0 * np.pi * f * t
    output = np.exp(1j * x)
    output *= np.exp(-0.5 * ((x / w0) ** 2))  # (Normalization comes later)
    return output


def Morlet_Wavelet_Decay(f, w0=6.0):
    """
    Time value of the wavelet where the amplitude decays of
    """
    return 2 ** 0.5 * (w0 / (np.pi * f))


def from_fourier_to_morlet(freq):
    x = np.linspace(0.1 / freq, 2.0 * freq, 1e3)
    return x[np.argmin((x - freq * (1 - np.exp(-freq * x))) ** 2)]


def get_Morlet_of_right_size(f, dt, w0=6.0, with_t=False):
    Tmax = Morlet_Wavelet_Decay(f, w0=w0)
    t = np.arange(-int(Tmax / dt), int(Tmax / dt) + 1) * dt
    if with_t:
        return t, Morlet_Wavelet(t, f, w0=w0)
    else:
        return Morlet_Wavelet(t, f, w0=w0)


def norm_constant_th(freq, dt, w0=6.0):
    # from theoretical calculus:
    n = (w0 / 2.0 / np.sqrt(2.0 * np.pi) / freq) * (1.0 + np.exp(-(w0 ** 2) / 2))
    return n / dt


def my_cwt(data, frequencies, dt, w0=6.0):
    """
    wavelet transform with normalization to catch the amplitude of a sinusoid
    """
    output = np.zeros([len(frequencies), len(data)], dtype=np.complex)

    for ind, freq in enumerate(frequencies):
        wavelet_data = np.conj(get_Morlet_of_right_size(freq, dt, w0=w0))
        sliding_mean = signal.convolve(
            data, np.ones(len(wavelet_data)) / len(wavelet_data), mode="same"
        )
        # the final convolution
        wavelet_data_norm = norm_constant_th(freq, dt, w0=w0)
        output[ind, :] = (
            signal.convolve(data - sliding_mean + 0.0 * 1j, wavelet_data, mode="same")
            / wavelet_data_norm
        )
    return output
