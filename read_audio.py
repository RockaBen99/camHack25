import scipy
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile


# now convert the signal to morse code
# first fourier transform the signal
# very narrow peaks are dot, very wide peaks are dash

def fft(signal, sample_rate, time_interval):
    # power spectrum in the given time interval
    start_index = int(time_interval[0] * sample_rate)
    end_index = int(time_interval[1] * sample_rate)
    segment = signal[start_index:end_index]
    freq = np.fft.fft(segment)

    # solve for freq_axis scale 
    power = np.abs(freq)**2
    length = (time_interval[1] - time_interval[0]) * sample_rate
    freq_axis = np.fft.fftfreq(length, 1/sample_rate)
    return freq_axis, power


def find_major_peaks(power, freq_axis, freq_range):
    # return true if large peak in the freq_range found 
    # locate index
    start = np.where(freq_axis==freq_range[0])[0][0]
    end = np.where(freq_axis==freq_range[1])[0][0]
    # search for major peaks within the index range
    power_seg = power[start:end]
    peak_indicies = np.where(power_seg>=0.4e14)[0]   # threshold to acknowledge a peak, need adjustment for optimal feedback
    return len(peak_indicies)>0


def morse(signal, sample_rate, freq_range):
    # split the entire signal to many small time_intervals
    # check if the survival of the major peak at each time_interval
    # thus convert it to morse code
    dt = 3 # differential time step of 3s, smaller values results in inability to 
    total_time = np.linspace(0, len(signal)/sample_rate, num=len(signal))
    morse = []
    tstart, tend=0, dt    # starting interval

    index=0
    # loop over all time steps
    while tend<=total_time[-1]:
        time_interval = (tstart, tend)
        freq_axis, power = fft(signal, sample_rate, time_interval)    # fft of signal in the small time step 
        if find_major_peaks(power, freq_axis, freq_range):
            morse.append(1)
        else:
            morse.append(0)
        index += 1
        tstart += dt
        tend += dt
    
    return morse
            

# plotting functions
def plot_time(signal, time):
    figt, axt = plt.subplots(figsize=(8, 6))
    axt.plot(time, signal)
    axt.set_title('time-domain')
    axt.set_xlabel('s')
    plt.show()

def plot_freq(signal, sample_rate, time_interval):
    freq_axis, power = fft(signal, sample_rate, time_interval)
    figf, axf = plt.subplots(figsize=(8, 6))
    axf.plot(freq_axis, power)
    axf.set_ylim(0, 0.25e15)
    axf.set_title('freq domain')
    axf.set_xlabel('Hz')
    plt.show()

# read audio 
sample_rate, signal = wavfile.read('morse-fan.wav')
time = np.linspace(0, len(signal) / sample_rate, num=len(signal))
time_interval = (20,23)
freq_axis, power = fft(signal, sample_rate, time_interval)
have_peak = find_major_peaks(power, freq_axis, freq_range=(1.8e4, 2.2e4))
morse_code = morse(signal, sample_rate, freq_range=(1.8e4, 2.2e4))

print(have_peak)
plt.plot(np.linspace(0, 28, num=len(morse_code)), morse_code)
plt.show()