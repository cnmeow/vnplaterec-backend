import os
import torch
from PIL import Image
import json
import time
import cv2
from src import helper, utils_rotate
import datetime
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import boto3
import numpy as np

app = FastAPI()
app.config = {}
app.config['UPLOAD_FOLDER'] = 'images'
app.config['CHECKPOINT_FOLDER'] = 'checkpoints'
app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg', 'png'}

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

BUCKET_NAME = "vnplaterec-bucket"

yolo_LP_detect = torch.hub.load('yolov5', 'custom', 
                                path=app.config['CHECKPOINT_FOLDER'] + '/LP_detector.pt', 
                                force_reload=True, source='local')
yolo_license_plate = torch.hub.load('yolov5', 'custom', 
                                path=app.config['CHECKPOINT_FOLDER']+ '/LP_ocr.pt', 
                                force_reload=True, source='local')
yolo_license_plate.conf = 0.60
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.post("/predict")
async def predict(
    image: UploadFile = File(...),
    id_user: str = Form(...)
):
    if not image or image is None:
        return JSONResponse(status_code=400, content={
            "error": "No file part"
        })
    
    if image.filename == '':
        return JSONResponse(status_code=400, content={
            "error": "No file"
        })
    
    if image and not allowed_file(image.filename):
        return JSONResponse(status_code=400, content={
            "error": "File type not supported"
        })

    if not id_user or id_user.strip() == "":
        return JSONResponse(status_code=400, content={
            "error": "User ID is required"
        })
    image_bytes = await image.read()
    if not image_bytes:
        return JSONResponse(status_code=400, content={
            "error": "Empty file"
        })

    filename = image.filename
    ext = filename.rsplit('.', 1)[1].lower()

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    image_path = app.config['UPLOAD_FOLDER'] + '/' + id_user + timestamp + '.jpg'

    with open(image_path, 'wb') as f:
        f.write(image_bytes)

    img = Image.open(image_path)
    img = img.convert('RGB')
    img.save(image_path, 'JPEG')

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

    if id_user == "test":
        return JSONResponse(status_code=200, content={
            "result_path": image_path,
            "plate_text": list_read_plates,
            "run_time": run_time
        })
        
    s3_client = boto3.client("s3", region_name="us-east-1")  
    s3_client.upload_fileobj(
        open(image_path, 'rb'),
        BUCKET_NAME,
        image_path,
        ExtraArgs={'ContentType': 'image/jpeg'}
    )

    url = s3_client.generate_presigned_url(
        ClientMethod="get_object",
        Params={"Bucket": BUCKET_NAME, "Key": image_path},
        ExpiresIn=3600
    )

    os.remove(image_path)
    return JSONResponse(status_code=200, content={
        "result_path": url,
        "plate_text": list_read_plates,
        "run_time": run_time
    })

@app.get('/health')
async def health_check():
    return JSONResponse(status_code=200, content={"status": "ok"})