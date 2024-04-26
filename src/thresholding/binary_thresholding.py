import cv2
import pytesseract
import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QWidget,
    QPushButton,
    QComboBox,
    QLabel,
    QSlider,
    QVBoxLayout,
    QMessageBox,
    QHBoxLayout,
    QCheckBox
)

from src.util.dialog import open_image_dialog
from src.util.accuracy import calculate_accuracy
from src.util.save import save_image
from src.util.histogram import HistogramWindow
from src.util.dilate_image import dilate_image

max_width = 512
max_height = 512


class BinaryThresholding(QWidget):
    """
    A GUI widget for applying binary thresholding to an image.

    This class provides a GUI for selecting an image and applying binary thresholding to it.
    Users can view the original grayscale image and several binary images that use binary thresholding, as well as
    obtain computer-extracted text from any of these images. The user may also save the preprocessed binary image with
    a specific filename, image format, and directory. The user can also display and save the corresponding histogram
    graphs of these images as well.

    If the user provides a clean version of the image, the user can see the differences between the extracted
    text of the clean image and any of the other images. On top of that, the feature will also provide a text
    extraction accuracy value.

    The user can also check a box to bold the text through a dilation of size 2x2.

    Attributes:
        image (np.ndarray): The currently displayed image.
        clean_image (np.ndarray): The clean version of the image for accuracy calculation.
        titles (list): A list of titles for different image display options.
    """

    image: np.ndarray
    clean_image: np.ndarray
    titles = [
        "Original Image",
        "THRESH_BINARY",
        "THRESH_BINARY_INV",
        "THRESH_TRUNC",
        "THRESH_TOZERO",
        "THRESH_TOZERO_INV",
    ]

    def __init__(self):
        """
        Initializes the binary thresholding window of the application.
        """

        # Initialize the parent class (QWidget)
        super().__init__()

        self.setWindowTitle("Binary Thresholding")

        # Go through the titles of all the binary thresholding methods and
        # allow the user to see them and choose one through a combo box.
        self.method_combobox = QComboBox()
        for title in self.titles:
            self.method_combobox.addItem(title)
        self.method_combobox.currentIndexChanged.connect(self.update_image)

        # Allow the user to check a box to "bold the text" by performing dilation
        self.dilation_request = QCheckBox("Bold Text")
        self.dilation_request.stateChanged.connect(self.update_image)

        # Have labels to keep track of the given noisy and clean files
        self.noisy_label = QLabel("Noisy File: N/A")
        self.clean_label = QLabel("Clean File: N/A")

        # Label that will keep track of the user-inputted threshold
        self.threshold_label = QLabel("Threshold Value: 127")

        # Create a QSlider that the user can interact with to dynamically change the threshold value
        # within the range of 0 to 255
        self.threshold_slider = QSlider()
        self.threshold_slider.setOrientation(Qt.Horizontal)
        self.threshold_slider.setTickPosition(QSlider.TicksBelow)
        self.threshold_slider.setTickInterval(10)
        self.threshold_slider.setMinimum(0)
        self.threshold_slider.setMaximum(255)
        self.threshold_slider.setValue(127)

        # When the threshold slider's value is changed, update the image label
        self.threshold_slider.valueChanged.connect(self.update_image)

        # Label that will hold the desired image
        self.image_label = QLabel()
        self.clean_image_label = QLabel()

        # Prepare to use a compressed image if the provided image is too large to fit in the GUI
        self.compressed_img = None

        # Initialize the image label
        self.image = np.tile(np.arange(256, dtype=np.uint8).repeat(2), (512, 1))
        q_img = QImage(self.image.data, 512, 512, 512, QImage.Format_Indexed8)
        self.image_label.setPixmap(QPixmap.fromImage(q_img))

        # Wait to display the histogram window until the user requests it
        self.histogram_window = None

        # Prepare a button that when pushed will open the file dialog for the user
        open_image_btn = QPushButton("Open Image", self)
        open_image_btn.clicked.connect(self.open_image)

        # Prepare an extract text button that will utilize the current image and slider values
        extract_text_btn = QPushButton("Extract Text", self)
        extract_text_btn.clicked.connect(self.extract_text)

        # Prepare a button to provide a clean version of the image
        provide_clean_image_btn = QPushButton("Provide Clean Image", self)
        provide_clean_image_btn.clicked.connect(self.provide_clean_image)

        # Prepare a button to allow the user to save the preprocessed binary image
        save_btn = QPushButton("Save Preprocessed Binary Image", self)
        save_btn.clicked.connect(self.prepare_to_save)

        # Prepare a button to show the histogram
        show_histogram_btn = QPushButton("Show/Hide Histogram")
        show_histogram_btn.clicked.connect(self.show_histogram)

        provide_help_btn = QPushButton("Help", self)
        provide_help_btn.clicked.connect(self.provide_help)

        button_layout = QHBoxLayout()
        button_layout.addWidget(extract_text_btn)
        button_layout.addWidget(provide_clean_image_btn)
        button_layout.addWidget(show_histogram_btn)
        button_layout.addWidget(provide_help_btn)

        preprocessing_layout = QHBoxLayout()
        preprocessing_layout.addWidget(self.method_combobox)
        preprocessing_layout.addWidget(self.dilation_request)

        image_layout = QHBoxLayout()
        image_layout.addWidget(self.image_label)
        image_layout.addWidget(self.clean_image_label)

        # Create layout and add widgets
        layout = QVBoxLayout()
        layout.addWidget(open_image_btn)
        layout.addLayout(preprocessing_layout)
        layout.addWidget(self.noisy_label)
        layout.addWidget(self.clean_label)
        layout.addWidget(self.threshold_label)
        layout.addWidget(self.threshold_slider)
        layout.addLayout(image_layout)
        layout.addLayout(button_layout)
        layout.addWidget(save_btn)

        # Set dialog layout
        self.setLayout(layout)

    def open_image(self):
        """
        Opens a file dialog and displays the user-selected image.
        """

        # Allow the user to select an image
        image, file_name = open_image_dialog()

        # Check if the user gave an image with a valid format. If so, update the instance's image
        # attribute and update the image label.
        if image is not None:
            self.image = np.array(image)
            self.noisy_label.setText("Noisy File: " + file_name)
            if image.shape[0] > max_height and image.shape[1] > max_width:     # Both height and width are too large
                image = cv2.resize(image, (max_width, max_height))
                self.compressed_img = np.array(image)
            elif image.shape[0] > max_height and image.shape[1] <= max_width:  # Height is too large
                image = cv2.resize(image, (image.shape[1], max_height))
                self.compressed_img = np.array(image)
            elif image.shape[0] <= max_height and image.shape[1] > max_width:  # Width is too large
                image = cv2.resize(image, (max_width, image.shape[0]))
                self.compressed_img = np.array(image)
            self.update_image()
        else:
            QMessageBox.warning(self, "Error", "Did not receive a valid image!")

    def update_image(self):
        """
        Updates the displayed image.
        """

        # Get the index of the selected combo box item
        method_idx = self.method_combobox.currentIndex()

        # Get the new threshold value from the slider
        threshold = self.threshold_slider.value()

        # Display the new threshold value
        self.threshold_label.setText(f"Threshold Value: {threshold}")

        # Using the grayscale image, perform the requested binary thresholding method
        # with the user-selected threshold value
        if method_idx == 1:
            # Choice 1: cv2.THRESH_BINARY
            _, image = cv2.threshold(self.image, threshold, 255, cv2.THRESH_BINARY)
        elif method_idx == 2:
            # Choice 2: cv2.THRESH_BINARY_INV
            _, image = cv2.threshold(self.image, threshold, 255, cv2.THRESH_BINARY_INV)
        elif method_idx == 3:
            # Choice 3: cv2.THRESH_TRUNC
            _, image = cv2.threshold(self.image, threshold, 255, cv2.THRESH_TRUNC)
        elif method_idx == 4:
            # Choice 4: cv2.THRESH_TOZERO
            _, image = cv2.threshold(self.image, threshold, 255, cv2.THRESH_TOZERO)
        elif method_idx == 5:
            # Choice 5: cv2.THRESH_TOZERO_INV
            _, image = cv2.threshold(self.image, threshold, 255, cv2.THRESH_TOZERO_INV)
        else:
            # Choice 0: Original Image
            image = self.image

        if self.dilation_request.isChecked():
            image = dilate_image(image)

        if self.compressed_img is not None:
            compressed_h, compressed_w = self.compressed_img.shape
            image = cv2.resize(image, (compressed_w, compressed_h))

        # Update the image label by converting the image to a QImage and setting it as the pixmap for the image label
        image_h, image_w = image.shape
        q_img = QImage(image.data, image_w, image_h, image_w, QImage.Format_Indexed8)
        self.image_label.setPixmap(QPixmap.fromImage(q_img))

        # Update the histogram if the window is displayed
        if self.histogram_window is not None:
            self.histogram_window.update_histogram(image)
            self.histogram_window.show()

    def extract_text(self):
        """
        Run Tesseract OCR using the user-selected image, binary thresholding method, and threshold value
        to extract and display the text on the image.
        """

        # Get the index of the selected combo box item
        method_idx = self.method_combobox.currentIndex()

        # Get the new threshold value from the slider
        threshold = self.threshold_slider.value()

        if method_idx == 1:
            _, image = cv2.threshold(self.image, threshold, 255, cv2.THRESH_BINARY)
        elif method_idx == 2:
            _, image = cv2.threshold(self.image, threshold, 255, cv2.THRESH_BINARY_INV)
        elif method_idx == 3:
            _, image = cv2.threshold(self.image, threshold, 255, cv2.THRESH_TRUNC)
        elif method_idx == 4:
            _, image = cv2.threshold(self.image, threshold, 255, cv2.THRESH_TOZERO)
        elif method_idx == 5:
            _, image = cv2.threshold(self.image, threshold, 255, cv2.THRESH_TOZERO_INV)
        else:
            image = self.image

        if self.dilation_request.isChecked():
            image = dilate_image(image)

        # Run Tesseract OCR on the image
        text = pytesseract.image_to_string(image)

        # Display the extracted text
        QMessageBox.information(self, "Text", "Extracted Text: \n\n" + text)

        # Calculate text extraction accuracy if a clean image is provided
        if hasattr(self, 'clean_image') and isinstance(self.clean_image, np.ndarray):
            clean_text = pytesseract.image_to_string(self.clean_image)
            accuracy = calculate_accuracy(text, clean_text)
            QMessageBox.information(self, "Clean Text", "Extracted Clean Text: \n\n" + clean_text)
            QMessageBox.information(self, "Accuracy", "Text Extraction Accuracy: " + str(accuracy) + "%")

    def provide_clean_image(self):
        """
        Allows the user to provide a clean version of the image for accuracy calculation.
        """

        clean_image, clean_file_name = open_image_dialog()
        if clean_image is not None:
            self.clean_image = np.array(clean_image)
            self.clean_label.setText("Clean File: " + clean_file_name)
            if clean_image.shape[0] > max_height and clean_image.shape[1] > max_width:
                clean_image = cv2.resize(clean_image, (max_width, max_height))
            elif clean_image.shape[0] > max_height and clean_image.shape[1] <= max_width:
                clean_image = cv2.resize(clean_image, (clean_image.shape[1], max_height))
            elif clean_image.shape[0] <= max_height and clean_image.shape[1] > max_width:
                clean_image = cv2.resize(clean_image, (max_width, clean_image.shape[0]))

            clean_image_h, clean_image_w = clean_image.shape
            q_img = QImage(clean_image.data, clean_image_w, clean_image_h, clean_image_w, QImage.Format_Indexed8)
            self.clean_image_label.setPixmap(QPixmap.fromImage(q_img))

            QMessageBox.information(self, "Success",
                                    "Valid clean image received! Press \"Extract Text\" for an accuracy calculation!")
        else:
            QMessageBox.warning(self, "Error", "Did not receive a valid clean image!")

    def prepare_to_save(self):
        """
        Obtain the user-selected preprocessed binary image to prepare for saving to a directory.
        """

        method_idx = self.method_combobox.currentIndex()
        threshold = self.threshold_slider.value()

        if method_idx == 1:
            _, image = cv2.threshold(self.image, threshold, 255, cv2.THRESH_BINARY)
        elif method_idx == 2:
            _, image = cv2.threshold(self.image, threshold, 255, cv2.THRESH_BINARY_INV)
        elif method_idx == 3:
            _, image = cv2.threshold(self.image, threshold, 255, cv2.THRESH_TRUNC)
        elif method_idx == 4:
            _, image = cv2.threshold(self.image, threshold, 255, cv2.THRESH_TOZERO)
        elif method_idx == 5:
            _, image = cv2.threshold(self.image, threshold, 255, cv2.THRESH_TOZERO_INV)
        else:
            QMessageBox.warning(self, "No Box Selected", "Please select a binary thresholding method before requesting"
                                                         " to save a binary image.")
            return
        if self.dilation_request.isChecked():
            image = dilate_image(image)
        save_image(self, image)

    def show_histogram(self):
        """
        Shows or hides the histogram with respect to the currently displayed image if the histogram button is pressed.
        """

        # Create the histogram window if it doesn't exist, otherwise remove it
        if self.histogram_window is None:
            self.histogram_window = HistogramWindow(self.image)
        else:
            self.histogram_window = None
        self.update_image()

    def provide_help(self):
        """
        Display help information for the "Binary Thresholding" program.
        """

        help_text = """How to Enhance and Extract Text from an Image with Binary Thresholding:

                Step 1: Pass in your noisy image with "Open Image."
                Step 2: Choose one of several binary thresholding methods from the drop-down menu. You will then see the resulting binary image.
                Step 3: Play with the "Threshold" slider to update the binary image.
                Step 4: Click on "Extract Text" to perform text extraction.
                Step 5: Save the preprocessed binary image if needed.

                Additional Features:

                If you pass in a clean version of your noisy image with "Provide Clean Image" and then press "Extract Text," you can get the extracted text from the noisy and clean counterparts. You will also get a text extraction accuracy from 0%-100%, which represents how well the extracted text from the noisy image resembles the extracted text from the clean image.

                Press "Show/Hide Histogram" to get or remove the histogram of the currently displayed image.
                
                You can also bold the text be clicking the "Bold Text" checkbox.

                BIG Note:
                 
                Your image will be compressed in the application if it is over 512x512. However, saving the binary image will be based on the original dimensions of the given image. The same applies to the extracted text, accuracy calculations, and histograms.  
                """

        QMessageBox.information(self, "Help", help_text)
