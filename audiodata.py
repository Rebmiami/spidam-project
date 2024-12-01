import analysis

class AudioData:
    # Initalize an AudioData object with a collection of audio samples and a sample rate
    def __init__(self, _audio_samples, _sampling_rate):
        self._audio_samples = _audio_samples
        self._sampling_rate = _sampling_rate

        # Perform analysis and store results
        self._audio_duration = analysis.get_duration(self)
        self._audio_resonance = analysis.get_resonance(self)
        self._rt60 = analysis.compute_rt60(self)
        pass