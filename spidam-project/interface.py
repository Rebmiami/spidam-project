import loading
import analysis
import tkinter as tk

from numpy import *
from librosa import display

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
# Todo: Store an AudioData object here directly?
audio_samples = None
sampling_rate = None

def load_audio_file():
    """Loads an audio file and displays its waveform."""
    global audio_samples, sampling_rate, audio_duration
    file_path = tk.filedialog.askopenfilename(
        title="Select Audio File",
        filetypes=(("Audio Files", "*.wav *.mp3"), ("All Files", "*.*"))
    )
    if not file_path:
        return  # User cancelled the file dialog

    # Attempt to load the file
    success, data, error = loading.load_file(file_path)
    if success:
        # If successful, display the waveform
        audio_samples = data._audio_samples
        sampling_rate = data._sampling_rate
        audio_duration = analysis.get_duration(data, file_path)
        display_waveform()
    else:
        # Otherwise, show an error message
        tk.messagebox.showerror("Error", f"Failed to load audio file: {error}")


def display_waveform():
    """Displays the waveform of the loaded audio."""
    if audio_samples is None:
        tk.messagebox.showwarning("Warning", "No audio file loaded.")
        return

    # Clear the previous figure and plot the waveform
    fig.clear()
    ax = fig.add_subplot()
    display.waveshow(audio_samples, sr=sampling_rate, ax=ax)
    ax.set_title("Waveform")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Amplitude")
    canvas.draw()

def display_spectrogram():
    if audio_samples is None:
        tk.messagebox.showwarning("Warning", "No audio file loaded.")
        return

    fig.clear()
    ax = fig.add_subplot()

    spec = analysis.get_spectrogram()
    mel = display.specshow(data=librosa.amplitude_to_db(spec, ref=max), y_axis='linear', x_axis='time', ax=ax, cmap='inferno')

    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.1)
    plt.colorbar(mel, cax=cax, label='Decibels', shrink=0.5, fraction=0.046, pad=0.04)

    ax.set_title("Spectrogram")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Frequency (Hz)")
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

buttonHist = tk.Button(master=root, text="Waveform", command=display_waveform)
buttonHist.pack(side=tk.LEFT)

buttonLFTest = tk.Button(master=root, text="MEL Spectrogram", command=display_spectrogram)
buttonLFTest.pack(side=tk.LEFT)

button1 = tk.Button(master=root, text="Test Graph 1", command=_change_graph_1)
button1.pack(side=tk.LEFT)

button2 = tk.Button(master=root, text="Test Graph 2", command=_change_graph_2)
button2.pack(side=tk.LEFT)

button3 = tk.Button(master=root, text="Test Graph 3", command=_change_graph_3)
button3.pack(side=tk.LEFT)

tk.mainloop()
