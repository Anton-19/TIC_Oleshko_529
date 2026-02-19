import numpy as np
import matplotlib.pyplot as plt
from scipy import signal, fft
import os

# Вхідні параметри
n = 500
Fs = 1000
F_max = 15


# Генерація випадкового сигналу
random_signal = np.random.normal(0, 10, n)

# Формування осі часу
time = np.arange(n) / Fs

#  Розрахунок ФНЧ
w = F_max / (Fs / 2)

sos = signal.butter(3, w, btype='low', output='sos')

# Фільтрація сигналу
filtered_signal = signal.sosfiltfilt(sos, random_signal)

# Функція для побудови графіку
def plot_graph(x, y, title, xlabel, ylabel):
    fig, ax = plt.subplots(figsize=(21/2.54, 14/2.54))
    ax.plot(x, y, linewidth=1)
    ax.set_xlabel(xlabel, fontsize=14)
    ax.set_ylabel(ylabel, fontsize=14)
    ax.set_title(title, fontsize=14)
    fig.savefig("figures/" + title + ".png", dpi=600)
    plt.close()

# Побдова сигналу
plot_graph(
    time,
    filtered_signal,
    "Сигнал з максимальною частотою F_max = 15 Гц",
    "Час (секунди)",
    "Амплітуда сигналу"
)

#  Розрахунок спектру
spectrum = fft.fft(filtered_signal)
spectrum_shifted = np.abs(fft.fftshift(spectrum))

freqs = fft.fftfreq(n, 1/Fs)
freqs_shifted = fft.fftshift(freqs)

#  Побудова спектру
plot_graph(
    freqs_shifted,
    spectrum_shifted,
    "Спектр сигналу з максимальною частотою F_max = 15 Гц",
    "Частота (Гц)",
    "Амплітуда спектру"
)

