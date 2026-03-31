import random
import string
import collections
import math
import matplotlib.pyplot as plt

surname = "олешко"
group_num = "529"
student_num = 7

N_sequence = 100
original_sequences = []

# Тестова послідовність 1
list1 = ['1'] * student_num
list0 = ['0'] * (N_sequence - student_num)
seq1_list = list1 + list0
random.shuffle(seq1_list)
original_sequence_1 = ''.join(seq1_list)
original_sequences.append(original_sequence_1)

# Тестова послідовність 2
list1 = list(surname)
list0 = ['0'] * (N_sequence - len(surname))
seq2_list = list1 + list0
original_sequence_2 = ''.join(seq2_list)
original_sequences.append(original_sequence_2)

# Тестова послідовність 3
list1 = list(surname)
list0 = ['0'] * (N_sequence - len(surname))
seq3_list = list1 + list0
random.shuffle(seq3_list)
original_sequence_3 = ''.join(seq3_list)
original_sequences.append(original_sequence_3)

# Тестова послідовність 4
letters_seq4 = list(surname) + list(group_num)
n_repeats = N_sequence // len(letters_seq4)
remainder = N_sequence % len(letters_seq4)
seq4_list = letters_seq4 * n_repeats + letters_seq4[:remainder]
original_sequence_4 = ''.join(seq4_list)
original_sequences.append(original_sequence_4)

# Тестова послідовність 5
letters_seq5 = list(surname[:2]) + list(group_num)
seq5_list = []
for char in letters_seq5:
    seq5_list.extend([char] * int(0.2 * N_sequence))
random.shuffle(seq5_list)
original_sequence_5 = ''.join(seq5_list)
original_sequences.append(original_sequence_5)

# Тестова послідовність 6
letters_only = list(surname[:2])
digits_only = list(group_num)
seq6_list = []
for _ in range(int(0.7 * N_sequence)):
    seq6_list.append(random.choice(letters_only))
for _ in range(int(0.3 * N_sequence)):
    seq6_list.append(random.choice(digits_only))
random.shuffle(seq6_list)
original_sequence_6 = ''.join(seq6_list)
original_sequences.append(original_sequence_6)

# Тестова послідовність 7
elements = string.ascii_lowercase + string.digits
seq7_list = [random.choice(elements) for _ in range(N_sequence)]
original_sequence_7 = ''.join(seq7_list)
original_sequences.append(original_sequence_7)

# Тестова послідовність 8
original_sequence_8 = '1' * N_sequence
original_sequences.append(original_sequence_8)

# розрахунки та збереження
# Збереження послідовностей
with open("results_sequence.txt", "w", encoding="utf-8") as file:
    for seq in original_sequences:
        file.write(seq + "\n")

results_for_table = []

# Очищення або створення файлу з результатами
open("results_sequence.txt", "w", encoding="utf-8").close()

with open("results_sequence.txt", "a", encoding="utf-8") as file:
    for i, sequence in enumerate(original_sequences):
        seq_num = i + 1
        sequence_alphabet_size = len(set(sequence))
        original_sequence_size = len(sequence)  # в байтах для UTF-8 латиниці/цифр

        counts = collections.Counter(sequence)
        probability = {symbol: count / N_sequence for symbol, count in counts.items()}

        mean_probability = sum(probability.values()) / len(probability)
        equal = all(abs(prob - mean_probability) < 0.05 * mean_probability for prob in probability.values())
        uniformity = "рівна" if equal else "нерівна"

        entropy = -sum(p * math.log2(p) for p in probability.values())

        if sequence_alphabet_size > 1:
            source_excess = 1 - entropy / math.log2(sequence_alphabet_size)
        else:
            source_excess = 1

        probability_str = ', '.join([f"{symbol}={prob:.4f}" for symbol, prob in probability.items()])

        file.write(f"Послідовність {seq_num}: {sequence}\n")
        file.write(f"Розмір послідовності {original_sequence_size} byte\n")
        file.write(f"Розмір алфавіту: {sequence_alphabet_size}\n")
        file.write(f"Ймовірності появи символів: {probability_str}\n")
        file.write(f"Середнє арифметичне ймовірностей: {mean_probability:.2f}\n")
        file.write(f"Ймовірність розподілу символів: {uniformity}\n")
        file.write(f"Ентропія: {entropy:.4f}\n")
        file.write(f"Надмірність джерела: {source_excess:.2f}\n")
        file.write("-" * 50 + "\n")

        # Додавання даних для таблиці
        results_for_table.append([sequence_alphabet_size, round(entropy, 2), round(source_excess, 2), uniformity])

# Побудова таблиці
N = 8
fig, ax = plt.subplots(figsize=(14 / 1.54, N / 1.54))

headers = ['Розмір алфавіту', 'Ентропія', 'Надмірність', 'Ймовірність']
row = [f'Послідовність {i + 1}' for i in range(N)]

ax.axis('off')
table = ax.table(cellText=results_for_table, colLabels=headers, rowLabels=row, loc='center', cellLoc='center')
table.set_fontsize(14)
table.scale(0.8, 2)

fig.savefig('Характеристики сформованих послідовностей.png', bbox_inches='tight')