import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime
from tkinter import Tk, Button, Label, Listbox, Scrollbar
import time

def load_known_faces(path='known_faces'):
    known_encodings = []
    known_names = []
    for file_name in os.listdir(path):
        image = face_recognition.load_image_file(f"{path}/{file_name}")
        encoding = face_recognition.face_encodings(image)[0]
        known_encodings.append(encoding)
        known_names.append(os.path.splitext(file_name)[0])
    return known_encodings, known_names

def mark_attendance(name, attended_names, listbox):
    attended_names.append(name)
    listbox.insert('end', name)  
    
    with open('attendance.csv', 'a') as f:
        now = datetime.now()
        time_str = now.strftime('%Y-%m-%d %H:%M:%S')
        f.write(f"{name},{time_str}\n")
        print(f"{name} حضر في {time_str}")

def check_attendance(attended_names, listbox):
    if os.path.exists('attendance.csv'):
        with open('attendance.csv', 'r') as file:
            for line in file.readlines():
                name = line.split(',')[0]
                if name not in attended_names:
                    attended_names.append(name)
                    listbox.insert('end', name)  
    else:
        open('attendance.csv', 'w').close()  

def recognize_faces(known_encodings, known_names, attended_names, listbox):
    cap = cv2.VideoCapture(0)
    attendance_marked = False  

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        
        for face_encoding, face_location in zip(face_encodings, face_locations):
            matches = face_recognition.compare_faces(known_encodings, face_encoding)
            if True in matches:
                match_index = matches.index(True)
                name = known_names[match_index]
                
                y1, x2, y2, x1 = face_location
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, name, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
                
                if name not in attended_names and not attendance_marked:
                    mark_attendance(name, attended_names, listbox)
                    attendance_marked = True
                    break
        
        cv2.imshow('Attendance System', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q') or attendance_marked:
            break
    
    cap.release()
    cv2.destroyAllWindows()

def start_app(known_encodings, known_names, attended_names, listbox):
    recognize_faces(known_encodings, known_names, attended_names, listbox)

def main_ui():
    root = Tk()
    root.title("Attendance System")
    root.geometry("400x300")
    
    label = Label(root, text="نظام تسجيل الحضور", font=("Arial", 14))
    label.pack(pady=10)
    
    listbox_label = Label(root, text="الطلاب الحاضرون", font=("Arial", 12))
    listbox_label.pack(pady=5)
    
    listbox = Listbox(root, height=8, width=30, font=("Arial", 12))
    listbox.pack(pady=10)
    
    scrollbar = Scrollbar(root)
    scrollbar.pack(side='right', fill='y')
    listbox.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=listbox.yview)
    
    start_button = Button(root, text="تسجيل الحضور ", command=lambda: start_app(known_encodings, known_names, attended_names, listbox), font=("Arial", 12))
    start_button.pack(pady=10)
    
    
    check_attendance(attended_names, listbox)
    
    root.mainloop()

if __name__ == "__main__":
    known_encodings, known_names = load_known_faces()  
    attended_names = []  
    main_ui()
