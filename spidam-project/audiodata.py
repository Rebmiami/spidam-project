class AudioData:
    # Initalize an AudioData object with a collection of audio samples and a sample rate
    def __init__(self, _audio_samples, sampling_rate):
        self._audio_samples = _audio_samples
        self._sampling_rate = sampling_rate
        pass