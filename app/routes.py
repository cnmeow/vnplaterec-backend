from flask import Blueprint, render_template, request, redirect, flash, current_app as app, jsonify
import os
from PIL import Image
import cv2
import time
from app.ml_models import yolo_LP_detect, yolo_license_plate
from app import utils_rotate, helper

main_bp = Blueprint('main', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@main_bp.route('/', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({
            "error": "No file"
        })
    
    file = request.files['file']
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
    id_user = request.form['id_user']
    
    filename = file.filename
    ext = filename.rsplit('.', 1)[1].lower()
    upload_path = os.path.join(app.config['UPLOAD_FOLDER'], id_user + '_upload.jpg')

    if ext in ['jpg', 'jpeg', 'png']:
        file.save(upload_path)
    else: 
        image = Image.open(file)
        image.save(upload_path, format='JPEG')

    img = cv2.imread(upload_path)
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

    result_path = os.path.join(app.config['UPLOAD_FOLDER'], id_user + '_result.jpg')
    cv2.imwrite(result_path, img)
    return jsonify({
        "upload_path": upload_path,
        "result_path": result_path,
        "run_time": run_time
    })