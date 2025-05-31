from flask import Flask, current_app as app, request, send_from_directory, jsonify
from flask_wtf import CSRFProtect
from flask_cors import CORS
import os
import torch
from PIL import Image
import json
import time
import cv2
from src import helper, utils_rotate
import datetime

app = Flask(__name__)
csrf = CSRFProtect()
csrf.init_app(app)
app.config.from_object('src.config.Config')

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

yolo_LP_detect = torch.hub.load('yolov5', 'custom', 
                                path=app.config['CHECKPOINT_FOLDER'] + '/LP_detector.pt', 
                                force_reload=True, source='local')
yolo_license_plate = torch.hub.load('yolov5', 'custom', 
                                path=app.config['CHECKPOINT_FOLDER']+ '/LP_ocr.pt', 
                                force_reload=True, source='local')
yolo_license_plate.conf = 0.60

CORS(app)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return jsonify({
            "error": "No file"
        })
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({
            "error": "No selected file"
        })
    
    if file and not allowed_file(file.filename):
        return jsonify({
            "error": "File type not supported"
        })

    if 'id_user' not in request.form:
        return jsonify({
            "error": "Not found user id"
        })
    
    try:
        img = Image.open(file.stream)
        img.verify()  
    except Exception:
        return jsonify({
            "error": "File type not supported"
        })
    
    yolo_LP_detect, yolo_license_plate
    id_user = request.form['id_user']
    filename = file.filename
    ext = filename.rsplit('.', 1)[1].lower()

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], id_user + timestamp + '.jpg')

    if ext in ['jpg', 'jpeg', 'png']:
        file.save(image_path)
    else: 
        image = Image.open(file)
        image.save(image_path, format='JPEG')

    img = cv2.imread(image_path)
    start_time = time.time()
    plates = yolo_LP_detect(img, size=640)
    list_plates = plates.pandas().xyxy[0].values.tolist()
    list_read_plates = set()
    lp = "unknown"

    if len(list_plates) == 0:
        lp = helper.read_plate(yolo_license_plate, img)
        if lp != "unknown":
            cv2.putText(img, lp, (7, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36,255,12), 2)
            list_read_plates.add(lp)
    else:
        for plate in list_plates:
            flag = 0
            x = int(plate[0])
            y = int(plate[1])
            w = int(plate[2] - plate[0])
            h = int(plate[3] - plate[1])
            crop_img = img[y:y+h, x:x+w]
            cv2.rectangle(img, (x, y), (x + w, y + h), (0,0,225), 2)

            for cc in range(2):
                for ct in range(2):
                    lp = helper.read_plate(yolo_license_plate, utils_rotate.deskew(crop_img, cc, ct))
                    if lp != "unknown":
                        list_read_plates.add(lp)
                        cv2.putText(img, lp, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36,255,12), 2)
                        flag = 1
                        break
                if flag == 1:
                    break
    end_time = time.time()
    run_time = str(round(end_time - start_time, 2))
    list_read_plates = json.dumps(list(list_read_plates))
    list_read_plates = list_read_plates.replace('"', '')
    list_read_plates = list_read_plates.replace('[', '')
    list_read_plates = list_read_plates.replace(']', '')
    cv2.imwrite(image_path, img)
    return jsonify({
        "result_path": image_path,
        "plate_text": list_read_plates,
        "run_time": run_time
    })

@app.route('/images/<filename>')
def get_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
