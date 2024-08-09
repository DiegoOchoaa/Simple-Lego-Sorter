import cv2
from picamera2 import Picamera2, Preview
import numpy as np
import os
import requests
import json
import time
import serial


import time

serial1 = serial.Serial('/dev/ttyACM0', 9600)

# Initialize Picamera2
picam2 = Picamera2()
config = picam2.create_preview_configuration()
picam2.configure(config)
picam2.start()
fgbg = cv2.createBackgroundSubtractorMOG2()
vizualise_guess = False
old_piece = None
guess_img = None

first_frame = None
timeout = 0

def mse(image1, image2):
    err = np.sum((image1.astype("float") - image2.astype("float")) ** 2)
    err /= float(image1.shape[0] * image1.shape[1])
    return err
def overlay_image(base_image, overlay_image, position=(0, 0), scale=1.0):
    # Resize the overlay image if a scale factor is provided
    if scale != 1.0:
        overlay_image = cv2.resize(overlay_image, (0, 0), fx=scale, fy=scale)

    # Get the dimensions of the overlay image
    overlay_height, overlay_width = overlay_image.shape[:2]

    # Get the region of interest (ROI) in the base image where the overlay will be placed
    x, y = position
    roi = base_image[y:y+overlay_height, x:x+overlay_width]

    # Create a mask of the overlay and create its inverse mask also
    gray_overlay = cv2.cvtColor(overlay_image, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray_overlay, 1, 255, cv2.THRESH_BINARY)
    mask_inv = cv2.bitwise_not(mask)

    # Black-out the area of overlay in ROI
    base_image_bg = cv2.bitwise_and(roi, roi, mask=mask_inv)

    # Take only region of overlay from overlay image.
    overlay_fg = cv2.bitwise_and(overlay_image, overlay_image, mask=mask)

    # Put overlay in ROI and modify the base image
    dst = cv2.add(base_image_bg, overlay_fg)
    base_image[y:y+overlay_height, x:x+overlay_width] = dst

    return base_image

while True:
        frame = picam2.capture_array()  # Capture frame as a numpy array
        
        
        
        height, width = frame.shape[:2]
        roi_x = int(0.1 * width)
        roi_y = int(0 * height)
        roi_w = int(0.7 * width)
        roi_h = int(1 * height)
        roi = frame[roi_y:roi_y+roi_h, roi_x:roi_x+roi_w]
        
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        frame = frame_bgr
        
        if first_frame is None:
            first_frame = roi
        
        
        empty = (mse(roi, first_frame))
        print(empty)
        
        if empty < 90:
            timeout  = 10
        elif empty > 90:
          timeout   -= 1
        
        print(timeout)
        if empty > 90 and timeout < 0:
            res = requests.post(
                            'https://api.brickognize.com/predict/',
                            headers={'accept': 'application/json'},
                            files={'query_image': ('frame.jpg', cv2.imencode('.jpg', roi)[1].tostring(), 'image/jpeg')},
                        )

                    
            if res.status_code == 200:
                # Parse the JSON response
                response_json = res.json()
                item = response_json['items'][0]

                # Display results
                    
                #print("LEGO Part ID:", item['id'])
                dicti = {"Technic":0,"Brick":2, "Minifigure":6, "Plate":1, "Tile":4, "Slope":5}
                message = None
                for piece_type in dicti:
                    
                    if piece_type in item['category']:
                        message = dicti[piece_type]
                if message == None:
                    message = 3
                    
                
               
                message = f'{message}'
                serial1.write(message.encode('utf-8'))
                print(item['category'], str(round(100 * item['score'])) + '%')
                print('mess = ',message)
                
                #print("LEGO Part Name:", item['name'])
                current_piece =  item['name']
                if 'Baseplate' in item['name'] :
                    first_frame = roi
                    print('baseplate reset')
                        

                #print("LEGO Part Image URL:", item['img_url'])
                #print("LEGO Part Category:", item['category'])
                #print("LEGO Part Type:", item['type'])
                #print("Confidence Score:", str(round(100 * item['score'])) + '%')
                print("-------------")
                        
                      

                # Display guess image
                if vizualise_guess == True:
                    if old_piece != current_piece:
                        guess_url = item['img_url']
                        guess_response = requests.get(guess_url, stream=True)
                        guess_response.raise_for_status()
                        guess_img_array = bytearray(guess_response.content)
                        guess_img = cv2.imdecode(np.asarray(guess_img_array, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
                    #cv2.imshow('guess', guess_img)
                   
                    
                old_piece = current_piece
                          
                

        cv2.rectangle(frame, (roi_x, roi_y), (roi_x + roi_w, roi_y + roi_h), (200, 20, 0), 2)
        if guess_img is not None:
            frame = overlay_image(frame, guess_img, (80,20), 0.6)
        cv2.imshow('Frame_final', frame)
        
        

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Release the camera and close the OpenCV window
picam2.stop()