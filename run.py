import sys

from PySide6.QtWidgets import (
    QApplication,
    QVBoxLayout,
    QMainWindow,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QWidget,
    QHBoxLayout,
    QMessageBox
)

from src.thresholding.adaptive_thresholding import AdaptiveThresholding
from src.thresholding.binary_thresholding import BinaryThresholding
from src.thresholding.otsus_thresholding import OtsusThresholding
from src.filtering.median_filtering import MedianFiltering
from src.filtering.gaussian_blur import GaussianBlur
from src.filtering.bilateral_filtering import BilateralFiltering
from src.morphology.opening_closing import OpeningClosing
from src.morphology.closing_opening import ClosingOpening
from src.util.get_best_image import GetBestImage

# Dictionary that holds the program names as keys, and class definitions as values
programs = {
    "Otsu's Thresholding": OtsusThresholding,
    "Binary Thresholding": BinaryThresholding,
    "Adaptive Thresholding": AdaptiveThresholding,
    "Opening-Closing Morphology": OpeningClosing,
    "Closing-Opening Morphology": ClosingOpening,
    "Median Filtering": MedianFiltering,
    "Gaussian Blur Filtering": GaussianBlur,
    "Bilateral Filtering": BilateralFiltering,
    "Get Best Image": GetBestImage
}


class ProgramSelector(QMainWindow):
    """
    A GUI application for selecting and running the available image preprocessing programs.

    This class represents the main window of the application. It allows the user to select
    an image preprocessing program from a list and execute it by clicking a start button.

    Attributes:
        instances (list): A list to keep track of instances of the selected image preprocessing programs.
    """

    instances = []

    def __init__(self):
        """
        Initializes the main window of the application.
        """

        # Need to initialize the parent class (QMainWindow) to show the main window
        super().__init__()

        self.setWindowTitle("Text Document Enhancer")

        layout = QVBoxLayout()
        self.program_list = QListWidget()

        # Iterate through each key in the programs dictionary to display all available thresholding programs
        # to the user as a list widget
        for program in programs:
            self.program_list.addItem(QListWidgetItem(program))

        start_button = QPushButton("Start")
        start_button.clicked.connect(self.start)

        help_button = QPushButton("Start Where?")
        help_button.clicked.connect(self.give_help)

        button_layout = QHBoxLayout()
        button_layout.addWidget(start_button)
        button_layout.addWidget(help_button)

        layout.addWidget(self.program_list)
        layout.addLayout(button_layout)

        # Set the central widget to ensure it contains the start button and thresholding programs
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def start(self):
        """
        Start the requested image preprocessing program.
        """

        try:
            # Get the text from the requested image preprocessing program to use as a key
            # to the programs dictionary and obtain an instance of its corresponding class
            item = self.program_list.selectedItems()[0]
            instance = programs.get(item.text())()

            # Save the instance for later use
            self.instances.append(instance)

            # Show the instance (can do this thanks to initializing the parent class)
            instance.show()
        except IndexError:
            # Reaches here if the user clicks the start and no image preprocessing program is selected.
            # In that case, do nothing
            return

    def give_help(self):
        """
        Display general help information
        """

        help_text = """To begin, choose any one of the nine subprograms and press the "Start" button. Here is a brief description of each subprogram:
                
                Otsu's Thresholding: Automatically calculates an optimal threshold value that separates the foreground from the background. Overall helpful, but probably not for "coffee-stain" or "salt-and-pepper" noise.
                
                Binary Thresholding: The user can manually input a threshold value rather than automatically. May be helpful if Otsu's thresholding worsens the noise.
                
                Adaptive Thresholding: Divides the image into regions and calculates thresholds for each region. Works generally well, including on "coffee-stain" noise.
                
                Opening-Closing Morphology: Dilates, then erodes specified image regions.
                
                Closing-Opening Morphology: Erodes, then dilates specified image regions.
                
                Median Filtering: Calculates the median value for every pixel based on a specified size of neighboring pixels.
                
                Gaussian Blur Filtering: Similar to "Median Filtering," except it uses weighted sums instead of medians.
                
                Bilateral Filtering: Goes through every pixel and considers a specified size of neighboring pixels and their intensity differences so that only nearby and similar pixels are blurred. Best for reducing "salt-and-pepper" noise.
                
                Get Best Image: Utilizes some of the above preprocessing methods to determine an ideal computer-readable image. Use this if you are trying to remove as much noise from a text document as possible.
                
                Acceptable file formats include .tiff, .png, .jpeg, .jpg, and .bmp.
                """

        QMessageBox.information(self, "Help", help_text)


# Check that run.py is executed directly, otherwise do not run the application
if __name__ == "__main__":
    # Initialize a QApplication and ProgramSelector class, show the subprogram
    # options, and keep allowing for input until the user closes out.
    app = QApplication(sys.argv)
    ex = ProgramSelector()
    ex.show()
    sys.exit(app.exec())
