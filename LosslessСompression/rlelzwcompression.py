import math
import collections
import matplotlib.pyplot as plt


# RLE КОДУВАННЯ
def encode_rle(sequence):
    if not sequence:
        return "", []

    result_tuples = []
    count = 1

    for i in range(1, len(sequence)):
        if sequence[i] == sequence[i - 1]:
            count += 1
        else:
            result_tuples.append((sequence[i - 1], count))
            count = 1

    result_tuples.append((sequence[-1], count))

    # Формуємо рядок для виводу
    encoded_str = "".join([f"{cnt}{char}" for char, cnt in result_tuples])

    return encoded_str, result_tuples


# RLE ДЕКОДУВАННЯ
def decode_rle(rle_tuples):
    result = "".join([char * count for char, count in rle_tuples])
    return result


# LZW КОДУВАННЯ
def encode_lzw(sequence):
    dictionary = {chr(i): i for i in range(65536)}
    current = ""
    result = []
    size = 0

    for c in sequence:
        new_str = current + c
        if new_str in dictionary:
            current = new_str
        else:
            code = dictionary[current]
            result.append(code)

            # Визначаємо кількість біт
            if code < 65536:
                size += 16
            else:
                size += math.ceil(math.log2(len(dictionary)))

            dictionary[new_str] = len(dictionary)
            current = c

    if current:
        code = dictionary[current]
        result.append(code)
        if code < 65536:
            size += 16
        else:
            size += math.ceil(math.log2(len(dictionary)))

    return result, size


# LZW ДЕКОДУВАННЯ
def decode_lzw(sequence):
    if not sequence:
        return ""

    dictionary = {i: chr(i) for i in range(65536)}

    result = ""
    previous = chr(sequence[0])
    result += previous

    for code in sequence[1:]:
        if code in dictionary:
            entry = dictionary[code]
        else:
            entry = previous + previous[0]

        result += entry
        dictionary[len(dictionary)] = previous + entry[0]
        previous = entry

    return result


# ОСНОВНА ПРОГРАМА
# Зчитування
original_sequences = []
try:
    with open("results_sequence.txt", "r", encoding="utf-8") as file:
        for line in file:
            # Шукаємо рядки, де є "Послідовність" та двокрапка
            if line.startswith("Послідовність") and ":" in line:
                seq = line.split(":", 1)[1].strip()
                if seq:
                    original_sequences.append(seq)
except FileNotFoundError:
    print("Помилка: Файл results_sequence.txt не знайдено.")
    exit()

if not original_sequences:
    print("Помилка: Послідовності не знайдені у файлі.")
    exit()

results = []

# Обробка та запис
with open("results_rle_lzw.txt", "w", encoding="utf-8") as file:
    for idx, sequence in enumerate(original_sequences, start=1):
        file.write(f"\n--- Послідовність {idx} ---\n")
        file.write(f"Original: {sequence}\n")

        counts = collections.Counter(sequence)
        probability = {symbol: count / len(sequence) for symbol, count in counts.items()}
        entropy = -sum(p * math.log2(p) for p in probability.values())

        original_size = len(sequence) * 16

        file.write(f"Ентропія: {round(entropy, 2)}\n")
        file.write(f"Розмір (original): {original_size} bits\n")

        # RLE
        encoded_rle_str, encoded_rle_tuples = encode_rle(sequence)
        decoded_rle = decode_rle(encoded_rle_tuples)

        # Рахуємо довжину закодованого рядка
        encoded_rle_size = len(encoded_rle_str) * 16

        cr_rle = round(original_size / encoded_rle_size, 2) if encoded_rle_size > 0 else 0
        if cr_rle < 1:
            cr_rle_display = "-"
        else:
            cr_rle_display = cr_rle

        file.write(f"\nRLE encoded: {encoded_rle_str}\n")
        file.write(f"RLE decoded: {decoded_rle}\n")
        file.write(f"RLE decoded match: {decoded_rle == sequence}\n")
        file.write(f"RLE size: {encoded_rle_size} bits\n")
        file.write(f"CR RLE: {cr_rle_display}\n")

        # LZW
        encoded_lzw, size_lzw = encode_lzw(sequence)
        decoded_lzw = decode_lzw(encoded_lzw)

        cr_lzw = round(original_size / size_lzw, 2) if size_lzw > 0 else 0

        file.write(f"\nLZW encoded: {encoded_lzw}\n")
        file.write(f"LZW decoded: {decoded_lzw}\n")
        file.write(f"LZW decoded match: {decoded_lzw == sequence}\n")
        file.write(f"LZW size: {size_lzw} bits\n")
        file.write(f"CR LZW: {cr_lzw}\n")

        # зберігаємо для таблиці
        results.append([round(entropy, 2), cr_rle_display, cr_lzw])

# ТАБЛИЦЯ
N = len(results)

fig, ax = plt.subplots(figsize=(8, N * 0.6))
ax.axis('off')

headers = ['Ентропія', 'КС RLE', 'КС LZW']
rows = [f'Послідовність {i + 1}' for i in range(N)]

table = ax.table(
    cellText=results,
    colLabels=headers,
    rowLabels=rows,
    loc='center',
    cellLoc='center'
)

table.set_fontsize(12)
table.scale(1, 2)

plt.title("Результати стиснення методами RLE та LZW", pad=20, fontsize=14)
plt.savefig("Результати стиснення методами RLE та LZW.png", bbox_inches='tight')
plt.close()
