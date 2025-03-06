import face_recognition
import cv2
import time
import datetime
import os
import glob

# Initialize variables for FPS calculation
prev_frame_time = 0
new_frame_time = 0

# Initialize video capture
video_capture = cv2.VideoCapture(0)

# Configure paths and parameters
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PHOTOS_DIR = os.path.join(SCRIPT_DIR, 'photos')
RESIZE_FRAME = 2
FONT = cv2.FONT_HERSHEY_COMPLEX

# Colors
COLOR_KNOWN = (0, 255, 0)     # BGR - green
COLOR_UNKNOWN = (0, 0, 255)   # BGR - red
COLOR_INFO = (255, 0, 0)      # BGR - blue

def load_known_faces():
    known_face_encodings = []
    known_face_names = []

    # Check if photos directory exists
    if not os.path.isdir(PHOTOS_DIR):
        raise FileNotFoundError(f"Photos directory '{PHOTOS_DIR}' not found")

    # Find all JPEG files in photos directory
    image_paths = glob.glob(os.path.join(PHOTOS_DIR, '*.jpg')) + glob.glob(os.path.join(PHOTOS_DIR, '*.jpeg'))

    if not image_paths:
        raise ValueError(f"No JPEG images found in {PHOTOS_DIR}")

    # Load each image and create encodings
    for image_path in image_paths:
        # Extract base name without extension
        name = os.path.splitext(os.path.basename(image_path))[0]
        
        # Load image
        image = face_recognition.load_image_file(image_path)
        
        # Get face encodings
        encodings = face_recognition.face_encodings(image)
        
        if not encodings:
            print(f"⚠️ No face found in {image_path}")
            continue
            
        # Add first found face encoding
        known_face_encodings.append(encodings[0])
        known_face_names.append(name)
        print(f"✅ Loaded {name} from {os.path.basename(image_path)}")

    return known_face_encodings, known_face_names

try:
    known_face_encodings, known_face_names = load_known_faces()
except Exception as e:
    print(f"❌ Error: {e}")
    exit()

def capture_and_process():
    global prev_frame_time

    process_this_frame = True

    while video_capture.isOpened():
        ret, frame = video_capture.read()
        if not ret:
            break

        # Mirror and resize frame
        frame = cv2.flip(frame, 1)
        frame = cv2.resize(frame, (1020, 720))

        # Process every other frame to save resources
        if process_this_frame:
            # Resize and convert to RGB
            small_frame = cv2.resize(frame, (0, 0), fx=1/RESIZE_FRAME, fy=1/RESIZE_FRAME)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

            # Find faces and their encodings
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            # Recognize faces
            face_names = []
            for face_encoding in face_encodings:
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = "Неизвестный"
                
                # Use the first match
                if True in matches:
                    first_match_index = matches.index(True)
                    name = known_face_names[first_match_index]
                
                face_names.append(name)

        process_this_frame = not process_this_frame

        # Display results
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Scale coordinates back to original size
            top *= RESIZE_FRAME
            right *= RESIZE_FRAME
            bottom *= RESIZE_FRAME
            left *= RESIZE_FRAME

            # Choose colors based on recognition status
            color = COLOR_KNOWN if name != "Неизвестный" else COLOR_UNKNOWN
            text_color = (255, 255, 255)  # White text

            # Draw rectangle around face
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)

            # Draw label background
            cv2.rectangle(frame, 
                        (left, bottom - 50), 
                        (right, bottom), 
                        color, cv2.FILLED)

            # Draw name label
            cv2.putText(frame, 
                       name, 
                       (left + 6, bottom - 16), 
                       FONT, 
                       1.0, 
                       text_color, 
                       2)

        # Calculate and display FPS
        new_frame_time = time.time()
        fps = 1 / (new_frame_time - prev_frame_time)
        prev_frame_time = new_frame_time
        cv2.putText(frame, 
                   f"FPS: {int(fps)}", 
                   (40, 50), 
                   FONT, 
                   1, 
                   COLOR_INFO, 
                   2)

        # Display current time
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        cv2.putText(frame, 
                   current_time, 
                   (40, 100), 
                   FONT, 
                   1, 
                   COLOR_INFO, 
                   2)

        # Show frame
        cv2.imshow("Video", frame)

        # Exit on ESC or window close
        if cv2.waitKey(1) & 0xFF == 27:
            break
        if cv2.getWindowProperty("Video", cv2.WND_PROP_VISIBLE) < 1:
            break

    # Cleanup
    video_capture.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    capture_and_process()