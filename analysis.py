import librosa
import audiodata
import numpy as np

# Todo: Remove magic numbers

def get_duration(data, file_path):
    return librosa.get_duration(y=data._audio_samples, sr=data._sampling_rate, n_fft=1024, hop_length=1024, center=True, path=file_path)

def get_spectrogram(data):
    return librosa.feature.melspectrogram(y=data._audio_samples, sr=data._sampling_rate, n_fft=1024, hop_length=1024, center=False)

def amplitude_to_db(spec):
    return librosa.amplitude_to_db(spec, ref=np.max)

import numpy as np
from scipy.signal import fftconvolve
from scipy.signal import welch

def compute_rt60(audio_samples, sampling_rate):
    """Compute RT60 using the Schroeder method."""
    # Create a Room Impulse Response (simplified for this demo)
    rir = fftconvolve(audio_samples, audio_samples[::-1])
    rir = rir / np.max(np.abs(rir))  # Normalize to avoid overflow

    energy = rir[::-1].cumsum()[::-1]  # Schroeder's integral
    energy = np.maximum(energy, 1e-10)  # Avoid zeros to prevent log10 issues

    energy_db = 10 * np.log10(energy / np.max(energy))

    # Find the indices for -5 dB and -35 dB (equivalent to -60 dB total)
    try:
        idx_5db = np.where(energy_db <= -5)[0][0]
        idx_35db = np.where(energy_db <= -35)[0][0]
        rt60 = (idx_35db - idx_5db) / sampling_rate
    except IndexError:
        rt60 = float('nan')  # If indices are not found, return NaN

    return rt60

def get_resonance(data, sr):
    frequencies, power = welch(data, sr, nperseg=4096)
    dominant_frequency = frequencies[np.argmax(power)]
    return dominant_frequency

def get_rt60_diff(rt60):
    if (rt60 > 0.5):
        rt60_diff = "+" + str(round(rt60 - 0.5, 2))
    else:
        rt60_diff = str(round(rt60 - 0.5, 2))
    return rt60_diff