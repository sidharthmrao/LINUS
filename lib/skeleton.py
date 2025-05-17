import cv2
import numpy as np
from skimage.morphology import skeletonize, thin, medial_axis


def gen_skel(file_path, output):
    """
    Generate a skeleton from an image file.
    """

    # Load and resize image
    img = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
    img = cv2.resize(img, (480, 480))  # Resize to square

    # Blur to reduce noise
    blurred = cv2.GaussianBlur(img, (5, 5), 0)

    # Canny edges
    edges = cv2.Canny(blurred, threshold1=50, threshold2=150)

    # Convert to binary boolean format for skeletonization
    edges_bool = edges > 0

    skeleton = medial_axis(edges_bool)

    # Thin image
    skeleton = thin(edges_bool, max_num_iter=10)

    # Skeleton must be uint8 for OpenCV
    skeleton_uint8 = (skeleton * 255).astype(np.uint8)

    kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE, (3, 3)
    )  # You can try (5,5) for more merging

    # Dilate slightly to connect small gaps in the skeleton
    dilated = cv2.dilate(skeleton_uint8, kernel, iterations=3)

    # Reskeletonize the dilated image
    skeleton = skeletonize(dilated > 0)
    # skeleton = medial_axis(dilated > 0)

    skeleton_uint8 = (skeleton * 255).astype(np.uint8)

    # Save the processed image skeleton to file
    cv2.imwrite(output, skeleton_uint8)

    return skeleton
