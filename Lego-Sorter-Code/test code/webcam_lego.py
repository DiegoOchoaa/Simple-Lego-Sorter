import cv2
import requests
import json
import numpy as np

# Define the video capture object
vid = cv2.VideoCapture(0)

while True:
    # Capture the video frame by frame
    ret, frame = vid.read()

    # Encode frame to bytes for API request
    #frame = frame[0:280, 600:600]
    ksize = (20, 20) 
  
    # Using cv2.blur() method  
    frame = cv2.blur(frame, ksize) 

    # Display the resulting frame
    cv2.imshow('frame', frame)

    
    _, img_encoded = cv2.imencode('.jpg', frame)
    img_bytes = img_encoded.tobytes()

    # Send POST request to LEGO recognition API
    res = requests.post(
        'https://api.brickognize.com/predict/',
        headers={'accept': 'application/json'},
        files={'query_image': ('frame.jpg', img_bytes, 'image/jpeg')}
    )

    # Check if the request was successful (status code 200)
    if res.status_code == 200:
        # Parse the JSON response
        response_json = res.json()

        # Extract and display LEGO part recognition results
        item = response_json['items'][0]
        print("LEGO Part ID:", item['id'])
        print("LEGO Part Name:", item['name'])
        print("LEGO Part Image URL:", item['img_url'])
        guess_url = item['img_url']
        guess_response = requests.get(guess_url, stream=True)
        guess_response.raise_for_status()
        guess_img_array = bytearray(guess_response.content)
        guess_img = cv2.imdecode(np.asarray(guess_img_array, dtype=np.uint8), cv2.IMREAD_UNCHANGED)

        #print("LEGO Part BrickLink URL:", item['external_sites'][0]['url'])  # Assuming there's only one external site (BrickLink)
        print("LEGO Part Category:", item['category'])
        print("LEGO Part Type:", item['type'])
        print("Confidence Score:", str(round(100*item['score'])) + '%')
        print("-------------")
    
    else:
        print("Request failed with status code:", res.status_code)

    # Display the annotated frame
    cv2.imshow('LEGO Recognition', frame)
    # Display the annotated frame
    cv2.namedWindow('guess', cv2.WINDOW_NORMAL)
    cv2.imshow('guess', guess_img)
    cv2.moveWindow('guess', 200, 0)  # Move window to (400, 100)

    # Press 'q' to exit the loop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture object and close all OpenCV windows
vid.release()
cv2.destroyAllWindows()
