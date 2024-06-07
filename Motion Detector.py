import imutils
import cv2
import requests
import numpy as np
from twilio.rest import Client
import pygame


# Initialize Pygame for sound
pygame.init()

# Load the buzzer sound
pygame.mixer.music.load("C:\\Users\\sirin\\Downloads\\Motion\\buzzer.mp3")


# Twilio credentials5r
account_sid = "ACc4db4ed5c644ec139a77dee16a002e2f"
auth_token = "4166acae80803e9be7c7a422040d80fd"
twilio_phone_number = "whatsapp:+14155238886"
your_phone_number = "whatsapp:+917760235161"

# API Key from imgbb.com
imgbb_api_key = "fe2bca17aaca09893a2db3bc1b910d7e"

# Twilio client setup
client = Client(account_sid, auth_token)

# Minimum length of time where no motion is detected it should take
#(in program cycles) for the program to declare that there is no movement
MOVEMENT_DETECTED_PERSISTENCE = 100

# Create capture object
cap = cv2.VideoCapture(5)  # Flush the stream
cap.release()
cap = cv2.VideoCapture(0)  # Then start the webcam

# Init frame variables
first_frame = None
next_frame = None

# Init display font and timeout counters
font = cv2.FONT_HERSHEY_SIMPLEX
delay_counter = 0
movement_persistent_counter = 0

# Flag to track whether the first frame has been sent
first_frame_sent = False

# LOOP
while True:

    # Read frame
    ret, frame = cap.read()
    text = "Unoccupied"

    # If there's an error in capturing
    if not ret:
        print("CAPTURE ERROR")
        continue

    # Resize and save a grayscale version of the image
    frame = imutils.resize(frame, width=750)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Blur it to remove camera noise (reducing false positives)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    # If the first frame is nothing, initialize it
    if first_frame is None:
        first_frame = gray

        # Capture the first frame to send
        first_frame_filename = "first_frame.jpg"
        cv2.imwrite(first_frame_filename, frame)

        # Upload the first frame to imgbb.com
        with open(first_frame_filename, "rb") as file:
            response = requests.post(
                "https://api.imgbb.com/1/upload",
                files={"image": file},
                data={"key": imgbb_api_key}
            )
            result = response.json()
            img_url = result["data"]["url"]

        # Send the first frame via Twilio WhatsApp API
        message = client.messages.create(
            body="Motion Detected!! Counter:100",
            from_=twilio_phone_number,
            to=your_phone_number,
            media_url=[img_url]
        )

        # Set the flag to indicate that the first frame has been sent
        first_frame_sent = True

    delay_counter += 1

    # Set the first frame to compare as the previous frame
    # after a certain number of frames
    if delay_counter > 10:
        delay_counter = 0
        first_frame = next_frame

    # Set the next frame to compare (the current frame)
    next_frame = gray

    # Compare the two frames, find the difference
    frame_delta = cv2.absdiff(first_frame, next_frame)
    thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]

    # Fill in holes via dilate(), and find contours of the thresholds
    thresh = cv2.dilate(thresh, None, iterations=2)
    cnts, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    transient_movement_flag = False  # Initialize flag to indicate transient movement

    # loop over the contours
    for c in cnts:
        # Save the coordinates of all found contours
        (x, y, w, h) = cv2.boundingRect(c)

        # If the contour is too small, ignore it
        if cv2.contourArea(c) > 2000:
            transient_movement_flag = True

            # Draw a rectangle around big enough movements
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    if transient_movement_flag:
        movement_persistent_flag = True
        movement_persistent_counter = MOVEMENT_DETECTED_PERSISTENCE

        # Play the buzzer sound
        pygame.mixer.music.play()

    # As long as there was recent transient movement, say a movement
    # was detected
    if movement_persistent_counter > 0:
        text = "Movement Detected " + str(movement_persistent_counter)

        movement_persistent_counter -= 1
    else:
        text = "No Movement Detected"

    # Print the text on the screen and display the raw and processed video feeds
    cv2.putText(frame, str(text), (10, 35), font, 0.75, (255, 255, 255), 2, cv2.LINE_AA)

    # Convert the frame_delta to color for splicing
    frame_delta = cv2.cvtColor(frame_delta, cv2.COLOR_GRAY2BGR)

    # Splice the two video frames together to make one long horizontal one
    cv2.imshow("frame", np.hstack((frame_delta, frame)))

    # Interrupt trigger by pressing q to quit the open CV program
    ch = cv2.waitKey(1)
    if ch & 0xFF == ord('q'):
        break

# Release the capture object and close the OpenCV window
cap.release()
cv2.destroyAllWindows()
