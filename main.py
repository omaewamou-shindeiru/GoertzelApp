import tkinter as tk
from tkinter import filedialog

import librosa
import math


def goertzel(samples, sample_rate, target_freq):
    # Calculate the coefficients
    omega = 2.0 * math.pi * target_freq / sample_rate
    coeff = 2.0 * math.cos(omega)

    # Initialize the variables
    Q1 = 0
    Q2 = 0
    for sample in samples:
        Q0 = coeff * Q1 - Q2 + sample
        Q2 = Q1
        Q1 = Q0

    # Calculate the magnitude
    power = Q1 ** 2 + Q2 ** 2 - coeff * Q1 * Q2
    magnitude = abs(power ** 0.5)
    normalized_magnitude = 2 * magnitude / sample_rate
    return normalized_magnitude


class App:
    def __init__(self, master):
        self.master = master
        self.freqs = []
        self.histogram = []
        self.filepath = ""

        # create GUI elements
        self.file_label = tk.Label(text="No audio file selected.")
        self.file_button = tk.Button(text="Select audio file", command=self.select_file)
        self.freq_label = tk.Label(text="Enter frequency/frequencies (comma-separated, Hz):")
        self.freq_entry = tk.Entry()
        self.freq_button = tk.Button(text="Calculate & Build Histogram", command=self.calculate_histogram)
        self.hist_label = tk.Label(text="Histogram:")
        self.hist_canvas = tk.Canvas(width=500, height=200)

        # layout GUI elements
        self.file_label.pack()
        self.file_button.pack()
        self.freq_label.pack()
        self.freq_entry.pack()
        self.freq_button.pack()
        self.hist_label.pack()
        self.hist_canvas.pack()

    def select_file(self):
        self.filepath = filedialog.askopenfilename()
        self.file_label.config(text="Selected file: {}".format(self.filepath))

    def calculate_histogram(self):
        if not self.filepath:
            return

        # get user-defined frequencies
        freq_str = self.freq_entry.get().strip()
        self.freqs = [int(f) for f in freq_str.split(",")]

        # load file info - sample rate and the sample array
        samples, sample_rate = librosa.load(self.filepath, sr=None, mono=True)

        # calculate histogram for each frequency
        self.histogram = []
        max_magnitude = 0
        for freq in self.freqs:
            magnitude = goertzel(samples, sample_rate, freq)
            self.histogram.append(magnitude)
            if magnitude > max_magnitude:
                max_magnitude = magnitude

        # redraw histogram canvas
        self.hist_canvas.delete("all")
        x0 = 0
        y0 = 200
        bar_width = 500 / len(self.histogram)
        for i, magnitude in enumerate(self.histogram):
            x1 = x0 + bar_width
            y1 = 250 - magnitude * 200 / max_magnitude
            self.hist_canvas.create_rectangle(x0, y0, x1, y1, fill="blue")

            freq_label = str(round(self.freqs[i], 4))
            hist_label = str(round(self.histogram[i], 4))

            self.hist_canvas.create_text(x0 + 25, y0 - 20, anchor=tk.N, text=freq_label)
            self.hist_canvas.create_text(x0 + 25, y0 - 50, anchor=tk.N, text=hist_label)
            x0 = x1


def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()


if __name__ == '__main__':
    main()
