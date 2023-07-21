from flask import Flask, render_template, request, Response, make_response, jsonify
import json
import cv2
import os
import numpy as np
import midas_processing as mp
import base64
from PIL import Image
import io

def get_base_url(port:int) -> str:
    '''
    Returns the base URL to the webserver if available.
    
    i.e. if the webserver is running on coding.ai-camp.org port 12345, then the base url is '/<your project id>/port/12345/'
    
    Inputs: port (int) - the port number of the webserver
    Outputs: base_url (str) - the base url to the webserver
    '''
    
    try:
        info = json.load(open(os.path.join(os.environ['HOME'], '.smc', 'info.json'), 'r'))
        project_id = info['project_id']
        base_url = f'/{project_id}/port/{port}/'
    except Exception as e:
        print(f'Server is probably running in production, so a base url does not apply: \n{e}')
        base_url = '/'
    return base_url

'''
    to run
flask --app server run
    or
python server.py

    to exit 
ctrl + c
'''
global tracker

vision_mode = 1 # 1 is normal, 2 is computer vision, 3 is rainbows and unicorns
port = 5000
base_url = get_base_url(port)

# Flask App
app = Flask(__name__)
# OpenCV Webcam

tracker = mp.MiDaS()
'''@app.route(f"{base_url}", methods=['GET', 'POST'])
def index():
    print("got something at base url")
    return "<p>hello there</p>"'''
# Home Page
@app.route(f"{base_url}", methods=['POST'])
def process():
    global tracker
    print("Loaded API...")
    if request.method == 'POST':
        print("Post Request Received")
        app_json = request.get_json(force=True)
        app_frame = app_json['image']
        
        if app_json['vibrate'] == "false":
            app_vibrate = False
        else:
            app_vibrate = True
        
        if app_json['indoor'] == "false":
            app_indoor = False
        else:
            app_indoor = True
        
        app_frame = str(app_frame)
        image = base64.b64decode(app_frame)
        image = Image.open(io.BytesIO(image))
        image = np.array(image)
        #print(image.shape)
        print("Image Decoded")
        tracker.filter(tracker.normalize(tracker.predict(image)), vibrate="Website", colorful_image=image)
        print("Image Processed")
        
        warning = tracker.current_warning
        amplitude = tracker.amplitude
        duration = tracker.period
        print("Received Parameters: \n  Vibrate ", app_vibrate,"\n  Indoors ", app_indoor)
        
        print("Warning: ", warning)
        print("Amplitude: ", amplitude)
        print("Duration: ", duration)
        pro_image = cv2.imencode('.jpg', tracker.website_image)[1]
        pro_image = base64.b64encode(pro_image)
        #print(pro_image)
        pro_image = str(pro_image)
        pro_image = pro_image[2:-1]
        
        return make_response(jsonify({"image": pro_image, "warning": warning, "amplitude": amplitude, "duration": duration}), 200)
    else:
        print("Receiving Get Request?")
        return make_response(jsonify({"error": "Invalid Request"}), 400)


if __name__ == "__main__":
    app.run(debug=True)
    print("Running")