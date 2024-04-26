import cv2
import pytesseract
from pytesseract import Output
import threading
from concurrent.futures import ThreadPoolExecutor
import multiprocessing
import numpy as np
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QWidget,
    QPushButton,
    QLabel,
    QMessageBox,
    QVBoxLayout,
    QComboBox,
    QHBoxLayout
)

from src.util.dialog import open_image_dialog
from src.util.accuracy import calculate_accuracy
from src.util.save import save_image
from src.util.histogram import HistogramWindow
from src.util.dilate_image import dilate_image

max_width = 512
max_height = 512


class GetBestImage(QWidget):

    image: np.ndarray
    best_image: np.ndarray
    best_image_confidence: float
    best_accuracy: float
    titles = ["Original Image", "Get Best Image"]
    clean_image: np.ndarray
    lock: threading.Lock

    def __init__(self):
        """
        Initializes the "Find Best Image" window for the application.
        """

        # Initialize the parent class (QWidget)
        super().__init__()

        self.setWindowTitle("Get Best Image")

        # Go through the titles and allow the user to see them and choose one through a combo box.
        self.method_combobox = QComboBox()
        for title in self.titles:
            self.method_combobox.addItem(title)
        self.method_combobox.currentIndexChanged.connect(self.update_image)

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

        # Label that will hold the histogram of the desired image
        self.histogram_label = QLabel()

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

        # Prepare a button that when pushed will provide help regarding Otsu's thresholding and the features of this
        # program
        provide_help_btn = QPushButton("Help", self)
        provide_help_btn.clicked.connect(self.provide_help)

        button_layout = QHBoxLayout()
        button_layout.addWidget(extract_text_btn)
        button_layout.addWidget(provide_clean_image_btn)
        button_layout.addWidget(show_histogram_btn)
        button_layout.addWidget(provide_help_btn)

        image_layout = QHBoxLayout()
        image_layout.addWidget(self.image_label)
        image_layout.addWidget(self.clean_image_label)

        # Label to display the current best preprocessing method and parameters
        self.method_label = QLabel("Best Preprocessing Method: N/A")

        self.best_image = None
        self.best_image_confidence = 0.0
        self.best_accuracy = 0.0
        self.lock = threading.Lock()

        # Create layout and add widgets
        layout = QVBoxLayout()
        layout.addWidget(open_image_btn)
        layout.addWidget(self.method_combobox)
        layout.addWidget(self.noisy_label)
        layout.addWidget(self.clean_label)
        layout.addWidget(self.method_label)
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
            self.best_image = None
            self.best_image_confidence = 0.0
            self.best_accuracy = 0.0
            self.update_image()
        else:
            QMessageBox.warning(self, "Error", "Did not receive a valid image!")

    def update_image(self):
        """
        Updates the displayed image.
        """

        # Get the index of the selected combo box item
        method_idx = self.method_combobox.currentIndex()

        if method_idx == 0:
            # Choice 0: Original Image
            image = self.image
        else:
            # Choice 1: Find Best Image
            if self.best_image is not None:
                image = self.best_image
            else:
                self.find_best_image()
                if self.best_image is not None:
                    image = self.best_image
                else:
                    image = self.image
                    QMessageBox.warning(self, "Error", "Could not calculate an ideal image!")

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
        Run Tesseract OCR using the currently displayed image and display the text on the image.
        """

        # Get the index of the selected combo box item
        method_idx = self.method_combobox.currentIndex()

        if method_idx == 0:
            image = self.image
        else:
            image = self.best_image

        if image is not None:
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
        else:
            QMessageBox.warning(self, "Preprocessing Error", "Cannot extract text from a nonexistent preprocessed image")

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

    def prepare_to_save(self):
        """
        Obtain the currently displayed preprocessed binary image to prepare for saving to a directory.
        """

        if self.best_image is not None:
            save_image(self, self.best_image)
        else:
            QMessageBox.warning(self, "Error", "Please wait until the best image has been created before saving.")

    def show_histogram(self):
        """
        Shows or hides the histogram with respect to the currently displayed image if the histogram button is pressed.
        """

        # Create the histogram window if it doesn't exist, otherwise remove it
        if self.histogram_window is None:
            if self.best_image is not None:
                self.histogram_window = HistogramWindow(self.best_image)
            else:
                self.histogram_window = HistogramWindow(self.image)
        else:
            self.histogram_window = None

        self.update_image()

    def find_best_image(self):
        """
        Runs through a variety of preprocessing methods in parallel to determine the image the computer is able to read
        with the most confidence.

        If a clean image is provided by the user, compare the preprocessed binary image with the clean image and
        return the image with the highest accuracy.
        """

        self.best_image = None
        self.best_image_confidence = 0.0
        self.best_accuracy = 0.0

        clean_img_text = None
        if hasattr(self, 'clean_image') and isinstance(self.clean_image, np.ndarray):
            clean_img_text = pytesseract.image_to_string(self.clean_image)

        # Track the number of words from the original noisy image
        original_text = pytesseract.image_to_string(self.image)
        original_word_count = len(original_text.split())

        if original_word_count != 0:
            methods = [
                ("Binary Thresholding", {"start": 100, "end": 200 + 1, "bold": False}),                         # Core 1
                ("Adaptive Thresholding (Mean)", {"c_constants": list(range(0, 100 + 1)), "bold": False}),      # Core 2
                ("Adaptive Thresholding (Gaussian)", {"c_constants": list(range(0, 100 + 1)), "bold": False}),  # Core 3
                ("Median Filtering", {"kernel_sizes": list(range(3, 21 + 1, 2)), "bold": False}),               # Core 4
                ("Binary Thresholding 2", {"start": 100, "end": 200 + 1, "bold": True}),                        # Core 5
                ("Adaptive Thresholding 2 (Mean)", {"c_constants": list(range(0, 100 + 1)), "bold": True}),     # Core 6
                ("Adaptive Thresholding 2 (Gaussian)", {"c_constants": list(range(0, 100 + 1)), "bold": True}), # Core 7
                ("Median Filtering 2", {"kernel_sizes": list(range(3, 21 + 1, 2)), "bold": True}),              # Core 8
            ]
            num_cores = multiprocessing.cpu_count()

            if num_cores >= 8:
                # Run methods concurrently if the user has 8 or more cores
                with ThreadPoolExecutor(max_workers=num_cores) as executor:

                    # Submit Otsu's method separately (Only 1 thread needed)
                    otsu_future = executor.submit(self.find_best_otsu_image, [False, True], original_word_count,
                                                  clean_img_text)

                    # Submit other methods to the thread pool
                    futures = [executor.submit(self.find_best_image_method, method, params, original_word_count,
                                               clean_img_text) for method, params in methods]

                    # Wait for Otsu's method
                    otsu_future.result()

                    # Wait for all other methods to finish
                    for future in futures:
                        future.result()
            else:
                # Run methods sequentially if the user has fewer than 8 cores
                self.find_best_otsu_image([False, True], original_word_count, clean_img_text)
                for method, params in methods:
                    self.find_best_image_method(method, params, original_word_count, clean_img_text)
        else:
            QMessageBox.warning(self, "Error", "Could not find any text in your image")

    def find_best_otsu_image(self, bold, original_word_count, clean_img_text):
        """
        Runs Otsu's method with and without the text "bolding" and checks if it is the most computer-recognizable image.
        """

        ret, image = cv2.threshold(self.image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        self.calculate_doc_confidence(image, "Otsu's Thresholding", f"\nCalculated Threshold: {ret}, Bold Text: "
                                                                    f"{bold[0]}", original_word_count, clean_img_text)
        image = dilate_image(image)
        self.calculate_doc_confidence(image, "Otsu's Thresholding", f"\nCalculated Threshold: {ret}, Bold Text: "
                                                                    f"{bold[1]}", original_word_count, clean_img_text)

    def find_best_image_method(self, method, params, original_word_count, clean_img_text):
        """
        Runs through ideal thresholding methods that are useful in removing noise from text documents by testing
        different parameter combinations (Binary Thresholding, Adaptive Thresholding, and Median Filtering). Check both
        original text and text "bolding"

        :param method: The assigned preprocessing method that a core will try
        :param params: The set of parameters the core will try on the assigned preprocessing method
        :param original_word_count: The number of words extracted from the original image
        :param clean_img_text: Optional, The extracted text from the provided clean image
        :type original_word_count: int
        """

        method_name, method_params = method, params
        if method_name == "Binary Thresholding" or method_name == "Binary Thresholding 2":
            start, end, bold = method_params["start"], method_params["end"], method_params["bold"]
            for i in range(start, end, 1):
                _, image = cv2.threshold(self.image, i, 255, cv2.THRESH_BINARY)
                if bold:
                    image = dilate_image(image)
                self.calculate_doc_confidence(image, "Binary Thresholding", f"\nThreshold: {i}, Bold Text: {bold}",
                                              original_word_count, clean_img_text)

        elif method_name == "Adaptive Thresholding (Mean)" or method_name == "Adaptive Thresholding 2 (Mean)":
            c_constants, bold = method_params["c_constants"], method_params["bold"]
            for c_constant in c_constants:
                image = cv2.adaptiveThreshold(self.image, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY,
                                              255, c_constant)
                if bold:
                    image = dilate_image(image)
                self.calculate_doc_confidence(image, "Adaptive Thresholding", f"\nParameters: ADAPTIVE_THRESH_MEAN_C, "
                                                                              f"Block Size: 255, C Constant: "
                                                                              f"{c_constant}, Bold Text: {bold}",
                                                                              original_word_count, clean_img_text)
        elif method_name == "Adaptive Thresholding (Gaussian)" or method_name == "Adaptive Thresholding 2 (Gaussian)":
            c_constants, bold = method_params["c_constants"], method_params["bold"]
            for c_constant in c_constants:
                image = cv2.adaptiveThreshold(self.image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,
                                              255, c_constant)
                if bold:
                    image = dilate_image(image)
                self.calculate_doc_confidence(image, "Adaptive Thresholding", f"\nParameters: "
                                                                              f"ADAPTIVE_THRESH_GAUSSIAN_C, "
                                                                              f"Block Size: 255, C Constant: "
                                                                              f"{c_constant}, Bold Text: {bold}",
                                                                              original_word_count, clean_img_text)
        elif method_name == "Median Filtering" or method_name == "Median Filtering 2":
            kernel_sizes, bold = method_params["kernel_sizes"], method_params["bold"]
            for kernel_size in kernel_sizes:
                image = cv2.medianBlur(self.image, kernel_size)
                if bold:
                    image = dilate_image(image)
                self.calculate_doc_confidence(image, "Median Filtering",
                                              f"\nParameters: Kernel Size: {kernel_size}, Bold Text: "
                                              f"{bold}", original_word_count, clean_img_text)

    def calculate_doc_confidence(self, image, method, parameters, original_word_count, clean_img_text):
        """
        Runs the preprocessed image through Tesseract and obtain word confidence values for every word extracted
        from the image. Keeps track of the image with the highest confidence average.

        If there is a clean image, keep track of the image with the highest accuracy instead.

        :param image: The preprocessed image
        :param method: The preprocessing method utilized
        :param parameters: The parameters used for the method
        :param original_word_count: The number of words extracted from the original image
        :param clean_img_text: Optional, The extracted text from the provided clean image
        :type image: np.ndarray
        :type original_word_count: int
        """

        if clean_img_text is None:
            result = pytesseract.image_to_data(image, config=r'--oem 3 --psm 6', output_type=Output.DICT)
            confidences = result['conf']

            num_words = 0.0
            confidence_total = 0

            for word, confidence in zip(result['text'], confidences):
                if word == "" and confidence == -1:     # More common error (no word and no confidence)
                    continue
                elif word != "" and confidence == -1:   # Less common error (word, but no confidence)
                    num_words = num_words + 1.0
                else:
                    num_words = num_words + 1.0
                    confidence_total = confidence_total + confidence

            if num_words != 0.0 and pytesseract.image_to_string(image).strip() != "":

                retained_word_percentage = num_words / original_word_count

                # Ignore text documents that lost more than 10% of text
                if retained_word_percentage >= 0.90:
                    doc_confidence_percentage = (confidence_total / num_words)

                    with self.lock:
                        if doc_confidence_percentage >= self.best_image_confidence:
                            self.best_image_confidence = doc_confidence_percentage
                            self.best_image = image.copy()  # Make a copy to avoid shared references
                            self.update_best_method_label(method, parameters)

        else:
            preprocess_text = pytesseract.image_to_string(image)
            accuracy = calculate_accuracy(preprocess_text, clean_img_text)
            with self.lock:
                if accuracy >= self.best_accuracy:
                    self.best_accuracy = accuracy
                    self.best_image = image.copy()
                    self.update_best_method_label(method, parameters)

    def update_best_method_label(self, method, parameters):
        """
        Change the label to show the user the preprocessing method and parameters used that produced the image
        that the computer believes is the most recognizable.

        If a clean image is provided, the label is based on the most accurate preprocessed image with respect to the
        clean image.

        :param method: The preprocessing method utilized
        :param parameters: The parameters used for the method
        """

        label_text = f"Best Preprocessing Method: {method} {parameters}"
        self.method_label.setText(label_text)

    def provide_help(self):
        """
        Display help information for the "Get Best Image" program.
        """

        help_text = """How to get "The Best Image":

                Step 1: Pass in your noisy image with "Open Image."
                Step 2: Choose "Get Best Image" from the drop-down menu. The program will calculate a binary image that the computer is able to recognize with the highest confidence based on extracted text (excluding calculated images with no recognizable text). This process will take some time, especially if your image is large. Once completed, you will be able to see the resulting binary image.
                Step 3: Click on "Extract Text" to perform text extraction.
                Step 4: Save the preprocessed binary image if needed.

                Additional Features:

                If you pass in a clean version of your noisy image with "Provide Clean Image" and then press "Extract Text," you can get the extracted text from the noisy and clean counterparts. You will also get a text extraction accuracy from 0%-100%, which represents how well the extracted text from the noisy image resembles the extracted text from the clean image. The best image will also be with respect to the given clean image rather than what the computer believes is the most recognizable image.

                Press "Show/Hide Histogram" to get or remove the histogram of the currently displayed image.
                
                Note:
                 
                "The Best Image" in terms of this application means the most computer-recognizable binary image, not necessarily the most human-recognizable image. Your image will be tested on popular preprocessing techniques that are most likely to enhance text documents, including Otsu's, binary, and adaptive thresholding, along with median filtering. It is almost certain the calculated image will not be the best it can possibly be because there are many other complex preprocessing techniques that are either available or under development that may work better than the ones available on this application. THERE IS NO ONE SIZE FITS ALL SOLUTION TO IMAGE ENHANCEMENT! 
                
                BIG Note:
                 
                Your image will be compressed in the application if it is over 512x512. However, saving the binary image will be based on the original dimensions of the given image. The same applies to the extracted text, accuracy calculations, and histograms.  
                """

        QMessageBox.information(self, "Help", help_text)
