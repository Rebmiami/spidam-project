import analysis

class AudioData:
    # Initalize an AudioData object with a collection of audio samples and a sample rate
    def __init__(self, _audio_samples, _sampling_rate):
        self._audio_samples = _audio_samples
        self._sampling_rate = _sampling_rate

        # Perform analysis and store results
        self._audio_duration = analysis.get_duration(self)
        self._audio_resonance = analysis.get_resonance(self)

        low_filtered, mid_filtered, high_filtered = analysis.compute_bands(self)
        energy_low, energy_mid, energy_high = analysis.compute_energy(low_filtered, mid_filtered, high_filtered, _sampling_rate)
        rt60_low, rt60_mid, rt60_high = analysis.compute_rt60(energy_low, energy_mid, energy_high, _sampling_rate)

        self._filtered = (low_filtered, mid_filtered, high_filtered)
        self._energy = (energy_low, energy_mid, energy_high)
        self._rt60 = (rt60_low, rt60_mid, rt60_high)
        pass