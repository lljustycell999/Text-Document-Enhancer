import cv2
import numpy as np
import pytesseract
import os
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QWidget,
    QPushButton,
    QLabel,
    QHBoxLayout,
    QFileDialog,
    QComboBox,
    QMessageBox,
    QVBoxLayout,
    QCheckBox
)

from src.util.dialog import open_image_dialog
from src.util.accuracy import calculate_accuracy
from src.util.save import save_image
from src.util.histogram import HistogramWindow
from src.util.dilate_image import dilate_image

max_width = 512
max_height = 512


class OtsusThresholding(QWidget):
    """
    A GUI widget for applying Otsu's Method for thresholding to an image.

    This class provides a GUI for selecting an image and applying Otsu's Method for thresholding to it.
    Users can view the original grayscale image and the binary image created via Otsu's Method, as well as
    obtain computer-extracted text from either of these images. The user may also save the preprocessed binary image
    with a specific filename, image format, and directory. The user can also display and save the corresponding
    histogram graphs of these images as well.

    If the user provides a clean version of the image, the user can see the differences between the extracted
    text of the clean image and any of the other images. On top of that, the feature will also provide a text
    extraction accuracy value.

    This specific widget also has a feature that when given two directories (one noisy and one clean),
    a bulk text extraction accuracy value can be calculated.

    The user can also check a box to bold the text through a dilation of size 2x2.

    Attributes:
        image (np.ndarray): The currently displayed image.
        compressed_img (np.ndarray): The compressed version of the currently displayed image (Only use if the image
        size is too large for the GUI)
        clean_image (np.ndarray): The clean version of the image for text extraction accuracy calculations.
        titles (list): A list of titles for different image display options.
        noisy_directory (str): The file path of a directory that has noisy images for bulk text extraction
        accuracy calculations.
        clean_directory (str): The file path of a directory that has clean images for bulk text extraction
        accuracy calculations.
    """

    image: np.ndarray
    compressed_img: np.ndarray
    clean_image: np.ndarray
    titles = ["Original Image", "THRESH_BINARY + cv2.THRESH_OTSU"]
    noisy_directory: str
    clean_directory: str

    def __init__(self):
        """
        Initializes the Otsu's thresholding window for the application.
        """

        # Initialize the parent class (QWidget)
        super().__init__()

        self.setWindowTitle("Otsu's Thresholding")

        # Go through the titles and allow the user to see them and choose one through a combo box.
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

        # Label that will hold the desired image
        self.image_label = QLabel()
        self.clean_image_label = QLabel()

        # Prepare to use a compressed image if the provided image is too large to fit in the GUI
        self.compressed_img = None

        # Initialize the image label
        self.image = np.tile(np.arange(256, dtype=np.uint8).repeat(2), (512, 1))
        q_img = QImage(self.image.data, 512, 512, 512, QImage.Format_Indexed8)
        self.image_label.setPixmap(QPixmap.fromImage(q_img))

        # Label that will keep track of the calculated threshold values
        self.threshold_label = QLabel("Calculated Threshold: N/A")

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

        # Prepare a button to provide a noisy directory
        provide_noisy_directory_btn = QPushButton("Provide Noisy Directory", self)
        provide_noisy_directory_btn.clicked.connect(self.provide_noisy_directory)

        # Prepare a button to provide a clean directory
        provide_clean_directory_btn = QPushButton("Provide Clean Directory", self)
        provide_clean_directory_btn.clicked.connect(self.provide_clean_directory)

        # Prepare a button to show the histogram
        show_histogram_btn = QPushButton("Show/Hide Histogram")
        show_histogram_btn.clicked.connect(self.show_histogram)

        # Prepare a button that when pushed will provide help regarding Otsu's thresholding and the features of this
        # program
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

        # Put the clean and noisy directory buttons side to side (and the help button)
        directory_layout = QHBoxLayout()
        directory_layout.addWidget(provide_noisy_directory_btn)
        directory_layout.addWidget(provide_clean_directory_btn)

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
        layout.addLayout(image_layout)
        layout.addLayout(button_layout)
        layout.addLayout(directory_layout)
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

        if method_idx == 1:
            # Choice 1: cv2.THRESH_BINARY + cv2.THRESH_OTSU

            # Using the grayscale image, calculate the new threshold value using Otsu's method
            # and retrieve the binary image that uses that value.
            ret, image = cv2.threshold(self.image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        else:
            # Choice 0: Original Image
            ret, image = "N/A", self.image

        if self.dilation_request.isChecked():
            image = dilate_image(image)

        if self.compressed_img is not None:
            compressed_h, compressed_w = self.compressed_img.shape
            image = cv2.resize(image, (compressed_w, compressed_h))

        # Display the new threshold value
        self.threshold_label.setText(f"Calculated Threshold: {ret}")

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
        Run Tesseract OCR using the user-selected image or its binary image after going through Otsu's method
        to extract and display the text on the image.
        """

        method_idx = self.method_combobox.currentIndex()
        if method_idx == 1:
            _, image = cv2.threshold(self.image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        else:
            _, image = "N/A", self.image

        if self.dilation_request.isChecked():
            image = dilate_image(image)

        # Run Tesseract OCR on the image
        text = pytesseract.image_to_string(image)

        # Display the extracted text
        QMessageBox.information(self, "Text", "Extracted Text: \n\n" + text)

        # Calculate the text extraction accuracy if a clean image is provided
        if hasattr(self, 'clean_image') and isinstance(self.clean_image, np.ndarray):
            clean_text = pytesseract.image_to_string(self.clean_image)
            accuracy = calculate_accuracy(text, clean_text)
            QMessageBox.information(self, "Clean Text", "Extracted Clean Text: \n\n" + clean_text)
            QMessageBox.information(self, "Accuracy", "Text Extraction Accuracy: " + str(accuracy) + "%")

    def provide_clean_image(self):
        """
        Allows the user to provide a clean version of the image for text extraction accuracy calculations.
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

    def provide_noisy_directory(self):
        """
        Allows the user to provide a noisy directory of images for bulk text extraction accuracy calculations.
        """

        noisy_directory = QFileDialog.getExistingDirectory(self, "Select Noisy Directory")
        if noisy_directory != "":
            self.noisy_directory = noisy_directory
            QMessageBox.information(self, "Success", "Received noisy directory!")
            self.process_directory()
        else:
            QMessageBox.warning(self, "Error", "Did not receive a noisy directory!")

    def provide_clean_directory(self):
        """
        Allows the user to provide a clean directory of images for bulk text extraction accuracy calculations.
        """

        clean_directory = QFileDialog.getExistingDirectory(self, "Select Clean Directory")
        if clean_directory != "":
            self.clean_directory = clean_directory
            QMessageBox.information(self, "Success", "Received clean directory!")
            self.process_directory()
        else:
            QMessageBox.warning(self, "Error", "Did not receive a clean directory!")

    def process_directory(self):
        """
        Checks that a noisy and clean directory have been provided. If so, iterates through both directories
        (assuming that both are alphabetically ordered so that the current file of each directory are the noisy and
        clean versions of the same image). Afterwards, a bulk text extraction accuracy will be calculated, along with
        the number of image comparisons used.
        """

        accuracy_sum = 0.0
        num_image_comparisons = 0

        # Check for a noisy and clean directory
        if hasattr(self, 'noisy_directory') and hasattr(self, 'clean_directory'):

            QMessageBox.information(self, "Got Both Directories", "Both directories received! Press OK to start, "
                                                                  "bulk text extraction!")

            # Get the list of files from both directories (Remove .DS_Store if running on a Mac)
            noisy_files = sorted([f for f in os.listdir(self.noisy_directory) if f != '.DS_Store'])
            clean_files = sorted([f for f in os.listdir(self.clean_directory) if f != '.DS_Store'])

            for i, cur_noisy_file in enumerate(noisy_files):
                if cur_noisy_file.lower().endswith((".tiff", ".png", ".jpeg", ".jpg", ".bmp")):
                    if clean_files[i].lower().endswith((".tiff", ".png", ".jpeg", ".jpg", ".bmp")):

                        # Get the grayscale image of the current noisy and clean valid images
                        valid_noisy_img = cv2.imread(self.noisy_directory + "/" + cur_noisy_file, 0)
                        valid_clean_img = cv2.imread(self.clean_directory + "/" + clean_files[i], 0)

                        # Perform Otsu's thresholding on the noisy image
                        _, otsu_noisy_img = cv2.threshold(valid_noisy_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

                        # Run Tesseract OCR on both images
                        noisy_text = pytesseract.image_to_string(otsu_noisy_img)
                        clean_text = pytesseract.image_to_string(valid_clean_img)

                        # Keep track of the accuracy sum and total number of image comparisons
                        cur_accuracy = calculate_accuracy(noisy_text, clean_text)
                        accuracy_sum += cur_accuracy
                        num_image_comparisons += 1

            bulk_accuracy = accuracy_sum / num_image_comparisons

            QMessageBox.information(self, "Image Comparisons", "# of Image Comparisons: " + str(num_image_comparisons))
            QMessageBox.information(self, "Bulk Accuracy", "Bulk Text Extraction Accuracy: " + str(bulk_accuracy) + "%")
        else:
            QMessageBox.warning(self, "Got One Directory",
                                "Provide the other directory to perform bulk text extraction!")

    def prepare_to_save(self):
        """
        Obtain the user-selected preprocessed binary image to prepare for saving to a directory.
        """

        _, image = cv2.threshold(self.image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
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
        Display help information for the "Otsu's Thresholding" program.
        """

        help_text = """How to Enhance and Extract Text from an Image with Otsu's Method:
        
                Step 1: Pass in your noisy image with "Open Image."
                Step 2: Choose "THRESH_BINARY + cv2.THRESH_OTSU" from the drop-down menu. You will then see the resulting binary image that went through Otsu's thresholding.
                Step 3: Click on "Extract Text" to perform text extraction.
                Step 4: Save the preprocessed binary image if needed.
                
                Additional Features:
                
                If you pass in a clean version of your noisy image with "Provide Clean Image" and then press "Extract Text," you can get the extracted text from the noisy and clean counterparts. You will also get a text extraction accuracy from 0%-100%, which represents how well the extracted text from the noisy image resembles the extracted text from the clean image.
                
                Press "Show/Hide Histogram" to get or remove the histogram of the currently displayed image.
                
                Provide a noisy and clean directory using the "Provide Noisy Directory" and "Provide Clean Directory" buttons to calculate a bulk text extraction accuracy for all of your images.
                
                You can also bold the text be clicking the "Bold Text" checkbox.
                
                Note:
                 
                If you want to calculate a bulk text extraction accuracy, make sure the files in both of your directories line up ALPHABETICALLY so that the first image in the noisy and clean directories are the noisy and clean versions of the same image, do this again for the second pair of images, and so on.
                
                BIG Note:
                 
                Your image will be compressed in the application if it is over 512x512. However, saving the binary image will be based on the original dimensions of the given image. The same applies to the extracted text, accuracy calculations, and histograms.  
                """

        QMessageBox.information(self, "Help", help_text)
