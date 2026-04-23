import os
import numpy as np
from scipy import fftpack
from PIL import Image

#  DCT
def dct_2d(block):
    return fftpack.dct(fftpack.dct(block.T, norm='ortho').T, norm='ortho')

def idct_2d(block):
    return fftpack.idct(fftpack.idct(block.T, norm='ortho').T, norm='ortho')

# QUANT
def load_quantization_table(component, quality):
    if quality == "low":  # сильне стиснення
        scale = 2
    else:  # medium
        scale = 1

    if component == 'lum':
        q = np.array([
            [16,11,10,16,24,40,51,61],
            [12,12,14,19,26,58,60,55],
            [14,13,16,24,40,57,69,56],
            [14,17,22,29,51,87,80,62],
            [18,22,37,56,68,109,103,77],
            [24,35,55,64,81,104,113,92],
            [49,64,78,87,103,121,120,101],
            [72,92,95,98,112,100,103,99]
        ])
    else:
        q = np.array([
            [17,18,24,47,99,99,99,99],
            [18,21,26,66,99,99,99,99],
            [24,26,56,99,99,99,99,99],
            [47,66,99,99,99,99,99,99],
            [99,99,99,99,99,99,99,99],
            [99,99,99,99,99,99,99,99],
            [99,99,99,99,99,99,99,99],
            [99,99,99,99,99,99,99,99]
        ])

    return q * scale


def quantize(block, component, quality):
    q = load_quantization_table(component, quality)
    return np.round(block / q).astype(np.int32)


def dequantize(block, component, quality):
    q = load_quantization_table(component, quality)
    return block * q


# ZIGZAG
def zigzag_indices(n=8):
    indices = []
    for i in range(2*n-1):
        if i % 2 == 0:
            for j in range(i+1):
                if j < n and i-j < n:
                    indices.append((j, i-j))
        else:
            for j in range(i+1):
                if j < n and i-j < n:
                    indices.append((i-j, j))
    return indices

ZZ = zigzag_indices()

def block_to_zigzag(block):
    return [block[i][j] for i, j in ZZ]

def zigzag_to_block(arr):
    block = np.zeros((8, 8))
    for idx, (i, j) in enumerate(ZZ):
        block[i][j] = arr[idx]
    return block


# ENCODE
def encode_image(image_path, quality):
    image = Image.open(image_path).convert('YCbCr')
    npmat = np.array(image, dtype=np.float32)

    h, w = npmat.shape[:2]

    if h % 8 != 0 or w % 8 != 0:
        raise ValueError("Image must be multiple of 8")

    encoded_blocks = []

    for y in range(0, h, 8):
        for x in range(0, w, 8):
            block = npmat[y:y+8, x:x+8]

            block_data = []

            for c in range(3):
                channel = block[:, :, c] - 128
                dct = dct_2d(channel)

                comp = 'lum' if c == 0 else 'chrom'
                q = quantize(dct, comp, quality)

                zz = block_to_zigzag(q)
                block_data.append(zz)

            encoded_blocks.append(block_data)

    return encoded_blocks, (h, w)


# DECODE
def decode_image(encoded_blocks, shape, quality):
    h, w = shape
    result = np.zeros((h, w, 3))

    idx = 0

    for y in range(0, h, 8):
        for x in range(0, w, 8):
            block = np.zeros((8, 8, 3))

            for c in range(3):
                zz = encoded_blocks[idx][c]
                block_q = zigzag_to_block(zz)

                comp = 'lum' if c == 0 else 'chrom'
                deq = dequantize(block_q, comp, quality)

                idct = idct_2d(deq) + 128
                block[:, :, c] = idct

            result[y:y+8, x:x+8] = block
            idx += 1

    result = np.clip(result, 0, 255).astype(np.uint8)
    return Image.fromarray(result, 'YCbCr').convert('RGB')


#  MAIN
def main():
    os.makedirs("Results", exist_ok=True)

    images = ["7_1.bmp", "7_2.bmp", "7_3.bmp"]
    qualities = ["low", "medium"]

    with open("results_jpeg.txt", "w", encoding="utf-8") as f:

        for img in images:
            for q in qualities:

                input_path = f"images/{img}"

                encoded, shape = encode_image(input_path, q)

                # save compressed
                compressed_path = f"Results/{img}_{q}.bin"
                with open(compressed_path, "w") as cf:
                    cf.write(str(encoded))

                # decode
                decoded_img = decode_image(encoded, shape, q)

                decoded_path = f"Results/{img}_{q}.jpg"
                decoded_img.save(decoded_path, "JPEG")

                # stats
                original_size = os.path.getsize(input_path)
                compressed_size = os.path.getsize(compressed_path)

                ratio = original_size / compressed_size

                f.write(f"{img} | {q}\n")
                width, height = shape[1], shape[0]

                jpeg_size = os.path.getsize(decoded_path)
                compression_ratio = original_size / jpeg_size

                f.write(f"Image: {img} ({q})\n\n")

                f.write(f"Розмір вихідного файла: {original_size} байт\n")
                f.write(f"Розмір файла JPEG: {jpeg_size} байт\n")
                f.write(f"Розмір зображення JPEG: {width}x{height}\n")
                f.write(f"Коефіцієнт стиснення: {compression_ratio:.2f}\n")

                f.write("\n----------------------------------------\n\n")

                print(f"Done: {img} ({q})")


if __name__ == "__main__":
    main()

