import os

class Config:
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static')
    DETECT_MODEL_PATH = os.getenv("DETECT_MODEL_PATH")
    OCR_MODEL_PATH = os.getenv("OCR_MODEL_PATH")
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'heic'}

    MIN_LP_ACREAGE = 0.02
    MAX_IN_PLANE_ROTATION = 25
