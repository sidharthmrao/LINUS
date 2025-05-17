import cv2
import numpy as np


AXIS_SIZE = 512
DOWNSAMPLE_FACTOR = 3


def reduce(path, output):
    img = cv2.imread(path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    img = cv2.resize(
        img,
        (AXIS_SIZE // DOWNSAMPLE_FACTOR, AXIS_SIZE // DOWNSAMPLE_FACTOR),
        interpolation=cv2.INTER_NEAREST,
    )

    # Make a white image of AXIS_SIZE x AXIS_SIZE with lesser points
    white = np.zeros((AXIS_SIZE, AXIS_SIZE), dtype=np.uint8) * 255

    for i in range(AXIS_SIZE // DOWNSAMPLE_FACTOR):
        for j in range(AXIS_SIZE // DOWNSAMPLE_FACTOR):
            white[i * DOWNSAMPLE_FACTOR, j * DOWNSAMPLE_FACTOR] = img[i, j]

    reduced_mask = cv2.bitwise_not(white)
    cv2.imwrite(output, reduced_mask)
