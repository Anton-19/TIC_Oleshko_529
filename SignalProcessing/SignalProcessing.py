import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftshift, fftfreq
from scipy.signal import butter, sosfiltfilt
import os

# Дано
n = 500
Fs = 1000
F_max = 15
F_filter = 22

Dt_values = [2, 4, 8, 16]

# Формування часу
t = np.arange(n) / Fs

# Генераія випадкового сигналу
signal = np.random.randn(n)

# Фільтрація для обмеження F_max
w0 = F_max / (Fs / 2)
sos0 = butter(3, w0, 'low', output='sos')
signal = sosfiltfilt(sos0, signal)

# Списки для збереження
discrete_signals = []
discrete_spectrums = []
restored_signals = []
variances = []
snr_values = []

# Основний цикл
for Dt in Dt_values:

# Дискретизація
    discrete_signal = np.zeros(n)

    for i in range(0, round(n / Dt)):
        discrete_signal[i * Dt] = signal[i * Dt]

    discrete_signals += [list(discrete_signal)]

# Розрахунок спектру
    spectrum = np.abs(fftshift(fft(discrete_signal)))
    discrete_spectrums += [list(spectrum)]

# Відновлення через ФНЧ
    w = F_filter / (Fs / 2)
    sos = butter(3, w, 'low', output='sos')
    restored_signal = sosfiltfilt(sos, discrete_signal)

    restored_signals += [list(restored_signal)]

# Розрахунок похибки
    E1 = restored_signal - signal

    var_signal = np.var(signal)
    var_error = np.var(E1)

    variances += [var_error]
    snr_values += [var_signal / var_error]

# Частотна вісь
freq = fftshift(fftfreq(n, d=1/Fs))

# Функція побудови
def plot_2x2(x, y, title, x_label, y_label):

    fig, ax = plt.subplots(2, 2, figsize=(21/2.54, 14/2.54))

    line_width = 1
    font_size = 14

    s = 0
    for i in range(2):
        for j in range(2):
            ax[i][j].plot(x, y[s], linewidth=line_width)
            ax[i][j].set_title(f'Dt = {Dt_values[s]}', fontsize=font_size)
            s += 1

    fig.supxlabel(x_label, fontsize=font_size)
    fig.supylabel(y_label, fontsize=font_size)
    fig.suptitle(title, fontsize=font_size)

    os.makedirs("figures", exist_ok=True)
    fig.savefig('./figures/' + title + '.png', dpi=600)
    plt.close()

# Побудова графіків
# Дискретизовані сигнали
plot_2x2(t, discrete_signals,
         "Дискретизовані сигнали",
         "Час (с)",
         "Амплітуда")

# Спектри
plot_2x2(freq, discrete_spectrums,
         "Дискретні спектри сигналів",
         "Частота (Гц)",
         "Амплітуда спектру")

# Відновлені сигнали
plot_2x2(t, restored_signals,
         "Відновлені сигнали",
         "Час (с)",
         "Амплітуда")

# Графік дисперсії
plt.figure(figsize=(21/2.54, 14/2.54))
plt.plot(Dt_values, variances, linewidth=1)
plt.xlabel("Dt", fontsize=14)
plt.ylabel("Дисперсія", fontsize=14)
plt.title("Дисперсія vs Dt", fontsize=14)
plt.savefig('./figures/Дисперсія_vs_Dt.png', dpi=600)
plt.close()

# Графік ССШ
plt.figure(figsize=(21/2.54, 14/2.54))
plt.plot(Dt_values, snr_values, linewidth=1)
plt.xlabel("Dt", fontsize=14)
plt.ylabel("ССШ", fontsize=14)
plt.title("ССШ vs Dt", fontsize=14)
plt.savefig('./figures/ССШ_vs_Dt.png', dpi=600)
plt.close()
