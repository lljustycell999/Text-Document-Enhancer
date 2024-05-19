# Text Document Enhancer

Welcome to the Text Document Enhancer's GitHub Repository! This page has the Python code, a project documentation report, and a presentation so that viewers may understand the project's purpose, functionality, and performance. This Python project primarily encompasses two image processing packages, OpenCV and PyTesseract, along with several other Python libraries. If you have any questions or concerns about the project, you may communicate with me through this GitHub account. Also, this project is open-source, so you may add or modify any of the project code to improve its quality and/or add more core image processing features by sending pull requests. If you choose to update this project in your repository, please be aware of the license requirements before doing so. Thank you, and I hope you enjoy the application!

Update: I have a requirements.txt file all set, so it is now possible to fully run the project from the terminal on MacOS, Windows, and Ubuntu Linux.

# MacOS Installation

1: Install the latest versions of [Python](https://www.python.org/downloads/), [Git](https://git-scm.com/download/mac), and [Homebrew](https://brew.sh/).

2: In the terminal, clone this GitHub repository with the commands:

  * git clone https://github.com/lljustycell999/Text-Document-Enhancer

  * cd Text-Document-Enhancer

3: Install the dependencies in the requirements.txt file by entering this terminal command:

  * pip install -r requirements.txt

4: For good measure, ensure that PyTesseract has been properly installed with this terminal command:

  * brew install tesseract

5: Run the project in the terminal with the command:

  * python run.py

# Windows Installation

1: Install the latest versions of [Python](https://www.python.org/downloads/) and [Git](https://git-scm.com/download/win).

2: Install the Windows version of Tesseract at https://github.com/UB-Mannheim/tesseract/wiki.

3: Add the path to the Tesseract-OCR directory to your system's PATH environment variable. You can do this by performing the following:

  * 3a: Copy the installation path to Tesseract-OCR.
  
  * 3b: Type in "Edit the system environment variables" in the Windows search bar. It should appear as the first search result, click on it.
  
  * 3c: Open the "Environment Variables" window.
  
  * 3d: Select the "Path" variable under "System Variables" (NOT "User Variables").
  
  * 3e: Click "New" and paste the Tesseract installation path. Press "OK" to save the changes.

4: In the Windows Powershell, clone this GitHub repository with the commands:

  * git clone https://github.com/lljustycell999/Text-Document-Enhancer

  * cd Text-Document-Enhancer

5: Install the dependencies in the requirements.txt file in the terminal:

  * pip install -r requirements.txt

6: Run the project in the terminal:

  * python run.py

# Ubuntu Linux Installation

1: Run the following commands in the terminal to install Git and Tesseract:

  * sudo apt update

  * sudo apt install git
   
  * sudo apt install tesseract-ocr

2: In the terminal, clone this GitHub repository with the commands:

  * git clone https://github.com/lljustycell999/Text-Document-Enhancer

  * cd Text-Document-Enhancer

3: Use the following terminal commands to ensure that Python is installed and updated:

  * sudo apt update

  * sudo apt install python3 python3-venv python3-pip

4: You NEED to have a virtual environment for this project to work. For the sake of convenience with Python, I recommend venv. To activate venv, use these terminal commands:

  * python3 -m venv venv
  
  * source venv/bin/activate

5: Just in case, update pip to its latest version using this terminal command:

  * pip install --upgrade pip

6: Install the dependencies in the requirements.txt file by using this terminal command:

  * pip install -r requirements.txt

7: Run the project in the terminal with this command:

  * python run.py

![image](https://github.com/lljustycell999/Text-Document-Enhancer/assets/123667513/38dcfdfc-3412-4f8d-a8ef-3725abc7ec44)
<img width="748" alt="image" src="https://github.com/lljustycell999/Text-Document-Enhancer/assets/123667513/aa05fc9a-36f2-4141-967d-1bf3229f0a33">

