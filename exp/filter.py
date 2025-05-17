import cv2
import matplotlib.pyplot as plt
import numpy as np

from skimage.morphology import skeletonize

AXIS_SIZE = 1000
DOWNSAMPLE_FACTOR = 8

image = "shrek.png"

img_name = image.split(".")[0]

img = cv2.imread(image)
if img is None:
    print("Error: Could not read image.")
    exit(1)

# Resize image to AXIS_SIZE x AXIS_SIZE
img = cv2.resize(img, (AXIS_SIZE, AXIS_SIZE))

# Convert to grayscale
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


# Apply bilateral filter to smooth image but preserve edges
bilateral = cv2.bilateralFilter(gray, 10, 100, 100)

# Sobel to take gradient
sobel_x = cv2.Sobel(bilateral, cv2.CV_64F, 1, 0, ksize=1)
sobel_y = cv2.Sobel(bilateral, cv2.CV_64F, 0, 1, ksize=1)
sobel = cv2.magnitude(sobel_x, sobel_y)

# Threshold sobel to keep only highest intensity edges
lowerb = np.zeros_like(sobel, dtype=np.float64)
upperb = np.full_like(sobel, 10, dtype=np.float64)
sobel_thresh = cv2.inRange(sobel, lowerb, upperb)

# Save sobel_thresh
cv2.imwrite(f"output/{img_name}_filtered.jpg", sobel_thresh)

img = cv2.resize(
    sobel_thresh,
    (AXIS_SIZE // DOWNSAMPLE_FACTOR, AXIS_SIZE // DOWNSAMPLE_FACTOR),
    interpolation=cv2.INTER_NEAREST,
)

cv2.imwrite(f"output/{img_name}_downsampled.jpg", img)

# Make a white image of AXIS_SIZE x AXIS_SIZE with lesser points
white = np.ones((AXIS_SIZE, AXIS_SIZE), dtype=np.uint8) * 255

for i in range(AXIS_SIZE // DOWNSAMPLE_FACTOR):
    for j in range(AXIS_SIZE // DOWNSAMPLE_FACTOR):
        white[i * DOWNSAMPLE_FACTOR, j * DOWNSAMPLE_FACTOR] = img[i, j]

reduced_mask = cv2.bitwise_not(white)
cv2.imwrite(f"output/{img_name}_reduced.jpg", reduced_mask)

edges = cv2.Canny(sobel_thresh, 50, 150)

edges_bool = edges > 0
skeleton = skeletonize(edges_bool)

# Step 5: Display
plt.figure(figsize=(15, 5))

plt.subplot(1, 3, 1)
plt.title("Original (Grayscale)")
plt.imshow(reduced_mask, cmap="gray")
plt.axis("off")

plt.subplot(1, 3, 2)
plt.title("Canny Edges")
plt.imshow(edges, cmap="gray")
plt.axis("off")

plt.subplot(1, 3, 3)
plt.title("Skeletonized Edges")
plt.imshow(skeleton, cmap="gray")
plt.axis("off")

plt.tight_layout()
plt.show()
