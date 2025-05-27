from flask import Flask
from flask_cors import CORS
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')
    
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    from app.models import load_model
    app.yolo_LP_detect, app.yolo_license_plate = load_model(app.config['CHECKPOINT_FOLDER'])
    
    CORS(app)

    from app.routes import main_bp
    app.register_blueprint(main_bp)
    return app
