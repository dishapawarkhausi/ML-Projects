import cv2
import dlib
import numpy as np
import os
import pickle

detector = dlib.get_frontal_face_detector()
shape_predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
face_rec_model = dlib.face_recognition_model_v1("dlib_face_recognition_resnet_model_v1.dat")

encodings_dir = 'trained_encodings_dlib'
os.makedirs(encodings_dir, exist_ok=True)

def process_images_from_folder_or_file(path, name):
    encodings = []
    resolved_path = os.path.abspath(path)
    print(f"Resolved path: {resolved_path}")

    if os.path.isfile(resolved_path):

        image = cv2.imread(resolved_path)
        if image is None:
            print(f"Could not read image: {resolved_path}")
            return
        process_single_image(image, resolved_path, encodings)
    elif os.path.isdir(resolved_path):
        
        images = [os.path.join(resolved_path, img) for img in os.listdir(resolved_path) if img.lower().endswith(('jpg', 'jpeg', 'png'))]
        if not images:
            print(f"No valid images found in folder: {resolved_path}")
            return

        print(f"Processing {len(images)} images from folder: {resolved_path}")
        for image_path in images:
            image = cv2.imread(image_path)
            if image is None:
                print(f"Could not read image: {image_path}")
                continue
            process_single_image(image, image_path, encodings)
    else:
        print(f"Invalid path: {resolved_path}")
        return

    if encodings:
        avg_encoding = np.mean(encodings, axis=0)
        save_encoding(avg_encoding, name)

def process_single_image(image, image_path, encodings):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)

    if not faces:
        print(f"No faces detected in image: {image_path}")
        return

    for face in faces:
        shape = shape_predictor(gray, face)
        encoding = np.array(face_rec_model.compute_face_descriptor(image, shape, 1))
        encodings.append(encoding)
        print(f"Captured encoding from image: {os.path.basename(image_path)}")

def capture_images_from_webcam(name):
    video_capture = cv2.VideoCapture(0)
    encodings = []

    print(f"Starting training for {name} using webcam. Please look at the camera.")

    while len(encodings) < 10:
        ret, frame = video_capture.read()
        if not ret:
            print("Error accessing the camera.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector(gray)

        for face in faces:
            shape = shape_predictor(gray, face)
            encoding = np.array(face_rec_model.compute_face_descriptor(frame, shape, 1))
            encodings.append(encoding)
            print(f"Captured encoding {len(encodings)}/10 for {name}.")

        cv2.putText(frame, f"Captured {len(encodings)}/10", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.imshow("Training - Press 'q' to exit", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Training interrupted by user.")
            break

    video_capture.release()
    cv2.destroyAllWindows()

    if encodings:
        avg_encoding = np.mean(encodings, axis=0)
        save_encoding(avg_encoding, name)

def save_encoding(encoding, name):
    filepath = f"{encodings_dir}/{name}.pkl"
    if os.path.exists(filepath):
        print(f"Overwriting existing encoding for {name}.")
    with open(filepath, "wb") as f:
        pickle.dump(encoding, f)
    print(f"Training for {name} completed and saved at {filepath}.")

def main():
    while True:
        name = input("Enter the name of the person to train (or type 'exit' to quit): ")
        if name.lower() == 'exit':
            print("Exiting training.")
            break

        choice = input("Choose input method: (1) Webcam (2) File : ")

        if choice == '1':
            capture_images_from_webcam(name)
        elif choice == '2':
            path = input("Enter the file or folder path: ")
            process_images_from_folder_or_file(path, name)
        else:
            print("Invalid choice. Please select 1 or 2.")

if __name__ == "__main__":
    main()
