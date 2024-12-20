import librosa
import numpy as np
from scipy.signal import welch, butter, sosfilt, fftconvolve

# Todo: Remove magic numbers

def get_duration(data):
    """Returns duration of an AudioData object in seconds"""
    return librosa.get_duration(y=data._audio_samples, sr=data._sampling_rate, n_fft=1024, hop_length=1024, center=True)

def get_spectrogram(data):
    """Returns a mel spectrogram of the AudioData object"""
    return librosa.feature.melspectrogram(y=data._audio_samples, sr=data._sampling_rate, n_fft=1024, hop_length=1024, center=False)

def amplitude_to_db(spec):
    """Converts a spectrogram from amplitude to decibels"""
    return librosa.amplitude_to_db(spec, ref=np.max)


def bandpass_filter(audio_samples, lowcut, highcut, sampling_rate, order=4):
    """Apply a bandpass filter to the data."""
    nyquist = 0.5 * sampling_rate  # Nyquist frequency is half the sampling rate.
    low = lowcut / nyquist  # Normalize low cutoff frequency.
    high = highcut / nyquist  # Normalize high cutoff frequency.
    sos = butter(order, [low, high], btype='bandpass', output="sos")  # Design a Butterworth bandpass filter.
    return sosfilt(sos, audio_samples)  # Apply the filter to the input signal.

def compute_energy_band(filtered_samples):
    """Compute energy in decibels using the Schroeder method for a given band."""
    # Create a Room Impulse Response (simplified for this demo)
    rir = fftconvolve(filtered_samples, filtered_samples[::-1], mode='full')  # Autocorrelation of the signal. (calculation of the RIR value)
    rir = rir / np.max(np.abs(rir))  # Normalize to avoid overflow. (calculation so the minimum value is one)

    energy = (np.square(rir[::-1]))[::-1].cumsum()[::-1]  # defines the decay curve of the audio using schroeder's method (cumulative sum of the RIR array in reverse)
    energy = np.maximum(energy, 1e-10)  # Avoid zero values by setting a floor at 1e - 10

    energy_db = 10 * np.log10(np.maximum(energy / np.max(energy), 1e-10))  # Convert energy to dB scale.

    return energy_db

def compute_rt60_band(energy_db, sampling_rate):
    """Compute RT60 using the Schroeder method for a given band."""

    # Find the indices for -5 dB and -65 dB points
    try:
        idx_5db = np.where(energy_db <= -5)[0][0]  # Time index where energy drops to -5 dB.
        idx_65db = np.where(energy_db <= -65)[0][0]  # Time index where energy drops to -65 dB.
        rt60 = (idx_65db - idx_5db) / sampling_rate  # Convert time difference to seconds.
    except IndexError:
        rt60 = float('nan')  # If indices are not found, return NaN.

    return rt60

def compute_bands(data):
    """Apply bandpass filters to data for low, mid, and high frequency bands."""
    # Define frequency bands (in Hz)
    low_band = (20, 250)
    mid_band = (250, 2000)
    high_band = (2000, 20000)

    # Filter the signal into bands
    low_filtered = bandpass_filter(data._audio_samples, low_band[0], low_band[1], data._sampling_rate)
    mid_filtered = bandpass_filter(data._audio_samples, mid_band[0], mid_band[1], data._sampling_rate)
    high_filtered = bandpass_filter(data._audio_samples, high_band[0], high_band[1], data._sampling_rate)

    return low_filtered, mid_filtered, high_filtered

def compute_energy(low_filtered, mid_filtered, high_filtered, sampling_rate):
    """Compute energy in decibels for low, mid, and high frequency bands."""

    # Compute RT60 for each band
    energy_low = compute_energy_band(low_filtered)
    energy_mid = compute_energy_band(mid_filtered)
    energy_high = compute_energy_band(high_filtered)

    return energy_low, energy_mid, energy_high

def compute_rt60(energy_low, energy_mid, energy_high, sampling_rate):
    """Compute RT60 for low, mid, and high frequency bands using energy."""

    # Compute RT60 for each band
    rt60_low = compute_rt60_band(energy_low, sampling_rate)
    rt60_mid = compute_rt60_band(energy_mid, sampling_rate)
    rt60_high = compute_rt60_band(energy_high, sampling_rate)

    return rt60_low, rt60_mid, rt60_high

def get_resonance(data):
    frequencies, power = welch(data._audio_samples, data._sampling_rate, nperseg=4096)
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
