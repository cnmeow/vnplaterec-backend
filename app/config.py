import os

class Config:
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'images')
    CHECKPOINT_FOLDER = os.path.join(os.getcwd(), 'checkpoints')
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'heic'}

    MIN_LP_ACREAGE = 0.02
    MAX_IN_PLANE_ROTATION = 25
