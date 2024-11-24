import librosa
from audiodata import *

# Returns 3 values:
# (bool) Success: Returns true if the file was successfully loaded, false if there was an error
# (AudioData) Data: AudioData object containing data loaded from the file. Will be None if Success is false.
# (Exception) Exception: Returns an error to be handled by the caller. Will be None if Success is true.
def load_file(file_path):
    try:
        # Load the audio file using librosa
        audio_samples, sampling_rate = librosa.load(file_path, sr=None)
        # Return AudioData class
        return True, AudioData(audio_samples, sampling_rate), None
    except Exception as e:
        # Should errors be handled differently?
        # Implemented this way because I did not want this file to have to import any UI classes
        return False, None, e