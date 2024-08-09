import os
import requests
import json
import cv2
import numpy as np
import concurrent.futures
import time

def process_image(file_name):
    img_path = os.path.join(images, file_name)
    img = cv2.imread(img_path)
    
    success = False
    retries = 5  # Number of retries for rate limiting
    backoff_factor = 1  # Exponential backoff factor

    while not success and retries > 0:
        with open(img_path, 'rb') as img_file:
            res = requests.post(
                'https://api.brickognize.com/predict/',
                headers={'accept': 'application/json'},
                files={'query_image': (img_path, img_file, 'image/jpeg')},
            )
        
        if res.status_code == 200:
            success = True
            # Parse the JSON response
            response_json = res.json()
            # Extract and print each item in the 'items' list
            item = response_json['items'][0]
            print("LEGO Part ID:", item['id'])
            print("LEGO Part Name:", item['name'])
            print("LEGO Part Image URL:", item['img_url'])
            guess_url = item['img_url']
            guess_response = requests.get(guess_url, stream=True)
            guess_response.raise_for_status()
            guess_img_array = bytearray(guess_response.content)
            guess_img = cv2.imdecode(np.asarray(guess_img_array, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
            print("LEGO Part Category:", item['category'])
            print("LEGO Part Type:", item['type'])
            print("Confidence Score:", str(round(100*item['score'])) + '%')
            print("-------------")

            # Display the images
            cv2.namedWindow('gues', cv2.WINDOW_NORMAL)
            cv2.imshow('gues', guess_img)
            cv2.moveWindow('gues', 300, 0)  # Move window to (300, 0)
            cv2.namedWindow('image', cv2.WINDOW_NORMAL)
            cv2.imshow('image', img)
            cv2.moveWindow('image', 600, 0)  # Move window to (600, 0)
            cv2.waitKey(1)
            cv2.destroyAllWindows()
        elif res.status_code == 429:
            retries -= 1
            wait_time = backoff_factor * (2 ** (5 - retries))
            print(f"Rate limit exceeded. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
        else:
            print("Request failed with status code:", res.status_code)
            break

# Main code
images = '/Users/diegoochoa/Documents/python/LEGO sorter/API brickgnz/images'
files = [name for name in os.listdir(images) if os.path.isfile(os.path.join(images, name))]

# Use ThreadPoolExecutor to process images concurrently
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    executor.map(process_image, files)
