import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime
import pandas as pd
import threading
import time
import sys

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

class AttendanceSystem:
    def __init__(self):
        self.attendance = pd.DataFrame(columns=['Name', 'Date', 'Time', 'Period'])
        self.lock = threading.Lock()
        self.video_capture = cv2.VideoCapture(0)
        
        # Check if camera opened successfully
        if not self.video_capture.isOpened():
            print("Error: Could not open camera")
            raise Exception("Camera not accessible")
            
        self.running = True
        self.period_completed = threading.Event()

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

            # Resize frame for faster processing
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            
            # Find face locations and encodings
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            # Draw rectangles and names for each face
            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                # Scale back up face locations since the frame we detected in was scaled
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                # Get name for the face
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

                # Draw a box around the face
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

                # Draw a label with a name below the face
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.6, (255, 255, 255), 1)

            # Display the resulting frame
            cv2.imshow('Attendance System', frame)

            # Break the loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.running = False
                break

            time.sleep(0.1)  # Small delay to prevent high CPU usage

        print(f"Finished attendance marking for Period {period}")
        self.period_completed.set()
        self.running = False

    def schedule_attendance(self):
        start_time = time.time()
        timeout = 3600  # 1 hour timeout

        while self.running:
            try:
                if time.time() - start_time > timeout:
                    print("Timeout reached while waiting for Period 1")
                    self.running = False
                    break

                class_in_session, current_period = self.is_class_time()
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Checking class time: "
                      f"class_in_session={class_in_session}, current_period={current_period}")
                
                if class_in_session and current_period == 1:  # Only run for period 1
                    self.mark_attendance(current_period)
                    break  # Exit after period 1
                else:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Waiting for Period 1. Sleeping for 60 seconds.")
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
        print("Attendance saved to Attendance.csv")

    def cleanup(self):
        self.running = False
        if self.video_capture.isOpened():
            self.video_capture.release()
        cv2.destroyAllWindows()
        self.save_attendance()
        print("Cleanup completed")

def main():
    try:
        attendance_system = AttendanceSystem()
        attendance_thread = threading.Thread(target=attendance_system.schedule_attendance)
        attendance_thread.start()

        while attendance_system.running:
            if attendance_system.period_completed.is_set():
                print("Period 1 completed. Shutting down...")
                break
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if 'attendance_system' in locals():
            attendance_system.cleanup()
            attendance_thread.join()
        print("Program exited gracefully.")
        sys.exit(0)

if __name__ == "__main__":
    main()
