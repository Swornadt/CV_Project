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

#OUTDATED 
#To run the program, make sure you are at root directory and type:
python main.py

#To exit the video feed, you must press "q" key on the keyboard, 
or force close programmatically using Ctrl+C while on the console.

#UPDATE - 22 Dec 2025
The video_view script is the core script for facilitating data flow through
the USB cable. Ensure that the ESP32-S has the "CameraSerial.ino" code
uploaded into it.
1. Use the RST button after upload; it generally refreshes the data stream
2. Ensure the right COM is selected, and update the code for both files if needed.
3. Use the "debug.py" to see crash logs from the ESP32

#SOME THINGS TO NOTE
1. Do NOT open Serial Monitor in Arduino IDE when trying to run python script.
When you run either the monitor or python script, it actually OCCUPIES the shared PORT,
which means one of them will not work.

2. config.frame_size is the setting responsible for the size of the frame/window.

3. config.jpeg_quality is responsible for the quality of the video streamed.

4. Voltage irregulaarity directly affects the stability of video flow.

5. The hardware/cable LIMITS the flow of data serially; 

6. The best outcome is sought through careful calibration of various parameters 
(BAUD, frame_size, jpeg_quality, loop delay, etc.)

7. Adding onto point 6, the setting of aforementioned parameters control
the flow of data; think of the USB as a funnel - too much data too quick will
make it leak (data loss), and too less too slowly will make quality bad (or corrupt
some jpeg images due to shortened bandwidth, and hence headers ending quicker
than expected by the processor - python)

8. Somehow, disabling the rtscts and dsrdtr are some paramters that enabled the camera to function
and actually pass readible data; I spent very long trying to figure out how to make
the python script catch the headers (0xAA and 0xBB), which failed in previous approaches. It's something to do with
Passive sensing, but I haven't figured it out yet.


# THINGS TO NOTE FOR PRESENTATION

Camera specifications:
Ensure that PSRAM is enabled. Or else there will be malloc
problems.
If memory problems persist, try decreasing the memory load
by adjusting quality and size of image streamed.

Hotspot Connectivity:
The follow connections must be established:- 
1. Redmi Hotspot ON
2. Desktop Hotspot ON
3. Desktop WiFi connected to Redmi Hotspot
4. ESP-32 connected to Desktop WiFi.
NOTE: The IP address assigned by the Desktop may change.
In such cases, you must change the hardcoded IP in the "esp_lazer.py"
file by checking in the "Mobile Hotspot" settings of Desktop and putting
that IP in the python script.