# Other code can be imported here once programmed

import tkinter as tk

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
