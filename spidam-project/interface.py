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
# Todo: Replace remaining invocations of the below variables
audio_samples = None
sampling_rate = None

def load_audio_file():
    update_status("Awaiting file. ")
    """Loads an audio file and displays its waveform."""
    global audio_data, audio_samples, sampling_rate, audio_duration
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
        audio_samples = data._audio_samples
        sampling_rate = data._sampling_rate
        audio_duration = analysis.get_duration(data, file_path)
        display_waveform()
        update_status("File loaded successfully. ")
    else:
        # Otherwise, show an error message
        messagebox.showerror("Error", f"Failed to load audio file: {error}")
        update_status("File loading failed")

def display_waveform():
    """Displays the waveform of the loaded audio."""
    if audio_samples is None:
        messagebox.showwarning("Warning", "No audio file loaded.")
        return

    # Clear the previous figure and plot the waveform
    fig.clear()
    ax = fig.add_subplot()
    display.waveshow(audio_samples, sr=sampling_rate, ax=ax)
    ax.set_title("Waveform")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Amplitude")
    canvas.draw()
    update_status("Finished drawing waveform. ")

def display_spectrogram():
    if audio_samples is None:
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
    if audio_samples is None:
        messagebox.showwarning("Warning", "No audio file loaded.")
        return

    rt60_values = analysis.compute_rt60(audio_samples, sampling_rate)
    fig.clear()
    ax = fig.add_subplot()
    ax.bar(["Low", "Mid", "High"], rt60_values, color=['blue', 'green', 'red'])
    ax.set_title("RT60 Analysis")
    ax.set_xlabel("Frequency Band")
    ax.set_ylabel("RT60 (seconds)")
    canvas.draw()
    update_status("RT60 Analysis Complete")
    
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

tk.mainloop()
