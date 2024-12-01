import loading
import analysis
import tkinter as tk
from tkinter import filedialog, messagebox

from numpy import *
from librosa import display

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from mpl_toolkits.axes_grid1 import make_axes_locatable

root = tk.Tk()
root.wm_title("Audio Analysis")

fig = Figure(figsize=(8, 6))
t = linspace(0, 2, 1000)


canvas = FigureCanvasTkAgg(fig, master=root)
canvas.draw()
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

# Variable to store the loaded audio
audio_data = None


def load_audio_file():
    update_status("Awaiting file. ")
    """Loads an audio file and displays its waveform."""
    global audio_data
    file_path = filedialog.askopenfilename(
        title="Select Audio File",
        filetypes=(("Audio Files", "*.wav *.mp3"), ("All Files", "*.*")),
        initialdir="./audio")
    if not file_path:
        update_status("File selection canceled. ")
        return  # User cancelled the file dialog

    # Attempt to load the file
    success, data, error = loading.load_file(file_path)
    if success:
        # If successful, display the waveform
        audio_data = data
        display_waveform()

        # RT60 difference value is temporary
        display_summary()
        update_status("File loaded successfully. ")
    else:
        # Otherwise, show an error message
        messagebox.showerror("Error", f"Failed to load audio file: {error}")
        update_status("File loading failed")

def display_waveform():
    """Displays the waveform of the loaded audio."""
    if audio_data is None:
        messagebox.showwarning("Warning", "No audio file loaded.")
        return

    # Clear the previous figure and plot the waveform
    fig.clear()
    ax = fig.add_subplot()
    display.waveshow(audio_data._audio_samples, sr=audio_data._sampling_rate, ax=ax)
    ax.set_title("Waveform")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Amplitude")
    canvas.draw()
    update_status("Finished drawing waveform. ")

def display_spectrogram():
    if audio_data is None:
        messagebox.showwarning("Warning", "No audio file loaded.")
        return

    fig.clear()
    ax = fig.add_subplot()

    spec = analysis.get_spectrogram(audio_data)
    mel = display.specshow(data=analysis.amplitude_to_db(spec), y_axis='linear', x_axis='time', ax=ax, cmap='inferno')

    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.1)
    plt.colorbar(mel, cax=cax, label='Decibels', shrink=0.5, fraction=0.046, pad=0.04)

    ax.set_title("Spectrogram")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Frequency (Hz)")
    canvas.draw()
    update_status("Finished drawing spectrogram. ")

def display_rt60_analysis():
    """Displays RT60 values for different frequency bands."""
    if audio_data is None:
        messagebox.showwarning("Warning", "No audio file loaded.")
        return

    # Retrieve RT60 for low, mid, and high frequency bands
    rt60_values = audio_data._rt60

    # Clear the previous figure and set up the bar chart
    fig.clear()
    ax = fig.add_subplot(1, 1, 1)
    ax.bar(["Low", "Mid", "High"], rt60_values, color=['blue', 'green', 'red'])
    ax.set_title("RT60 Analysis")
    ax.set_xlabel("Frequency Band")
    ax.set_ylabel("RT60 (seconds)")
    ax.set_ylim(0, max(rt60_values) * 1.2)  # Add some padding to the y-axis

    # Update the canvas to display the new graph
    canvas.draw()
    update_status("Finished drawing RT60 graph")

def display_filtered_waveforms():
    """Displays the waveform of the loaded audio after being run through each filter."""
    if audio_data is None:
        messagebox.showwarning("Warning", "No audio file loaded.")
        return

    # Clear the previous figure and plot the waveform
    fig.clear()
    ax = fig.add_subplot()

    # TODO: This is a hacky implementation and should only be kept as long as it is needed for debugging

    # Define frequency bands (in Hz)
    low_band = (20, 250)
    mid_band = (250, 2000)
    high_band = (2000, 20000)

    # Filter the signal into bands
    low_filtered = analysis.bandpass_filter(audio_data._audio_samples, low_band[0], low_band[1], audio_data._sampling_rate)
    mid_filtered = analysis.bandpass_filter(audio_data._audio_samples, mid_band[0], mid_band[1], audio_data._sampling_rate)
    high_filtered = analysis.bandpass_filter(audio_data._audio_samples, high_band[0], high_band[1], audio_data._sampling_rate)

    display.waveshow(low_filtered, sr=audio_data._sampling_rate, ax=ax, label="Low freq")
    display.waveshow(mid_filtered, sr=audio_data._sampling_rate, ax=ax, label="Mid freq")
    display.waveshow(high_filtered, sr=audio_data._sampling_rate, ax=ax, label="High freq")

    ax.set_title("Waveform")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Amplitude")
    ax.legend(loc="lower right")
    canvas.draw()
    update_status("Finished drawing filtered waveforms. ")

