import ast
import random

CHUNK_LENGTH = 8

assert not CHUNK_LENGTH % 8, 'Довжина блоку має бути кратна 8'

CHECK_BITS = [i for i in range(1, CHUNK_LENGTH + 1) if not i & (i - 1)]


# Перетворення символів у біти
def getCharsToBin(chars):
    assert not len(chars) * 8 % CHUNK_LENGTH, 'Довжина кодових даних повинна бути кратною довжині блоку кодування'

    return ''.join([bin(ord(c))[2:].zfill(8) for c in chars])


# Поблоковий вивід
def getChunkIterator(text_bin, chunk_size=CHUNK_LENGTH):
    for i in range(len(text_bin)):
        if not i % chunk_size:
            yield text_bin[i:i + chunk_size]


# Отримання контрольних бітів
def getCheckBitsData(value_bin):
    check_bits_count_map = {k: 0 for k in CHECK_BITS}

    for index, value in enumerate(value_bin, 1):

        if int(value):
            bin_char_list = list(bin(index)[2:].zfill(8))
            bin_char_list.reverse()

            for degree in [2 ** int(i) for i, value in enumerate(bin_char_list) if int(value)]:
                if degree in check_bits_count_map:
                    check_bits_count_map[degree] += 1

    check_bits_value_map = {}

    for check_bit, count in check_bits_count_map.items():
        check_bits_value_map[check_bit] = 0 if not count % 2 else 1

    return check_bits_value_map


# Додавання пустих контрольних бітів
def getSetEmptyCheckBits(value_bin):

    for bit in CHECK_BITS:
        value_bin = value_bin[:bit - 1] + '0' + value_bin[bit - 1:]

    return value_bin


# Встановлення контрольних бітів
def getSetCheckBits(value_bin):

    value_bin = getSetEmptyCheckBits(value_bin)

    check_bits_data = getCheckBitsData(value_bin)

    for check_bit, bit_value in check_bits_data.items():
        value_bin = value_bin[:check_bit - 1] + str(bit_value) + value_bin[check_bit:]

    return value_bin


# Отримання контрольних бітів при декодуванні
def getCheckBits(value_bin):

    check_bits = {}

    for index, value in enumerate(value_bin, 1):
        if index in CHECK_BITS:
            check_bits[index] = int(value)

    return check_bits


# Видалення контрольних бітів
def getExcludeCheckBits(value_bin):

    clean_value_bin = ''

    for index, char_bin in enumerate(list(value_bin), 1):

        if index not in CHECK_BITS:
            clean_value_bin += char_bin

    return clean_value_bin


# Додавання помилок
def getSetErrors(encoded):

    result = ''

    for chunk in getChunkIterator(encoded, CHUNK_LENGTH + len(CHECK_BITS)):

        num_bit = random.randint(1, len(chunk))

        chunk = (
                chunk[:num_bit - 1] +
                str(int(chunk[num_bit - 1]) ^ 1) +
                chunk[num_bit:]
        )

        result += chunk

    return result


# Пошук та виправлення помилки
def getCheckAndFixError(encoded_chunk):

    check_bits_encoded = getCheckBits(encoded_chunk)

    check_item = getExcludeCheckBits(encoded_chunk)

    check_item = getSetCheckBits(check_item)

    check_bits = getCheckBits(check_item)

    if check_bits_encoded != check_bits:

        invalid_bits = []

        for check_bit_encoded, value in check_bits_encoded.items():

            if check_bits[check_bit_encoded] != value:
                invalid_bits.append(check_bit_encoded)

        num_bit = sum(invalid_bits)

        encoded_chunk = (
                encoded_chunk[:num_bit - 1] +
                str(int(encoded_chunk[num_bit - 1]) ^ 1) +
                encoded_chunk[num_bit:]
        )

    return encoded_chunk


# Індекси помилок
def getDiffIndexList(value_bin1, value_bin2):

    diff_index_list = []

    for index, char_bin_items in enumerate(zip(list(value_bin1), list(value_bin2)), 1):

        if char_bin_items[0] != char_bin_items[1]:
            diff_index_list.append(index)

    return diff_index_list


# Кодування
def encode(source):

    text_bin = getCharsToBin(source)

    result = ''

    for chunk_bin in getChunkIterator(text_bin):

        chunk_bin = getSetCheckBits(chunk_bin)

        result += chunk_bin

    return text_bin, result


# Декодування
def decode(encoded, fix_errors=True):

    decoded_value = ''

    fixed_encoded_list = []

    for encoded_chunk in getChunkIterator(encoded, CHUNK_LENGTH + len(CHECK_BITS)):

        if fix_errors:
            encoded_chunk = getCheckAndFixError(encoded_chunk)

        fixed_encoded_list.append(encoded_chunk)

    clean_chunk_list = []

    for encoded_chunk in fixed_encoded_list:

        encoded_chunk = getExcludeCheckBits(encoded_chunk)

        clean_chunk_list.append(encoded_chunk)

    for clean_chunk in clean_chunk_list:

        for clean_char in [clean_chunk[i:i + 8] for i in range(len(clean_chunk)) if not i % 8]:

            decoded_value += chr(int(clean_char, 2))

    return decoded_value


# Основний код
if __name__ == '__main__':

    open("results_hamming.txt", "w", encoding="utf-8")

    with open("results_sequence.txt", "r", encoding="utf-8") as file:

        original_sequences = []

        for line in file:

            if ":" in line:
                sequence = line.split(":")[1].strip()

                original_sequences.append(sequence)

    for sequence in original_sequences:

        source = sequence[:10]

        source_bin, encoded = encode(source)

        decoded = decode(encoded)

        encoded_with_error = getSetErrors(encoded)

        diff_index_list = getDiffIndexList(encoded, encoded_with_error)

        decoded_with_error = decode(encoded_with_error, fix_errors=False)

        decoded_without_error = decode(encoded_with_error)

        with open("results_hamming.txt", "a", encoding="utf-8") as result_file:

            result_file.write("/" * 30 + "\n")

            result_file.write(f"Оригінальна послідовність: {source}\n")
            result_file.write(f"Оригінальна послідовність в бітах: {source_bin}\n")
            result_file.write(f"Розмір оригінальної послідовності: {len(source_bin)} bits\n")
            result_file.write(f"Довжина блоку кодування: {CHUNK_LENGTH}\n")
            result_file.write(f"Позиції контрольних біт: {CHECK_BITS}\n")
            result_file.write(f"Відносна надмірність коду: {len(CHECK_BITS) / CHUNK_LENGTH}\n")

            result_file.write("-----------Кодування-----------\n")
            result_file.write(f"Закодовані дані: {encoded}\n")
            result_file.write(f"Розмір закодованих даних: {len(encoded)} bits\n")

            result_file.write("-----------Декодування-----------\n")
            result_file.write(f"Декодовані дані: {decoded}\n")
            result_file.write(f"Розмір декодованих даних: {len(decoded) * 8} bits\n")

            result_file.write("-----------Внесення помилки-----------\n")
            result_file.write(f"Закодовані дані з помилками: {encoded_with_error}\n")
            result_file.write(f"Кількість помилок: {len(diff_index_list)}\n")
            result_file.write(f"Індекси помилок: {diff_index_list}\n")

            result_file.write("-----------Виправлення помилки-----------\n")
            result_file.write(f"Декодовані дані без виправлення помилки: {decoded_with_error}\n")
            result_file.write(f"Декодовані дані з виправленням помилки: {decoded_without_error}\n")

            result_file.write("/" * 30 + "\n\n")