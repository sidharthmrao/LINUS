import cv2
import numpy as np
import matplotlib.pyplot as plt
from skimage.morphology import skeletonize, thin


def visualize_skeleton_steps(file_path):
    fig, axs = plt.subplots(1, 5, figsize=(20, 5))
    axs = axs.ravel()

    # Step 1: Load and resize image
    img = cv2.imread(file_path)
    img_resized = cv2.resize(img, (480, 480))
    axs[0].imshow(cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB))
    axs[0].set_title("Original (Resized)")

    # Step 2: Convert to grayscale and blur
    gray = cv2.cvtColor(img_resized, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    axs[1].imshow(blurred, cmap="gray")
    axs[1].set_title("Grayscale + Blurred")

    # Step 3: Canny edge detection
    edges = cv2.Canny(blurred, threshold1=50, threshold2=150)
    axs[2].imshow(edges, cmap="gray")
    axs[2].set_title("Canny Edges")

    # Step 4: Thin edges (skeleton)
    edges_bool = edges > 0
    skeleton_thin = thin(edges_bool, max_num_iter=10)
    axs[3].imshow(skeleton_thin, cmap="gray")
    axs[3].set_title("Skeleton (Thin)")

    # Step 5: Reskeletonize after dilation
    skeleton_uint8 = (skeleton_thin * 255).astype(np.uint8)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    dilated = cv2.dilate(skeleton_uint8, kernel, iterations=3)
    final_skeleton = skeletonize(dilated > 0)
    axs[4].imshow(final_skeleton, cmap="gray")
    axs[4].set_title("Reskeletonized")

    for ax in axs:
        ax.axis("off")

    plt.tight_layout()
    plt.show()


# Example usage
visualize_skeleton_steps("input/handsome_squidward.png")
