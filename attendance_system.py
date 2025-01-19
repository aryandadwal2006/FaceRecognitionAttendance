import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime
import pandas as pd
import threading
import time

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

# Create a class to handle attendance
class AttendanceSystem:
    def __init__(self):
        self.attendance = pd.DataFrame(columns=['Name', 'Date', 'Time', 'Period'])
        self.lock = threading.Lock()
        self.video_capture = cv2.VideoCapture(0)
        self.running = True

    def is_class_time(self):
        now_time = datetime.now().time()
        for index, row in timetable.iterrows():
            start_time = datetime.strptime(row['Start_Time'], "%H:%M:%S").time()
            end_time = datetime.strptime(row['End_Time'], "%H:%M:%S").time()
            if start_time <= now_time <= end_time:
                return True, row['Period']
        return False, None

    def mark_attendance(self, period):
        print(f"Starting attendance marking for Period {period}")
        end_time_str = timetable.loc[timetable['Period'] == period]['End_Time'].values[0]
        end_time = datetime.strptime(end_time_str, "%H:%M:%S").time()

        while datetime.now().time() <= end_time and self.running:
            ret, frame = self.video_capture.read()
            if not ret:
                print("Failed to capture frame from camera.")
                break

            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            for face_encoding, face_location in zip(face_encodings, face_locations):
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = "Unknown"

                if len(known_face_encodings) > 0:
                    face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        name = known_face_names[best_match_index]
                        now = datetime.now()
                        date_string = now.strftime("%Y-%m-%d")
                        time_string = now.strftime("%H:%M:%S")

                        with self.lock:
                            if not ((self.attendance['Name'] == name) & 
                                  (self.attendance['Date'] == date_string) & 
                                  (self.attendance['Period'] == period)).any():
                                new_entry = pd.DataFrame([{
                                    'Name': name,
                                    'Date': date_string,
                                    'Time': time_string,
                                    'Period': period
                                }])
                                self.attendance = pd.concat([self.attendance, new_entry], ignore_index=True)
                                print(f'Attendance marked for {name} at {time_string} during Period {period}')

            time.sleep(1)

        print(f"Finished attendance marking for Period {period}")

    def schedule_attendance(self):
        while self.running:
            try:
                class_in_session, current_period = self.is_class_time()
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Checking class time: "
                      f"class_in_session={class_in_session}, current_period={current_period}")
                
                if class_in_session:
                    self.mark_attendance(current_period)
                    time.sleep(60)
                else:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] No class in session. Sleeping for 60 seconds.")
                    time.sleep(60)
            except Exception as e:
                print(f"Exception in schedule_attendance: {e}")
                break

    def save_attendance(self):
        attendance_file = 'Attendance.csv'
        with self.lock:
            if os.path.exists(attendance_file):
                self.attendance.to_csv(attendance_file, mode='a', header=False, index=False)
            else:
                self.attendance.to_csv(attendance_file, index=False)

    def cleanup(self):
        self.running = False
        self.video_capture.release()
        cv2.destroyAllWindows()

# Create instance of AttendanceSystem
attendance_system = AttendanceSystem()

# Start the scheduling in a separate thread
attendance_thread = threading.Thread(target=attendance_system.schedule_attendance)
attendance_thread.start()

try:
    while True:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Main thread running...")
        time.sleep(60)
except KeyboardInterrupt:
    print("Exiting program and saving attendance...")
    attendance_system.cleanup()
    attendance_system.save_attendance()
    attendance_thread.join()
    print("Program exited gracefully.")
