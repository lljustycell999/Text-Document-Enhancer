from typing import Optional
import cv2
from PySide6.QtWidgets import QFileDialog, QWidget


def open_image_dialog(parent: Optional[QWidget] = None):
    """
    Opens a file dialog for the user to select an image file.

    :param parent: The parent widget for the file dialog. Set to None as default.
    :type parent: Optional[QWidget]

    :return: The grayscale version of the selected image as a NumPy array, or None if no image is selected that is in
             an acceptable format or the operation is cancelled by the user.
    :rtype: Optional[numpy.ndarray]

    :return: The file name of the given image or None if no image is selected that is in an acceptable format or the
             operation is cancelled by the user.

    """

    # Image must satisfy the filter, otherwise image_path will just be an empty string
    image_path, _ = \
        QFileDialog.getOpenFileName(parent, "Load Image", filter="Image Files (*.tiff *.png *.jpeg *.jpg *.bmp)")

    if image_path:
        # Extract the file name from the full path
        file_name = image_path.split("/")[-1]  # Unix-like path (Mac & Linux)
        file_name = file_name.split("\\")[-1]  # Windows path

        return cv2.imread(image_path, 0), file_name

    return None, None
