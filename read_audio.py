import scipy
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.signal import stft

# now convert the signal to morse code
# first fourier transform the signal
# very narrow peaks are dot, very wide peaks are dash


# plotting functions
def plot_time(signal, time):
    figt, axt = plt.subplots(figsize=(8, 6))
    axt.plot(time, signal)
    axt.set_title('time-domain')
    axt.set_xlabel('s')
    plt.show()

# read audio 
sample_rate, signal = wavfile.read('dddashd.wav')
time = np.linspace(0, len(signal) / sample_rate, num=len(signal))

freq_range=(1.9e4, 2.1e4)
dt = 0.01
overlap = 0.9
threshold= 12e4 

nperseg = int(dt*sample_rate)
noverlap = int(overlap*nperseg)
f, t_stft, zxx = stft(signal, fs=sample_rate, nperseg=nperseg, noverlap=noverlap)
power = np.abs(zxx)**2
band = (f>=freq_range[0]) & (f<=freq_range[1])
band_power = power[band, :]

morse_code = np.any(band_power>threshold, axis=0).astype(int)

plt.plot(t_stft, morse_code)
plt.show()


