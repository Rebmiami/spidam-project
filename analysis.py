import librosa
import audiodata
import numpy as np
from scipy.signal import welch, butter, lfilter, fftconvolve

# Todo: Remove magic numbers

def get_duration(data, file_path):
    return librosa.get_duration(y=data._audio_samples, sr=data._sampling_rate, n_fft=1024, hop_length=1024, center=True, path=file_path)

def get_spectrogram(data):
    return librosa.feature.melspectrogram(y=data._audio_samples, sr=data._sampling_rate, n_fft=1024, hop_length=1024, center=False)

def amplitude_to_db(spec):
    return librosa.amplitude_to_db(spec, ref=np.max)


def bandpass_filter(data, lowcut, highcut, sampling_rate, order=4):
    """Apply a bandpass filter to the data."""
    nyquist = 0.5 * sampling_rate
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band')
    return lfilter(b, a, data)

def compute_rt60_band(audio_samples, sampling_rate):
    """Compute RT60 using the Schroeder method for a given band."""
    # Create a Room Impulse Response (simplified for this demo)
    rir = fftconvolve(audio_samples, audio_samples[::-1], mode='full')
    rir = rir / np.max(np.abs(rir))  # Normalize to avoid overflow

    energy = rir[::-1].cumsum()[::-1]  # Schroeder's integral
    energy = np.maximum(energy, 1e-10)  # Avoid zeros to prevent log10 issues

    energy_db = 10 * np.log10(np.maximum(energy / np.max(energy), 1e-10))
    # Find the indices for -5 dB and -35 dB (equivalent to -60 dB total)
    try:
        idx_5db = np.where(energy_db <= -5)[0][0]
        idx_35db = np.where(energy_db <= -35)[0][0]
        rt60 = (idx_35db - idx_5db) / sampling_rate
    except IndexError:
        rt60 = float('nan')  # If indices are not found, return NaN

    return rt60

def compute_rt60(audio_samples, sampling_rate):
    """Compute RT60 for low, mid, and high frequency bands."""
    # Define frequency bands (in Hz)
    low_band = (20, 250)
    mid_band = (250, 2000)
    high_band = (2000, 20000)

    # Filter the signal into bands
    low_filtered = bandpass_filter(audio_samples, low_band[0], low_band[1], sampling_rate)
    mid_filtered = bandpass_filter(audio_samples, mid_band[0], mid_band[1], sampling_rate)
    high_filtered = bandpass_filter(audio_samples, high_band[0], high_band[1], sampling_rate)

    # Compute RT60 for each band
    rt60_low = compute_rt60_band(low_filtered, sampling_rate)
    rt60_mid = compute_rt60_band(mid_filtered, sampling_rate)
    rt60_high = compute_rt60_band(high_filtered, sampling_rate)

    return rt60_low, rt60_mid, rt60_high

def get_resonance(data, sr):
    frequencies, power = welch(data, sr, nperseg=4096)
    dominant_frequency = frequencies[np.argmax(power)]
    return dominant_frequency

def get_rt60_diff(rt60):
    low_rt60, mid_rt60, high_rt60 = rt60  # Unpack the tuple
    # Handle case where any RT60 value exceeds 0.5
    if low_rt60 > 0.5 or mid_rt60 > 0.5 or high_rt60 > 0.5:
        rt60_diff = "+" + str(round(rt60 - 0.5, 2))
    else:
        rt60_diff = str(round(rt60 - 0.5, 2))
    return rt60_diff
