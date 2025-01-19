Face Recognition Attendance System
This project is a Face Recognition Attendance System that automates attendance marking using facial recognition technology. It utilizes a webcam or CCTV camera to detect and recognize faces of students and marks their attendance based on a predefined timetable.

Table of Contents
Features
Prerequisites
Installation
1. Clone the Repository
2. Create a Virtual Environment (Optional but Recommended)
3. Install Required Packages
For Windows Users
For macOS Users
4. Set Up Known Faces
5. Configure the Timetable
Project Structure
Usage
Running the Attendance System
Exiting the Program
Viewing Attendance Records
Configuration
Changing Camera Source
Adjusting Recognition Sensitivity
Troubleshooting
Common Issues and Solutions
License


Features
Automated Attendance: Automatically marks attendance by recognizing faces captured through a camera.
Timetable Integration: Marks attendance according to a customizable timetable.
Real-Time Recognition: Processes live video feed for face detection and recognition.
CSV Attendance Logs: Stores attendance records in a CSV file for easy access and analysis.
Scalable: Can be extended to use CCTV cameras for broader coverage.


Prerequisites
Before you begin, ensure you have met the following requirements:

Operating System: Windows 10 or later / macOS / Linux
Python Version: Python 3.7 or higher (Python 3.11 recommended)
pip: Python package manager should be installed and updated.


Installation
Follow these steps to set up and run the project on your local machine.

1. Clone the Repository
BASH

git clone https://github.com/yourusername/FaceRecognitionAttendance.git
cd FaceRecognitionAttendance
2. Create a Virtual Environment (Optional but Recommended)
Create a virtual environment to manage project dependencies.

BASH

python -m venv venv
Activate the virtual environment:

Windows:

BASH

venv\Scripts\activate
macOS/Linux:

BASH

source venv/bin/activate
3. Install Required Packages
Install the necessary Python libraries using pip:

BASH

pip install -r requirements.txt
If requirements.txt is not present, you can install the packages individually:

BASH

pip install opencv-python face_recognition numpy pandas schedule
Note: Installing face_recognition will also require cmake and dlib. Installation might vary based on your operating system.

For Windows Users
Install CMake:

Download CMake from cmake.org.
Choose the Windows installer and add CMake to your system PATH during installation.
Install Visual C++ Build Tools:

Download and install from Microsoft C++ Build Tools.
Select "Desktop development with C++" workload during installation.
Install dlib:

If you encounter issues installing dlib via pip, download a precompiled wheel from Unofficial Windows Binaries and install it:

BASH

pip install path\to\dlib_whl_file.whl
For macOS Users
Ensure you have Xcode Command Line Tools installed:

BASH

xcode-select --install
Install Homebrew if you haven't already:

BASH

/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
Install cmake using Homebrew:

BASH

brew install cmake
4. Set Up Known Faces
Organize images of students in the KnownFaces directory.


Structure:


KnownFaces/
├── Student Name 1/
│   ├── image1.jpg
│   ├── image2.jpg
├── Student Name 2/
│   ├── image1.jpg
│   ├── image2.jpg

Guidelines:

Use clear images with the student's face prominently visible.
Include multiple images per student for better accuracy.
Images should be in .jpg or .png format.
5. Configure the Timetable
Edit the TimeTable.csv file to reflect your class schedule.

Format:

CSV

Period,Start_Time,End_Time
1,09:00:00,10:00:00
2,10:00:00,11:00:00
3,11:00:00,12:00:00
4,12:30:00,13:30:00
5,13:30:00,14:30:00
6,14:30:00,15:30:00
Instructions:

Times should be in HH:MM:SS format (24-hour clock).
Adjust periods and times according to your schedule.
Project Structure

FaceRecognitionAttendance/
├── KnownFaces/
│   ├── Student Name 1/
│   │   ├── image1.jpg
│   │   ├── image2.jpg
│   ├── Student Name 2/
│       ├── image1.jpg
│       ├── image2.jpg
├── attendance_system.py
├── TimeTable.csv
├── requirements.txt
├── README.md

KnownFaces/: Directory containing subfolders of student images.
attendance_system.py: Main script for the attendance system.
TimeTable.csv: CSV file defining the class schedule.
requirements.txt: List of required Python packages.
README.md: Documentation and instructions (this file).

Usage
Running the Attendance System
Ensure your virtual environment is activated and execute the script:

BASH

python attendance_system.py
The system will start and run continuously.
Attendance will be marked automatically based on the timetable.
Exiting the Program
To stop the program, press Ctrl+C in the terminal.
The program will save the attendance records and release resources.
Viewing Attendance Records
Attendance is saved in Attendance.csv.
Open the file with a spreadsheet application or text editor to view records.
Configuration
Changing Camera Source
Default: The system uses the default webcam (VideoCapture(0)).

To Use a Different Camera:

Modify the line in attendance_system.py:

Python

video_capture = cv2.VideoCapture(camera_index_or_url)
Replace camera_index_or_url with the appropriate index or stream URL.

Adjusting Recognition Sensitivity
Tolerance:

Default tolerance is set within the compare_faces method.
Lowering the tolerance value increases strictness.
Example:

Python

matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.5)

Troubleshooting
Common Issues and Solutions
1. ModuleNotFoundError for Packages
Solution: Ensure all packages are installed in your virtual environment.

BASH

pip install -r requirements.txt
2. Camera Not Detected
Solution: Check that your camera is properly connected and not being used by another application.
3. Faces Not Recognized
Solution:

Ensure the known faces are correctly loaded.
Improve image quality in the KnownFaces directory.
Ensure consistent lighting and position during recognition.
4. Errors Installing dlib or face_recognition
Solution:

Install the required build tools and dependencies.
Use precompiled binaries if necessary.
License
This project is licensed under the MIT License.

Disclaimer: This system involves the use of facial recognition technology, which may have privacy and legal implications. Ensure that you have the consent of individuals whose images you are using and that you comply with all relevant laws and regulations.

Contributions: Contributions are welcome. Please open issues and submit pull requests for improvements
