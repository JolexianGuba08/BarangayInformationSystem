import cv2

def capture_face():
    # Create a VideoCapture object to read from the webcam
    cap = cv2.VideoCapture(0)

    # Check if the webcam is opened successfully
    if not cap.isOpened():
        print("Unable to access the webcam.")
        return

    # Read the first frame from the webcam
    ret, frame = cap.read()

    # Display the captured frame until the user presses a key
    cv2.imshow("Capture Face", frame)
    cv2.waitKey(0)

    # Save the captured frame as an image file
    image_file = "captured_face.jpg"
    cv2.imwrite(image_file, frame)

    # Release the VideoCapture object and close the display window
    cap.release()
    cv2.destroyAllWindows()

    return image_file

# Call the capture_face function to capture the user's face and get the image file path
image_path = capture_face()

# Print the image file path
print("Captured face image stored at:", image_path)
