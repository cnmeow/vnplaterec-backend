import torch
import pillow_heif

pillow_heif.register_heif_opener()

def load_model(checkpoint_folder):
  yolo_LP_detect = torch.hub.load('yolov5', 'custom', path=checkpoint_folder + '/LP_detector.pt', force_reload=True, source='local')
  yolo_license_plate = torch.hub.load('yolov5', 'custom', path=checkpoint_folder+ '/LP_ocr.pt', force_reload=True, source='local')
  yolo_license_plate.conf = 0.60

  return yolo_LP_detect, yolo_license_plate
