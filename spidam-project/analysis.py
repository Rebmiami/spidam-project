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