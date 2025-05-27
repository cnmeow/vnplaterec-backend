import torch
import pillow_heif
import os

detect_path = os.getenv("DETECT_MODEL_PATH")
ocr_path = os.getenv("OCR_MODEL_PATH")
pillow_heif.register_heif_opener()

yolo_LP_detect = torch.hub.load('yolov5', 'custom', path=detect_path, force_reload=True, source='local')
yolo_license_plate = torch.hub.load('yolov5', 'custom', path=ocr_path, force_reload=True, source='local')
yolo_license_plate.conf = 0.60
