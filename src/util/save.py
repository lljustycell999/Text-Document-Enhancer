import cv2
from PySide6.QtWidgets import (QFileDialog, QMessageBox)


def save_image(self, preprocessed_binary_img):
    """
    Opens a file dialog to allow the user to select a directory, valid image format, and file name. If the user confirms
    the save operation, the preprocessed binary image is saved to the chosen filepath, converted to the requested
    image format (or a default format if the given format is not valid), and given the chosen filename.

    :param self: The instance of the main window or widget.
    :param preprocessed_binary_img: The preprocessed binary image to be saved.
    :type preprocessed_binary_img: np.ndarray
    """

    # Open a file dialog to allow the user to select a save location, image format, and file name
    # Note: The image format is set to .png by default
    file_path, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "Images (*.png *.tiff *.jpeg *.jpg *.bmp)")

    # Check if the user entered a directory and did not cancel the operation
    if file_path != "":
        # Use OpenCV to write the image to the chosen file path
        cv2.imwrite(file_path, preprocessed_binary_img)
        QMessageBox.information(self, "Success", "Image saved successfully!")
    else:
        QMessageBox.warning(self, "Error", "Saving operation cancelled or failed!")
