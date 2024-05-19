# Text Document Enhancer

Welcome to the Text Document Enhancer's GitHub Repository! Right now, I have the Python code, a project documentation report, and a presentation so that viewers may understand the project's purpose, functionality, and performance. This Python project primarily encompasses two image processing package libraries, OpenCV and PyTesseract, along with several other Python libraries. If you have any questions or concerns about the project, you may communicate with me through this GitHub account. Also, this project is open-source, so you may add or modify any of the project code to improve its quality and/or add more core image processing features by sending pull requests. If you choose to update this project in your repository, please be aware of the license requirements before doing so. Thank you, and I hope you enjoy the application!

Update: I have a requirements.txt file all set, so it is now possible to fully run the project from the terminal on MacOS, Windows, and Ubuntu Linux.

# MacOS Installation

1: In the terminal, clone this GitHub repository with:

git clone https://github.com/lljustycell999/Text-Document-Enhancer

cd Text-Document-Enhancer

2: (Optional) Use a virtual environment like venv. If you choose venv, run these terminal commands as well:

python3 -m venv venv

source venv/bin/activate

3: Install the dependencies in the requirements.txt file in the terminal:

pip install -r requirements.txt

4: For good measure because PyTesseract has been giving me lots of trouble with the deployment process, ensure it is installed with this terminal command:

brew install tesseract

5: Run the project in the terminal:

python run.py

# Windows Installation

1: My best bet was running this in Visual Studio Code, so install that first.

2: Install the GitHub Pull Requests extension for Visual Studio Code.

3: Open the command palette (The search bar in the top-center) and enter >Git: Clone. Then provide the repository URL: https://github.com/lljustycell999/Text-Document-Enhancer. You may need to log in to your GitHub account. You can then choose a folder to clone the project files over to.

4: Install the Windows version of Tesseract at https://github.com/UB-Mannheim/tesseract/wiki.

5: Add the path to the Tesseract-OCR directory to your system's PATH environment variable. You can do this by performing the following:

  * 5a: Copy the installation path to Tesseract-OCR.
  
  * 5b: Type in "Edit the system environment variables" in the Windows search bar. It should appear as the first search result, click on it.
  
  * 5c: Open the "Environment Variables" window.
  
  * 5d: Select the "Path" variable under "System Variables" (NOT "User Variables").
  
  * 5e: Click "New" and paste the Tesseract installation path. Press "OK" to save the changes.
  
6: Restart Visual Studio Code for the path changes to occur.

7: Execute the run.py file in Visual Studio Code.

Note: If you have pip working on Windows, you could use Git Bash instead. You would also have to configure Git Bash to work with Python.

# Ubuntu Linux Installation

1: Run the following commands:

sudo apt update

sudo apt git

git clone https://github.com/lljustycell999/Text-Document-Enhancer

cd Text-Document-Enhancer

2: Ensure that Python (and venv if you want a virtual environment) is installed:

sudo apt update

sudo apt install python3 python3-venv python3-pip

3: (Optional) Use a virtual environment like venv. If you choose venv, run these terminal commands as well:

python3 -m venv venv

source venv/bin/activate

pip install --upgrade pip

4: Install the dependencies in the requirements.txt file in the terminal:

pip install -r requirements.txt

5: Run the project in the terminal:

python run.py

![image](https://github.com/lljustycell999/Text-Document-Enhancer/assets/123667513/38dcfdfc-3412-4f8d-a8ef-3725abc7ec44)
<img width="748" alt="image" src="https://github.com/lljustycell999/Text-Document-Enhancer/assets/123667513/aa05fc9a-36f2-4141-967d-1bf3229f0a33">