# This option should be removed or hidden in the final program
def display_impulse_response():
    if audio_data is None:
        messagebox.showwarning("Warning", "No audio file loaded.")
        return
    from scipy.signal import fftconvolve
    import numpy as np

    # Clear the previous figure and plot the waveform
    fig.clear()
    ax = fig.add_subplot()

    # Create a Room Impulse Response (simplified for this demo)
    rir = fftconvolve(audio_data._audio_samples, audio_data._audio_samples[::-1], mode='full')  # Autocorrelation of the signal. (calculation of the RIR value)
    rir = rir / np.max(np.abs(rir))  # Normalize to avoid overflow. (calculation so the minimum value is one)

    energy = rir[::-1].cumsum()[::-1]  # defines the decay curve of the audio using schroeder's method (cumulative sum of the RIR array in reverse)
    energy = np.maximum(energy, 1e-10)  # Avoid zero values by setting a floor at 1e - 10

    energy_db = 10 * np.log10(np.maximum(energy / np.max(energy), 1e-10))  # Convert energy to dB scale.

    # Find the indices for -5 dB and -35 dB points
    try:
        idx_5db = np.where(energy_db <= -5)[0][0]  # Time index where energy drops to -5 dB.
        idx_35db = np.where(energy_db <= -35)[0][0]  # Time index where energy drops to -35 dB.
        rt60 = (idx_35db - idx_5db) / audio_data._sampling_rate  # Convert time difference to seconds.
    except IndexError:
        rt60 = float('nan')  # If indices are not found, return NaN.

    # Change this to change which graph is displayed
    debugGraph = sliderRT60Debug.get()

    if debugGraph == 1:
        display.waveshow(rir, sr=audio_data._sampling_rate, ax=ax, label="Reverse impulse response")
    elif debugGraph == 2:
        display.waveshow(energy, sr=audio_data._sampling_rate, ax=ax, label="Energy")
    else:
        display.waveshow(energy_db, sr=audio_data._sampling_rate, ax=ax, label="Energy (decibels)")


    ax.set_title("Testing")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Amplitude")
    ax.legend(loc="lower right")
    canvas.draw()
    update_status("Finished drawing RT60 test graph. ")

summary_frame = tk.Frame(master=root, relief="sunken", borderwidth=1)
summary_frame.pack(side=tk.TOP, fill=tk.X)

summary_text = tk.Label(master=summary_frame, text="Summary will display after audio is loaded.")
summary_text.pack(side=tk.BOTTOM)

def display_summary():
    # Convert duration to min:sec format
    sec = audio_data._audio_duration
    min = 0
    while sec >= 60:
        min+=1
        sec -= 60
    if sec < 10:
        duration_text = str(min) + ":0" + str(round(sec, 3))
    else:
        duration_text = str(min) + ":" + str(round(sec, 3))

    # Calculate RT60 differences for all three bands
    rt60_diff = []
    for value in audio_data._rt60:  # rt60 is a tuple (low_rt60, mid_rt60, high_rt60)
        if value > 0.5:
            diff = "+" + str(round(value - 0.5, 2))
        else:
            diff = str(round(value - 0.5, 2))  # Explicitly show negative difference
        rt60_diff.append(diff)

    # Format the differences for display
    rt60_diff_text = f"Low: {rt60_diff[0]}, Mid: {rt60_diff[1]}, High: {rt60_diff[2]}"

    # Update the summary text
    summary_text.config(
        text=(
            f"Duration: {duration_text} sec | "
            f"Resonance: {round(audio_data._audio_resonance, 2)} Hz | "
            f"RT60 Differences vs. 0.5 Seconds: {rt60_diff_text}"
        )
    )

status_frame = tk.Frame(master=root, relief="sunken", borderwidth=1)
status_frame.pack(side=tk.BOTTOM, fill=tk.X)

status_label = tk.Label(master=status_frame, text="Ready")
status_label.pack(side=tk.LEFT)

def update_status(message):
    status_label.config(text=message)


control_frame = tk.Frame(master=root)
control_frame.pack(side=tk.BOTTOM, fill=tk.X)

# Add buttons for GUI interactions
load_button = tk.Button(master=control_frame, text="Load Audio File", command=load_audio_file)
load_button.pack(side=tk.LEFT)

exit_button = tk.Button(master=control_frame, text="Exit", command=root.quit)
exit_button.pack(side=tk.RIGHT)

buttonHist = tk.Button(master=control_frame, text="Waveform", command=display_waveform)
buttonHist.pack(side=tk.LEFT)

buttonLFTest = tk.Button(master=control_frame, text="MEL Spectrogram", command=display_spectrogram)
buttonLFTest.pack(side=tk.LEFT)

buttonRT60 = tk.Button(master=control_frame, text="RT60 Analysis", command=display_rt60_analysis)
buttonRT60.pack(side=tk.LEFT)

buttonFiltered = tk.Button(master=control_frame, text="Filtered Waveforms", command=display_filtered_waveforms)
buttonFiltered.pack(side=tk.LEFT)

# These two options should be removed or hidden in the final version
sliderRT60Debug = tk.Scale(master=control_frame, from_=1, to=3)
sliderRT60Debug.pack(side=tk.LEFT)

buttonRT60Debug = tk.Button(master=control_frame, text="RT60 Debug", command=display_impulse_response)
buttonRT60Debug.pack(side=tk.LEFT)

tk.mainloop()
