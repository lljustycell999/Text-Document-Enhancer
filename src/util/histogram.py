import cv2
import matplotlib.pyplot as plt
import os
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QMessageBox
)


class HistogramWindow(QWidget):
    """
    A widget for displaying and saving the histogram of an image.

    This class provides a GUI for displaying the histogram of an image and allowing the user to save it
    as an image file.

    Attributes:
        image (np.ndarray): The image data for which the histogram is to be displayed.
        histogram_label (QLabel): A label for displaying the histogram.
    """

    def __init__(self, image):
        """
        Initializes the HistogramWindow with the given image.

        :param image: The image data for which the histogram is to be displayed.
        :type image: np.ndarray
        """

        super().__init__()

        self.image = image
        self.histogram_label = QLabel("Histogram")

        # Allow the user to save the current histogram being displayed
        save_histogram_btn = QPushButton("Save Histogram")
        save_histogram_btn.clicked.connect(self.save_histogram)

        layout = QVBoxLayout()
        layout.addWidget(self.histogram_label)
        layout.addWidget(save_histogram_btn)

        self.calculate_histogram()

        self.setLayout(layout)

    def update_histogram(self, new_image):
        """
        Updates the displayed histogram with respect to a new image.

        :param new_image: The new image data for which the histogram needs to be based on.
        :type new_image: np.ndarray
        """

        self.image = new_image
        self.calculate_histogram()

    def save_histogram(self):
        """
        Saves the displayed histogram as an image file.
        """

        self.calculate_histogram()

        # Open a file dialog to allow the user to select a save location and filename (set to .png as default)
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Histogram", "",
                                                   "Images (*.png *.tiff *.jpeg *.jpg *.bmp)")

        # Check if the user entered a directory and did not cancel the operation
        if file_path != "":
            # Save the histogram to the requested file path
            if self.histogram_label.pixmap().save(file_path):
                QMessageBox.information(self, "Success", "Histogram saved successfully!")
            else:
                QMessageBox.warning(self, "Error", "Failed to save histogram!")
        else:
            QMessageBox.warning(self, "Error", "Saving operation cancelled!")

    def calculate_histogram(self):
        """
        Calculates and displays the histogram of the current image.
        """

        hist = cv2.calcHist([self.image], [0], None, [256], [0, 256])
        hist /= hist.sum()

        # Clear the previous histogram data
        plt.clf()

        # Plot the histogram
        plt.plot(hist)
        plt.xlabel('Pixel Value')
        plt.ylabel('Normalized Frequency')
        plt.title("Histogram")
        plt.xlim(0 - 2, 255 + 2)
        plt.ylim(0 - 0.01, 1 + 0.01)

        # Save the histogram to a temporary file
        plt.savefig('histogram.png')

        # Set the pixmap to the histogram label
        pixmap = QPixmap('histogram.png')

        # Set the pixmap to the histogram label
        self.histogram_label.setPixmap(pixmap)

        # Remove the temporary file
        os.remove('histogram.png')
