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

from analysis import get_rt60_diff, compute_rt60

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
        audio_resonance = analysis.get_resonance(audio_samples, sampling_rate)
        rt60 = analysis.compute_rt60(audio_samples, sampling_rate)
        display_waveform()

        # RT60 difference value is temporary
        display_summary(audio_duration, audio_resonance, rt60)
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

    # Compute RT60 for low, mid, and high frequency bands
    rt60_values = compute_rt60(audio_samples, sampling_rate)  # Assuming compute_rt60 is already defined

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
    update_status("RT60 Analysis Complete")

summary_frame = tk.Frame(master=root, relief="sunken", borderwidth=1)
summary_frame.pack(side=tk.TOP, fill=tk.X)

summary_text = tk.Label(master=summary_frame, text="Audio must be loaded before summary can be displayed.")
summary_text.pack(side=tk.BOTTOM)

def display_summary(duration, resonance, rt60):
    # Convert duration to min:sec format
    sec = duration
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
    for value in rt60:  # rt60 is assumed to be a tuple (low_rt60, mid_rt60, high_rt60)
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
            f"Duration: {duration_text} | "
            f"Resonance: {round(resonance, 2)} | "
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

tk.mainloop()
