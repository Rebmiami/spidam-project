import os
import sys

import librosa
import soundfile as sf
from audiodata import *

# Returns 3 values:
# (bool) Success: Returns true if the file was successfully loaded, false if there was an error
# (AudioData) Data: AudioData object containing data loaded from the file. Will be None if Success is false.
# (Exception) Exception: Returns an error to be handled by the caller. Will be None if Success is true.
def load_file(file_path):
    try:
        # Load the audio file using librosa
        audio_samples, sampling_rate = librosa.load(file_path, sr=None)

        ext = file_path.split('.')[-1]
        if ext == 'mp3':
            # If file is a mp3, convert to wav

            root_pkg_name, _, _ = __name__.partition('.')
            root_pkg_module = sys.modules[root_pkg_name]
            root_pkg_dirname = os.path.dirname(root_pkg_module.__file__)
            path = os.path.join(root_pkg_dirname, "audio", "converted_to_wav.wav")
            sf.write(path, audio_samples, sampling_rate)

        # Return AudioData class
        return True, AudioData(audio_samples, sampling_rate), None
    except Exception as e:
        # Should errors be handled differently?
        # Implemented this way because I did not want this file to have to import any UI classes
        return False, None, e