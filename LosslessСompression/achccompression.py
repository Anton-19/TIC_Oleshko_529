import math
import collections
import ast
import matplotlib.pyplot as plt


# Функція перетворення числа з плаваючою комою у двійковий рядок
def float_bin(point, size_cod):
    binary_code = ""
    for x in range(size_cod):
        point = point * 2
        if point > 1:
            binary_code = binary_code + str(1)
            x_int = int(point)
            point = point - x_int
        elif point < 1:
            binary_code = binary_code + str(0)
        elif point == 1:
            binary_code = binary_code + str(1)
            binary_code = binary_code.ljust(size_cod, '0')
            break
    return binary_code[:size_cod]


# Арифметичне кодування (AC)
def encode_ac(uniq_chars, probabilitys, alphabet_size, sequence):
    alphabet = list(uniq_chars)
    probability = [probabilitys[symbol] for symbol in alphabet]

    unity = []
    probability_range = 0.0
    for i in range(alphabet_size):
        l = probability_range
        probability_range = probability_range + probability[i]
        u = probability_range
        unity.append([alphabet[i], l, u])

    # Основний цикл
    for i in range(len(sequence) - 1):
        for j in range(len(unity)):
            if sequence[i] == unity[j][0]:
                probability_low = unity[j][1]
                probability_high = unity[j][2]
                diff = probability_high - probability_low

                for k in range(len(unity)):
                    if k == 0:
                        unity[k][1] = probability_low
                    else:
                        unity[k][1] = unity[k - 1][2]
                    unity[k][2] = probability[k] * diff + unity[k][1]
                break

    # Визначення діапазону для останнього символу
    low = 0
    high = 0
    for i in range(len(unity)):
        if unity[i][0] == sequence[-1]:
            low = unity[i][1]
            high = unity[i][2]
            break

    point = (low + high) / 2
    # Захист від ділення на 0
    if high - low == 0:
        size_cod = 1
        bin_code = "0"
    else:
        size_cod = math.ceil(math.log2(1 / (high - low)) + 1)
        bin_code = float_bin(point, size_cod)
    bin_code = float_bin(point, size_cod)

    return [point, alphabet_size, alphabet, probability], bin_code


# Арифметичне декодування (AC)
def decode_ac(encoded_data_ac, length_seq):
    point = encoded_data_ac[0]
    alphabet_size = encoded_data_ac[1]
    alphabet = encoded_data_ac[2]
    probability = encoded_data_ac[3]

    unity = []
    probability_range = 0.0
    for i in range(alphabet_size):
        l = probability_range
        probability_range = probability_range + probability[i]
        u = probability_range
        unity.append([alphabet[i], l, u])

    decoded_sequence = ""
    for i in range(length_seq):
        for j in range(len(unity)):
            # Перевіряємо в який інтервал потрапляє point
            if unity[j][1] <= point < unity[j][2]:
                prob_low = unity[j][1]
                prob_high = unity[j][2]
                diff = prob_high - prob_low
                decoded_sequence = decoded_sequence + unity[j][0]

                # Оновлюємо інтервали
                for k in range(len(unity)):
                    if k == 0:
                        unity[k][1] = prob_low
                    else:
                        unity[k][1] = unity[k - 1][2]
                    unity[k][2] = probability[k] * diff + unity[k][1]
                break
    return decoded_sequence


# Кодування Хаффмана (CH)
def encode_ch(uniq_chars, probabilitys, sequence):
    alphabet = list(uniq_chars)
    probability = [probabilitys[symbol] for symbol in alphabet]

    final = []
    for i in range(len(alphabet)):
        final.append([alphabet[i], probability[i]])

    final.sort(key=lambda x: x[1])

    # Випадок коли в алфавіті лише 1 символ
    if 1 in probability and len(set(probability)) == 1:
        symbol_code = []
        for i in range(len(alphabet)):
            code = "1" * i + "0"
            symbol_code.append([alphabet[i], code])
        encode = "".join([symbol_code[alphabet.index(c)][1] for c in sequence])
        return [encode, symbol_code], encode
    else:
        tree = []
        # Копіюємо список для побудови дерева
        nodes = list(final)
        while len(nodes) > 1:
            nodes.sort(key=lambda x: x[1])
            left = nodes.pop(0)
            right = nodes.pop(0)
            tot = left[1] + right[1]
            tree.append([left[0], right[0]])
            nodes.append([left[0] + right[0], tot])

        tree.reverse()
        alphabet.sort()
        symbol_code = []
        for i in range(len(alphabet)):
            code = ""
            for j in range(len(tree)):
                if alphabet[i] in tree[j][0]:
                    code = code + '0'
                    if alphabet[i] == tree[j][0]: break
                elif alphabet[i] in tree[j][1]:
                    code = code + '1'
                    if alphabet[i] == tree[j][1]: break
            symbol_code.append([alphabet[i], code])

        encode = ""
        for c in sequence:
            encode += [sc[1] for sc in symbol_code if sc[0] == c][0]
        return [encode, symbol_code], encode


