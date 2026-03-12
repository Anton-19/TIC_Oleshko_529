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

# Генерація випадкового сигналу
signal = np.random.randn(n)

# Фільтрація для обмеження F_max
w0 = F_max / (Fs / 2)
sos0 = butter(3, w0, 'low', output='sos')
signal = sosfiltfilt(sos0, signal)

os.makedirs("figures", exist_ok=True)

# ДИСКРЕТИЗАЦІЯ
discrete_signals = []
discrete_spectrums = []
restored_signals = []
variances = []
snr_values = []

for Dt in Dt_values:
    # Дискретизація
    discrete_signal = np.zeros(n)
    for i in range(0, round(n / Dt)):
        discrete_signal[i * Dt] = signal[i * Dt]
    discrete_signals.append(discrete_signal)

    # Розрахунок спектру
    spectrum = np.abs(fftshift(fft(discrete_signal)))
    discrete_spectrums.append(spectrum)

    # Відновлення через ФНЧ
    w = F_filter / (Fs / 2)
    sos = butter(3, w, 'low', output='sos')
    restored_signal = sosfiltfilt(sos, discrete_signal)
    restored_signals.append(restored_signal)

    # Розрахунок похибки
    E1 = restored_signal - signal
    var_signal = np.var(signal)
    var_error = np.var(E1)

    variances.append(var_error)
    snr_values.append(var_signal / var_error)

freq = fftshift(fftfreq(n, d=1 / Fs))


def plot_2x2(x, y, title, x_label, y_label):
    fig, ax = plt.subplots(2, 2, figsize=(21 / 2.54, 14 / 2.54))
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
    fig.savefig('./figures/' + title + '.png', dpi=600, bbox_inches='tight')
    plt.close()


plot_2x2(t, discrete_signals, "Дискретизовані сигнали", "Час (с)", "Амплітуда")
plot_2x2(freq, discrete_spectrums, "Дискретні спектри сигналів", "Частота (Гц)", "Амплітуда спектру")
plot_2x2(t, restored_signals, "Відновлені сигнали", "Час (с)", "Амплітуда")

plt.figure(figsize=(21 / 2.54, 14 / 2.54))
plt.plot(Dt_values, variances, linewidth=1)
plt.xlabel("Dt", fontsize=14)
plt.ylabel("Дисперсія", fontsize=14)
plt.title("Дисперсія vs Dt", fontsize=14)
plt.savefig('./figures/Дисперсія_vs_Dt.png', dpi=600, bbox_inches='tight')
plt.close()

plt.figure(figsize=(21 / 2.54, 14 / 2.54))
plt.plot(Dt_values, snr_values, linewidth=1)
plt.xlabel("Dt", fontsize=14)
plt.ylabel("ССШ", fontsize=14)
plt.title("ССШ vs Dt", fontsize=14)
plt.savefig('./figures/ССШ_vs_Dt.png', dpi=600, bbox_inches='tight')
plt.close()

# КВАНТУВАННЯ
M_levels = [4, 16, 64, 256]
quantized_signals_list = []
variances_quant = []
snr_quant_values = []

for M in M_levels:
    # Квантування сигналу
    delta = (np.max(signal) - np.min(signal)) / (M - 1)

    # Нормалізуємо та квантуємо, щоб отримати рівно M рівнів
    normalized_signal = (signal - np.min(signal)) / (np.max(signal) - np.min(signal))
    quantize_signal = np.round(normalized_signal * (M - 1)) / (M - 1) * (np.max(signal) - np.min(signal)) + np.min(
        signal)

    quantized_signals_list.append(quantize_signal)
    quantize_levels = np.linspace(np.min(quantize_signal), np.max(quantize_signal), M)

    # Формування бітових послідовностей для таблиці
    quantize_bit = np.arange(0, M)
    bit_length = int(np.log2(M))
    quantize_bit_str = [format(bits, f'0{bit_length}b') for bits in quantize_bit]

    # Побудова таблиці квантування
    quantize_table = np.c_[np.round(quantize_levels, 14), quantize_bit_str]
    fig, ax = plt.subplots(figsize=(14 / 2.54, M / 2.54 + 1))
    table = ax.table(cellText=quantize_table, colLabels=['Значення сигналу', 'Кодова послідовність'], loc='center')
    table.set_fontsize(14)
    table.scale(1, 2)
    ax.axis('off')
    fig.savefig(f'./figures/Таблиця квантування для {M} рівнів.png', dpi=600, bbox_inches='tight')
    plt.close()

    # Кодування сигналу у біти
    bits_sequence = []
    for signal_value in quantize_signal:
        # Знаходимо найближчий рівень для уникнення похибок округлення
        index = np.argmin(np.abs(quantize_levels - signal_value))
        bits_sequence.append(quantize_bit_str[index])

    # Перетворення у список цілих чисел [0, 1, 0, 0, ...]
    bits_array = [int(item) for item in list(''.join(bits_sequence))]

    # Побудова графіку кодової послідовності
    fig, ax = plt.subplots(figsize=(21 / 2.54, 14 / 2.54))
    x_axis = np.arange(len(bits_array))

    ax.step(x_axis, bits_array, where='post', linewidth=0.5, alpha=0.5)
    ax.fill_between(x_axis, bits_array, step="post", alpha=0.25)

    ax.set_title(f"Кодова послідовність сигналу при кількості рівнів квантування {M}")
    ax.set_xlabel("Біти")
    ax.set_ylabel("Амплітуда сигналу")
    ax.grid(True)
    fig.savefig(f'./figures/Кодова послідовність при {M}.png', dpi=600, bbox_inches='tight')
    plt.close()

    # Розрахунок дисперсії та ССШ
    noise = quantize_signal - signal
    var_signal = np.var(signal)
    var_noise = np.var(noise)

    variances_quant.append(var_noise)
    snr_quant_values.append(var_signal / var_noise if var_noise != 0 else float('inf'))

# Побудова графіка 2х2 цифрових сигналів
fig, ax = plt.subplots(2, 2, figsize=(21 / 2.54, 14 / 2.54))
idx = 0
for i in range(2):
    for j in range(2):
        ax[i][j].step(t, quantized_signals_list[idx], where='post', linewidth=1)
        idx += 1
fig.suptitle("Цифрові сигнали з рівнями квантування (4, 16, 64, 256)")
fig.supxlabel("Час (секунди)")
fig.supylabel("Амплітуда сигналу")
fig.savefig('./figures/Цифрові_сигнали_квантування.png', dpi=600, bbox_inches='tight')
plt.close()

# Графік залежності дисперсії
plt.figure(figsize=(21 / 2.54, 14 / 2.54))
plt.plot(M_levels, variances_quant, linewidth=1)
plt.grid(True)
plt.xlabel("Кількість рівнів квантування")
plt.ylabel("Дисперсія")
plt.title("Залежність дисперсії від кількості рівнів квантування")
plt.savefig('./figures/Дисперсія_vs_М_Квантування.png', dpi=600, bbox_inches='tight')
plt.close()

# Графік залежності ССШ
plt.figure(figsize=(21 / 2.54, 14 / 2.54))
plt.plot(M_levels, snr_quant_values, linewidth=1)
plt.grid(True)
plt.xlabel("Кількість рівнів квантування")
plt.ylabel("ССШ")
plt.title("Залежність співвідношення сигнал-шум від кількості рівнів квантування")
plt.savefig('./figures/ССШ_vs_М_Квантування.png', dpi=600, bbox_inches='tight')
plt.close()
