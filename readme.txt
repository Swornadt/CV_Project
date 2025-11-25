Setup Code:

Follow the steps SEQUENTIALLY. This is meant for Windows.

#Firstly, you start at the root directory.

#Create a virtual environment which stores dependencies and frameworks
python -m venv venv

#Activate the virtual environment. After this step, you will see a "(venv)" in the command console.
#Don't exit the venv during production. Everything runs fine, but if you need to exit this, type "deactivate".
.\venv\Scripts\activate

#May have to install a new version of Python to be compatible with OpenCV
python -m pip install --upgrade pip

#Install opencv and caer
pip install opencv-contrib-python
pip install caer

#The project directory should be:
/root
/root/venv
/root/main.py

#To run the program, make sure you are at root directory and type:
python main.py

#To exit the video feed, you must press "q" key on the keyboard, 
or force close programmatically using Ctrl+C while on the console.