# Декодування Хаффмана (CH)
def decode_ch(encoded_sequence):
    encode_str = encoded_sequence[0]
    symbol_code = encoded_sequence[1]

    encode = list(encode_str)
    sequence_res = ""
    flag = 0

    i = 0
    while i < len(encode):
        current_bit_seq = encode[i]
        count = 0
        for j in range(len(symbol_code)):
            if current_bit_seq == symbol_code[j][1]:
                sequence_res = sequence_res + str(symbol_code[j][0])
                flag = 1
                break

        if flag == 1:
            flag = 0
            i += 1
        else:
            count += 1
            if i + 1 < len(encode):
                # Об'єднуємо поточний елемент з наступним
                encode[i + 1] = encode[i] + encode[i + 1]
                i += 1
            else:
                break
    return sequence_res


def main():
    with open("results_sequence.txt", "r", encoding="utf-8") as file:
        original_sequences = []
        for line in file:
            if "Послідовність" in line:
                seq = line.split(":")[1].strip()
                original_sequences.append(seq)

    with open("results_AC_CH.txt", "w", encoding="utf-8") as file:
        file.write("Результати стиснення:\n\n")

    results = []
    N_total = 8  # кількість послідовностей

    for idx, seq_raw in enumerate(original_sequences):
        # Очищення послідовності
        sequence_full = seq_raw.strip("[]'\"() ")
        # Обмеження 10 символами
        sequence = sequence_full[:10]
        sequence_length = len(sequence)

        unique_chars = set(sequence)
        sequence_alphabet_size = len(unique_chars)
        counts = collections.Counter(sequence)

        # Ймовірність
        probability = {symbol: count / sequence_length for symbol, count in counts.items()}

        # Ентропія
        entropy = -sum(p * math.log2(p) for p in probability.values() if p > 0)

        # Кодування AC
        encoded_data_ac, encoded_sequence_ac = encode_ac(unique_chars, probability, sequence_alphabet_size, sequence)
        decoded_sequence_ac = decode_ac(encoded_data_ac, sequence_length)
        bps_ac = len(encoded_sequence_ac) / sequence_length

        # Кодування CH
        encoded_data_ch, encoded_sequence_ch = encode_ch(unique_chars, probability, sequence)
        decoded_sequence_ch = decode_ch(encoded_data_ch)
        bps_ch = len(encoded_sequence_ch) / sequence_length

        # Збереження у файл
        with open("results_AC_CH.txt", "a", encoding="utf-8") as file:
            file.write(f"--- Послідовність {idx + 1} ---\n")
            file.write(f"Оригінал (10 симв): {sequence}\n")
            file.write(f"Ентропія: {round(entropy, 4)}\n")
            file.write(f"AC bps: {bps_ac}, Код: {encoded_sequence_ac}\n")
            file.write(f"AC Декодовано: {decoded_sequence_ac}\n")
            file.write(f"CH bps: {bps_ch}, Код: {encoded_sequence_ch}\n")
            file.write(f"CH Декодовано: {decoded_sequence_ch}\n\n")

        results.append([round(entropy, 2), round(bps_ac, 2), round(bps_ch, 2)])

    # Побудова таблиці результатів
    fig, ax = plt.subplots(figsize=(14/1.54, len(results)/1.54))

    ax.axis('off')

    table = ax.table(
        cellText=results,
        colLabels=['Ентропія', 'bps AC', 'bps CH'],
        rowLabels=[f'Послідовність {i + 1}' for i in range(len(results))],
        loc='center',
        cellLoc='center'
    )

    table.set_fontsize(12)
    table.scale(1, 1.2)
    table.auto_set_column_width(col=list(range(len(results[0]))))

    plt.tight_layout()
    fig.savefig("Результати стиснення методами AC та CH.png")


if __name__ == "__main__":
    main()