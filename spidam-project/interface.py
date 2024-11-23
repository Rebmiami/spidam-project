# Other code can be imported here once programmed

import tkinter as tk

from tkinter import filedialog, messagebox
import librosa
import librosa.display
import numpy as np

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from numpy import *

root = tk.Tk()
root.wm_title("Audio Analysis")

fig = Figure(figsize=(8, 6))
t = linspace(0, 2, 1000)

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.draw()
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

# Variable to store the loaded audio
audio_data = None
sampling_rate = None

def load_audio_file():
    """Loads an audio file and displays its waveform."""
    global audio_data, sampling_rate
    file_path = filedialog.askopenfilename(
        title="Select Audio File",
        filetypes=(("Audio Files", "*.wav *.mp3"), ("All Files", "*.*"))
    )
    if not file_path:
        return  # User cancelled the file dialog

    try:
        # Load the audio file using librosa
        audio_data, sampling_rate = librosa.load(file_path, sr=None)
        display_waveform()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load audio file: {e}")

def display_waveform():
    """Displays the waveform of the loaded audio."""
    if audio_data is None:
        messagebox.showwarning("Warning", "No audio file loaded.")
        return

    # Clear the previous figure and plot the waveform
    fig.clear()
    ax = fig.add_subplot()
    librosa.display.waveshow(audio_data, sr=sampling_rate, ax=ax)
    ax.set_title("Waveform")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Amplitude")
    canvas.draw()

# Add buttons for GUI interactions
load_button = tk.Button(master=root, text="Load Audio File", command=load_audio_file)
load_button.pack(side=tk.LEFT)

exit_button = tk.Button(master=root, text="Exit", command=root.quit)
exit_button.pack(side=tk.RIGHT)

def _change_graph_1():
    fig.clear()
    fig.add_subplot().plot(t, 2 * sin(2 * pi * t))
    canvas.draw()

def _change_graph_2():
    fig.clear()
    fig.add_subplot().plot(t, t % 1)
    canvas.draw()

def _change_graph_3():
    fig.clear()
    fig.add_subplot().plot(t, exp(t))
    canvas.draw()

button1 = tk.Button(master=root, text="Graph 1", command=_change_graph_1)
button1.pack(side=tk.LEFT)

button2 = tk.Button(master=root, text="Graph 2", command=_change_graph_2)
button2.pack(side=tk.LEFT)

button3 = tk.Button(master=root, text="Graph 3", command=_change_graph_3)
button3.pack(side=tk.LEFT)

tk.mainloop()
