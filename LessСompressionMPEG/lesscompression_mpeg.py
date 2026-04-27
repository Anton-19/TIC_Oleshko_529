import numpy as np
import cv2
import matplotlib.pyplot as plt
import math
import os
import random


# Сегментація
def segmentImage(anchor, blockSize=16):
    h, w = anchor.shape
    return int(h / blockSize), int(w / blockSize)


# Центр блоку
def getCenter(x, y, blockSize):
    return int(x + blockSize / 2), int(y + blockSize / 2)


# Зона пошуку
def getAnchorSearchArea(x, y, anchor, blockSize, searchArea):
    h, w = anchor.shape
    cx, cy = getCenter(x, y, blockSize)

    sx = max(0, cx - int(blockSize / 2) - searchArea)
    sy = max(0, cy - int(blockSize / 2) - searchArea)

    return anchor[
        sy:min(sy + searchArea * 2 + blockSize, h),
        sx:min(sx + searchArea * 2 + blockSize, w)
    ]


# Блок
def getBlockZone(p, aSearch, tBlock, blockSize):
    px, py = p
    px, py = px - int(blockSize / 2), py - int(blockSize / 2)
    px, py = max(0, px), max(0, py)

    aBlock = aSearch[py:py + blockSize, px:px + blockSize]

    if aBlock.shape != tBlock.shape:
        return None

    return aBlock


# MAD
def getMAD(tBlock, aBlock):
    return np.sum(np.abs(tBlock - aBlock)) / (tBlock.shape[0] * tBlock.shape[1])


# кращий блок
def getBestMatch(tBlock, aSearch, blockSize):
    step = 4
    ah, aw = aSearch.shape
    acy, acx = int(ah / 2), int(aw / 2)

    minMAD = float("+inf")
    minP = (acx, acy)

    while step >= 1:
        points = [
            (acx, acy),
            (acx + step, acy),
            (acx, acy + step),
            (acx + step, acy + step),
            (acx - step, acy),
            (acx, acy - step),
            (acx - step, acy - step),
            (acx + step, acy - step),
            (acx - step, acy + step),
        ]

        for p in points:
            aBlock = getBlockZone(p, aSearch, tBlock, blockSize)

            if aBlock is None:
                continue

            MAD = getMAD(tBlock, aBlock)

            if MAD < minMAD:
                minMAD = MAD
                minP = p

        acx, acy = minP
        step = int(step / 2)

    px, py = minP
    px, py = px - int(blockSize / 2), py - int(blockSize / 2)
    px, py = max(0, px), max(0, py)

    return aSearch[py:py + blockSize, px:px + blockSize]


# ОСНОВНИЙ ПОШУК
def blockSearchBody(anchor, target, blockSize, searchArea=7):
    h, w = anchor.shape
    hSegments, wSegments = segmentImage(anchor, blockSize)

    predicted = np.zeros((h, w))

    for y in range(0, int(hSegments * blockSize), blockSize):
        for x in range(0, int(wSegments * blockSize), blockSize):

            targetBlock = target[y:y + blockSize, x:x + blockSize]

            searchZone = getAnchorSearchArea(x, y, anchor, blockSize, searchArea)

            bestMatch = getBestMatch(targetBlock, searchZone, blockSize)

            predicted[y:y + blockSize, x:x + blockSize] = bestMatch

    return predicted


# RESIDUAL
def getResidual(target, predicted):
    return np.subtract(target, predicted)


# RECONSTRUCT
def getReconstructTarget(residual, predicted):
    return np.add(residual, predicted)


# BITS PER PIXEL
def getBitsPerPixel(im):
    h, w = im.shape
    bits = 0

    for row in im:
        for pixel in row:
            bits += math.log2(abs(int(pixel)) + 1)

    return bits / (h * w)


# Зчитування кадрів
def getFrames(filename, first_frame, second_frame):
    cap = cv2.VideoCapture(filename)

    cap.set(cv2.CAP_PROP_POS_FRAMES, first_frame - 1)
    _, fr1 = cap.read()

    cap.set(cv2.CAP_PROP_POS_FRAMES, second_frame - 1)
    _, fr2 = cap.read()

    cap.release()
    return fr1, fr2


#MAIN
def main(anchorFrame, targetFrame, blockSize=16, saveOutput=True):
    outfile = "Results"

    bitsAnchor = []
    bitsDiff = []
    bitsPredicted = []

    h, w, ch = anchorFrame.shape

    diffFrameRGB = np.zeros((h, w, ch))
    predictedFrameRGB = np.zeros((h, w, ch))
    residualFrameRGB = np.zeros((h, w, ch))
    restoreFrameRGB = np.zeros((h, w, ch))

    for i in range(3):
        anchorFrame_c = anchorFrame[:, :, i]
        targetFrame_c = targetFrame[:, :, i]

        diffFrame = cv2.absdiff(anchorFrame_c, targetFrame_c)

        predictedFrame = blockSearchBody(anchorFrame_c, targetFrame_c, blockSize)
        residualFrame = getResidual(targetFrame_c, predictedFrame)
        reconstructFrame = getReconstructTarget(residualFrame, predictedFrame)

        bitsAnchor.append(getBitsPerPixel(anchorFrame_c))
        bitsDiff.append(getBitsPerPixel(diffFrame))
        bitsPredicted.append(getBitsPerPixel(residualFrame))

        diffFrameRGB[:, :, i] = diffFrame
        predictedFrameRGB[:, :, i] = predictedFrame
        residualFrameRGB[:, :, i] = residualFrame
        restoreFrameRGB[:, :, i] = reconstructFrame

    if not os.path.isdir(outfile):
        os.mkdir(outfile)


    if saveOutput:
        cv2.imwrite(f"{outfile}/First frame.png", anchorFrame)
        cv2.imwrite(f"{outfile}/Second frame.png", targetFrame)

        cv2.imwrite(f"{outfile}/Difference between frame.png",
                    np.clip(diffFrameRGB, 0, 255).astype(np.uint8))

        cv2.imwrite(f"{outfile}/Prediction frame.png",
                    np.clip(predictedFrameRGB, 0, 255).astype(np.uint8))

        cv2.imwrite(f"{outfile}/Residual frame.png",
                    np.clip(residualFrameRGB, 0, 255).astype(np.uint8))

        cv2.imwrite(f"{outfile}/Restore frame.png",
                    np.clip(restoreFrameRGB, 0, 255).astype(np.uint8))

    # Графік
    barWidth = 0.25

    P1 = [sum(bitsAnchor), *bitsAnchor]
    Diff = [sum(bitsDiff), *bitsDiff]
    Mpeg = [sum(bitsPredicted), *bitsPredicted]

    br1 = np.arange(len(P1))
    br2 = [x + barWidth for x in br1]
    br3 = [x + barWidth for x in br2]

    plt.figure(figsize=(12, 8))

    plt.bar(br1, P1, width=barWidth, label='Original')
    plt.bar(br2, Diff, width=barWidth, label='Difference')
    plt.bar(br3, Mpeg, width=barWidth, label='MPEG')

    plt.title(f'Compression = {round(sum(bitsAnchor)/sum(bitsPredicted), 2)}')
    plt.ylabel('Bits per pixel')

    plt.xticks([r + barWidth for r in range(len(P1))],
               ['RGB', 'R', 'G', 'B'])

    plt.legend()
    plt.savefig(f"{outfile}/histogram.png", dpi=600)

    return None


# Запуск
if __name__ == "__main__":
    fr = random.randint(1, 1000)

    frame1, frame2 = getFrames('sample4.avi', fr, fr + 1)

    main(frame1, frame2, saveOutput=True)