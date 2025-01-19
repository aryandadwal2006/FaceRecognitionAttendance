import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime, time as time_module
import pandas as pd
import threading

# Path to the Known Faces directory
path = 'KnownFaces'

# Lists to hold encodings and names
known_face_encodings = []
known_face_names = []

# Load known faces and their encodings
student_folders = os.listdir(path)
for student_name in student_folders:
    student_folder_path = os.path.join(path, student_name)
    if os.path.isdir(student_folder_path):
        images = os.listdir(student_folder_path)
        for image_name in images:
            image_path = os.path.join(student_folder_path, image_name)
            image = face_recognition.load_image_file(image_path)
            face_locations = face_recognition.face_locations(image)
            if face_locations:
                encodings = face_recognition.face_encodings(image, face_locations)[0]
                known_face_encodings.append(encodings)
                known_face_names.append(student_name)
            else:
                print(f"No faces found in {image_name}")

# Load the timetable
timetable = pd.read_csv('TimeTable.csv')

# Initialize an empty DataFrame for attendance
attendance = pd.DataFrame(columns=['Name', 'Date', 'Time', 'Period'])

# Function to check if the current time is within a class period
def is_class_time():
    now = datetime.now().time()
    for index, row in timetable.iterrows():
        start_time = datetime.strptime(row['Start_Time'], "%H:%M:%S").time()
        end_time = datetime.strptime(row['End_Time'], "%H:%M:%S").time()
        if start_time <= now <= end_time:
            return True, row['Period']
    return False, None

# Initialize webcam
video_capture = cv2.VideoCapture(0)

# Function to mark attendance
def mark_attendance(period):
    print(f"Marking attendance for Period {period}")
    end_time = datetime.strptime(timetable.loc[timetable['Period'] == period]['End_Time'].values[0], "%H:%M:%S").time()

    while datetime.now().time() <= end_time:
        # Capture a single frame from the webcam
        ret, frame = video_capture.read()
        if not ret:
            print("Failed to capture frame from camera.")
            break

        # Resize frame for faster processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # Convert BGR to RGB
        rgb_small_frame = small_frame[:, :, ::-1]

        # Find face locations
        face_locations = face_recognition.face_locations(rgb_small_frame)

        # Get face encodings
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        # Loop through each face in the frame
        for face_encoding, face_location in zip(face_encodings, face_locations):
            # Compare face encodings with known faces
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"

            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]

                # Mark attendance
                now = datetime.now()
                date_string = now.strftime("%Y-%m-%d")
                time_string = now.strftime("%H:%M:%S")

                # Check if the student is already marked present for the current period
                if not ((attendance['Name'] == name) & (attendance['Date'] == date_string) & (attendance['Period'] == period)).any():
                    new_entry = {'Name': name, 'Date': date_string, 'Time': time_string, 'Period': period}
                    attendance = attendance.append(new_entry, ignore_index=True)
                    print(f'Attendance marked for {name} at {time_string} during Period {period}')

        # Wait for a short period before capturing the next frame
        cv2.waitKey(1)

# Function to schedule attendance marking
def schedule_attendance():
    while True:
        class_in_session, current_period = is_class_time()
        if class_in_session:
            mark_attendance(current_period)
            # Sleep until the next minute to avoid redundant checks
            time_module.sleep(60)
        else:
            # Sleep for a minute before checking again
            time_module.sleep(60)

# Start the scheduling in a separate thread
attendance_thread = threading.Thread(target=schedule_attendance)
attendance_thread.start()

try:
    while True:
        # Keep the main thread running
        time_module.sleep(1)
except KeyboardInterrupt:
    print("Exiting program and saving attendance...")
    # Save the attendance DataFrame to a CSV file
    attendance_file = 'Attendance.csv'
    if os.path.exists(attendance_file):
        attendance.to_csv(attendance_file, mode='a', header=False, index=False)
    else:
        attendance.to_csv(attendance_file, index=False)
    print("Attendance saved to Attendance.csv")
    # Release webcam and close any OpenCV windows
    video_capture.release()
    cv2.destroyAllWindows()
    # Stop the attendance thread
    attendance_thread.join()