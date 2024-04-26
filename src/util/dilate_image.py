import numpy as np
import cv2


def dilate_image(image):
    """
    Dilates the foreground of the given image.
    :param image: The image of which to dilate the foreground
    :type image: np.ndarray

    :return: The image after the foreground undergoes dilation.
    :rtype: np.ndarray
    """

    # Bold text with have a dilation with a matrix size of 2x2.
    kernel = np.ones((2, 2), np.uint8)

    # Invert the image
    image = 255 - image

    # Dilate the image
    image = cv2.dilate(image, kernel, iterations=1)

    # Un-invert the dilated image
    image = 255 - image  # Un-invert the dilated image

    return image
